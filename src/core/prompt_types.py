"""
Prompt system type definitions for the Stock Investment Assistant.

Defines the core data contracts for the prompt compiler path:
- PromptAsset: A versioned, frontmatter-annotated markdown prompt file
- PromptSelection: The output contract from PromptAssetLoader
- SelectionTuple: The 8-field selection tuple per TECHNICAL_DESIGN.md §3.5.2.2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class PromptAsset:
    """A versioned, frontmatter-annotated markdown prompt file.

    Represents a single prompt file under ``src/prompts/`` with its parsed
    frontmatter metadata and content body.

    Attributes:
        name: Human-readable prompt identifier from frontmatter.
        version: Semantic version string (e.g. ``"1.0.0"``).
        agent_role: Role this prompt targets (e.g. ``"react_analyst"``).
        status: Lifecycle status (e.g. ``"active"``, ``"draft"``, ``"deprecated"``).
        locale: Locale code (e.g. ``"en"``, ``"vi"``).
        parity_group: Locale parity group for cross-locale validation.
        variant: Variant label for A/B testing cohorts (e.g. ``"baseline"``).
        content: The prompt body text (everything after frontmatter).
        file_path: Absolute path to the prompt markdown file on disk.
        frontmatter: Raw parsed frontmatter dictionary.
    """
    name: str
    version: str
    agent_role: str
    status: str
    locale: str
    parity_group: str
    variant: str
    content: str
    file_path: Path
    frontmatter: Dict[str, Any]


@dataclass(frozen=True)
class PromptSelection:
    """Output contract from ``PromptAssetLoader.resolve()``.

    Identifies which assets were selected, which baseline lineage was used,
    whether fallback occurred, and trace metadata for observability.

    Attributes:
        selected_assets: List of relative asset paths selected (e.g. ``["system/react_analyst.md"]``).
        prompt_version: Semantic version string of the resolved prompt.
        prompt_variant: Variant label (e.g. ``"baseline"``).
        selection_mode: How the prompt was selected (``fixed``, ``forced``, ``shadow``, ``weighted``).
        fallback_used: Whether a fallback baseline was used instead of the configured version.
        degraded_reason: Human-readable explanation when ``fallback_used`` is ``True``.
        trace_metadata: Dictionary of metadata for observability (LangSmith traces, response metadata).
    """
    selected_assets: List[str]
    prompt_version: str
    prompt_variant: str
    selection_mode: str
    fallback_used: bool
    degraded_reason: Optional[str]
    trace_metadata: Dict[str, Any]


@dataclass(frozen=True)
class SelectionTuple:
    """8-field selection tuple per TECHNICAL_DESIGN.md §3.5.2.2.

    Defines the parameters that ``PromptAssetLoader.resolve()`` uses to
    select the appropriate prompt asset for a request.

    At M1 scope, ``route``, ``locale``, ``prompt_experiment_id``,
    ``workspace_mode``, and ``env`` accept documented defaults and are
    wired for M2+-ready expansion.
    """
    agent_role: str
    route: str = "general_chat"
    locale: str = "en"
    selection_mode: str = "fixed"
    requested_version: Optional[str] = None
    prompt_experiment_id: Optional[str] = None
    workspace_mode: str = "default"
    env: str = "production"
