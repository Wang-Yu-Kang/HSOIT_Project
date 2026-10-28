"""Phase-0 baseline run on the development period (2006 forecasts onward, through 2021).

Usage, from the finance/ directory:
    python -m scripts.run_baselines            # both primary markets
    python -m scripts.run_baselines --market SPX

Writes results/forecasts_<market>.csv and results/BASELINES_DEV.md. The best
baseline per target chosen here becomes the reference for the skill scores.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from hsoit_fm import baselines as bl
from hsoit_fm import evaluate as ev
from hsoit_fm import targets as tg
from hsoit_fm.config import (
    CRISIS_HORIZON,
    CRISIS_THRESHOLDS,
    DIRECTION_HORIZONS,
    EXOGENOUS,
    PRIMARY_MARKETS,
    RV_HORIZONS,
    SHORT_DD_HORIZON,
    SHORT_DD_THRESHOLD,
)
from hsoit_fm.data import load
from hsoit_fm.features import align_exogenous, base_features
from hsoit_fm.walkforward import walk_forward

RESULTS = Path(__file__).resolve().parents[1] / "results"
# The US closes after Taiwan on the same calendar day, so US inputs lag one day there.
US_LAG = {"SPX": 0, "TAIEX": 1}


def build(market: str):
    df = load(PRIMARY_MARKETS[market])
    lag = US_LAG[market]
    vix = align_exogenous(load(EXOGENOUS["VIX"])["close"], df.index, lag)
    tnx = align_exogenous(load("^TNX")["close"], df.index, lag)
    irx = align_exogenous(load(EXOGENOUS["TBILL3M"])["close"], df.index, lag)
    X = base_features(df, vix=vix, slope=tnx - irx)
    return df, X


def run_market(market: str) -> tuple[pd.DataFrame, list[dict]]:
    df, X = build(market)
    close = df["close"]
    forecasts, rows = {}, []

    def record(target, h, y, preds, kind):
        for name, f in preds.items():
            forecasts[f"{target}|{name}"] = f
        losses = {}
        for name, f in preds.items():
            yy, ff = y.align(f, join="inner")
            ok = yy.notna() & ff.notna()
            yy, ff = yy[ok], ff[ok]
            if kind == "var":
                losses[name] = ev.qlike(yy, ff)
                rows.append(dict(market=market, target=target, model=name, n=len(yy),
                                 qlike=losses[name].mean(), mse_log=ev.mse_log(yy, ff).mean()))
            else:
                losses[name] = ev.brier(yy, ff) if kind == "event" else ev.log_loss(yy, ff)
                rows.append(dict(market=market, target=target, model=name, n=len(yy),
                                 brier=ev.brier(yy, ff).mean(), log_loss=ev.log_loss(yy, ff).mean(),
                                 auc=ev.auc(yy, ff), hit=ev.hit_rate(yy, ff), base_rate=yy.mean()))
        best = min(losses, key=lambda k: losses[k].mean())
        for r in rows:
            if r["market"] == market and r["target"] == target:
                r["best"] = r["model"] == best
                if r["model"] != best:
                    _, r["dm_p_vs_best"] = ev.dm_test(losses[best], losses[r["model"]], h)

    # A1: realised variance
    for h in RV_HORIZONS:
        y = tg.forward_rv(X["gk_var"], h)
        preds = {
            "HAR-RV": walk_forward(X[bl.HAR_COLS], y, h, bl.har_fit, bl.har_predict),
            "EWMA": walk_forward(X[["ewma_var"]], y, h, bl.ewma_fit, bl.ewma_predict),
            "GARCH-t": bl.garch_walk_forward(X["ret"], y, h),
        }
        record(f"A1_rv{h}", h, y, preds, "var")

    # A2: 20-day 10% drawdown
    y = tg.short_drawdown_event(close, SHORT_DD_HORIZON, SHORT_DD_THRESHOLD)
    cols = ["log_rv_m", "dd252"] + (["log_vix"] if market == "SPX" else [])
    fit, pred = bl.logit_factory(cols)
    preds = {
        "frequency": walk_forward(X[cols], y, SHORT_DD_HORIZON, bl.frequency_fit, bl.frequency_predict),
        "logit-EW": walk_forward(X[cols], y, SHORT_DD_HORIZON, fit, pred),
    }
    record("A2_dd20", SHORT_DD_HORIZON, y, preds, "event")

    # B1: direction
    for h in DIRECTION_HORIZONS:
        y = tg.direction(close, h)
        cols = ["r22", "r252"]
        fit, pred = bl.logit_factory(cols)
        preds = {
            "frequency": walk_forward(X[cols], y, h, bl.frequency_fit, bl.frequency_predict),
            "momentum-logit": walk_forward(X[cols], y, h, fit, pred),
        }
        record(f"B1_up{h}", h, y, preds, "direction")

    # C1 / C2: crisis onset
    for label, thr in CRISIS_THRESHOLDS.items():
        y = tg.crisis_onset(close, thr, CRISIS_HORIZON)
        cols = ["dd252", "log_rv_m", "slope"] + (["log_vix"] if market == "SPX" else [])
        fit, pred = bl.logit_factory(cols)
        preds = {
            "frequency": walk_forward(X[cols], y, CRISIS_HORIZON, bl.frequency_fit, bl.frequency_predict),
            "logit-EW": walk_forward(X[cols], y, CRISIS_HORIZON, fit, pred),
        }
        record(label, CRISIS_HORIZON, y, preds, "event")

    return pd.DataFrame(forecasts), rows


def to_markdown(table: pd.DataFrame) -> str:
    lines = [
        "# 開發期基準模型結果",
        "",
        "由 `scripts/run_baselines.py` 產生。樣本外預測自 2006 年起，至 2021-12-31 為止，封存期未開啟。",
        "`best` 標記每個目標損失最低的基準，作為之後技能分數的參照。`dm_p_vs_best` 是最佳基準勝過該模型的單尾 DM 檢定 p 值。",
        "",
    ]
    for (market, target), g in table.groupby(["market", "target"], sort=False):
        lines.append(f"## {market} · {target}")
        lines.append("")
        g = g.drop(columns=["market", "target"]).dropna(axis=1, how="all")
        lines.append(g.to_markdown(index=False, floatfmt=".4g"))
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", choices=list(PRIMARY_MARKETS), action="append")
    args = ap.parse_args()
    RESULTS.mkdir(exist_ok=True)
    all_rows = []
    for m in args.market or list(PRIMARY_MARKETS):
        fc, rows = run_market(m)
        fc.to_csv(RESULTS / f"forecasts_{m}.csv")
        all_rows += rows
    table = pd.DataFrame(all_rows)
    table.to_csv(RESULTS / "baselines_dev.csv", index=False)
    (RESULTS / "BASELINES_DEV.md").write_text(to_markdown(table), encoding="utf-8")
    print(table.to_string())


if __name__ == "__main__":
    np.seterr(all="ignore")
    main()
