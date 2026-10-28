import numpy as np
import pandas as pd

from hsoit_fm import targets as tg

IDX = pd.bdate_range("2020-01-01", periods=8)


def test_forward_rv_uses_next_h_days_only():
    var = pd.Series([1, 2, 3, 4, 5, 6, 7, 8], index=IDX, dtype=float)
    rv = tg.forward_rv(var, 3)
    assert rv.iloc[0] == 3.0  # mean of 2, 3, 4
    assert rv.iloc[4] == 7.0
    assert rv.iloc[5:].isna().all()


def test_direction():
    close = pd.Series([10, 11, 10.5, 10.5, 12, 11, 11, 13], index=IDX, dtype=float)
    up = tg.direction(close, 1)
    assert up.iloc[:4].tolist() == [1.0, 0.0, 0.0, 1.0]
    assert np.isnan(up.iloc[-1])


def test_short_drawdown_event():
    close = pd.Series([100, 99, 89, 95, 100, 100, 100, 100], index=IDX, dtype=float)
    ev = tg.short_drawdown_event(close, h=2, threshold=-0.10)
    assert ev.iloc[0] == 1.0  # 89 / 100 - 1 = -11%
    assert ev.iloc[1] == 1.0  # 89 / 99 - 1 = -10.1%
    assert ev.iloc[2] == 0.0


def test_crisis_onset_excludes_days_already_in_drawdown():
    close = pd.Series([100, 100, 85, 70, 75, 80, 80, 80], index=IDX, dtype=float)
    c = tg.crisis_onset(close, -0.20, horizon=2, lookback=252)
    assert c.iloc[0] == 0.0  # window: 100, 85 -> -15%
    assert c.iloc[1] == 1.0  # window: 85, 70 -> -30%
    assert c.iloc[2] == 1.0  # at -15%, then -30%
    assert np.isnan(c.iloc[3])  # already -30%: excluded


def test_gk_variance_positive(ohlc):
    v = tg.gk_variance(ohlc)
    assert (v > 0).all()
