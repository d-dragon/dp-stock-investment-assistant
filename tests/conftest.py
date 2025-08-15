import pytest

# Lightweight stub clients used across tests
class StubFailClient:
    def __init__(self, config):
        self.provider = "grok"
        self.model_name = "grok-fail"

    def generate(self, prompt, context=None):
        raise RuntimeError("simulated failure")

    def generate_stream(self, prompt, context=None):
        raise RuntimeError("simulated failure")


class StubOKClient:
    def __init__(self, config):
        self.provider = "openai"
        self.model_name = "openai-ok"

    def generate(self, prompt, context=None):
        return "ok-response"

    def generate_stream(self, prompt, context=None):
        yield "ok-response"


@pytest.fixture
def sample_config():
    return {
        "model": {
            "provider": "grok",
            "allow_fallback": True,
            "fallback_order": ["openai"]
        }
    }


@pytest.fixture
def data_manager_stub():
    class DM:
        def get_stock_info(self, symbol):
            return {
                "current_price": 123.45,
                "previous_close": 120.00,
                "pe_ratio": 18.2,
            }
    return DM()


@pytest.fixture
def patch_model_factory(monkeypatch):
    """
    Patch ModelClientFactory.get_client so that:
      - requests for 'grok' return a failing client
      - requests for 'openai' return an OK client
    """
    def fake_get_client(config, provider=None, model_name=None):
        # treat no-provider as default based on config
        effective = provider or config.get("model", {}).get("provider")
        if effective == "grok":
            return StubFailClient(config)
        return StubOKClient(config)

    # patch by target string so pytest can import even if package layout changes
    monkeypatch.setattr("core.model_factory.ModelClientFactory.get_client", staticmethod(fake_get_client))
    return fake_get_client