"""Internal tool-output normalization contracts for M2B.2."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence


class NormalizedOutputKind(str, Enum):
    """Admitted normalized output classes before prompt assembly."""

    EVIDENCE_FACT = "EvidenceFact"
    EVIDENCE_SNIPPET = "EvidenceSnippet"
    EVIDENCE_DOCUMENT = "EvidenceDocument"
    SYSTEM_RECORD = "SystemRecord"
    MUTATION_RECEIPT = "MutationReceipt"
    VISUALIZATION_PROVENANCE = "VisualizationProvenance"
    GENERATED_ARTIFACT = "GeneratedArtifact"
    DEGRADED_STATE = "DegradedState"


class AssetType(str, Enum):
    """Internal symbol asset classes admitted by M2B.2."""

    EQUITY = "equity"
    INDEX = "index"
    FUND = "fund"
    OTHER = "other"


class FreshnessStatus(str, Enum):
    """Freshness state used by normalized outputs and envelopes."""

    CURRENT = "current"
    STALE = "stale"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class AdmissionOutcome(str, Enum):
    """Tool or provider admission outcomes."""

    ALLOWED = "allowed"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class DegradedReason(str, Enum):
    """Machine-detectable degraded-state reasons."""

    AMBIGUOUS_SYMBOL = "ambiguous_symbol"
    MISSING_SYMBOL = "missing_symbol"
    DUPLICATE_ALIAS = "duplicate_alias"
    STALE_RECORD = "stale_record"
    CONFLICTING_RECORD = "conflicting_record"
    LIVE_MARKET_DATA_NOT_OWNED = "live_market_data_not_owned"
    PROVIDER_DOWN = "provider_down"
    PARSER_LIMITED = "parser_limited"
    BLOCKED_LICENSE = "blocked_license"
    FRESHNESS_UNKNOWN = "freshness_unknown"
    VALIDATION_FAILED = "validation_failed"
    UNSUPPORTED_PROVIDER = "unsupported_provider"
    MISSING_SOURCE = "missing_source"
    NO_SOURCE_AVAILABLE = "no_source_available"
    RAW_PAYLOAD_BLOCKED = "raw_payload_blocked"
    MUTATION_DISABLED = "mutation_disabled"


BLOCKED_PROMPT_KEY_FRAGMENTS = (
    "raw",
    "html",
    "pdf_bytes",
    "script",
    "hidden_text",
    "untrusted_instruction",
    "credential",
    "password",
    "token",
    "parser_internal",
    "raw_trace",
)


@dataclass(frozen=True)
class CanonicalSymbolIdentity:
    """Provider-neutral identity for an internal symbol record."""

    symbol: str
    exchange: Optional[str] = None
    currency: Optional[str] = None
    asset_type: AssetType = AssetType.EQUITY
    aliases: Sequence[str] = field(default_factory=tuple)
    identifiers: Mapping[str, str] = field(default_factory=dict)
    locale: str = "VN"

    def __post_init__(self) -> None:
        symbol = normalize_symbol_code(self.symbol)
        object.__setattr__(self, "symbol", symbol)
        if self.exchange:
            object.__setattr__(self, "exchange", str(self.exchange).upper())
        if self.currency:
            object.__setattr__(self, "currency", str(self.currency).upper())
        object.__setattr__(self, "aliases", tuple(normalize_symbol_code(alias) for alias in self.aliases))
        object.__setattr__(self, "identifiers", {str(k): str(v) for k, v in self.identifiers.items()})

    def to_dict(self) -> Dict[str, Any]:
        return _to_plain_dict(self)


@dataclass(frozen=True)
class InternalSymbolRecord:
    """Internal symbol-store record admitted for StockSymbolTool target behavior."""

    identity: CanonicalSymbolIdentity
    display_name: str
    coverage: Sequence[str] = field(default_factory=tuple)
    tags: Sequence[str] = field(default_factory=tuple)
    stored_snapshot_metadata: Mapping[str, Any] = field(default_factory=dict)
    source_record_reference: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "coverage", tuple(str(item) for item in self.coverage))
        object.__setattr__(self, "tags", tuple(str(item) for item in self.tags))
        if contains_blocked_prompt_payload(self.stored_snapshot_metadata):
            raise ValueError("InternalSymbolRecord cannot contain raw provider payloads")

    def to_dict(self) -> Dict[str, Any]:
        return _to_plain_dict(self)


@dataclass(frozen=True)
class SourceMetadata:
    """Source lineage metadata carried by normalized outputs and retained derivatives."""

    provider_id: Optional[str] = None
    provider_class: Optional[str] = None
    source_url_or_reference: Optional[str] = None
    retrieved_at: Optional[str] = None
    source_timestamp: Optional[str] = None
    published_at: Optional[str] = None
    effective_at: Optional[str] = None
    symbol_identity: Optional[CanonicalSymbolIdentity] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None
    license_posture: Optional[str] = None
    freshness_status: FreshnessStatus = FreshnessStatus.UNKNOWN
    warnings: Sequence[str] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "warnings", tuple(str(warning) for warning in self.warnings))

    def to_dict(self) -> Dict[str, Any]:
        return _to_plain_dict(self)


@dataclass(frozen=True)
class AttributionCoverageCounters:
    """Small coverage summary for market-data attribution evidence."""

    complete_attribution: int = 0
    degraded_no_source: int = 0
    stale_cache: int = 0
    provider_or_license_blocked: int = 0
    unsafe_trace_leak: int = 0

    def to_dict(self) -> Dict[str, int]:
        return _to_plain_dict(self)


@dataclass(frozen=True)
class DegradedState:
    """Safe degraded outcome for blocked, stale, missing, or invalid tool results."""

    code: str
    safe_message: str
    reason: DegradedReason | str
    route: Optional[str] = None
    tool_name: Optional[str] = None
    provider_id: Optional[str] = None
    retryable: bool = False
    user_visible: bool = True
    trace_reference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _to_plain_dict(self)


@dataclass(frozen=True)
class NormalizedOutput:
    """Data-only tool output admitted at the prompt boundary."""

    kind: NormalizedOutputKind
    content: Mapping[str, Any]
    source_metadata: Optional[SourceMetadata] = None
    freshness_metadata: Mapping[str, Any] = field(default_factory=dict)
    symbol_identity: Optional[CanonicalSymbolIdentity] = None
    warnings: Sequence[str] = field(default_factory=tuple)
    degraded_state: Optional[DegradedState] = None
    output_id: str = ""

    def __post_init__(self) -> None:
        if contains_blocked_prompt_payload(self.content):
            raise ValueError("NormalizedOutput content contains blocked raw prompt payload")
        if self.kind == NormalizedOutputKind.DEGRADED_STATE and self.degraded_state is None:
            raise ValueError("DegradedState output requires degraded_state")
        if self.kind != NormalizedOutputKind.DEGRADED_STATE and self.degraded_state is not None:
            raise ValueError("Only DegradedState outputs can carry degraded_state")
        object.__setattr__(self, "warnings", tuple(str(warning) for warning in self.warnings))
        if not self.output_id:
            object.__setattr__(self, "output_id", stable_output_id(self.kind.value, self.content))

    def to_dict(self) -> Dict[str, Any]:
        return _to_plain_dict(self)

    def prompt_projection(self) -> Dict[str, Any]:
        """Return data permitted to enter prompt assembly."""

        payload = self.to_dict()
        return sanitize_prompt_payload(payload)


@dataclass(frozen=True)
class ToolExecutionEnvelope:
    """Inspectable internal outcome record for one governed tool execution."""

    route: str
    selected_tool: str
    descriptor_identity: str
    admission_outcome: AdmissionOutcome | str
    normalized_output: NormalizedOutput
    selected_adapter: Optional[str] = None
    cache_status: str = "not_applicable"
    freshness_status: FreshnessStatus | str = FreshnessStatus.NOT_APPLICABLE
    warnings: Sequence[str] = field(default_factory=tuple)
    degraded_state_reason: Optional[str] = None
    trace_metadata: Mapping[str, Any] = field(default_factory=dict)
    envelope_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "warnings", tuple(str(warning) for warning in self.warnings))
        object.__setattr__(self, "trace_metadata", sanitize_trace_metadata(self.trace_metadata))
        if not self.envelope_id:
            object.__setattr__(
                self,
                "envelope_id",
                stable_output_id(
                    "ToolExecutionEnvelope",
                    {
                        "route": self.route,
                        "selected_tool": self.selected_tool,
                        "output_id": self.normalized_output.output_id,
                    },
                ),
            )

    @property
    def normalized_output_ref(self) -> str:
        return self.normalized_output.output_id

    def to_dict(self) -> Dict[str, Any]:
        payload = _to_plain_dict(self)
        payload["normalized_output_ref"] = self.normalized_output_ref
        return payload

    def public_metadata(self) -> Dict[str, Any]:
        metadata = {
            "route": self.route,
            "selected_tool": self.selected_tool,
            "admission_outcome": _enum_value(self.admission_outcome),
            "normalized_output_kind": self.normalized_output.kind.value,
            "warnings": list(self.warnings),
        }
        if self.degraded_state_reason:
            metadata["degraded_state_reason"] = self.degraded_state_reason
        return metadata


def normalize_symbol_code(value: str) -> str:
    """Normalize a symbol or alias string without provider-specific assumptions."""

    return str(value or "").strip().upper().replace(" ", "")


def symbol_identity_from_record(record: Mapping[str, Any]) -> CanonicalSymbolIdentity:
    """Build a canonical identity from a repository-style symbol document."""

    listing = _mapping(record.get("listing"))
    identifiers = _mapping(record.get("identifiers"))
    classification = _mapping(record.get("classification"))
    symbol = str(record.get("symbol") or record.get("ticker") or "")
    asset_type = str(record.get("asset_type") or "equity").lower()
    if asset_type in {"stock", "common_stock"}:
        asset_type = AssetType.EQUITY.value
    if symbol in {"VNINDEX", "VN30", "HNXINDEX", "UPINDEX"} or asset_type == "index":
        asset_type = AssetType.INDEX.value
    aliases = tuple(record.get("aliases") or record.get("alias") or ())
    if isinstance(aliases, str):
        aliases = (aliases,)
    return CanonicalSymbolIdentity(
        symbol=symbol,
        exchange=listing.get("exchange") or record.get("exchange"),
        currency=listing.get("currency") or record.get("currency") or ("VND" if classification.get("market") == "VN" else None),
        asset_type=AssetType(asset_type) if asset_type in {item.value for item in AssetType} else AssetType.OTHER,
        aliases=aliases,
        identifiers={str(k): str(v) for k, v in identifiers.items() if v not in (None, "")},
        locale=str(record.get("locale") or classification.get("market") or "VN"),
    )


def internal_symbol_record_from_document(record: Mapping[str, Any]) -> InternalSymbolRecord:
    """Build an internal symbol record from repository data."""

    identity = symbol_identity_from_record(record)
    return InternalSymbolRecord(
        identity=identity,
        display_name=str(record.get("name") or record.get("display_name") or identity.symbol),
        coverage=tuple(_iter_strings(_mapping(record.get("coverage")).get("capabilities") or record.get("coverage_tags") or ())),
        tags=tuple(_iter_strings(record.get("tags") or ())),
        stored_snapshot_metadata=_mapping(record.get("stored_snapshot_metadata")),
        source_record_reference=str(record.get("_id") or record.get("source_record_reference") or identity.symbol),
        updated_at=str(record.get("updated_at")) if record.get("updated_at") else None,
    )


def make_system_record_output(record: InternalSymbolRecord | Mapping[str, Any]) -> NormalizedOutput:
    """Create a SystemRecord normalized output for an internal symbol record."""

    internal = record if isinstance(record, InternalSymbolRecord) else internal_symbol_record_from_document(record)
    source = SourceMetadata(
        provider_id="internal_symbol_store",
        provider_class="internal_system",
        source_url_or_reference=internal.source_record_reference,
        retrieved_at=utc_now_iso(),
        source_timestamp=internal.updated_at,
        symbol_identity=internal.identity,
        exchange=internal.identity.exchange,
        currency=internal.identity.currency,
        license_posture="not_applicable",
        freshness_status=FreshnessStatus.UNKNOWN if internal.updated_at is None else FreshnessStatus.CURRENT,
    )
    return NormalizedOutput(
        kind=NormalizedOutputKind.SYSTEM_RECORD,
        content=internal.to_dict(),
        source_metadata=source,
        freshness_metadata={"updated_at": internal.updated_at},
        symbol_identity=internal.identity,
    )


def make_evidence_fact_output(
    *,
    output_type: str,
    content: Mapping[str, Any],
    source_metadata: SourceMetadata,
    freshness_metadata: Optional[Mapping[str, Any]] = None,
    warnings: Sequence[str] = (),
) -> NormalizedOutput:
    """Create a source-attributed market evidence output."""

    payload = {"output_type": output_type, **dict(content)}
    if not has_complete_market_attribution(source_metadata):
        return make_degraded_output(
            code=DegradedReason.MISSING_SOURCE.value,
            safe_message="Market data source attribution is incomplete.",
            reason=DegradedReason.MISSING_SOURCE,
            provider_id=source_metadata.provider_id,
        )
    return NormalizedOutput(
        kind=NormalizedOutputKind.EVIDENCE_FACT,
        content=payload,
        source_metadata=source_metadata,
        freshness_metadata=dict(freshness_metadata or {}),
        symbol_identity=source_metadata.symbol_identity,
        warnings=tuple(warnings) + tuple(source_metadata.warnings),
    )


def make_visualization_provenance_output(
    *,
    provider_id: str,
    symbol: str,
    payload: Mapping[str, Any],
    source_url_or_reference: Optional[str] = None,
    warnings: Sequence[str] = (),
) -> NormalizedOutput:
    """Create a TradingView-style visualization output that is never evidence by default."""

    warning = "Visualization provenance is not canonical market evidence."
    source = SourceMetadata(
        provider_id=provider_id,
        provider_class="visualization",
        source_url_or_reference=source_url_or_reference,
        retrieved_at=utc_now_iso(),
        license_posture="not_applicable",
        freshness_status=FreshnessStatus.NOT_APPLICABLE,
        warnings=(warning, *tuple(warnings)),
    )
    return NormalizedOutput(
        kind=NormalizedOutputKind.VISUALIZATION_PROVENANCE,
        content={
            "output_type": "VisualizationProvenance",
            "symbol": normalize_symbol_code(symbol),
            "canonical_evidence": False,
            **dict(payload),
        },
        source_metadata=source,
        warnings=(warning, *tuple(warnings)),
    )


def cache_freshness_metadata(
    *,
    provider_id: str,
    retrieved_at: str,
    freshness_status: FreshnessStatus | str,
    source_timestamp: Optional[str] = None,
    ttl_seconds: Optional[int] = None,
    expires_at: Optional[str] = None,
    warnings: Sequence[str] = (),
    degraded_state_reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Build cache freshness metadata required by market-data evidence gates."""

    return {
        "provider_id": provider_id,
        "source_timestamp": source_timestamp,
        "retrieved_at": retrieved_at,
        "freshness_status": _enum_value(freshness_status),
        "ttl_seconds": ttl_seconds,
        "expires_at": expires_at,
        "warnings": list(warnings),
        "degraded_state_reason": degraded_state_reason,
    }


