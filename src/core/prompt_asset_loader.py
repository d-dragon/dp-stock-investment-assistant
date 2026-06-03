"""
PromptAssetLoader — resolve, cache, and fallback for prompt assets.

Implements the ``PromptAssetLoader`` component that sits between
configuration and the agent prompt source per TECHNICAL_DESIGN.md §3.5.2.2.
Accepts the full 8-field ``SelectionTuple`` and resolves against a manifest
derived from asset directory scanning. Falls back to baseline lineage on
failure.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from core.prompt_types import PromptAsset, PromptSelection, SelectionTuple


class PromptAssetLoader:
    """Resolve, cache, and fall back for prompt assets.

    The loader accepts a full 8-field ``SelectionTuple`` per
    TECHNICAL_DESIGN.md §3.5.2.2 and resolves it against a manifest
    derived from scanning the prompt asset directory.

    At M1 scope, ``route``, ``locale``, ``prompt_experiment_id``,
    ``workspace_mode``, and ``env`` accept documented defaults;
    ``agent_role``, ``requested_version``, and ``selection_mode`` are
    the active discriminators.
    """

    def __init__(
        self,
        prompt_root: Path,
        config: dict,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize the loader.

        Args:
            prompt_root: Root directory containing ``system/``, ``skills/``,
                ``experiments/`` subdirectories.
            config: Configuration dict (reads ``prompts.registry.*`` keys).
            logger: Optional logger instance.
        """
        self._prompt_root = prompt_root
        self._config = config
        self._logger = logger or logging.getLogger(__name__)

        # Cached manifest: {agent_role: [PromptAsset, ...]}
        self._cached_manifest: Optional[Dict[str, List[PromptAsset]]] = None
        self._manifest_timestamp: float = 0.0

        # Cache TTL from config (default 300s)
        prompts_config = config.get("prompts", {})
        registry_config = prompts_config.get("registry", {})
        self._refresh_window = registry_config.get("refresh_window_seconds", 300)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve(self, selection: SelectionTuple) -> PromptSelection:
        """Resolve a ``PromptSelection`` from the given selection tuple.

        Args:
            selection: The 8-field selection tuple.

        Returns:
            A ``PromptSelection`` with resolved asset metadata.
            ``fallback_used`` is ``True`` when the configured version
            could not be matched and the baseline lineage was used instead.

        Raises:
            RuntimeError: When no baseline lineage is available (all
                assets missing or unresolvable).
        """
        manifest = self._get_manifest()
        agent_role = selection.agent_role
        requested_version = selection.requested_version

        assets = manifest.get(agent_role, [])
        if not assets:
            # No assets registered for this role — try baseline fallback
            return self._resolve_fallback(
                agent_role=agent_role,
                failed_version=requested_version or "unknown",
                failed_reason=f"No assets found for agent_role='{agent_role}'",
            )

        if requested_version:
            # Try exact version match
            for asset in assets:
                if asset.version == requested_version:
                    return PromptSelection(
                        selected_assets=[str(asset.file_path.relative_to(self._prompt_root))],
                        prompt_version=asset.version,
                        prompt_variant=asset.variant,
                        selection_mode=selection.selection_mode,
                        fallback_used=False,
                        degraded_reason=None,
                        trace_metadata={
                            "prompt_version": asset.version,
                            "prompt_variant": asset.variant,
                            "prompt_selection_mode": selection.selection_mode,
                            "agent_role": asset.agent_role,
                        },
                    )

            # Version not found — fall back to baseline
            return self._resolve_fallback(
                agent_role=agent_role,
                failed_version=requested_version,
                failed_reason=(
                    f"Version '{requested_version}' not found for "
                    f"agent_role='{agent_role}', fell back to baseline lineage"
                ),
            )

        # No version requested — return the highest-version active asset
        baseline = self._find_baseline_lineage(agent_role, assets)
        if baseline is None:
            raise RuntimeError(
                f"Unresolvable prompt: no active baseline found for "
                f"agent_role='{agent_role}'"
            )
        return PromptSelection(
            selected_assets=[str(baseline.file_path.relative_to(self._prompt_root))],
            prompt_version=baseline.version,
            prompt_variant=baseline.variant,
            selection_mode=selection.selection_mode,
            fallback_used=False,
            degraded_reason=None,
            trace_metadata={
                "prompt_version": baseline.version,
                "prompt_variant": baseline.variant,
                "prompt_selection_mode": selection.selection_mode,
                "agent_role": baseline.agent_role,
            },
        )

    # ------------------------------------------------------------------
    # Manifest management
    # ------------------------------------------------------------------

    def _get_manifest(self) -> Dict[str, List[PromptAsset]]:
        """Get the prompt manifest, rebuilding from disk if cache is stale."""
        now = time.time()
        if self._cached_manifest is not None and (
            now - self._manifest_timestamp < self._refresh_window
        ):
            return self._cached_manifest

        self._cached_manifest = self._build_manifest()
        self._manifest_timestamp = now
        return self._cached_manifest

    def _build_manifest(self) -> Dict[str, List[PromptAsset]]:
        """Scan the prompt directory and build a manifest of all assets.

        Scans ``system/``, ``skills/``, and ``experiments/`` subdirectories
        for ``.md`` files with YAML frontmatter. Missing subdirectories
        (``skills/``, ``experiments/`` at M1 scope) are silently skipped.
        """
        manifest: Dict[str, List[PromptAsset]] = {}

        for subdir in ("system", "skills", "experiments"):
            dir_path = self._prompt_root / subdir
            if not dir_path.is_dir():
                # Silently skip missing subdirectories
                continue

            for md_file in sorted(dir_path.glob("*.md")):
                asset = self._parse_asset_file(md_file)
                if asset is not None:
                    manifest.setdefault(asset.agent_role, []).append(asset)

        return manifest

    def _parse_asset_file(self, path: Path) -> Optional[PromptAsset]:
        """Parse a single prompt markdown file into a ``PromptAsset``.

        Returns ``None`` if the file lacks valid frontmatter (logged at
        WARN level).
        """
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self._logger.warning("Cannot read prompt file %s: %s", path, exc)
            return None

        if not text.startswith("---"):
            self._logger.warning(
                "Prompt file %s has no frontmatter delimiters — skipping.",
                path,
            )
            return None

        parts = text.split("---", 2)
        if len(parts) < 3:
            self._logger.warning(
                "Prompt file %s has malformed frontmatter (no closing ---) — skipping.",
                path,
            )
            return None

        raw_frontmatter = parts[1].strip()
        content = parts[2].strip()

        try:
            frontmatter = yaml.safe_load(raw_frontmatter)
        except yaml.YAMLError as exc:
            self._logger.warning(
                "Prompt file %s has invalid YAML frontmatter: %s — skipping.",
                path, exc,
            )
            return None

        if not isinstance(frontmatter, dict):
            self._logger.warning(
                "Prompt file %s frontmatter is not a mapping — skipping.",
                path,
            )
            return None

        return PromptAsset(
            name=frontmatter.get("name", path.stem),
            version=str(frontmatter.get("version", "0.0.0")),
            agent_role=str(frontmatter.get("agent_role", "unknown")),
            status=str(frontmatter.get("status", "unknown")),
            locale=str(frontmatter.get("locale", "en")),
            parity_group=str(frontmatter.get("parity_group", "")),
            variant=str(frontmatter.get("variant", "unknown")),
            content=content,
            file_path=path,
            frontmatter=frontmatter,
        )

    # ------------------------------------------------------------------
    # Fallback resolution
    # ------------------------------------------------------------------

    def _resolve_fallback(
        self,
        agent_role: str,
        failed_version: str,
        failed_reason: str,
    ) -> PromptSelection:
        """Resolve to the baseline lineage when the preferred asset fails.

        Logs a WARN-level event with the failed identity and returns a
        ``PromptSelection`` with ``fallback_used=True``.
        """
        manifest = self._get_manifest()
        assets = manifest.get(agent_role, [])
        baseline = self._find_baseline_lineage(agent_role, assets)

        if baseline is None:
            raise RuntimeError(
                f"Unresolvable prompt for agent_role='{agent_role}': "
                f"{failed_reason}. No baseline lineage available."
            )

        self._logger.warning(
            "Prompt fallback for role=%s: %s. "
            "Using baseline %s v%s (%s).",
            agent_role, failed_reason,
            baseline.name, baseline.version, baseline.variant,
        )

        return PromptSelection(
            selected_assets=[str(baseline.file_path.relative_to(self._prompt_root))],
            prompt_version=baseline.version,
            prompt_variant=baseline.variant,
            selection_mode="fixed",
            fallback_used=True,
            degraded_reason=failed_reason,
            trace_metadata={
                "prompt_version": baseline.version,
                "prompt_variant": baseline.variant,
                "prompt_selection_mode": "fixed",
                "agent_role": baseline.agent_role,
                "fallback_used": True,
                "degraded_reason": failed_reason,
            },
        )

    @staticmethod
    def _find_baseline_lineage(
        agent_role: str,
        assets: List[PromptAsset],
    ) -> Optional[PromptAsset]:
        """Find the baseline lineage asset for the given agent role.

        Selects the asset with ``status: active`` and the highest version
        within that agent_role group. Returns ``None`` when no active
        asset exists (triggers unresolvable-prompt error).
        """
        active = [a for a in assets if a.status == "active"]
        if not active:
            return None
        # Sort by version descending — assumes semver-comparable strings
        active.sort(key=lambda a: a.version, reverse=True)
        return active[0]


