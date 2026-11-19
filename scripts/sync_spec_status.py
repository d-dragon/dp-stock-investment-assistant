from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "specs" / "spec-traceability.yaml"
DEFAULT_OUTPUT = ROOT / "specs" / "spec-sync-status.md"
DEFAULT_REVERSE_OUTPUT = ROOT / "docs" / "domains" / "agent" / "SRS_SPEC_TRACEABILITY.md"


TASK_PATTERN = re.compile(r"^- \[(?P<mark>[ xX])\] (?P<task>T\d+)\b")
STATUS_PATTERN = re.compile(r"^\*\*Status\*\*:\s*(?P<value>.+?)\s*$", re.MULTILINE)
# Optional in-cell anchors (<a id="sr-1-4-2"></a>) keep the ID in column 1.
# SR-/SNR- are the system SRS families; the agent families stay unchanged.
TABLE_ROW_ID_PATTERN = re.compile(
    r"^\|\s*(?:<a\s+id=[\"'][^\"']+[\"']></a>)?\s*"
    r"((?:FR|NFR|AC|IR|CON|ERR|PRIV|SR|SNR)-\d+(?:\.\d+)*[a-z]?)\s*\|"
)
DEFAULT_SRS_ID = "agent"
PITCH_TRACE_BEGIN = "# BEGIN GENERATED: pitch-trace"
PITCH_TRACE_END = "# END GENERATED: pitch-trace"
PITCH_FILE_ID = re.compile(r"^(M-\d+)(?:-([A-Z]))?(?:-|$)")
SLICE_HEADING = re.compile(r"^#{2,4}\s+([A-Z]\d+)\b")
SLICE_MARK = re.compile(r"\*\*([A-Z]\d+)\s+[\u2014\u2013-]")
PROSE_TIER = re.compile(
    r"\b([DFPST])(\d+)\s*[-\u2013\u2014]\s*(?:[DFPST])?(\d+)\s+are tier\s+([MD])\b",
    re.IGNORECASE,
)
ROW_CELL = re.compile(r"^(?:([A-Z]\d+)-([DFPST])(\d+)|([DFPST])(\d+))$")
MOVED_TIER = re.compile(r"^Moved to (M-\d+)\b")
ROW_TOKEN = re.compile(r"\b([A-Za-z]\d+)-([DFPSTdfpst])(\d+)\b")
# wt/m001-s3 is a worktree path. The row scanner would read it as M001-S3.
IGNORED_ROW_IDS = {"M001-S3"}
ROW_RANGE = re.compile(
    r"\b([A-Za-z]\d+)-([DFPSTdfpst])(\d+)\.\.(?:([A-Za-z]\d+)-)?([DFPSTdfpst])?(\d+)\b"
)
TEST_FILE_NAME = re.compile(r"(\.test|\.spec)\.[jt]sx?$", re.IGNORECASE)
GENERATED_LINE = re.compile(r"^> \*\*Generated\*\*: .*$", re.MULTILINE)
FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)


@dataclass(frozen=True)
class SrsTraceItem:
    item_id: str
    line_number: int


@dataclass(frozen=True)
class PitchRow:
    row_id: str
    tier: str
    deferred_to: str | None


@dataclass
class FeatureSyncResult:
    feature_id: str
    feature_title: str
    feature_path: str
    reference_document: str
    reference_anchor: str | None
    mapping_status: str
    coverage_status: str
    derived_status: str
    sync_status: str
    gate_enforced: bool
    task_total: int
    task_completed: int
    spec_status: str | None
    observations: List[str]
    evidence_links: List[Dict[str, str]]
    mapped_srs_items: List[str]
    srs_id: str


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def parse_spec_status(path: Path) -> str | None:
    text = read_text(path)
    if not text:
        return None
    match = STATUS_PATTERN.search(text)
    return match.group("value").strip() if match else None


def parse_tasks(path: Path) -> tuple[int, int]:
    total = 0
    completed = 0
    for line in read_text(path).splitlines():
        match = TASK_PATTERN.match(line)
        if not match:
            continue
        total += 1
        if match.group("mark").lower() == "x":
            completed += 1
    return total, completed


def normalize_status_value(value: str) -> str:
    return value.strip().lower().replace("-", " ")


def expected_spec_status(derived_status: str) -> str:
    return derived_status.replace("-", " ").title()


def pick_reference_document(feature: Dict[str, Any]) -> str:
    explicit_reference = feature.get("reference_document")
    if explicit_reference:
        return explicit_reference

    feature_path = ROOT / feature["feature_path"]
    for candidate in ("spec.md", "plan.md", "tasks.md", "analysis.md", "review.md"):
        candidate_path = feature_path / candidate
        if candidate_path.exists():
            return candidate_path.relative_to(ROOT).as_posix()
    return feature["feature_path"]


def normalize_evidence_links(entries: List[Any]) -> List[Dict[str, str]]:
    normalized: List[Dict[str, str]] = []
    for entry in entries:
        if isinstance(entry, str):
            normalized.append({"path": entry, "label": entry})
            continue
        if isinstance(entry, dict) and entry.get("path"):
            normalized.append(
                {
                    "path": str(entry["path"]),
                    "label": str(entry.get("label") or entry["path"]),
                    "anchor": str(entry.get("anchor", "")),
                }
            )
    return normalized


def make_markdown_link(report_path: Path, target_path: Path, label: str, anchor: str | None = None) -> str:
    relative_target = Path(os.path.relpath(target_path, report_path.parent))
    target = relative_target.as_posix()
    if anchor:
        target = f"{target}#{anchor}"
    return f"[{label}]({target})"