def has_complete_market_attribution(source: Optional[SourceMetadata]) -> bool:
    """Return true when a market fact has the minimum required attribution."""

    if source is None:
        return False
    required = (
        source.provider_id,
        source.source_url_or_reference,
        source.retrieved_at,
        source.exchange,
        source.currency,
        source.license_posture,
    )
    return all(value not in (None, "") for value in required)


def attribution_coverage_counters(outputs: Iterable[NormalizedOutput]) -> AttributionCoverageCounters:
    """Count complete and degraded attribution outcomes for verification evidence."""

    complete = degraded_no_source = stale_cache = blocked = unsafe = 0
    for output in outputs:
        if contains_blocked_prompt_payload(output.to_dict()):
            unsafe += 1
        if output.degraded_state and output.degraded_state.code in {
            DegradedReason.MISSING_SOURCE.value,
            DegradedReason.NO_SOURCE_AVAILABLE.value,
        }:
            degraded_no_source += 1
        if output.degraded_state and output.degraded_state.code in {
            DegradedReason.BLOCKED_LICENSE.value,
            DegradedReason.PROVIDER_DOWN.value,
            DegradedReason.UNSUPPORTED_PROVIDER.value,
        }:
            blocked += 1
        freshness = output.freshness_metadata.get("freshness_status") if output.freshness_metadata else None
        if freshness == FreshnessStatus.STALE.value:
            stale_cache += 1
        if output.kind == NormalizedOutputKind.EVIDENCE_FACT and has_complete_market_attribution(output.source_metadata):
            complete += 1
    return AttributionCoverageCounters(
        complete_attribution=complete,
        degraded_no_source=degraded_no_source,
        stale_cache=stale_cache,
        provider_or_license_blocked=blocked,
        unsafe_trace_leak=unsafe,
    )


