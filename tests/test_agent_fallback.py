import pytest
from core.agent import StockAgent
from core.model_factory import ModelClientFactory
from core.base_model_client import BaseModelClient


class StubFailClient(BaseModelClient):
    provider = "grok"
    model_name = "grok-fail"

    def generate(self, prompt, context=None):
        raise RuntimeError("simulated failure")

    def generate_stream(self, prompt, context=None):
        raise RuntimeError("simulated failure")


class StubOKClient(BaseModelClient):
    provider = "openai"
    model_name = "openai-ok"

    def generate(self, prompt, context=None):
        return "ok-response"

    def generate_stream(self, prompt, context=None):
        yield "ok-response"


def test_agent_fallback(monkeypatch):
    cfg = {"model": {"provider": "grok", "allow_fallback": True, "fallback_order": ["openai"]}}
    # monkeypatch factory to return failing client for grok and OK for openai
    def fake_get_client(config, provider=None, model_name=None):
        if provider == "grok" or (provider is None and config["model"]["provider"]=="grok"):
            return StubFailClient(config)
        return StubOKClient(config)
    monkeypatch.setattr(ModelClientFactory, "get_client", staticmethod(fake_get_client))
    # minimal data manager stub
    class DM: pass
    agent = StockAgent(cfg, DM())
    res = agent._process_query("What's the price of AAPL?")
    assert "ok-response" in res or res.startswith("[fallback")