def extract_srs_items(path: Path) -> List[SrsTraceItem]:
    ordered: List[SrsTraceItem] = []
    seen = set()
    for line_number, line in enumerate(read_text(path).splitlines(), start=1):
        match = TABLE_ROW_ID_PATTERN.match(line)
        if not match:
            continue
        value = match.group(1)
        if value in seen:
            continue
        seen.add(value)
        ordered.append(SrsTraceItem(item_id=value, line_number=line_number))
    return ordered


def derive_feature_status(feature: Dict[str, Any], manifest: Dict[str, Any]) -> FeatureSyncResult:
    feature_path = ROOT / feature["feature_path"]
    reference_document = pick_reference_document(feature)
    reference_anchor = feature.get("reference_anchor")
    mapping_status = feature.get("mapping_status", "unmapped")
    title = feature.get("feature_title", feature["feature_id"])
    coverage_status = feature.get("srs_mapping", {}).get("coverage_status", "n/a")
    observations: List[str] = []
    gate_enforced = feature.get("status_sync", {}).get("gate_enforced", mapping_status == "mapped")

    spec_path = feature_path / "spec.md"
    plan_path = feature_path / "plan.md"
    tasks_path = feature_path / "tasks.md"
    analysis_path = feature_path / "analysis.md"
    review_path = feature_path / "review.md"
    analyze_done = feature_path / ".analyze-done"
    verify_done = feature_path / ".verify-done"

    spec_status = parse_spec_status(spec_path)
    task_total, task_completed = parse_tasks(tasks_path)
    mapped_srs_items = feature.get("srs_mapping", {}).get("mapped_srs_items", [])

    analyzed = analysis_path.exists() and analyze_done.exists()
    planned = plan_path.exists()
    implemented = task_total > 0 and task_total == task_completed
    verified = review_path.exists() and verify_done.exists() and implemented

    if mapping_status != "mapped":
        derived_status = "unmapped"
        sync_status = "unmapped"
    elif verified:
        derived_status = "verified"
        sync_status = "current"
    elif implemented:
        derived_status = "implemented"
        sync_status = "current"
    elif planned:
        derived_status = "planned"
        sync_status = "current"
    elif analyzed:
        derived_status = "analyzed"
        sync_status = "current"
    elif normalize_status_value(spec_status or "") == "clarified":
        derived_status = "clarified"
        sync_status = "current"
    else:
        derived_status = "draft"
        sync_status = "stale"

    if mapping_status == "mapped" and not gate_enforced and sync_status == "current":
        sync_status = "informational"
        observations.append("Mapping is excluded from the sync gate and retained for historical overlap traceability.")

    baseline_version = feature.get("srs_mapping", {}).get("baseline_version")
    srs_id = resolve_feature_srs_id(feature, manifest)
    manifest_srs_version = resolve_feature_srs_version(feature, manifest)
    if mapping_status == "mapped" and baseline_version != manifest_srs_version:
        sync_status = "stale"
        observations.append(
            f"Mapped baseline version is {baseline_version or 'unset'} but manifest SRS version is {manifest_srs_version}."
        )

    expected_status = expected_spec_status(derived_status)
    if mapping_status == "mapped" and spec_status and normalize_status_value(spec_status) != normalize_status_value(expected_status):
        observations.append(
            f"spec.md status is '{spec_status}' but derived lifecycle status is '{expected_status}'."
        )
        if sync_status == "current":
            sync_status = "current-with-notes"

    if mapping_status == "mapped" and not feature.get("srs_mapping", {}).get("mapped_functional_groups"):
        sync_status = "stale"
        observations.append("Mapped feature is missing functional-group links to the SRS.")

    evidence_links = normalize_evidence_links(feature.get("speckit_mapping", {}).get("evidence_paths", []))

    return FeatureSyncResult(
        feature_id=feature["feature_id"],
        feature_title=title,
        feature_path=feature["feature_path"],
        reference_document=reference_document,
        reference_anchor=reference_anchor,
        mapping_status=mapping_status,
        coverage_status=coverage_status,
        derived_status=derived_status,
        sync_status=sync_status,
        gate_enforced=gate_enforced,
        task_total=task_total,
        task_completed=task_completed,
        spec_status=spec_status,
        observations=observations,
        evidence_links=evidence_links,
        mapped_srs_items=mapped_srs_items,
        srs_id=srs_id,
    )


def build_reverse_index(
    results: List[FeatureSyncResult],
    srs_id: str | None = None,
) -> Dict[str, List[FeatureSyncResult]]:
    reverse: Dict[str, List[FeatureSyncResult]] = {}
    for result in results:
        if result.mapping_status != "mapped":
            continue
        if srs_id is not None and result.srs_id != srs_id:
            continue
        for item in result.mapped_srs_items:
            reverse.setdefault(item, []).append(result)
    return reverse


def render_revision_history(report_metadata: Dict[str, Any]) -> List[str]:
    history = report_metadata.get("revision_history", [])
    if not history:
        return []

    lines: List[str] = []
    lines.append("## Revision History")
    lines.append("")
    lines.append("| Version | Date | Summary |")
    lines.append("|---------|------|---------|")
    for entry in history:
        lines.append(
            f"| `{entry.get('version', 'n/a')}` | `{entry.get('date', 'n/a')}` | {entry.get('summary', '')} |"
        )
    lines.append("")
    return lines


def get_requirement_family(item_id: str) -> str:
    parts = item_id.split("-")
    prefix = parts[0]
    if len(parts) == 1:
        return item_id
    suffix = parts[1]
    major = suffix.split(".")[0]
    if prefix in {"CON", "ERR", "PRIV"}:
        return prefix
    return f"{prefix}-{major}"


def get_family_anchor(family: str) -> str:
    return family.lower()