def make_degraded_output(
    *,
    code: str,
    safe_message: str,
    reason: DegradedReason | str,
    route: Optional[str] = None,
    tool_name: Optional[str] = None,
    provider_id: Optional[str] = None,
    retryable: bool = False,
) -> NormalizedOutput:
    """Create a degraded normalized output."""

    degraded = DegradedState(
        code=code,
        safe_message=safe_message,
        reason=reason,
        route=route,
        tool_name=tool_name,
        provider_id=provider_id,
        retryable=retryable,
    )
    return NormalizedOutput(
        kind=NormalizedOutputKind.DEGRADED_STATE,
        content={"code": code, "message": safe_message},
        degraded_state=degraded,
        warnings=(code,),
    )


def classify_normalized_output(value: Any) -> NormalizedOutputKind:
    """Return exactly one normalized output kind for a supported value."""

    if isinstance(value, NormalizedOutput):
        return value.kind
    if isinstance(value, DegradedState):
        return NormalizedOutputKind.DEGRADED_STATE
    if isinstance(value, InternalSymbolRecord):
        return NormalizedOutputKind.SYSTEM_RECORD
    if isinstance(value, Mapping):
        kind = value.get("kind")
        if kind:
            return NormalizedOutputKind(kind)
        if value.get("mutation_id"):
            return NormalizedOutputKind.MUTATION_RECEIPT
        if value.get("visualization_url") or value.get("chart_url"):
            return NormalizedOutputKind.VISUALIZATION_PROVENANCE
        if value.get("artifact_id") or value.get("artifact_reference"):
            return NormalizedOutputKind.GENERATED_ARTIFACT
        if value.get("source_record_reference") or value.get("identity"):
            return NormalizedOutputKind.SYSTEM_RECORD
    raise ValueError("Unable to classify normalized output kind")


