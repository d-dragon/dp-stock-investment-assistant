from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "specs" / "spec-traceability.yaml"
DEFAULT_OUTPUT = ROOT / "specs" / "spec-sync-status.md"
DEFAULT_REVERSE_OUTPUT = ROOT / "docs" / "langchain-agent" / "SRS_SPEC_TRACEABILITY.md"


TASK_PATTERN = re.compile(r"^- \[(?P<mark>[ xX])\] (?P<task>T\d+)\b")
STATUS_PATTERN = re.compile(r"^\*\*Status\*\*:\s*(?P<value>.+?)\s*$", re.MULTILINE)
TABLE_ROW_ID_PATTERN = re.compile(r"^\|\s*((?:FR|NFR|AC|IR|CON|ERR|PRIV)-\d+(?:\.\d+)*[a-z]?)\s*\|")


@dataclass(frozen=True)
class SrsTraceItem:
    item_id: str
    line_number: int


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
    else:
        derived_status = "draft"
        sync_status = "stale"

    if mapping_status == "mapped" and not gate_enforced and sync_status == "current":
        sync_status = "informational"
        observations.append("Mapping is excluded from the sync gate and retained for historical overlap traceability.")

    baseline_version = feature.get("srs_mapping", {}).get("baseline_version")
    manifest_srs_version = manifest.get("srs", {}).get("version")
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
    )


def build_reverse_index(results: List[FeatureSyncResult]) -> Dict[str, List[FeatureSyncResult]]:
    reverse: Dict[str, List[FeatureSyncResult]] = {}
    for result in results:
        if result.mapping_status != "mapped":
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


def render_report(manifest: Dict[str, Any], results: List[FeatureSyncResult], output_path: Path) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    srs_target = ROOT / manifest["srs"]["path"]
    report_metadata = manifest.get("reports", {}).get("spec_sync_status", {})
    lines: List[str] = []
    lines.append("# Spec Sync Status")
    lines.append("")
    lines.append(f"> **Document Version**: {report_metadata.get('version', '1.0')}  ")
    lines.append(f"> **Generated**: {generated_at}  ")
    lines.append(f"> **Status**: {report_metadata.get('status', 'Active')}  ")
    lines.append(f"> **Traceability Manifest Version**: {manifest.get('version', 'n/a')}  ")
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
    lines.append("- `derived status` is computed from spec-kit artifacts, not from manual document headers.")
    lines.append("- `sync status` reports whether the feature-to-SRS mapping is current against the manifest SRS baseline.")
    lines.append("- `coverage status` shows whether the feature covers all, some, or none of the linked SRS scope.")
    lines.append("")
    lines.append("## Operational Rule")
    lines.append("")
    lines.append("- Update `spec-traceability.yaml` when a feature gains or changes SRS scope.")
    lines.append("- Update `tasks.md` and workflow markers during delivery.")
    lines.append("- Regenerate this report with `python scripts/sync_spec_status.py` whenever either side changes.")
    lines.append("")
    return "\n".join(lines)


def render_reverse_trace(manifest: Dict[str, Any], results: List[FeatureSyncResult], output_path: Path) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    srs_path = ROOT / manifest["srs"]["path"]
    srs_items = extract_srs_items(srs_path)
    reverse = build_reverse_index(results)
    report_metadata = manifest.get("reports", {}).get("srs_spec_traceability", {})

    lines: List[str] = []
    lines.append("# SRS To Spec Traceability")
    lines.append("")
    lines.append(f"> **Document Version**: {report_metadata.get('version', '1.0')}  ")
    lines.append(f"> **Generated**: {generated_at}  ")
    lines.append(f"> **Status**: {report_metadata.get('status', 'Active')}  ")
    lines.append(f"> **Traceability Manifest Version**: {manifest.get('version', 'n/a')}  ")
    lines.append("")
    lines.append("## Baseline")
    lines.append("")
    lines.append(f"- SRS: {make_markdown_link(output_path, srs_path, manifest['srs']['path'])}")
    lines.append(f"- SRS version: `{manifest['srs']['version']}`")
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
    ordered_types = ["FR", "NFR", "AC", "IR", "CON", "ERR", "PRIV"]
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
    report = render_report(manifest, results, args.output)
    reverse_report = render_reverse_trace(manifest, results, args.reverse_output)
    args.output.write_text(report + "\n", encoding="utf-8")
    args.reverse_output.write_text(reverse_report + "\n", encoding="utf-8")

    if args.gate:
        failures = compute_gate_failures(results)
        if failures:
            for failure in failures:
                print(f"SYNC GATE FAIL: {failure}")
            raise SystemExit(1)
        print("SYNC GATE PASS")


if __name__ == "__main__":
    main()