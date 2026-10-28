import numpy as np
import pandas as pd

from hsoit_fm import baselines as bl
from hsoit_fm import evaluate as ev


def test_har_recovers_coefficients():
    rng = np.random.default_rng(1)
    n = 4000
    X = pd.DataFrame(rng.standard_normal((n, 3)), columns=bl.HAR_COLS)
    z = -1 + X @ np.array([0.4, 0.3, 0.2]) + 0.1 * rng.standard_normal(n)
    beta, _ = bl.har_fit(X, np.exp(z))
    np.testing.assert_allclose(beta, [-1, 0.4, 0.3, 0.2], atol=0.02)


def test_logit_recovers_direction_of_effect():
    rng = np.random.default_rng(2)
    X = pd.DataFrame({"a": rng.standard_normal(5000), "b": rng.standard_normal(5000)})
    p = 1 / (1 + np.exp(-(-1 + 1.5 * X["a"])))
    y = pd.Series((rng.uniform(size=5000) < p).astype(float))
    fit, pred = bl.logit_factory(["a", "b"], l2=0.1)
    w, mu, sd = fit(X, y)
    assert w[1] > 1.0 and abs(w[2]) < 0.15
    assert ev.auc(y, pred((w, mu, sd), X)) > 0.75


def test_dm_detects_better_model():
    rng = np.random.default_rng(3)
    base = pd.Series(rng.exponential(1.0, 3000))
    better = base * 0.9
    _, p = ev.dm_test(better, base, h=1)
    assert p < 0.01
    _, p = ev.dm_test(base, better, h=1)
    assert p > 0.99


def test_qlike_minimised_at_truth():
    y = pd.Series([1.0, 2.0, 3.0])
    assert ev.qlike(y, y).abs().max() < 1e-12
    assert (ev.qlike(y, y * 1.2) > 0).all()


def test_skill_and_holm():
    a, b = pd.Series([1.0, 1.0]), pd.Series([2.0, 2.0])
    assert ev.skill(a, b) == 0.5
    adj = ev.holm({"x": 0.01, "y": 0.04, "z": 0.03})
    assert adj == {"x": 0.03, "z": 0.06, "y": 0.06}
