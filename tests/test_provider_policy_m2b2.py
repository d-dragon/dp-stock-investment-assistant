"""M2B.2 tests for internal provider policy contracts."""

from __future__ import annotations

from core.routes import StockQueryRoute
from core.tools.provider_policy import (
    DataCategory,
    ProviderAdmissionOutcome,
    assert_provider_hidden_from_model_visible_surface,
)
from core.tools.registry import ToolRegistry
from core.tools.surface import ToolSurfaceBuilder
from tests.fixtures.tool_system_m2b2.providers import (
    FALLBACK_PROVIDER,
    OFFICIAL_PROVIDER,
    PROVIDER_POLICY,
    UNREVIEWED_PROVIDER,
)


def test_provider_descriptor_completeness():
    assert OFFICIAL_PROVIDER.validation_issues() == ()
    assert OFFICIAL_PROVIDER.production_admissible is True
    assert OFFICIAL_PROVIDER.to_source_metadata().provider_id == "hose_official"


def test_provider_selection_uses_order_and_records_fallback():
    providers = {"hose_official": OFFICIAL_PROVIDER, "yahoo_fallback": FALLBACK_PROVIDER}
    decision = PROVIDER_POLICY.select_provider(
        providers,
        market="VN",
        data_category=DataCategory.QUOTE,
        provider_health={"hose_official": "down"},
    )

    assert decision.allowed is True
    assert decision.selected_adapter == "yahoo_fallback"
    assert decision.fallback_used is True
    assert "hose_official:provider_down" in decision.warnings


def test_market_session_closed_fails_closed():
    decision = PROVIDER_POLICY.select_provider(
        {"hose_official": OFFICIAL_PROVIDER},
        market="VN",
        data_category=DataCategory.QUOTE,
        market_session_open=False,
    )

    assert decision.admission_outcome == ProviderAdmissionOutcome.BLOCKED
    assert decision.degraded_reason == "market_closed"


def test_provider_adapters_are_hidden_from_model_visible_surface():
    registry = ToolRegistry()
    surface = ToolSurfaceBuilder(registry=registry).build_for_route(StockQueryRoute.PRICE_CHECK)

    assert assert_provider_hidden_from_model_visible_surface(surface.model_visible_descriptors())


def test_fail_closed_for_unreviewed_licensing_and_missing_credentials():
    providers = {"public_scrape": UNREVIEWED_PROVIDER}
    policy = PROVIDER_POLICY.__class__(
        **{
            **PROVIDER_POLICY.__dict__,
            "provider_order": ("public_scrape",),
            "fallback_eligibility": {"public_scrape": False},
        }
    )
    decision = policy.select_provider(providers, market="VN", data_category=DataCategory.QUOTE)

    assert decision.allowed is False
    assert decision.admission_outcome == ProviderAdmissionOutcome.BLOCKED
    assert decision.degraded_reason in {"blocked_license", "missing_credential_scope", "not_production_eligible"}


def test_provider_decision_metadata_is_envelope_ready():
    decision = PROVIDER_POLICY.select_provider(
        {"hose_official": OFFICIAL_PROVIDER},
        market="VN",
        data_category=DataCategory.QUOTE,
    )
    metadata = decision.to_metadata()

    assert metadata["selected_adapter"] == "hose_official"
    assert metadata["admission_outcome"] == "allowed"
    assert metadata["license_status"] == "reviewed"
