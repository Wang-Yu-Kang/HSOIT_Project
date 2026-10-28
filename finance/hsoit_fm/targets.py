"""Forecast targets, exactly as defined in PREREGISTRATION.md section 2.

Each target at date t only looks at t+1 onward; rows whose window runs past the
end of the data are NaN, never partially filled.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def gk_variance(df: pd.DataFrame) -> pd.Series:
    """Garman–Klass daily variance from open, high, low, close."""
    hl = np.log(df["high"] / df["low"])
    co = np.log(df["close"] / df["open"])
    var = 0.5 * hl**2 - (2 * np.log(2) - 1) * co**2
    return var.clip(lower=1e-12).rename("gk_var")


def _forward_window(s: pd.Series, h: int) -> pd.DataFrame:
    return pd.concat({i: s.shift(-i) for i in range(1, h + 1)}, axis=1)


def forward_rv(var: pd.Series, h: int) -> pd.Series:
    """A1: mean daily variance over t+1..t+h."""
    w = _forward_window(var, h)
    return w.mean(axis=1, skipna=False).rename(f"rv_{h}")


def short_drawdown_event(close: pd.Series, h: int = 20, threshold: float = -0.10) -> pd.Series:
    """A2: any close in t+1..t+h at or below (1 + threshold) * close_t."""
    w = _forward_window(close, h)
    worst = w.min(axis=1, skipna=False) / close - 1
    out = (worst <= threshold).astype(float)
    return out.where(worst.notna()).rename(f"dd{h}")


def direction(close: pd.Series, h: int) -> pd.Series:
    """B1: 1 if log close rises from t to t+h."""
    r = np.log(close.shift(-h) / close)
    return (r > 0).astype(float).where(r.notna()).rename(f"up_{h}")


def drawdown_from_high(close: pd.Series, lookback: int = 252) -> pd.Series:
    peak = close.rolling(lookback, min_periods=1).max()
    return (close / peak - 1).rename("dd_high")


def crisis_onset(close: pd.Series, threshold: float, horizon: int = 60, lookback: int = 252) -> pd.Series:
    """C1/C2: not yet below threshold at t, and drawdown from the 252-day high reaches it within t+1..t+horizon.

    Days already at or below the threshold are NaN (excluded from evaluation).
    """
    dd = drawdown_from_high(close, lookback)
    w = _forward_window(dd, horizon)
    worst = w.min(axis=1, skipna=False)
    out = (worst <= threshold).astype(float)
    return out.where(worst.notna() & (dd > threshold)).rename(f"crisis_{int(-threshold * 100)}")