def get_family_type(family: str) -> str:
    return family.split("-")[0]


def render_report(
    manifest: Dict[str, Any],
    results: List[FeatureSyncResult],
    output_path: Path,
    pitches: List[Dict[str, Any]] | None = None,
) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    srs_target = ROOT / manifest["srs"]["path"]
    report_metadata = manifest.get("reports", {}).get("spec_sync_status", {})
    lines: List[str] = []
    lines.append("# Spec Sync Status")
    lines.append("")
    lines.append(f"> **Document Version**: {report_metadata.get('version', '1.0')}")
    lines.append(f"> **Generated**: {generated_at}")
    lines.append(f"> **Status**: {report_metadata.get('status', 'Active')}")
    lines.append(f"> **Traceability Manifest Version**: {manifest.get('version', 'n/a')}")
    lines.append("")
    lines.append("## Baseline")
    lines.append("")
    lines.append(f"- SRS: {make_markdown_link(output_path, srs_target, manifest['srs']['path'])}")
    lines.append(f"- SRS version: `{manifest['srs']['version']}`")
    lines.append(f"- SRS last updated: `{manifest['srs']['last_updated']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Feature | Mapping | Coverage | Derived Status | Sync Status | Tasks |")
    lines.append("|---------|---------|----------|----------------|-------------|-------|")
    for result in results:
        task_cell = "n/a" if result.mapping_status != "mapped" or result.task_total == 0 else f"{result.task_completed}/{result.task_total}"
        feature_link = make_markdown_link(output_path, ROOT / result.reference_document, result.feature_id, anchor=result.reference_anchor)
        lines.append(
            f"| {feature_link} | `{result.mapping_status}` | `{result.coverage_status}` | `{result.derived_status}` | `{result.sync_status}` | `{task_cell}` |"
        )
    lines.append("")
    if pitches is not None:
        lines.extend(render_pitch_delivery(pitches, output_path))
    lines.extend(render_revision_history(report_metadata))

    for result in results:
        lines.append(f"## {result.feature_id}")
        lines.append("")
        lines.append(f"- Title: {result.feature_title}")
        lines.append(f"- Path: {make_markdown_link(output_path, ROOT / result.reference_document, result.feature_path, anchor=result.reference_anchor)}")
        lines.append(f"- Mapping status: `{result.mapping_status}`")
        lines.append(f"- Coverage status: `{result.coverage_status}`")
        lines.append(f"- Derived status: `{result.derived_status}`")
        lines.append(f"- Sync status: `{result.sync_status}`")
        lines.append(f"- Sync gate enforced: `{'yes' if result.gate_enforced else 'no'}`")
        if result.spec_status:
            lines.append(f"- spec.md status field: `{result.spec_status}`")
        if result.mapping_status == "mapped" and result.task_total:
            lines.append(f"- Task completion: `{result.task_completed}/{result.task_total}`")
        if result.mapping_status == "mapped" and result.mapped_srs_items:
            lines.append(f"- Linked SRS items: `{', '.join(result.mapped_srs_items)}`")
        if result.observations:
            lines.append("- Observations:")
            for note in result.observations:
                lines.append(f"  - {note}")
        if result.evidence_links:
            lines.append("- Evidence:")
            for evidence in result.evidence_links:
                lines.append(
                    f"  - {make_markdown_link(output_path, ROOT / evidence['path'], evidence['label'], anchor=evidence.get('anchor') or None)}"
                )
        lines.append("")

    lines.append("## Status Semantics")
    lines.append("")
    lines.append("- `derived status` is computed from spec-kit artifacts, with a pre-planning `clarified` stage recognized from a spec header of `Status: Clarified`.")
    lines.append("- `sync status` reports whether the feature-to-SRS mapping is current against the manifest SRS baseline.")
    lines.append("- `coverage status` shows whether the feature covers all, some, or none of the linked SRS scope.")
    lines.append("")
    lines.append("## Operational Rule")
    lines.append("")
    lines.append("- Update `spec-traceability.yaml` when a feature gains or changes SRS scope.")
    lines.append("- Update `tasks.md` and workflow markers during delivery.")
    lines.append("- Regenerate this report with `python scripts/sync_spec_status.py --gate` whenever either side changes.")
    lines.append("")
    return "\n".join(lines)


