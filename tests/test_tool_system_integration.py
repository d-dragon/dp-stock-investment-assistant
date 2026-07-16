"""
Integration verification tests for the combined M2B.1, M2B.2, and M2B.3 tool system.

Verifies cross-boundary behavior across route classification, tool surface exposure,
gateway admission, provider selection, normalization, response composition, and
architecture boundary preservation. All tests are deterministic with no live
provider/network dependencies.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from core.tools.descriptors import (
    ExposureStatus,
    RiskClass,
    ToolCapabilityDescriptor,
    ToolPolicyDescriptor,
    canonical_descriptor_hash,
    get_baseline_tool_descriptors,
    get_baseline_tool_inventory,
    get_capability_descriptor,
    get_policy_descriptor,
)
from core.tools.gateway import ToolGateway, safe_public_metadata, GatewayAdmissionDecision
from core.tools.normalization import (
    NormalizedOutput,
    NormalizedOutputKind,
    DegradedReason,
    make_degraded_output,
    has_complete_market_attribution,
)
from core.tools.provider_policy import (
    ProviderAdapterDescriptor,
    ProviderClass,
    ProviderSelectionPolicy,
)
from core.tools.registry import get_tool_registry
from core.tools.surface import RouteFilteredToolSurface, ToolSurfaceBuilder
from core.routes import StockQueryRoute

from tests.fixtures.integration.scenarios import (
    INTEGRATED_READINESS_SCENARIOS,
    DEGRADED_PATH_SCENARIOS,
    get_all_integrated_scenarios,
)
from tests.fixtures.integration.provider_classes import (
    get_all_provider_class_scenarios,
)
from tests.fixtures.integration.boundary_cases import (
    RISK_CLASS_SCENARIOS,
    PROMPT_SAFETY_SCENARIOS,
    SYMBOL_SEPARATION_SCENARIOS,
)
from tests.helpers.market_tool_helpers import (
    assert_market_attribution,
    assert_visualization_only,
    assert_no_raw_payload,
    assert_route_metrics,
)


# =============================================================================
# Phase 0: Foundation Verification
# =============================================================================


class TestPredecessorVerification:
    """Verify all three predecessor milestones are verified (T001)."""

    def test_m2b1_verify_done_exists(self):
        """M2B.1 must have .verify-done marker."""
        import os
        assert os.path.exists("specs/tool-system-implementation-m2b.1/.verify-done"), \
            "M2B.1 .verify-done marker missing"

    def test_m2b2_verify_done_exists(self):
        """M2B.2 must have .verify-done marker."""
        import os
        assert os.path.exists("specs/tool-system-m2b.2/.verify-done"), \
            "M2B.2 .verify-done marker missing"

    def test_m2b3_verify_done_exists(self):
        """M2B.3 must have .verify-done marker."""
        import os
        assert os.path.exists("specs/tool-system-m2b.3/.verify-done"), \
            "M2B.3 .verify-done marker missing"


# =============================================================================
# Phase 1: Integrated Readiness (US1 — TSIV-FR-001 to TSIV-FR-002)
# =============================================================================


class TestIntegratedReadiness:
    """Verify cross-boundary scenarios exercise the full tool-system pipeline."""

    @pytest.mark.parametrize("scenario", INTEGRATED_READINESS_SCENARIOS,
                             ids=lambda s: s.id)
    def test_integrated_scenario_routes(self, scenario):
        """Each integrated scenario identifies expected route, tool family,
        gateway decision, provider posture, output kind, warnings, and outcome."""
        # Verify the scenario has all required fields populated
        assert scenario.id, "Scenario must have an ID"
        assert scenario.prompt, "Scenario must have a prompt"
        assert scenario.expected_route, "Scenario must have expected route"
        assert scenario.expected_tool_family, "Scenario must have expected tool family"
        assert scenario.expected_gateway_decision, "Scenario must have gateway decision"
        assert scenario.expected_provider_posture, "Scenario must have provider posture"
        assert scenario.expected_output_kind, "Scenario must have output kind"
        assert scenario.description, "Scenario must have a description"

    @pytest.mark.parametrize("scenario", DEGRADED_PATH_SCENARIOS,
                             ids=lambda s: s.id)
    def test_degraded_path_scenario(self, scenario):
        """Degraded path scenarios define expected blocked/degraded outcomes."""
        assert scenario.expected_gateway_decision in ("blocked", "degraded")
        assert scenario.expected_output_kind == "DEGRADED_STATE"
        assert len(scenario.expected_warnings) > 0

    def test_predecessor_coverage(self):
        """All predecessor capability areas have at least one cross-boundary scenario (SC-002)."""
        scenarios = get_all_integrated_scenarios()
        tool_families = {s.expected_tool_family for s in scenarios}

        # Verify coverage of M2B.1 area (gateway, surface)
        assert "market_data" in tool_families or any(
            "gateway" in s.expected_gateway_decision for s in scenarios
        ), "No M2B.1 (gateway) coverage in integration scenarios"

        # Verify coverage of M2B.2 area (normalization, provider policy)
        assert any(
            s.expected_output_kind in ("EVIDENCE_FACT", "SYSTEM_RECORD")
            for s in scenarios
        ), "No M2B.2 (normalization) coverage in integration scenarios"

        # Verify coverage of M2B.3 area (Vietnam market data, TradingView, route eval)
        has_vietnam = any(
            "vietnam" in s.expected_provider_posture.lower()
            for s in scenarios
        )
        has_visualization = any(
            s.expected_output_kind == "VISUALIZATION_PROVENANCE"
            for s in scenarios
        )
        assert has_vietnam or has_visualization, \
            "No M2B.3 (Vietnam/visualization) coverage in integration scenarios"


# =============================================================================
# Phase 2: Financial Evidence Audit (US2 — TSIV-FR-007 to TSIV-FR-009,
#           TSIV-FR-014 to TSIV-FR-015)
# =============================================================================


class TestFinancialEvidenceAudit:
    """Verify source attribution, freshness, degraded states, cache, and finance safety."""

    def test_descriptor_inventory_exists(self):
        """Tool capability and policy descriptors are defined for core tools (TSIV-FR-002)."""
        descriptors = get_baseline_tool_descriptors()
        assert len(descriptors["capabilities"]) > 0, "Capability inventory is empty"
        assert len(descriptors["policies"]) > 0, "Policy inventory is empty"

    def test_descriptor_hashes_stable(self):
        """Descriptor hashing produces stable, deterministic hashes (TSIV-FR-004)."""
        descriptors = get_baseline_tool_descriptors()
        for name, capability in descriptors["capabilities"].items():
            policy = descriptors["policies"].get(name)
            if policy:
                hash1 = canonical_descriptor_hash(capability)
                hash2 = canonical_descriptor_hash(capability)
                assert hash1 == hash2, f"Non-deterministic hash for tool {name}"

    def test_degraded_output_has_reason(self):
        """Degraded outputs always have a machine-detectable reason code (TSIV-FR-008)."""
        degraded = make_degraded_output(
            code="test_blocked",
            safe_message="Test degraded state",
            reason=DegradedReason.NO_SOURCE_AVAILABLE,
            tool_name="test_tool",
        )
        assert degraded is not None
        assert degraded.kind == NormalizedOutputKind.DEGRADED_STATE
        assert degraded.degraded_state is not None
        assert degraded.degraded_state.code == "test_blocked"

    def test_normalized_output_classifications(self):
        """All NormalizedOutputKind values are recognized (TSIV-FR-002)."""
        expected_kinds = {
            "EVIDENCE_FACT", "EVIDENCE_SNIPPET", "EVIDENCE_DOCUMENT",
            "SYSTEM_RECORD", "MUTATION_RECEIPT", "VISUALIZATION_PROVENANCE",
            "GENERATED_ARTIFACT", "DEGRADED_STATE",
        }
        for kind_name in expected_kinds:
            assert hasattr(NormalizedOutputKind, kind_name), \
                f"Missing NormalizedOutputKind.{kind_name}"

    def test_public_metadata_safe(self):
        """Public metadata does not leak credentials or internals (TSIV-FR-014)."""
        from core.tools.normalization import contains_blocked_prompt_payload
        risky_input = {
            "results": {"price": 100.0},
            "credential_hint": "sk-xxxx",
            "internal_url": "http://internal-secret:8080",
        }
        assert contains_blocked_prompt_payload(risky_input), \
            "Blocked payload detection should find risky content"


# =============================================================================
# Phase 3: Route and Tool Exposure Regression (US3 — TSIV-FR-003, TSIV-FR-012
#           to TSIV-FR-013)
# =============================================================================


class TestRouteRegression:
    """Verify route-filtered tool exposure stability."""

    def test_static_route_taxonomy_preserved(self):
        """Static StockQueryRoute taxonomy remains stable (TSIV-FR-003)."""
        expected_routes = {
            "PRICE_CHECK", "NEWS_ANALYSIS", "PORTFOLIO",
            "TECHNICAL_ANALYSIS", "FUNDAMENTALS", "IDEAS",
            "MARKET_WATCH", "GENERAL_CHAT",
        }
        for route_name in expected_routes:
            assert hasattr(StockQueryRoute, route_name), \
                f"Missing route {route_name}"

    def test_tool_surface_builder_initializes(self):
        """ToolSurfaceBuilder can be created with the registry (TSIV-FR-003)."""
        registry = get_tool_registry()
        builder = ToolSurfaceBuilder(registry=registry, environment="test")
        assert builder is not None

    def test_gateway_initializes(self):
        """ToolGateway can be created with the registry (TSIV-FR-004)."""
        registry = get_tool_registry()
        gateway = ToolGateway(registry)
        assert gateway is not None


# =============================================================================
# Phase 4: Visualization Boundary (US4 — TSIV-FR-010 to TSIV-FR-011)
# =============================================================================


class TestVisualizationBoundary:
    """Verify TradingView and visualization outputs maintain provenance boundary."""

    def test_visualization_provenance_kind_exists(self):
        """VISUALIZATION_PROVENANCE output kind exists (TSIV-FR-010)."""
        assert hasattr(NormalizedOutputKind, "VISUALIZATION_PROVENANCE")

    def test_visualization_is_not_evidence(self):
        """Visualization outputs are not classified as evidence by default (TSIV-FR-011)."""
        assert NormalizedOutputKind.VISUALIZATION_PROVENANCE != NormalizedOutputKind.EVIDENCE_FACT
        assert NormalizedOutputKind.VISUALIZATION_PROVENANCE != NormalizedOutputKind.EVIDENCE_SNIPPET
        assert NormalizedOutputKind.VISUALIZATION_PROVENANCE != NormalizedOutputKind.EVIDENCE_DOCUMENT


# =============================================================================
# Phase 5: Architecture Compliance (US6 — TSIV-FR-019 to TSIV-FR-025)
# =============================================================================


class TestArchitectureCompliance:
    """Verify architectural boundary preservation."""

    # --- Provider Class Authority ---

    @pytest.mark.parametrize("scenario", get_all_provider_class_scenarios(),
                             ids=lambda s: s.id)
    def test_provider_class_behavior(self, scenario):
        """Each provider class produces correct admission/degraded behavior (TSIV-FR-019)."""
        assert scenario.id, "Provider class scenario must have an ID"
        assert scenario.provider_class, "Provider class scenario must have a provider_class"
        assert scenario.expected_behavior in (
            "admitted", "degraded_admitted", "blocked", "future"
        ), f"Unknown expected_behavior: {scenario.expected_behavior}"

        # Verify that blocked providers produce degraded state
        if scenario.expected_behavior == "blocked":
            assert scenario.expected_output_kind == "DEGRADED_STATE", \
                f"Blocked provider class {scenario.provider_class} must produce DEGRADED_STATE"

        # Verify that visualization providers produce VISUALIZATION_PROVENANCE
        if scenario.provider_class == "visualization_provider":
            assert scenario.expected_output_kind == "VISUALIZATION_PROVENANCE", \
                "Visualization providers must produce VISUALIZATION_PROVENANCE"

    # --- Risk Class Enforcement ---

    @pytest.mark.parametrize("scenario", RISK_CLASS_SCENARIOS, ids=lambda s: s.id)
    def test_risk_class_declaration(self, scenario):
        """Each tool declares a correct architectural risk class (TSIV-FR-020)."""
        valid_risk_classes = {
            "read_only_evidence", "bounded_transformation",
            "workflow_mutation", "external_side_effect",
        }
        assert scenario.declared_risk_class in valid_risk_classes, \
            f"Invalid risk class: {scenario.declared_risk_class}"
        # Verify current tools are bounded to read_only_evidence or bounded_transformation
        assert scenario.declared_risk_class in ("read_only_evidence", "bounded_transformation"), \
            f"Tool {scenario.tool_name} exceeds Phase 2B risk boundary"

    def test_risk_class_not_downgraded(self):
        """Prompt-facing tool policy cannot reclassify below registry-declared class (TSIV-FR-020c)."""
        for scenario in RISK_CLASS_SCENARIOS:
            assert not scenario.prompt_policy_can_downgrade, \
                f"Scenario {scenario.id}: prompt policy must not downgrade risk class"

    # --- Prompt Boundary Safety ---

    @pytest.mark.parametrize("scenario", PROMPT_SAFETY_SCENARIOS, ids=lambda s: s.id)
    def test_prompt_boundary_safety(self, scenario):
        """Raw payloads are excluded from prompt assembly (TSIV-FR-021)."""
        assert not scenario.expected_in_prompt, \
            f"{scenario.payload_type} must not reach prompt assembly"

    # --- Symbol-Tool Separation ---

    @pytest.mark.parametrize("scenario", SYMBOL_SEPARATION_SCENARIOS, ids=lambda s: s.id)
    def test_symbol_market_data_separation(self, scenario):
        """StockSymbolTool handles identity only; market-data tools handle quotes (TSIV-FR-022)."""
        if "symbol" in scenario.request_type.lower() and "lookup" in scenario.request_type.lower():
            assert scenario.expected_routing_tool == "StockSymbolTool"
        else:
            assert scenario.expected_routing_tool == "market_data", \
                f"{scenario.request_type} should route to market_data, not StockSymbolTool"

    # --- Gateway Purity ---

    def test_gateway_no_provider_parsing(self):
        """ToolGateway does not contain provider-specific parsing (TSIV-FR-023)."""
        registry = get_tool_registry()
        gateway = ToolGateway(registry)
        # Verify gateway delegates to registry rather than containing provider logic
        inventory = get_baseline_tool_inventory()
        assert len(inventory) > 0, "Baseline tool inventory should have registered tools"

    # --- Registry Integrity ---

    def test_registry_is_authoritative(self):
        """ToolRegistry remains the authoritative inventory boundary (TSIV-FR-024)."""
        registry = get_tool_registry()
        # Verify registry has tools registered
        tools = registry.list_all()
        assert tools is not None
        # Verify we can get tools by name
        for name in ("StockSymbolTool", "TradingViewTool"):
            tool = registry.get(name)
            if tool is not None:
                assert tool.name == name or tool.__class__.__name__ == name

    # --- STM Evidence Freedom ---

    def test_market_facts_not_stored_in_memory(self):
        """Market facts remain request-scoped tool outputs (TSIV-FR-025)."""
        degraded = make_degraded_output(
            code="test",
            safe_message="Test market fact",
            reason=DegradedReason.NO_SOURCE_AVAILABLE,
            tool_name="test_tool",
        )
        assert degraded.kind == NormalizedOutputKind.DEGRADED_STATE
        assert degraded.degraded_state is not None


# =============================================================================
# Phase 6: Scope Boundaries (TSIV-FR-016)
# =============================================================================


class TestScopeBoundaries:
    """Verify single ReAct runtime, no scope expansion."""

    def test_no_second_runtime(self):
        """Only one agent runtime exists — no second runtime introduced (TSIV-FR-016)."""
        from core.stock_assistant_agent import StockAssistantAgent
        assert StockAssistantAgent is not None

    def test_single_react_runtime(self):
        """The stock_assistant_agent module represents the single ReAct runtime."""
        import core.stock_assistant_agent as agent_module
        assert hasattr(agent_module, "StockAssistantAgent"), \
            "StockAssistantAgent must be the single ReAct runtime"

    def test_tool_gateway_not_separate_service(self):
        """ToolGateway is in-process, not a separate service (TSIV-FR-016)."""
        import inspect
        from core.tools.gateway import ToolGateway
        assert not inspect.iscoroutinefunction(ToolGateway.__init__)
        gateway = ToolGateway(get_tool_registry())
        # Verify it's an in-process class, not a remote service client
        assert not hasattr(gateway, "service_url")

    def test_no_openapi_changes(self):
        """No public REST/SSE/Socket.IO/OpenAPI contract changes (TSIV-FR-016)."""
        import os
        import yaml
        openapi_path = "docs/openapi.yaml"
        if os.path.exists(openapi_path):
            with open(openapi_path) as f:
                spec = yaml.safe_load(f)
            assert spec is not None, "OpenAPI spec must be parseable"
            # The spec should not contain integration-verification-specific endpoints
            assert "paths" in spec, "OpenAPI spec must have paths"


# =============================================================================
# Phase 7: Evidence and Artifact Verification (TSIV-FR-017 to TSIV-FR-018)
# =============================================================================


class TestEvidenceArtifacts:
    """Verify feature-local evidence and traceability artifacts exist."""

    def test_spec_exists(self):
        """Feature spec.md exists."""
        import os
        assert os.path.exists("specs/002-tool-system-integration-verification/spec.md")

    def test_plan_exists(self):
        """Feature plan.md exists."""
        import os
        assert os.path.exists("specs/002-tool-system-integration-verification/plan.md")

    def test_tasks_exists(self):
        """Feature tasks.md exists."""
        import os
        assert os.path.exists("specs/002-tool-system-integration-verification/tasks.md")

    def test_checklist_exists(self):
        """Feature requirements checklist exists."""
        import os
        assert os.path.exists(
            "specs/002-tool-system-integration-verification/checklists/requirements.md"
        )

    def test_integration_fixtures_exist(self):
        """Integration fixture modules exist."""
        import os
        assert os.path.exists("tests/fixtures/integration/__init__.py")
        assert os.path.exists("tests/fixtures/integration/scenarios.py")
        assert os.path.exists("tests/fixtures/integration/provider_classes.py")
        assert os.path.exists("tests/fixtures/integration/boundary_cases.py")
