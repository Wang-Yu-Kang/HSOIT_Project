"""Losses and forecast-comparison tests from PREREGISTRATION.md section 8."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

EPS = 1e-6


def qlike(y: pd.Series, f: pd.Series) -> pd.Series:
    ratio = y / f
    return ratio - np.log(ratio) - 1


def mse_log(y: pd.Series, f: pd.Series) -> pd.Series:
    return (np.log(y) - np.log(f)) ** 2


def brier(y: pd.Series, p: pd.Series) -> pd.Series:
    return (p - y) ** 2


def log_loss(y: pd.Series, p: pd.Series) -> pd.Series:
    p = p.clip(EPS, 1 - EPS)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def hit_rate(y: pd.Series, p: pd.Series) -> float:
    return float(((p > 0.5).astype(float) == y).mean())


def auc(y: pd.Series, p: pd.Series) -> float:
    """Rank-based AUC (Mann–Whitney); NaN when only one class is present."""
    pos, neg = p[y == 1], p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    ranks = pd.concat([pos, neg]).rank()
    return float((ranks.iloc[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def skill(loss_model: pd.Series, loss_baseline: pd.Series) -> float:
    a, b = loss_model.align(loss_baseline, join="inner")
    return float(1 - a.mean() / b.mean())


def newey_west_var(d: np.ndarray, lags: int) -> float:
    d = d - d.mean()
    T = len(d)
    v = d @ d / T
    for k in range(1, lags + 1):
        v += 2 * (1 - k / (lags + 1)) * (d[k:] @ d[:-k]) / T
    return v


def dm_test(loss_a: pd.Series, loss_b: pd.Series, h: int) -> tuple[float, float]:
    """One-sided Diebold–Mariano with the Harvey–Leybourne–Newbold correction.

    H1: model a has lower expected loss than model b. Returns (statistic, p-value).
    """
    a, b = loss_a.align(loss_b, join="inner")
    d = (a - b).dropna().to_numpy()
    T = len(d)
    v = newey_west_var(d, max(h - 1, 0))
    if v <= 0:
        return float("nan"), float("nan")
    stat = d.mean() / np.sqrt(v / T)
    stat *= np.sqrt((T + 1 - 2 * h + h * (h - 1) / T) / T)
    return float(stat), float(stats.t.cdf(stat, df=T - 1))


def skill_ci(loss_model: pd.Series, loss_baseline: pd.Series, block: int = 22, reps: int = 999, level: float = 0.90, seed: int = 0):
    """Stationary-bootstrap confidence interval for the skill score."""
    from arch.bootstrap import StationaryBootstrap

    a, b = loss_model.align(loss_baseline, join="inner")
    bs = StationaryBootstrap(block, a.to_numpy(), b.to_numpy(), seed=seed)
    draws = np.array([1 - x.mean() / y.mean() for (x, y), _ in bs.bootstrap(reps)])
    lo, hi = np.quantile(draws, [(1 - level) / 2, (1 + level) / 2])
    return float(lo), float(hi)


def model_confidence_set(losses: pd.DataFrame, size: float = 0.10, block: int = 22, reps: int = 999, seed: int = 0) -> list[str]:
    from arch.bootstrap import MCS

    mcs = MCS(losses.dropna(), size=size, block_size=block, reps=reps, seed=seed)
    mcs.compute()
    return list(mcs.included)


def spa_test(benchmark_loss: pd.Series, model_losses: pd.DataFrame, block: int = 22, reps: int = 999, seed: int = 0) -> float:
    """Hansen SPA consistent p-value for H0: no model beats the benchmark."""
    from arch.bootstrap import SPA

    df = model_losses.join(benchmark_loss.rename("__bench__"), how="inner").dropna()
    spa = SPA(df["__bench__"], df.drop(columns="__bench__"), block_size=block, reps=reps, seed=seed)
    spa.compute()
    return float(spa.pvalues["consistent"])


def holm(pvalues: dict[str, float]) -> dict[str, float]:
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m, running, out = len(items), 0.0, {}
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out
