"""Fixed study settings. Values mirror PREREGISTRATION.md v1; change them only via a recorded amendment."""
import pandas as pd

DEV_START = pd.Timestamp("2000-01-01")
DEV_END = pd.Timestamp("2021-12-31")
SEAL_START = pd.Timestamp("2022-01-01")
FIRST_FORECAST = pd.Timestamp("2006-01-01")
REFIT_EVERY = 22

PRIMARY_MARKETS = {"SPX": "^GSPC", "TAIEX": "^TWII"}
AUX_MARKETS = {
    "N225": "^N225",
    "STOXX50": "^STOXX50E",
    "UST10Y": "^TNX",
    "GOLD": "GC=F",
    "USDTWD": "TWD=X",
}
EXOGENOUS = {"VIX": "^VIX", "TBILL3M": "^IRX"}

RV_HORIZONS = (1, 5, 22)
DIRECTION_HORIZONS = (1, 5, 22)
SHORT_DD_HORIZON, SHORT_DD_THRESHOLD = 20, -0.10
CRISIS_HORIZON, CRISIS_LOOKBACK = 60, 252
CRISIS_THRESHOLDS = {"C1": -0.20, "C2": -0.10}

PHI = 1.618033988749895
