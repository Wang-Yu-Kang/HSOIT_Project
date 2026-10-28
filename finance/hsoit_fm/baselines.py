"""Baseline models from PREREGISTRATION.md section 7.

Each baseline is a (fit, predict) pair for `walk_forward`, except GARCH, which
filters the return series itself and so has its own walk-forward loop.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .config import FIRST_FORECAST, REFIT_EVERY
from .walkforward import refit_origins

HAR_COLS = ["log_rv_d", "log_rv_w", "log_rv_m"]


# --- A1 variance baselines -------------------------------------------------

def har_fit(X: pd.DataFrame, y: pd.Series):
    A = np.column_stack([np.ones(len(X)), X[HAR_COLS].to_numpy()])
    z = np.log(y.to_numpy())
    beta, *_ = np.linalg.lstsq(A, z, rcond=None)
    resid = z - A @ beta
    return beta, resid.var()


def har_predict(model, X: pd.DataFrame) -> pd.Series:
    beta, s2 = model
    A = np.column_stack([np.ones(len(X)), X[HAR_COLS].to_numpy()])
    return pd.Series(np.exp(A @ beta + s2 / 2), index=X.index)


def ewma_fit(X: pd.DataFrame, y: pd.Series):
    # Close-to-close EWMA and the Garman–Klass target differ in level, so the
    # one level constant is taken from the training window.
    return float((y / X["ewma_var"]).mean())


def ewma_predict(scale, X: pd.DataFrame) -> pd.Series:
    return scale * X["ewma_var"]


def garch_walk_forward(
    ret: pd.Series,
    y: pd.Series,
    h: int,
    first=FIRST_FORECAST,
    every: int = REFIT_EVERY,
) -> pd.Series:
    """GARCH(1,1) with Student-t errors; mean of the 1..h step variance forecasts."""
    from arch import arch_model

    r = (100 * ret).dropna()
    y = y.reindex(r.index)
    out = []
    for p in refit_origins(r.index, first, every):
        if p - h < 250:
            continue
        am = arch_model(r, mean="Constant", vol="GARCH", p=1, q=1, dist="t")
        # last_obs is exclusive, so p + 1 estimates on returns through the origin p.
        res = am.fit(last_obs=p + 1 if p + 1 < len(r) else None, disp="off")
        fc = res.forecast(horizon=h, start=r.index[0], reindex=False).variance.mean(axis=1) / 1e4
        train = fc.iloc[: p - h + 1]
        ok = y.iloc[: p - h + 1].notna()
        scale = float((y.iloc[: p - h + 1][ok] / train[ok]).mean())
        out.append(scale * fc.iloc[p : p + every])
    return pd.concat(out).rename(y.name)


# --- probability baselines ------------------------------------------------

def frequency_fit(X: pd.DataFrame, y: pd.Series):
    return float(y.mean())


def frequency_predict(p, X: pd.DataFrame) -> pd.Series:
    return pd.Series(p, index=X.index)


def logit_factory(cols: list[str], l2: float = 1.0):
    """L2-penalised logistic regression on standardised `cols`."""

    def fit(X: pd.DataFrame, y: pd.Series):
        Z = X[cols].to_numpy(float)
        mu, sd = Z.mean(0), Z.std(0)
        sd[sd == 0] = 1.0
        Z = np.column_stack([np.ones(len(Z)), (Z - mu) / sd])
        t = y.to_numpy(float)

        def nll(w):
            s = Z @ w
            return np.sum(np.logaddexp(0, s) - t * s) + 0.5 * l2 * np.sum(w[1:] ** 2)

        def grad(w):
            p = 1 / (1 + np.exp(-(Z @ w)))
            g = Z.T @ (p - t)
            g[1:] += l2 * w[1:]
            return g

        w0 = np.zeros(Z.shape[1])
        base = np.clip(t.mean(), 1e-4, 1 - 1e-4)
        w0[0] = np.log(base / (1 - base))
        w = minimize(nll, w0, jac=grad, method="L-BFGS-B").x
        return w, mu, sd

    def predict(model, X: pd.DataFrame) -> pd.Series:
        w, mu, sd = model
        Z = (X[cols].to_numpy(float) - mu) / sd
        s = w[0] + Z @ w[1:]
        return pd.Series(1 / (1 + np.exp(-s)), index=X.index)

    return fit, predict
