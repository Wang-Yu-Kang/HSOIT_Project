import numpy as np
import pandas as pd

from hsoit_fm import baselines as bl
from hsoit_fm import targets as tg
from hsoit_fm.data import apply_seal
from hsoit_fm.features import base_features
from hsoit_fm.walkforward import walk_forward


def _pipeline(ohlc, h=5):
    df = apply_seal(ohlc)
    X = base_features(df)
    y = tg.forward_rv(X["gk_var"], h)
    return df, X, y


def test_embargo_training_labels_end_h_rows_before_origin(ohlc):
    h = 22
    _, X, y = _pipeline(ohlc, h)
    audit = []
    walk_forward(X[bl.HAR_COLS], y, h, bl.har_fit, bl.har_predict, audit=audit)
    pos = {d: i for i, d in enumerate(X.index)}
    assert audit
    for origin, last_train in audit:
        assert pos[last_train] <= pos[origin] - h


def _no_lookahead(ohlc, make_forecasts, cut="2012-06-01"):
    cut = pd.Timestamp(cut)
    base = make_forecasts(ohlc)
    shocked = ohlc.copy()
    later = shocked.index >= cut
    shocked.loc[later, ["open", "high", "low", "close"]] *= np.linspace(1, 3, later.sum())[:, None]
    shocked.loc[later, "high"] *= 1.05
    alt = make_forecasts(shocked)
    a, b = base[base.index < cut], alt[alt.index < cut]
    assert len(a) > 100
    pd.testing.assert_series_equal(a, b)


def test_har_has_no_lookahead(ohlc):
    def run(df):
        _, X, y = _pipeline(df)
        return walk_forward(X[bl.HAR_COLS], y, 5, bl.har_fit, bl.har_predict)

    _no_lookahead(ohlc, run)


def test_garch_has_no_lookahead(ohlc):
    small = ohlc.loc[:"2013-12-31"]

    def run(df):
        _, X, y = _pipeline(df)
        return bl.garch_walk_forward(X["ret"], y, 5, first=pd.Timestamp("2010-01-01"), every=66)

    _no_lookahead(small, run)


def test_logit_event_has_no_lookahead(ohlc):
    def run(df):
        df = apply_seal(df)
        X = base_features(df)
        y = tg.short_drawdown_event(df["close"], 20, -0.05)
        cols = ["log_rv_m", "dd252"]
        fit, pred = bl.logit_factory(cols)
        return walk_forward(X[cols], y, 20, fit, pred)

    _no_lookahead(ohlc, run)