def render_reverse_trace(
    manifest: Dict[str, Any],
    results: List[FeatureSyncResult],
    output_path: Path,
    srs_document: Dict[str, Any] | None = None,
    srs_id: str | None = None,
) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    document = srs_document or manifest["srs"]
    srs_path = ROOT / document["path"]
    srs_items = extract_srs_items(srs_path)
    reverse = build_reverse_index(results, srs_id=srs_id)
    report_metadata = dict(manifest.get("reports", {}).get("srs_spec_traceability", {}))
    # The shared changelog describes the agent reverse index. Other SRS reports
    # keep the same header fields and omit that history so the agent file stays put.
    if srs_id not in (None, DEFAULT_SRS_ID):
        report_metadata.pop("revision_history", None)

    lines: List[str] = []
    lines.append("# SRS To Spec Traceability")
    lines.append("")
    lines.append(f"> **Document Version**: {report_metadata.get('version', '1.0')}")
    lines.append(f"> **Generated**: {generated_at}")
    lines.append(f"> **Status**: {report_metadata.get('status', 'Active')}")
    lines.append(f"> **Traceability Manifest Version**: {manifest.get('version', 'n/a')}")
    lines.append("")
    lines.append("## Baseline")
    lines.append("")
    lines.append(f"- SRS: {make_markdown_link(output_path, srs_path, document['path'])}")
    lines.append(f"- SRS version: `{document['version']}`")
    lines.append("")
    mapped_count = sum(1 for item in srs_items if item.item_id in reverse)
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total traced SRS items discovered: `{len(srs_items)}`")
    lines.append(f"- Items with linked specs: `{mapped_count}`")
    lines.append(f"- Items without linked specs: `{len(srs_items) - mapped_count}`")
    lines.append("")
    lines.extend(render_revision_history(report_metadata))
    families: List[str] = []
    grouped_items: Dict[str, List[SrsTraceItem]] = {}
    for item in srs_items:
        family = get_requirement_family(item.item_id)
        if family not in grouped_items:
            grouped_items[family] = []
            families.append(family)
        grouped_items[family].append(item)

    lines.append("## Family Index")
    lines.append("")
    family_groups: Dict[str, List[str]] = {}
    for family in families:
        family_type = get_family_type(family)
        family_groups.setdefault(family_type, []).append(family)
    lines.append("| Type | Families |")
    lines.append("|------|----------|")
    ordered_types = ["FR", "NFR", "AC", "IR", "CON", "ERR", "PRIV", "SR", "SNR"]
    for family_type in ordered_types:
        grouped_family_list = family_groups.get(family_type)
        if not grouped_family_list:
            continue
        family_links = ", ".join(
            f"[{family}](#{get_family_anchor(family)})" for family in grouped_family_list
        )
        lines.append(f"| `{family_type}` | {family_links} |")
    lines.append("")
    lines.append("## Reverse Trace")
    lines.append("")

    for family in families:
        lines.append(f"### {family}")
        lines.append("")
        family_items = grouped_items[family]
        family_mapped = sum(1 for item in family_items if item.item_id in reverse)
        lines.append(f"Mapped: `{family_mapped}/{len(family_items)}`. Unmapped: `{len(family_items) - family_mapped}`.")
        lines.append("")
        lines.append("| SRS Item | Linked Spec | Current Status | Sync Status |")
        lines.append("|----------|-------------|----------------|-------------|")
        for item in family_items:
            linked = reverse.get(item.item_id, [])
            item_link = make_markdown_link(output_path, srs_path, item.item_id, anchor=f"L{item.line_number}")
            if not linked:
                lines.append(f"| {item_link} | `-` | `unmapped` | `unmapped` |")
                continue
            for index, entry in enumerate(linked):
                srs_cell = item_link if index == 0 else ""
                feature_link = make_markdown_link(
                    output_path,
                    ROOT / entry.reference_document,
                    entry.feature_id,
                    anchor=entry.reference_anchor,
                )
                lines.append(f"| {srs_cell} | {feature_link} | `{entry.derived_status}` | `{entry.sync_status}` |")
        lines.append("")
    lines.append("## Gate Rule")
    lines.append("")
    lines.append("- A mapped feature is in sync only when its derived status and its feature `spec.md` status agree, and its SRS baseline version matches the manifest baseline.")
    lines.append("- Informational mappings remain visible in the reverse trace but are excluded from gate enforcement.")
    lines.append("- Use `python scripts/sync_spec_status.py --gate` after each development iteration.")
    lines.append("")
    return "\n".join(lines)


def resolve_feature_srs_id(feature: Dict[str, Any], manifest: Dict[str, Any]) -> str:
    selected = (feature.get("srs_mapping") or {}).get("srs")
    if selected:
        return str(selected)
    documents = manifest.get("srs_documents") or {}
    if documents and DEFAULT_SRS_ID not in documents:
        return str(next(iter(documents)))
    return DEFAULT_SRS_ID


def resolve_feature_srs_version(feature: Dict[str, Any], manifest: Dict[str, Any]) -> Any:
    """Baseline version for this feature. Absent srs_mapping.srs keeps the agent default."""
    srs_id = resolve_feature_srs_id(feature, manifest)
    documents = manifest.get("srs_documents") or {}
    document = documents.get(srs_id)
    if isinstance(document, dict) and document.get("version") is not None:
        return document.get("version")
    return (manifest.get("srs") or {}).get("version")


def write_generated_report(path: Path, content: str) -> None:
    """Write a report, keeping the previous file when only the timestamp changed.

    The clock is not part of the trace. CI runs `git diff --exit-code` after
    this script, so a fresh timestamp on an otherwise identical report would
    fail every build.
    """
    text = content.rstrip("\n") + "\n"
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if GENERATED_LINE.sub("> **Generated**:", existing) == GENERATED_LINE.sub("> **Generated**:", text):
            return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def reverse_output_for(srs_id: str, document: Dict[str, Any], cli_path: Path) -> Path:
    if srs_id == DEFAULT_SRS_ID and cli_path != DEFAULT_REVERSE_OUTPUT:
        return cli_path
    declared = document.get("reverse_output")
    if declared:
        declared_path = Path(str(declared))
        return declared_path if declared_path.is_absolute() else ROOT / declared_path
    if srs_id == DEFAULT_SRS_ID:
        return cli_path
    return ROOT / "docs" / srs_id / "SRS_SPEC_TRACEABILITY.md"


