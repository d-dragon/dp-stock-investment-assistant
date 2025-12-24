import pytest
from unittest.mock import MagicMock, patch
from core.stock_assistant_agent import StockAssistantAgent
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
    """Test that StockAssistantAgent falls back to secondary provider when primary fails."""
    cfg = {
        "model": {"provider": "grok", "allow_fallback": True, "fallback_order": ["openai"]},
        "openai": {"api_key": "test-key", "model": "gpt-4"},
    }
    
    # Monkeypatch factory to return failing client for grok and OK for openai
    def fake_get_client(config, provider=None, model_name=None):
        if provider == "grok" or (provider is None and config["model"]["provider"] == "grok"):
            return StubFailClient(config)
        return StubOKClient(config)
    
    monkeypatch.setattr(ModelClientFactory, "get_client", staticmethod(fake_get_client))
    
    # Data manager stub with required methods
    class DM:
        def get_stock_info(self, symbol):
            return {"current_price": 150.0, "previous_close": 148.0}
        
        def get_market_news(self, symbol):
            return []
    
    # Mock tool registry to return empty tools (forces legacy path for fallback testing)
    mock_registry = MagicMock()
    mock_registry.get_enabled_tools.return_value = []
    
    agent = StockAssistantAgent(cfg, DM(), tool_registry=mock_registry)
    res = agent.process_query("What's the price of AAPL?")
    
    # Should get ok-response from fallback or with fallback prefix
    assert res == "ok-response" or res.startswith("[fallback:openai]")