"""
PromptAssembler — compose a deterministic prompt from governed assets.

Implements the ``PromptAssembler`` component per TECHNICAL_DESIGN.md §3.5.2.3.
Accepts a ``PromptSelection``, normalized route result, and optional runtime
context, then composes one ``CompiledPrompt`` with deterministic segment
ordering and authority-based classification.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.prompt_types import (
    CompiledPrompt,
    PromptSelection,
    SEGMENT_AUTHORITY,
    SegmentEntry,
    SegmentType,
)
from core.routes import StockQueryRoute


class PromptAssembler:
    """Compose a deterministic prompt from governed assets.

    Assembly order per TECHNICAL_DESIGN.md §3.5.2.3:
    1. Shared policy (authority 1)
    2. Role prompt (authority 2)
    3. Route-specific skill (authority 3)
    4. Bounded memory context (authority 4)
    5. Evidence and tool-derived facts (authority 5)
    6. Task framing (authority 6)
    7. Output contract (authority 7)

    Missing route skills degrade gracefully: the assembler continues with
    available segments, records the gap in trace metadata, and never
    synthesizes substitute instructions.
    """

    ASSEMBLY_ORDER: List[SegmentType] = [
        SegmentType.SHARED_POLICY,
        SegmentType.ROLE_PROMPT,
        SegmentType.ROUTE_SKILL,
        SegmentType.MEMORY_CONTEXT,
        SegmentType.EVIDENCE,
        SegmentType.TASK_FRAMING,
        SegmentType.OUTPUT_CONTRACT,
    ]

    def __init__(
        self,
        prompt_root: Path,
        config: dict,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize the assembler.

        Args:
            prompt_root: Root directory of prompt assets (``src/prompts/``).
            config: Application config dict (reads ``prompts.*`` keys).
            logger: Optional logger instance.
        """
        self._prompt_root = prompt_root
        self._config = config
        self._logger = logger or logging.getLogger(__name__)

        # Approved dynamic controls from config
        prompts_cfg = config.get("prompts", {})
        dc_cfg = prompts_cfg.get("dynamic_controls", {})
        self._allowed_fields: set[str] = set(dc_cfg.get("allowed_fields", []))
        self._reject_unknown: bool = dc_cfg.get("reject_unknown_fields", True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compile(
        self,
        selection: PromptSelection,
        route: StockQueryRoute,
        runtime_context: Optional[Dict[str, Any]] = None,
    ) -> CompiledPrompt:
        """Compose a ``CompiledPrompt`` from the given inputs.

        Args:
            selection: Resolved prompt assets from ``PromptAssetLoader``.
            route: Normalized route classification from the semantic router.
            runtime_context: Optional dict with approved dynamic controls,
                memory summary, evidence bundles, and output contract.

        Returns:
            A ``CompiledPrompt`` with assembled text, segment manifest,
            and trace metadata.

        Raises:
            ValueError: If ``selection`` has no assets.
        """
        if not selection.selected_assets:
            raise ValueError(
                "Cannot compile: PromptSelection has no selected assets"
            )

        runtime_context = runtime_context or {}
        dropped_fields: List[str] = []
        segment_manifest: List[SegmentEntry] = []
        assembled_parts: List[str] = []

        # --- 1. Shared policy ---
        # At M2 scope, shared policy is embedded in the role prompt.
        # Future M3+ may extract it to dedicated assets.
        role_text = self._read_asset_text(selection)
        if role_text:
            assembled_parts.append(role_text)
            segment_manifest.append(SegmentEntry(
                type=SegmentType.SHARED_POLICY,
                source_path="inline (role_prompt embedded policy)",
                authority_level=SEGMENT_AUTHORITY[SegmentType.SHARED_POLICY],
            ))
            # The role prompt content IS the shared policy at M2 scope
            segment_manifest.append(SegmentEntry(
                type=SegmentType.ROLE_PROMPT,
                source_path=selection.selected_assets[0]
                if selection.selected_assets else "inline",
                authority_level=SEGMENT_AUTHORITY[SegmentType.ROLE_PROMPT],
            ))

        # --- 2. Route-specific skill ---
        route_skill_used = False
        missing_skills: List[str] = []
        route_text = self._resolve_route_skill(route)
        if route_text:
            assembled_parts.append(route_text)
            route_skill_used = True
            segment_manifest.append(SegmentEntry(
                type=SegmentType.ROUTE_SKILL,
                source_path=f"skills/routes/{route.value}.md",
                authority_level=SEGMENT_AUTHORITY[SegmentType.ROUTE_SKILL],
            ))
        else:
            missing_skills.append(route.value)

        # --- 3. Memory context (from runtime_context) ---
        memory_text = runtime_context.get("memory_summary") or ""
        if memory_text:
            assembled_parts.append(memory_text)
            segment_manifest.append(SegmentEntry(
                type=SegmentType.MEMORY_CONTEXT,
                source_path="runtime (memory_summary)",
                authority_level=SEGMENT_AUTHORITY[SegmentType.MEMORY_CONTEXT],
            ))

        # --- 4. Evidence (from runtime_context) ---
        evidence_text = runtime_context.get("evidence") or ""
        if evidence_text:
            assembled_parts.append(evidence_text)
            segment_manifest.append(SegmentEntry(
                type=SegmentType.EVIDENCE,
                source_path="runtime (evidence)",
                authority_level=SEGMENT_AUTHORITY[SegmentType.EVIDENCE],
            ))

        # --- 5. Task framing (from runtime_context) ---
        task_text = runtime_context.get("task_framing") or ""
        if task_text:
            assembled_parts.append(task_text)
            segment_manifest.append(SegmentEntry(
                type=SegmentType.TASK_FRAMING,
                source_path="runtime (task_framing)",
                authority_level=SEGMENT_AUTHORITY[SegmentType.TASK_FRAMING],
            ))

        # --- 6. Output contract (from runtime_context) ---
        contract_text = runtime_context.get("output_contract") or ""
        if contract_text:
            assembled_parts.append(contract_text)
            segment_manifest.append(SegmentEntry(
                type=SegmentType.OUTPUT_CONTRACT,
                source_path="runtime (output_contract)",
                authority_level=SEGMENT_AUTHORITY[SegmentType.OUTPUT_CONTRACT],
            ))

        # --- 7. Validate dynamic controls ---
        for key in runtime_context:
            if key in ("memory_summary", "evidence", "task_framing",
                        "output_contract"):
                continue  # approved built-in keys
            if self._reject_unknown and key not in self._allowed_fields:
                dropped_fields.append(key)

        # --- Build trace metadata ---
        trace_metadata = {
            "route": route.value,
            "route_skill_used": route_skill_used,
            "selected_skills": [
                s.source_path for s in segment_manifest
                if s.type != SegmentType.SHARED_POLICY
            ],
            "prompt_selection_mode": selection.selection_mode,
            "prompt_version": selection.prompt_version,
            "prompt_variant": selection.prompt_variant,
            "fallback_used": selection.fallback_used,
        }
        if missing_skills:
            trace_metadata["missing_route_skills"] = missing_skills
        if dropped_fields:
            trace_metadata["dropped_dynamic_fields"] = dropped_fields

        # --- Build compiled text ---
        compiled_text = "\n---\n".join(assembled_parts)

        return CompiledPrompt(
            compiled_text=compiled_text,
            segment_manifest=segment_manifest,
            prompt_version=selection.prompt_version,
            prompt_variant=selection.prompt_variant,
            trace_metadata=trace_metadata,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_asset_text(self, selection: PromptSelection) -> str:
        """Read the content of the first selected prompt asset from disk."""
        if not selection.selected_assets:
            return ""
        rel_path = selection.selected_assets[0]
        full_path = self._prompt_root / rel_path
        try:
            text = full_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self._logger.warning(
                "Cannot read prompt asset %s: %s", full_path, exc,
            )
            return ""
        # Strip frontmatter delimiters
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return text.strip()

    def _resolve_route_skill(self, route: StockQueryRoute) -> str:
        """Resolve the route-skill asset content for the given route.

        Returns the content text if found, or empty string if the asset
        does not exist (graceful degradation).
        """
        route_path = (
            self._prompt_root / "skills" / "routes" / f"{route.value}.md"
        )
        if not route_path.is_file():
            self._logger.debug(
                "Route-skill asset not found for route '%s' at %s — "
                "degrading gracefully.",
                route.value, route_path,
            )
            return ""
        try:
            text = route_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self._logger.warning(
                "Cannot read route-skill asset %s: %s — degrading.",
                route_path, exc,
            )
            return ""
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return text.strip()