def iter_srs_documents(manifest: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    documents = manifest.get("srs_documents")
    if not isinstance(documents, dict) or not documents:
        legacy = manifest.get("srs")
        if not isinstance(legacy, dict):
            return []
        return [(DEFAULT_SRS_ID, legacy)]
    return [(str(srs_id), document) for srs_id, document in documents.items() if isinstance(document, dict)]


def pitch_id_from_name(name: str) -> str | None:
    match = PITCH_FILE_ID.match(name)
    if not match:
        return None
    milestone, letter = match.group(1), match.group(2)
    return f"{milestone}-{letter}" if letter else milestone


def milestone_of(pitch_id: str) -> str:
    parts = pitch_id.split("-")
    if len(parts) >= 2 and parts[1].isdigit():
        return f"{parts[0]}-{parts[1]}"
    return pitch_id


def current_milestone(pitch_ids: List[str]) -> str | None:
    """Lowest milestone number among pitches. Later milestones are not the fail scope."""
    ranked = [milestone_of(pitch_id) for pitch_id in pitch_ids]
    if not ranked:
        return None

    def sort_key(value: str) -> Tuple[int, str]:
        parts = value.split("-")
        number = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10**9
        return number, value

    return sorted(set(ranked), key=sort_key)[0]


def parse_step_aliases(text: str) -> set[str]:
    """Bn-Tn labels for migration steps T0-T8. They are not acceptance rows."""
    marks = list(SLICE_MARK.finditer(text))
    aliases: set[str] = set()
    for index, mark in enumerate(marks):
        next_mark = marks[index + 1].start() if index + 1 < len(marks) else len(text)
        heading = re.search(r"\n## ", text[mark.end():])
        end = next_mark
        if heading:
            end = min(end, mark.end() + heading.start())
        window = text[mark.start():end]
        slice_id = mark.group(1)
        for raw_number in re.findall(r"T(\d+)", window):
            number = int(raw_number)
            if 0 <= number <= 8:
                aliases.add(f"{slice_id}-T{number}")
    return aliases


def split_table_cells(line: str) -> List[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    if cells and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells if cell != ""):
        return None
    if cells and re.fullmatch(r":?-{3,}:?", cells[0].replace(" ", "")):
        return None
    return cells


def tier_from_cells(cells: List[str]) -> Tuple[str | None, str | None]:
    for cell in cells:
        cleaned = cell.strip().strip("*").strip()
        moved = MOVED_TIER.match(cleaned)
        if moved:
            return "moved", moved.group(1)
        if cleaned in {"M", "D"}:
            return cleaned, None
    return None, None


def parse_pitch_rows(text: str) -> Tuple[Dict[str, PitchRow], set[str]]:
    aliases = parse_step_aliases(text)
    pending: Dict[str, Tuple[str | None, str | None]] = {}
    current_slice: str | None = None
    for line in text.splitlines():
        heading = SLICE_HEADING.match(line)
        if heading:
            current_slice = heading.group(1)
        prose = PROSE_TIER.search(line)
        if prose and current_slice:
            kind, start, end, tier = prose.groups()
            for number in range(int(start), int(end) + 1):
                row_id = f"{current_slice}-{kind.upper()}{number}"
                if row_id in pending:
                    _tier, moved = pending[row_id]
                    pending[row_id] = (tier.upper(), moved)
        cells = split_table_cells(line)
        if not cells:
            continue
        raw_id = cells[0].strip().strip("`").strip("*")
        match = ROW_CELL.match(raw_id)
        if not match:
            continue
        slice_id, kind, number, bare_kind, bare_number = match.groups()
        if slice_id:
            row_id = f"{slice_id}-{kind}{number}"
        elif current_slice:
            # Prefix-less IDs are canonical only inside their slice table (P1 in B4 -> B4-P1).
            row_id = f"{current_slice}-{bare_kind}{bare_number}"
        else:
            continue
        tier, moved = tier_from_cells(cells[1:])
        pending[row_id] = (tier, moved)
    rows: Dict[str, PitchRow] = {}
    for row_id, (tier, moved) in pending.items():
        # An acceptance row with no D or Moved mark is must-have. The B4 edge-case
        # table omits the Tier column; the following sentence sets those rows to M.
        rows[row_id] = PitchRow(row_id=row_id, tier=tier or "M", deferred_to=moved)
    return rows, aliases


def parse_pitch_slices(text: str) -> List[str]:
    """Slice ids in first-seen order.

    Solution sketches head each slice as a bold bullet (`**B0 — ...`).
    A later section may repeat the same id as a markdown heading (`### B3:`).
    A pitch with neither form has no slices.
    """
    found: List[str] = []
    seen: set[str] = set()

    def add(slice_id: str) -> None:
        if slice_id in seen:
            return
        seen.add(slice_id)
        found.append(slice_id)

    for line in text.splitlines():
        heading = SLICE_HEADING.match(line)
        if heading:
            add(heading.group(1))
        for mark in SLICE_MARK.finditer(line):
            add(mark.group(1))
    return found


# Least-delivered first. A slice shared by several specs stays at the earliest status.
SLICE_STATUS_ORDER = (
    "unmapped",
    "draft",
    "clarified",
    "analyzed",
    "planned",
    "implemented",
    "verified",
)


def derive_directory_status(spec_dir: Path) -> str:
    """Lifecycle status for a spec directory that is not a manifest feature.

    Same artifact ladder as derive_feature_status after the mapped/unmapped branch.
    A present spec that is not yet planned is draft. A missing spec.md is unmapped.
    """
    spec_status = parse_spec_status(spec_dir / "spec.md")
    task_total, task_completed = parse_tasks(spec_dir / "tasks.md")
    analyzed = (spec_dir / "analysis.md").exists() and (spec_dir / ".analyze-done").exists()
    planned = (spec_dir / "plan.md").exists()
    implemented = task_total > 0 and task_total == task_completed
    verified = (spec_dir / "review.md").exists() and (spec_dir / ".verify-done").exists() and implemented
    if verified:
        return "verified"
    if implemented:
        return "implemented"
    if planned:
        return "planned"
    if analyzed:
        return "analyzed"
    if normalize_status_value(spec_status or "") == "clarified":
        return "clarified"
    if spec_status or (spec_dir / "spec.md").exists():
        return "draft"
    return "unmapped"


def feature_status_by_spec_id(results: List[FeatureSyncResult]) -> Dict[str, str]:
    indexed: Dict[str, str] = {}
    for result in results:
        indexed[result.feature_id] = result.derived_status
        indexed[Path(result.feature_path).name] = result.derived_status
    return indexed


def status_for_spec(spec: Dict[str, Any], root: Path, status_by_id: Dict[str, str]) -> str:
    """Derived feature status when the spec is in the manifest; otherwise the directory ladder."""
    spec_id = str(spec["id"])
    if spec_id in status_by_id:
        return status_by_id[spec_id]
    return derive_directory_status(root / Path(str(spec["path"])).parent)


def combine_slice_status(statuses: List[str]) -> str:
    """One status for every spec that claims the slice. Empty means unclaimed."""
    if not statuses:
        return "unclaimed"

    def rank(value: str) -> Tuple[int, str]:
        try:
            return (SLICE_STATUS_ORDER.index(value), "")
        except ValueError:
            return (-1, value)

    return min(statuses, key=rank)


def build_slice_delivery(
    pitch_id: str,
    slice_ids: List[str],
    specs: List[Dict[str, Any]],
    root: Path,
    status_by_id: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
    """Slice order follows the pitch. Unknown claims fail; unclaimed slices warn."""
    known = set(slice_ids)
    claims: Dict[str, List[Dict[str, str]]] = {slice_id: [] for slice_id in slice_ids}
    failures: List[str] = []
    for spec in specs:
        seen_slices: set[str] = set()
        for slice_id in spec["slices"]:
            if slice_id in seen_slices:
                continue
            seen_slices.add(slice_id)
            if slice_id not in known:
                failures.append(
                    f"pitch {pitch_id}: spec {spec['id']} claims slice {slice_id} that does not exist in the pitch"
                )
                continue
            claims[slice_id].append(
                {
                    "id": spec["id"],
                    "path": spec["path"],
                    "status": status_for_spec(spec, root, status_by_id),
                }
            )
    entries: List[Dict[str, Any]] = []
    warnings: List[str] = []
    for slice_id in slice_ids:
        spec_rows = claims[slice_id]
        if not spec_rows:
            warnings.append(f"{pitch_id} {slice_id}: slice has no claiming spec")
        entries.append(
            {
                "slice": slice_id,
                "specs": [row["id"] for row in spec_rows],
                "status": combine_slice_status([row["status"] for row in spec_rows]),
                "spec_rows": spec_rows,
            }
        )
    return entries, failures, warnings


def canon_row(slice_id: str, kind: str, number: str) -> str:
    return f"{slice_id.upper()}-{kind.upper()}{int(number)}"


def extract_row_ids(text: str) -> List[str]:
    found: List[str] = []
    seen: set[str] = set()
    for match in ROW_RANGE.finditer(text):
        slice_id, kind, start, end_slice, end_kind, end = match.groups()
        end_slice = end_slice or slice_id
        end_kind = end_kind or kind
        if end_slice.upper() != slice_id.upper() or end_kind.upper() != kind.upper():
            continue
        start_number = int(start)
        end_number = int(end)
        if end_number < start_number:
            continue
        for number in range(start_number, end_number + 1):
            token = canon_row(slice_id, kind, str(number))
            if token in IGNORED_ROW_IDS or token in seen:
                continue
            seen.add(token)
            found.append(token)
    for match in ROW_TOKEN.finditer(text):
        token = canon_row(*match.groups())
        if token in IGNORED_ROW_IDS or token in seen:
            continue
        seen.add(token)
        found.append(token)
    return found


def parse_front_matter(text: str) -> Dict[str, Any] | None:
    match = FRONT_MATTER.search(text)
    if not match:
        return None
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict) or not data.get("pitch"):
        return None
    return data


def as_str_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def classify_row_token(token: str, rows: Dict[str, PitchRow], aliases: set[str]) -> str:
    # Step aliases such as B1-T0 and B4-T6 (migration T6) are not row links,
    # even when an acceptance row reuses the same id.
    if token in aliases:
        return "alias"
    if token in rows:
        return "row"
    return "unknown"


def scan_task_row_ids(tasks_path: Path) -> List[str]:
    if not tasks_path.exists():
        return []
    found: List[str] = []
    seen: set[str] = set()
    for line in read_text(tasks_path).splitlines():
        if not TASK_PATTERN.match(line):
            continue
        for token in extract_row_ids(line):
            if token not in seen:
                seen.add(token)
                found.append(token)
    return found


def scan_frontend_test_ids(frontend_src: Path) -> List[str]:
    if not frontend_src.exists():
        return []
    found: List[str] = []
    seen: set[str] = set()

    def add_from(text: str) -> None:
        for token in extract_row_ids(text):
            if token not in seen:
                seen.add(token)
                found.append(token)

    for path in frontend_src.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(frontend_src).as_posix()
        add_from(path.name)
        is_test = bool(TEST_FILE_NAME.search(path.name) or "/__tests__/" in f"/{relative}")
        if not is_test:
            continue
        add_from(read_text(path))
    return found


def yaml_flow(items: List[str]) -> str:
    if not items:
        return "[]"
    rendered: List[str] = []
    for item in items:
        if re.fullmatch(r"[A-Za-z0-9_./-]+", item):
            rendered.append(item)
        else:
            rendered.append(json_quote(item))
    return "[" + ", ".join(rendered) + "]"


def json_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_pitch_delivery(pitches: List[Dict[str, Any]], output_path: Path) -> List[str]:
    """One row per pitch slice. Several claiming specs share the row and its combined status."""
    lines: List[str] = [
        "## Pitch delivery",
        "",
        "| Pitch | Slice | Spec | Status |",
        "|-------|-------|------|--------|",
    ]
    for pitch in pitches:
        pitch_link = make_markdown_link(output_path, ROOT / pitch["path"], pitch["pitch"])
        for entry in pitch.get("slice_delivery", []):
            spec_rows = entry.get("spec_rows") or []
            if spec_rows:
                spec_cell = ", ".join(
                    make_markdown_link(output_path, ROOT / row["path"], row["id"]) for row in spec_rows
                )
            else:
                spec_cell = "`-`"
            lines.append(f"| {pitch_link} | `{entry['slice']}` | {spec_cell} | `{entry['status']}` |")
    lines.append("")
    return lines


def render_slice_delivery_lines(entries: List[Dict[str, Any]]) -> List[str]:
    if not entries:
        return ["    slice_delivery: []"]
    lines = ["    slice_delivery:"]
    for entry in entries:
        lines.append(f"      - slice: {entry['slice']}")
        lines.append(f"        specs: {yaml_flow(entry['specs'])}")
        lines.append(f"        status: {entry['status']}")
    return lines


def render_pitch_trace(pitches: List[Dict[str, Any]]) -> str:
    lines: List[str] = [
        "# Generated by scripts/sync_spec_status.py. Do not edit by hand.",
        "# Source of truth: specs/pitches/*.md acceptance tables and solution-sketch slice headings, spec.md front matter, tasks.md row tags, and frontend/src tests.",
        "pitch_trace:",
    ]
    for pitch in pitches:
        lines.append(f"  - pitch: {pitch['pitch']}")
        lines.append(f"    path: {pitch['path']}")
        specs = pitch["specs"]
        if not specs:
            lines.append("    specs: []")
        else:
            lines.append("    specs:")
            for spec in specs:
                lines.append(f"      - id: {spec['id']}")
                lines.append(f"        path: {spec['path']}")
                lines.append(f"        slices: {yaml_flow(spec['slices'])}")
                lines.append(f"        rows: {yaml_flow(spec['rows'])}")
                lines.append(f"        task_rows: {yaml_flow(spec['task_rows'])}")
                lines.append(f"        test_rows: {yaml_flow(spec['test_rows'])}")
        lines.extend(render_slice_delivery_lines(pitch.get("slice_delivery") or []))
        deferred = pitch["deferred_rows"]
        if not deferred:
            lines.append("    deferred_rows: []")
        else:
            lines.append("    deferred_rows:")
            for row_id in deferred:
                lines.append(f"      - {row_id}")
        lines.append(f"    orphans: {yaml_flow(pitch['orphans'])}")
        lines.append(f"    warnings: {yaml_flow(pitch['warnings'])}")
    return "\n".join(lines) + "\n"


def replace_pitch_trace_block(manifest_path: Path, body: str) -> None:
    text = manifest_path.read_text(encoding="utf-8")
    begin_at = text.find(PITCH_TRACE_BEGIN)
    end_at = text.find(PITCH_TRACE_END)
    if begin_at < 0 or end_at < 0 or end_at < begin_at:
        return
    begin_line_end = text.find("\n", begin_at)
    if begin_line_end < 0:
        return
    updated = text[: begin_line_end + 1] + body + text[end_at:]
    if updated != text:
        manifest_path.write_text(updated, encoding="utf-8")


def collect_pitch_trace(
    root: Path,
    results: List[FeatureSyncResult] | None = None,
) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
    pitches_dir = root / "specs" / "pitches"
    pitch_files = sorted(path for path in pitches_dir.glob("M-*.md") if pitch_id_from_name(path.name))
    pitch_rows: Dict[str, Dict[str, PitchRow]] = {}
    pitch_aliases: Dict[str, set[str]] = {}
    pitch_paths: Dict[str, str] = {}
    pitch_slices: Dict[str, List[str]] = {}
    for path in pitch_files:
        pitch_id = pitch_id_from_name(path.name)
        if pitch_id is None:
            continue
        text = read_text(path)
        rows, aliases = parse_pitch_rows(text)
        pitch_rows[pitch_id] = rows
        pitch_aliases[pitch_id] = aliases
        pitch_slices[pitch_id] = parse_pitch_slices(text)
        pitch_paths[pitch_id] = path.relative_to(root).as_posix()
    status_by_id = feature_status_by_spec_id(results or [])

    active_milestone = current_milestone(list(pitch_paths))
    specs_by_pitch: Dict[str, List[Dict[str, Any]]] = {pitch_id: [] for pitch_id in pitch_paths}
    unknown_by_pitch: Dict[str, List[str]] = {pitch_id: [] for pitch_id in pitch_paths}
    test_tokens = scan_frontend_test_ids(root / "frontend" / "src")

    for spec_md in sorted((root / "specs").glob("*/spec.md")):
        front_matter = parse_front_matter(read_text(spec_md))
        if not front_matter:
            continue
        pitch_id = str(front_matter["pitch"])
        if pitch_id not in pitch_rows:
            continue
        rows = pitch_rows[pitch_id]
        aliases = pitch_aliases[pitch_id]
        spec_dir = spec_md.parent
        declared_rows = as_str_list(front_matter.get("rows"))
        declared_deferred = as_str_list(front_matter.get("deferred_rows"))
        for row_id in declared_rows + declared_deferred:
            if classify_row_token(row_id, rows, aliases) == "unknown":
                unknown_by_pitch[pitch_id].append(f"unknown:{spec_md.relative_to(root).as_posix()}:{row_id}")
        task_rows: List[str] = []
        tasks_path = spec_dir / "tasks.md"
        for token in scan_task_row_ids(tasks_path):
            kind = classify_row_token(token, rows, aliases)
            if kind == "row":
                task_rows.append(token)
            elif kind == "unknown":
                unknown_by_pitch[pitch_id].append(
                    f"unknown:{tasks_path.relative_to(root).as_posix()}:{token}"
                )
        claimed = set(declared_rows + declared_deferred)
        test_rows = [
            token
            for token in test_tokens
            if token in claimed and classify_row_token(token, rows, aliases) == "row"
        ]
        specs_by_pitch[pitch_id].append(
            {
                "id": spec_dir.name,
                "path": spec_md.relative_to(root).as_posix(),
                "slices": as_str_list(front_matter.get("slices")),
                "rows": declared_rows,
                "task_rows": task_rows,
                "test_rows": test_rows,
            }
        )

    linked_tests: Dict[str, set[str]] = {pitch_id: set() for pitch_id in pitch_paths}
    global_test_unknowns: List[str] = []
    for token in test_tokens:
        kinds = [
            classify_row_token(token, pitch_rows[pitch_id], pitch_aliases[pitch_id])
            for pitch_id in pitch_rows
        ]
        if "alias" in kinds:
            continue
        if "row" in kinds:
            for pitch_id in pitch_rows:
                if classify_row_token(token, pitch_rows[pitch_id], pitch_aliases[pitch_id]) == "row":
                    linked_tests[pitch_id].add(token)
            continue
        global_test_unknowns.append(f"unknown:frontend/src:{token}")
    if global_test_unknowns and pitch_paths:
        first_pitch = next(iter(pitch_paths))
        for unknown in global_test_unknowns:
            if unknown not in unknown_by_pitch[first_pitch]:
                unknown_by_pitch[first_pitch].append(unknown)

    pitches: List[Dict[str, Any]] = []
    failures: List[str] = []
    warnings: List[str] = []
    for pitch_id in pitch_paths:
        rows = pitch_rows[pitch_id]
        specs = specs_by_pitch[pitch_id]
        linked: set[str] = set(linked_tests[pitch_id])
        for spec in specs:
            linked.update(spec["rows"])
            linked.update(spec["task_rows"])
            linked.update(spec["test_rows"])
        orphans: List[str] = []
        pitch_warnings: List[str] = []
        for row_id, row in rows.items():
            if row.deferred_to or row_id in linked:
                continue
            in_current = milestone_of(pitch_id) == active_milestone
            if row.tier == "M" and in_current:
                orphans.append(row_id)
            else:
                pitch_warnings.append(row_id)
        for unknown in unknown_by_pitch[pitch_id]:
            if unknown not in orphans:
                orphans.append(unknown)
        deferred_rows = [row_id for row_id, row in rows.items() if row.deferred_to]
        slice_delivery, slice_failures, slice_warnings = build_slice_delivery(
            pitch_id,
            pitch_slices[pitch_id],
            specs,
            root,
            status_by_id,
        )
        pitches.append(
            {
                "pitch": pitch_id,
                "path": pitch_paths[pitch_id],
                "specs": specs,
                "slice_delivery": slice_delivery,
                "deferred_rows": deferred_rows,
                "orphans": orphans,
                "warnings": pitch_warnings,
            }
        )
        for orphan in orphans:
            if orphan.startswith("unknown:"):
                _kind, location, row_id = orphan.split(":", 2)
                failures.append(f"pitch {pitch_id}: link to nonexistent row id {row_id} in {location}")
            else:
                failures.append(f"pitch {pitch_id}: must-have row {orphan} has no spec, task, or test link")
        for row_id in pitch_warnings:
            warnings.append(f"{pitch_id} {row_id}: lower-tier row has no spec, task, or test link")
        failures.extend(slice_failures)
        warnings.extend(slice_warnings)
    return pitches, failures, warnings


def compute_gate_failures(results: List[FeatureSyncResult]) -> List[str]:
    failures: List[str] = []
    for result in results:
        if result.mapping_status != "mapped":
            continue
        if not result.gate_enforced:
            continue
        if result.sync_status != "current":
            failures.append(
                f"{result.feature_id}: sync status is {result.sync_status}"
            )
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a sync status report for spec-kit artifacts against the SRS manifest.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reverse-output", type=Path, default=DEFAULT_REVERSE_OUTPUT)
    parser.add_argument("--gate", action="store_true", help="Fail if any mapped feature is not fully synchronized with the SRS mapping and feature status.")
    args = parser.parse_args()

    manifest = load_yaml(args.manifest)
    results = [derive_feature_status(feature, manifest) for feature in manifest.get("features", [])]
    pitches, pitch_failures, pitch_warnings = collect_pitch_trace(ROOT, results)
    report = render_report(manifest, results, args.output, pitches)
    write_generated_report(args.output, report + "\n")
    documents = iter_srs_documents(manifest)
    multiple_documents = isinstance(manifest.get("srs_documents"), dict) and bool(manifest.get("srs_documents"))
    for srs_id, document in documents:
        # A manifest with only the legacy srs: block still writes one reverse report.
        if not multiple_documents:
            output_path = args.reverse_output
            reverse_report = render_reverse_trace(manifest, results, output_path)
        else:
            output_path = reverse_output_for(srs_id, document, args.reverse_output)
            reverse_report = render_reverse_trace(
                manifest,
                results,
                output_path,
                srs_document=document,
                srs_id=srs_id,
            )
        write_generated_report(output_path, reverse_report + "\n")

    replace_pitch_trace_block(args.manifest, render_pitch_trace(pitches))

    if args.gate:
        for warning in pitch_warnings:
            print(f"PITCH TRACE WARN: {warning}")
        failures = compute_gate_failures(results) + pitch_failures
        if failures:
            for failure in failures:
                print(f"SYNC GATE FAIL: {failure}")
            raise SystemExit(1)
        print("SYNC GATE PASS")


if __name__ == "__main__":
    main()
