"""Provider policy fixtures for M2B.2 tests."""

from core.tools.provider_policy import (
    CredentialOwner,
    DataCategory,
    LicensePosture,
    ProviderAdapterDescriptor,
    ProviderClass,
    ProviderSelectionPolicy,
)


OFFICIAL_PROVIDER = ProviderAdapterDescriptor(
    provider_id="hose_official",
    provider_class=ProviderClass.OFFICIAL,
    supported_markets=("VN",),
    supported_data_categories=(DataCategory.SYMBOL_REFERENCE, DataCategory.QUOTE),
    license_posture=LicensePosture.REVIEWED,
    credential_owner=CredentialOwner.APPLICATION,
    freshness_policy={"mode": "market_session"},
    parser_limits={"max_records": 500},
    source_attribution_requirements=("provider_id", "source_timestamp"),
    production_eligible=True,
    integrity_marker="official:v1",
)

FALLBACK_PROVIDER = ProviderAdapterDescriptor(
    provider_id="yahoo_fallback",
    provider_class=ProviderClass.INTERNATIONAL_FALLBACK,
    supported_markets=("US", "VN"),
    supported_data_categories=(DataCategory.QUOTE,),
    license_posture=LicensePosture.REVIEWED,
    credential_owner=CredentialOwner.NONE,
    freshness_policy={"mode": "best_effort"},
    parser_limits={"max_records": 100},
    source_attribution_requirements=("provider_id",),
    production_eligible=True,
    integrity_marker="fallback:v1",
)

UNREVIEWED_PROVIDER = ProviderAdapterDescriptor(
    provider_id="public_scrape",
    provider_class=ProviderClass.PUBLIC_WEB,
    supported_markets=("VN",),
    supported_data_categories=(DataCategory.QUOTE,),
    license_posture=LicensePosture.UNCLEAR,
    credential_owner=CredentialOwner.MISSING,
    freshness_policy={"mode": "unknown"},
    parser_limits={"max_records": 10},
    source_attribution_requirements=("url",),
    production_eligible=False,
    integrity_marker="public:v1",
    redistribution_posture="unclear",
)

PROVIDER_POLICY = ProviderSelectionPolicy(
    tool_name="market_data",
    route="price_check",
    provider_order=("hose_official", "yahoo_fallback"),
    fallback_eligibility={"hose_official": True, "yahoo_fallback": False},
    market_session_rules={"VN": "weekday_session"},
    freshness_expectations={"quote": "market_session"},
    timeout_budget=2.5,
    fail_closed_conditions=("blocked_license", "missing_credential_scope"),
    degraded_state_mapping={"provider_down": "provider_down", "blocked_license": "blocked_license"},
)
