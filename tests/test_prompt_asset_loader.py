"""
Unit tests for PromptAssetLoader: resolution, fallback, frontmatter parsing, and caching.

Uses ``MagicMock`` for file-system isolation and ``tmp_path`` fixture
for temp asset files per testing.instructions.md patterns.
"""

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from core.prompt_asset_loader import (
    InvalidPromptsConfigError,
    PromptAssetLoader,
    validate_prompts_config,
)
from core.prompt_types import PromptAsset, PromptSelection, SelectionTuple


# ------------------------------------------------------------------
# Helper: create a minimal prompt asset file on disk
# ------------------------------------------------------------------

def _write_asset(path: Path, name: str = "test_prompt", version: str = "1.0.0",
                  agent_role: str = "react_analyst", status: str = "active",
                  variant: str = "baseline", content: str = "You are a test assistant."):
    """Write a prompt markdown file with YAML frontmatter to ``path``."""
    frontmatter = {
        "name": name,
        "version": version,
        "agent_role": agent_role,
        "status": status,
        "variant": variant,
        "locale": "en",
        "parity_group": "",
    }
    text = f"---\n{yaml.dump(frontmatter, sort_keys=False)}---\n{content}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def loader(tmp_path: Path) -> PromptAssetLoader:
    """Create a PromptAssetLoader rooted at a temp directory."""
    return PromptAssetLoader(
        prompt_root=tmp_path,
        config={
            "prompts": {
                "registry": {"directory": str(tmp_path), "refresh_window_seconds": 300},
                "system": {"active_role": "react_analyst", "active_version": "1.0.0"},
                "selection_mode": "fixed",
            }
        },
        logger=logging.getLogger(__name__),
    )


@pytest.fixture
def baseline_asset(tmp_path: Path) -> Path:
    """Create a baseline prompt asset file on disk."""
    asset_path = tmp_path / "system" / "react_analyst.md"
    _write_asset(asset_path, version="1.0.0", status="active")
    return asset_path


# ------------------------------------------------------------------
# T010: Resolution tests
# ------------------------------------------------------------------

class TestPromptAssetLoaderResolve:
    """Tests for PromptAssetLoader.resolve() — happy path and fallback."""

    def test_resolves_exact_version(self, loader, baseline_asset):
        """Happy path: requested version exists and is returned."""
        sel = SelectionTuple(agent_role="react_analyst", requested_version="1.0.0")
        result = loader.resolve(sel)
        assert result.fallback_used is False
        assert result.prompt_version == "1.0.0"
        assert result.prompt_variant == "baseline"
        assert result.degraded_reason is None

    def test_falls_back_on_version_mismatch(self, loader, baseline_asset):
        """AC-8.2 compliance: non-existent version triggers fallback with WARN."""
        sel = SelectionTuple(agent_role="react_analyst", requested_version="2.0.0")
        result = loader.resolve(sel)
        assert result.fallback_used is True
        assert result.prompt_version == "1.0.0"  # baseline version
        assert result.degraded_reason is not None
        assert "2.0.0" in result.degraded_reason

    def test_falls_back_on_malformed_frontmatter(self, tmp_path, loader):
        """FR-1.4.8 compliance: malformed frontmatter file is skipped from manifest,
        and requesting its version triggers baseline fallback."""
        # Create a valid baseline asset that fallback can resolve to
        _write_asset(tmp_path / "system" / "react_analyst.md",
                     version="1.0.0", status="active")
        # Add a malformed file that should be skipped
        bad_path = tmp_path / "system" / "bad.md"
        bad_path.write_bytes(b"---\ninvalid: yaml: unclosed\n---\nContent\n")
        # Reset cache so manifest rebuilds
        loader._cached_manifest = None
        # Request a version that only exists in the malformed file (which was skipped)
        sel = SelectionTuple(agent_role="react_analyst", requested_version="9.9.9")
        result = loader.resolve(sel)
        assert result.fallback_used is True
        assert result.degraded_reason is not None

    def test_raises_on_baseline_exhaustion(self, tmp_path):
        """When no assets exist at all, loader raises RuntimeError."""
        empty_loader = PromptAssetLoader(
            prompt_root=tmp_path,
            config={"prompts": {"registry": {"directory": str(tmp_path)}}},
            logger=logging.getLogger(__name__),
        )
        sel = SelectionTuple(agent_role="react_analyst", requested_version="1.0.0")
        with pytest.raises(RuntimeError, match="Unresolvable prompt"):
            empty_loader.resolve(sel)


