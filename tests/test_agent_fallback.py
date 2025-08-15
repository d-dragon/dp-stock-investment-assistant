from core.agent import StockAgent


def test_agent_fallback(patch_model_factory, sample_config, data_manager_stub):
    """
    Validate that when the primary provider fails, the agent falls back to the configured provider.
    Uses patched ModelClientFactory via the patch_model_factory fixture.
    """
    agent = StockAgent(sample_config, data_manager_stub)
    res = agent._process_query("What's the price of AAPL?")
    assert "ok-response" in res, f"Expected fallback response to include 'ok-response', got: {res}"