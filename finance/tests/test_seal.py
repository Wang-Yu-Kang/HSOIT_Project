import pandas as pd
import pytest

from hsoit_fm import data
from hsoit_fm.config import SEAL_START


@pytest.fixture
def cache(tmp_path, monkeypatch, ohlc):
    monkeypatch.setattr(data, "RAW_DIR", tmp_path)
    monkeypatch.setattr(data, "UNSEAL_LOG", tmp_path / "UNSEAL_LOG.md")
    ohlc.to_csv(tmp_path / "TEST.csv")
    return tmp_path


def test_load_truncates_at_seal(cache, monkeypatch):
    monkeypatch.delenv("HSOIT_UNSEAL", raising=False)
    df = data.load("TEST")
    assert df.index.max() < SEAL_START
    assert df.index.max() >= pd.Timestamp("2021-12-30")


def test_unseal_requires_existing_freeze_tag(cache, monkeypatch):
    monkeypatch.setenv("HSOIT_UNSEAL", "freeze-v999-does-not-exist")
    with pytest.raises(data.SealedDataError):
        data.load("TEST")
    monkeypatch.setenv("HSOIT_UNSEAL", "anything-else")
    with pytest.raises(data.SealedDataError):
        data.load("TEST")


def test_unseal_with_tag_is_logged(cache, monkeypatch):
    monkeypatch.setattr(data, "_tag_exists", lambda tag: True)
    monkeypatch.setenv("HSOIT_UNSEAL", "freeze-v1")
    df = data.load("TEST")
    assert df.index.max() >= SEAL_START
    assert "freeze-v1" in (cache / "UNSEAL_LOG.md").read_text()
