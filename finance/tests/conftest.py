import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def synthetic_ohlc(start="2000-01-03", end="2023-12-29", seed=0) -> pd.DataFrame:
    """GARCH(1,1)-driven price path with OHLC bars; for testing code paths only."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, end)
    n = len(idx)
    w, a, b = 2e-6, 0.08, 0.9
    var, r = np.empty(n), np.empty(n)
    var[0] = w / (1 - a - b)
    for t in range(n):
        if t:
            var[t] = w + a * r[t - 1] ** 2 + b * var[t - 1]
        r[t] = np.sqrt(var[t]) * rng.standard_normal()
    close = 1000 * np.exp(np.cumsum(r))
    open_ = close * np.exp(-r * rng.uniform(0.2, 0.8, n))
    spread = np.sqrt(var) * np.abs(rng.standard_normal((2, n)))
    high = np.maximum(open_, close) * np.exp(spread[0])
    low = np.minimum(open_, close) * np.exp(-spread[1])
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": 1.0}, index=idx)


@pytest.fixture
def ohlc():
    return synthetic_ohlc()
