"""Daily OHLC loading with the sealed-period lock from PREREGISTRATION.md section 4.

Every loader path ends in `apply_seal`, so nothing on or after SEAL_START reaches
model code unless the study has been formally unsealed.
"""
from __future__ import annotations

import datetime as dt
import os
import subprocess
from pathlib import Path

import pandas as pd

from .config import DEV_START, SEAL_START

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
UNSEAL_LOG = ROOT / "UNSEAL_LOG.md"
COLUMNS = ["open", "high", "low", "close", "volume"]


class SealedDataError(RuntimeError):
    pass


def _tag_exists(tag: str) -> bool:
    out = subprocess.run(["git", "-C", str(ROOT), "tag", "-l", tag], capture_output=True, text=True)
    return out.stdout.strip() == tag


def unsealed() -> str | None:
    """Return the freeze tag if the sealed period is formally open, else None."""
    tag = os.environ.get("HSOIT_UNSEAL", "")
    if not tag:
        return None
    if not tag.startswith("freeze-v") or not _tag_exists(tag):
        raise SealedDataError(f"HSOIT_UNSEAL={tag!r} does not name an existing freeze-v* git tag")
    return tag


def _log_unseal(tag: str, what: str) -> None:
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with UNSEAL_LOG.open("a", encoding="utf-8") as f:
        f.write(f"- {stamp} · {tag} · {what}\n")


def apply_seal(df: pd.DataFrame, name: str = "") -> pd.DataFrame:
    tag = unsealed()
    if tag is None:
        return df.loc[df.index < SEAL_START]
    _log_unseal(tag, f"read {name or 'frame'} through {df.index.max().date()}")
    return df


def _cache_path(ticker: str) -> Path:
    safe = "".join(c if c.isalnum() else "_" for c in ticker)
    return RAW_DIR / f"{safe}.csv"


def _normalise(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df = df.droplevel(1, axis=1)
    df = df.rename(columns=str.lower)
    df = df[[c for c in COLUMNS if c in df.columns]]
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    df.index.name = "date"
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df.dropna(subset=["close"])


def download(ticker: str) -> pd.DataFrame:
    """Fetch from Yahoo Finance. While sealed, the request itself stops before SEAL_START."""
    import yfinance as yf

    end = None if unsealed() else SEAL_START
    df = yf.download(ticker, start=DEV_START, end=end, progress=False, auto_adjust=False)
    if df.empty:
        raise RuntimeError(f"no data returned for {ticker}")
    return _normalise(df)


def load(ticker: str, refresh: bool = False) -> pd.DataFrame:
    """Load daily OHLC for `ticker` from the local cache, downloading if missing.

    A CSV with columns date, open, high, low, close[, volume] can be placed at
    data/raw/<ticker>.csv by hand when the network cannot reach Yahoo.
    """
    path = _cache_path(ticker)
    if refresh or not path.exists():
        df = download(ticker)
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(path)
    else:
        df = _normalise(pd.read_csv(path, index_col=0, parse_dates=True))
    return apply_seal(df.loc[df.index >= DEV_START], ticker)