VALID_SELECTION_MODES = frozenset({"fixed", "forced", "shadow", "weighted"})


class InvalidPromptsConfigError(ValueError):
    """Raised when the ``prompts.*`` configuration is structurally invalid."""
    pass


def validate_prompts_config(config: dict) -> None:
    """Validate the ``prompts.*`` configuration namespace structurally.

    Checks that required keys exist, ``selection_mode`` is one of the
    supported values, and paths are non-empty. Raises
    ``InvalidPromptsConfigError`` with an actionable message on failure.

    This is the **structural** validation layer (M1-FR-009a). Content-
    resolution errors (non-existent version) are handled by
    ``PromptAssetLoader.resolve()`` as a runtime fallback.

    Args:
        config: The full application configuration dict.

    Raises:
        InvalidPromptsConfigError: When the config structure is invalid.
    """
    prompts = config.get("prompts")
    if prompts is None:
        raise InvalidPromptsConfigError(
            "Missing 'prompts' configuration section in config.yaml. "
            "Add a 'prompts:' top-level key with 'registry', 'system', "
            "and 'selection_mode' sub-keys."
        )

    if not isinstance(prompts, dict):
        raise InvalidPromptsConfigError(
            f"'prompts' configuration must be a mapping, got {type(prompts).__name__}."
        )

    # --- registry ---
    registry = prompts.get("registry")
    if registry is None:
        raise InvalidPromptsConfigError(
            "Missing 'prompts.registry' configuration. "
            "Add a 'registry:' section with 'directory' key."
        )
    if not isinstance(registry, dict):
        raise InvalidPromptsConfigError(
            f"'prompts.registry' must be a mapping, got {type(registry).__name__}."
        )
    directory = registry.get("directory")
    if not directory or not isinstance(directory, str):
        raise InvalidPromptsConfigError(
            f"'prompts.registry.directory' must be a non-empty string, "
            f"got {directory!r}."
        )

    # --- system ---
    system = prompts.get("system")
    if system is None:
        raise InvalidPromptsConfigError(
            "Missing 'prompts.system' configuration. "
            "Add a 'system:' section with 'active_role' and 'active_version' keys."
        )
    if not isinstance(system, dict):
        raise InvalidPromptsConfigError(
            f"'prompts.system' must be a mapping, got {type(system).__name__}."
        )
    active_role = system.get("active_role")
    if not active_role or not isinstance(active_role, str):
        raise InvalidPromptsConfigError(
            f"'prompts.system.active_role' must be a non-empty string, "
            f"got {active_role!r}."
        )
    active_version = system.get("active_version")
    if not active_version or not isinstance(active_version, str):
        raise InvalidPromptsConfigError(
            f"'prompts.system.active_version' must be a non-empty string, "
            f"got {active_version!r}."
        )

    # --- selection_mode ---
    selection_mode = prompts.get("selection_mode")
    if not selection_mode or not isinstance(selection_mode, str):
        raise InvalidPromptsConfigError(
            f"'prompts.selection_mode' must be a non-empty string, "
            f"got {selection_mode!r}."
        )
    if selection_mode not in VALID_SELECTION_MODES:
        raise InvalidPromptsConfigError(
            f"Unsupported 'prompts.selection_mode': '{selection_mode}'. "
            f"Valid modes: {', '.join(sorted(VALID_SELECTION_MODES))}."
        )

    # --- experiments (optional, validate if present) ---
    experiments = prompts.get("experiments", {})
    if experiments and not isinstance(experiments, dict):
        raise InvalidPromptsConfigError(
            f"'prompts.experiments' must be a mapping, got {type(experiments).__name__}."
        )