def contains_blocked_prompt_payload(value: Any) -> bool:
    """Return true if a payload contains raw or unsafe prompt-boundary content."""

    if isinstance(value, bytes):
        return True
    if isinstance(value, str):
        lowered = value.lower()
        return "<script" in lowered or "<html" in lowered or "%pdf" in lowered
    if isinstance(value, Mapping):
        for key, item in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in BLOCKED_PROMPT_KEY_FRAGMENTS):
                return True
            if contains_blocked_prompt_payload(item):
                return True
    if isinstance(value, (list, tuple, set)):
        return any(contains_blocked_prompt_payload(item) for item in value)
    return False


def sanitize_prompt_payload(value: Any) -> Any:
    """Remove raw/unsafe content from a prompt-boundary projection."""

    if isinstance(value, bytes):
        return "[blocked-by-normalizer]"
    if isinstance(value, str):
        lowered = value.lower()
        if "<script" in lowered or "<html" in lowered or "%pdf" in lowered:
            return "[blocked-by-normalizer]"
        return value
    if isinstance(value, Mapping):
        clean: Dict[str, Any] = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in BLOCKED_PROMPT_KEY_FRAGMENTS):
                continue
            clean[str(key)] = sanitize_prompt_payload(item)
        return clean
    if isinstance(value, (list, tuple, set)):
        return [sanitize_prompt_payload(item) for item in value]
    return value


def sanitize_trace_metadata(value: Mapping[str, Any]) -> Dict[str, Any]:
    """Remove sensitive raw trace internals."""

    return sanitize_prompt_payload(value)


def stable_output_id(kind: str, payload: Mapping[str, Any]) -> str:
    """Build a deterministic short id for normalized outputs and envelopes."""

    data = json.dumps(_to_plain_dict(payload), sort_keys=True, default=str, separators=(",", ":"))
    return f"{kind.lower().replace(' ', '_')}:{hashlib.sha256(data.encode('utf-8')).hexdigest()[:16]}"


def utc_now_iso() -> str:
    """Return a UTC timestamp string."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return (str(item) for item in value)
    return ()


def _enum_value(value: Any) -> Any:
    return value.value if isinstance(value, Enum) else value


def _to_plain_dict(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _to_plain_dict(item) for key, item in asdict(value).items() if item is not None}
    if isinstance(value, Mapping):
        return {str(key): _to_plain_dict(item) for key, item in value.items() if item is not None}
    if isinstance(value, (list, tuple, set)):
        return [_to_plain_dict(item) for item in value]
    return value