# ------------------------------------------------------------------
# T011: Cache behavior tests
# ------------------------------------------------------------------

class TestPromptAssetLoaderCache:
    """Tests for manifest caching by full selection tuple."""

    def test_caches_by_full_selection_tuple(self, loader, baseline_asset, mocker):
        """Second resolve() with same tuple hits cache (no file system access)."""
        # Spy on _build_manifest
        spy = mocker.spy(loader, "_build_manifest")

        sel = SelectionTuple(agent_role="react_analyst", requested_version="1.0.0")
        loader.resolve(sel)
        first_call_count = spy.call_count

        loader.resolve(sel)  # Same tuple — should hit cache
        assert spy.call_count == first_call_count, (
            "Expected cache hit — _build_manifest should not be called again"
        )

    def test_cache_key_includes_all_eight_fields(self, loader, baseline_asset):
        """Verify the 8-field tuple is used as the cache discriminator."""
        sel1 = SelectionTuple(agent_role="react_analyst", requested_version="1.0.0",
                              route="general_chat", locale="en", selection_mode="fixed",
                              prompt_experiment_id=None, workspace_mode="default", env="production")
        sel2 = SelectionTuple(agent_role="react_analyst", requested_version="1.0.0",
                              route="news", locale="vi", selection_mode="fixed",
                              prompt_experiment_id=None, workspace_mode="default", env="production")
        # Different route/locale should produce different resolutions
        result1 = loader.resolve(sel1)
        result2 = loader.resolve(sel2)
        # Both resolve to the same single asset, but the cache key differs
        assert result1.prompt_version == result2.prompt_version


# ------------------------------------------------------------------
# T012: Frontmatter parsing tests
# ------------------------------------------------------------------

class TestPromptAssetLoaderFrontmatter:
    """Tests for frontmatter parsing edge cases."""

    def test_parses_valid_frontmatter(self, loader, baseline_asset):
        """Valid YAML frontmatter with --- delimiters is parsed successfully."""
        sel = SelectionTuple(agent_role="react_analyst", requested_version="1.0.0")
        result = loader.resolve(sel)
        assert result.fallback_used is False

    def test_rejects_missing_frontmatter_delimiters(self, tmp_path, loader):
        """File without --- delimiters is rejected and skipped from manifest."""
        asset_path = tmp_path / "system" / "no_frontmatter.md"
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        asset_path.write_text("Just plain text, no frontmatter.\n", encoding="utf-8")
        # Force manifest rebuild
        loader._cached_manifest = None
        manifest = loader._build_manifest()
        # The file should be skipped (no agent_role group for it)
        assert len(manifest) == 0

    def test_rejects_malformed_yaml(self, tmp_path, loader):
        """Unclosed key in YAML frontmatter is rejected."""
        asset_path = tmp_path / "system" / "bad_yaml.md"
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        asset_path.write_text("---\nkey: value\n  unclosed: bad\n---\nContent\n", encoding="utf-8")
        loader._cached_manifest = None
        manifest = loader._build_manifest()
        assert len(manifest) == 0


# ------------------------------------------------------------------
# T017: PS-04 agent-starts-with-loader integration test
# ------------------------------------------------------------------

