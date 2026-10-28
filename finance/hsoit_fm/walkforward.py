"""Expanding-window walk-forward with the label embargo from PREREGISTRATION.md section 5.

At a refit origin p (a row position), the model may train only on rows q <= p - h,
because the label at q needs data through q + h.
"""
from __future__ import annotations

from typing import Callable

import pandas as pd

from .config import FIRST_FORECAST, REFIT_EVERY

Fit = Callable[[pd.DataFrame, pd.Series], object]
Predict = Callable[[object, pd.DataFrame], pd.Series]


def refit_origins(index: pd.DatetimeIndex, first=FIRST_FORECAST, every: int = REFIT_EVERY) -> list[int]:
    start = int(index.searchsorted(first))
    return list(range(start, len(index), every))


def walk_forward(
    X: pd.DataFrame,
    y: pd.Series,
    h: int,
    fit: Fit,
    predict: Predict,
    first=FIRST_FORECAST,
    every: int = REFIT_EVERY,
    audit: list | None = None,
) -> pd.Series:
    X = X.loc[y.index] if not X.index.equals(y.index) else X
    idx = X.index
    out = []
    for p in refit_origins(idx, first, every):
        train_end = p - h
        if train_end < 0:
            continue
        Xt, yt = X.iloc[: train_end + 1], y.iloc[: train_end + 1]
        ok = Xt.notna().all(axis=1) & yt.notna()
        if ok.sum() < 50:
            continue
        model = fit(Xt[ok], yt[ok])
        Xb = X.iloc[p : p + every]
        Xb = Xb[Xb.notna().all(axis=1)]
        if Xb.empty:
            continue
        if audit is not None:
            audit.append((idx[p], Xt[ok].index.max()))
        out.append(predict(model, Xb))
    if not out:
        return pd.Series(dtype=float, name=y.name)
    return pd.concat(out).rename(y.name)
