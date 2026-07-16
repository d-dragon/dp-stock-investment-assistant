"""Provider class verification fixtures.

Covers all 7 architectural provider classes defined in the architecture design:
1. In-system persistent data
2. Official exchange / depository
3. Licensed commercial
4. Vietnam-native public web
5. Wrapper / prototype
6. Visualization provider
7. International fallback
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ProviderClassScenario:
    """A single provider class verification case.

    Attributes:
        id: Unique scenario identifier
        provider_class: The architectural provider class name
        expected_behavior: Expected behavior ("admitted"|"degraded_admitted"|"blocked"|"future")
        expected_output_kind: Expected NormalizedOutputKind
        expected_warnings: Expected warnings
        description: Purpose of this scenario
    """
    id: str
    provider_class: str
    expected_behavior: str
    expected_output_kind: str
    expected_warnings: List[str] = field(default_factory=list)
    description: str = ""


PROVIDER_CLASS_SCENARIOS: List[ProviderClassScenario] = [
    ProviderClassScenario(
        id="PC-001",
        provider_class="in_system_persistent_data",
        expected_behavior="admitted",
        expected_output_kind="SYSTEM_RECORD",
        expected_warnings=[],
        description="In-system persistent data (symbol identity, aliases, coverage) is admitted",
    ),
    ProviderClassScenario(
        id="PC-002",
        provider_class="official_exchange_depository",
        expected_behavior="admitted",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=[],
        description="Official exchange/depository sources (HOSE, HNX, VSDC) are admitted",
    ),
    ProviderClassScenario(
        id="PC-003",
        provider_class="licensed_commercial",
        expected_behavior="admitted",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=[],
        description="Licensed commercial sources are admitted when terms allow",
    ),
    ProviderClassScenario(
        id="PC-004",
        provider_class="vietnam_native_public_web",
        expected_behavior="admitted",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=["subject_to_terms_and_parser_controls"],
        description="Vietnam-native public web sources admitted with parser caveats",
    ),
    ProviderClassScenario(
        id="PC-005",
        provider_class="wrapper_prototype",
        expected_behavior="degraded_admitted",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=["wrapper_prototype_connector", "subject_to_license_review"],
        description="Wrapper/prototype connectors produce degraded-admitted with license caveats",
    ),
    ProviderClassScenario(
        id="PC-006",
        provider_class="visualization_provider",
        expected_behavior="admitted",
        expected_output_kind="VISUALIZATION_PROVENANCE",
        expected_warnings=["non_authoritative_visualization"],
        description="Visualization providers produce VisualizationProvenance, not evidence",
    ),
    ProviderClassScenario(
        id="PC-007",
        provider_class="international_fallback",
        expected_behavior="admitted",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=["international_fallback_used"],
        description="International fallback sources admitted with fallback warnings",
    ),
    ProviderClassScenario(
        id="PC-008",
        provider_class="license_unclear_source",
        expected_behavior="blocked",
        expected_output_kind="DEGRADED_STATE",
        expected_warnings=["license_posture_not_acceptable"],
        description="License-unclear sources are blocked with degraded state",
    ),
    ProviderClassScenario(
        id="PC-009",
        provider_class="unsupported_provider",
        expected_behavior="blocked",
        expected_output_kind="DEGRADED_STATE",
        expected_warnings=["unsupported_provider"],
        description="Unsupported providers are blocked with degraded state",
    ),
]


def get_all_provider_class_scenarios() -> List[ProviderClassScenario]:
    """Return all provider class verification scenarios."""
    return PROVIDER_CLASS_SCENARIOS