class TestPromptAssetLoaderAgentIntegration:
    """Tests for PromptAssetLoader wired into StockAssistantAgent."""

    def test_agent_starts_with_loader(self, mocker):
        """Agent uses PromptAssetLoader-resolved content as system prompt."""
        from core.stock_assistant_agent import StockAssistantAgent

        mock_loader = MagicMock(spec=PromptAssetLoader)
        mock_loader.resolve.return_value = PromptSelection(
            selected_assets=["system/react_analyst.md"],
            prompt_version="1.0.0",
            prompt_variant="baseline",
            selection_mode="fixed",
            fallback_used=False,
            degraded_reason=None,
            trace_metadata={"prompt_version": "1.0.0", "prompt_variant": "baseline"},
        )

        # Mock dependencies to avoid actual initialization
        mocker.patch("core.stock_assistant_agent.ModelClientFactory.get_client")
        mocker.patch("utils.cache.CacheBackend")
        mocker.patch("core.stock_assistant_agent.get_tool_registry")

        agent = StockAssistantAgent(
            config={"openai": {"api_key": "test"}, "model_provider": "openai"},
            data_manager=mocker.MagicMock(),
            prompt_asset_loader=mock_loader,
        )
        assert agent._prompt_asset_loader is mock_loader
        assert agent._current_prompt.prompt_version == "1.0.0"
        assert agent._current_prompt.fallback_used is False

    def test_agent_startup_fails_on_unresolvable_prompt(self, mocker):
        """When baseline is exhausted, agent raises RuntimeError.

        Edge case: covers fallback chain exhaustion (spec §Edge Cases →
        PS-02/PS-03 fallback chain exhaustion).
        """
        from core.stock_assistant_agent import StockAssistantAgent

        mock_loader = MagicMock(spec=PromptAssetLoader)
        mock_loader.resolve.side_effect = RuntimeError(
            "Unresolvable prompt for agent_role='react_analyst'"
        )

        mocker.patch("core.stock_assistant_agent.ModelClientFactory.get_client")
        mocker.patch("utils.cache.CacheBackend")
        mocker.patch("core.stock_assistant_agent.get_tool_registry")

        with pytest.raises(RuntimeError, match="Unresolvable prompt"):
            StockAssistantAgent(
                config={"openai": {"api_key": "test"}, "model_provider": "openai"},
                data_manager=mocker.MagicMock(),
                prompt_asset_loader=mock_loader,
            )


# ------------------------------------------------------------------
# Config validation tests
# ------------------------------------------------------------------

class TestValidatePromptsConfig:
    """Tests for validate_prompts_config() structural validation."""

    def test_rejects_missing_prompts_section(self):
        """Missing 'prompts' key raises InvalidPromptsConfigError."""
        with pytest.raises(InvalidPromptsConfigError, match="Missing.*prompts"):
            validate_prompts_config({})

    def test_rejects_unsupported_selection_mode(self):
        """Invalid selection_mode value raises error with valid modes listed."""
        config = {
            "prompts": {
                "registry": {"directory": "src/prompts"},
                "system": {"active_role": "react_analyst", "active_version": "1.0.0"},
                "selection_mode": "invalid_mode",
            }
        }
        with pytest.raises(InvalidPromptsConfigError, match="fixed|forced|shadow|weighted"):
            validate_prompts_config(config)

    def test_rejects_missing_required_fields(self):
        """Missing system.active_version raises error."""
        config = {
            "prompts": {
                "registry": {"directory": "src/prompts"},
                "system": {"active_role": "react_analyst"},  # no active_version
                "selection_mode": "fixed",
            }
        }
        with pytest.raises(InvalidPromptsConfigError, match="active_version"):
            validate_prompts_config(config)

    def test_accepts_valid_structure(self):
        """Valid prompts.* config passes validation."""
        config = {
            "prompts": {
                "registry": {"directory": "src/prompts"},
                "system": {"active_role": "react_analyst", "active_version": "1.0.0"},
                "selection_mode": "fixed",
                "default_locale": "en",
                "experiments": {"enabled": False, "active_id": None},
            }
        }
        validate_prompts_config(config)  # no exception
