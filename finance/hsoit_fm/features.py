"""Causal predictors shared by the baselines (everything at t uses data through t only)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .targets import drawdown_from_high, gk_variance


def align_exogenous(series: pd.Series, index: pd.DatetimeIndex, lag: int = 0) -> pd.Series:
    """Put another market's series on `index`, carrying the last known value forward.

    lag=1 is used when the other market closes after the target market on the same
    calendar day (for example US data against the Taiwan close).
    """
    s = series.reindex(series.index.union(index)).ffill().reindex(index)
    return s.shift(lag)


def base_features(df: pd.DataFrame, vix: pd.Series | None = None, slope: pd.Series | None = None) -> pd.DataFrame:
    var = gk_variance(df)
    close = df["close"]
    ret = np.log(close).diff()
    out = pd.DataFrame(index=df.index)
    out["ret"] = ret
    out["gk_var"] = var
    out["log_rv_d"] = np.log(var)
    out["log_rv_w"] = np.log(var.rolling(5).mean())
    out["log_rv_m"] = np.log(var.rolling(22).mean())
    out["ewma_var"] = (ret**2).ewm(alpha=1 - 0.94, adjust=False).mean()
    out["r22"] = np.log(close / close.shift(22))
    out["r252"] = np.log(close / close.shift(252))
    out["dd252"] = drawdown_from_high(close, 252)
    if vix is not None:
        out["log_vix"] = np.log(vix)
    if slope is not None:
        out["slope"] = slope
    return out
