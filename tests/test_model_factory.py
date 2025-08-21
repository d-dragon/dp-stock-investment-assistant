import pytest
from core.model_factory import ModelClientFactory

def test_get_client_returns_openai_by_default(tmp_path, monkeypatch):
    cfg = {"model": {"provider": "openai"}}
    client = ModelClientFactory.get_client(cfg)
    assert client.provider == "openai"
    # repeated call uses cache (same key)
    client2 = ModelClientFactory.get_client(cfg)
    assert client is client2