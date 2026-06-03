"""
Integration tests for prompts.* config surface validation (US3).

Tests:
- Structural validation: invalid keys block startup
- Content resolution: non-existent version falls back with WARN
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import yaml

from core.prompt_asset_loader import (
    InvalidPromptsConfigError,
    PromptAssetLoader,
    validate_prompts_config,
)


# ------------------------------------------------------------------
# T022: Structural validation tests
# ------------------------------------------------------------------

class TestConfigStructuralValidation:
    """Structural config errors block startup with clear error messages."""

    def test_rejects_unsupported_selection_mode(self):
        """Invalid mode blocks startup — error must list valid modes."""
        config = {
            "prompts": {
                "registry": {"directory": "src/prompts"},
                "system": {"active_role": "react_analyst", "active_version": "1.0.0"},
                "selection_mode": "invalid_mode",
            }
        }
        with pytest.raises(InvalidPromptsConfigError) as exc_info:
            validate_prompts_config(config)
        msg = str(exc_info.value)
        assert "fixed" in msg
        assert "forced" in msg
        assert "shadow" in msg
        assert "weighted" in msg

    def test_rejects_missing_required_fields(self):
        """Missing system.active_version blocks startup."""
        config = {
            "prompts": {
                "registry": {"directory": "src/prompts"},
                "system": {"active_role": "react_analyst"},
                "selection_mode": "fixed",
            }
        }
        with pytest.raises(InvalidPromptsConfigError, match="active_version"):
            validate_prompts_config(config)

    def test_accepts_valid_structure(self):
        """Valid config passes structural validation."""
        config = {
            "prompts": {
                "registry": {"directory": "src/prompts", "refresh_window_seconds": 300},
                "system": {
                    "active_role": "react_analyst",
                    "active_version": "1.0.0",
                    "variants": [
                        {"name": "baseline", "version": "1.0.0",
                         "file": "system/react_analyst.md", "status": "active"}
                    ],
                },
                "selection_mode": "fixed",
                "default_locale": "en",
                "experiments": {"enabled": False, "active_id": None},
            }
        }
        validate_prompts_config(config)  # no exception

    def test_rejects_non_dict_prompts(self):
        """Non-dict prompts value raises error."""
        config = {"prompts": "not_a_dict"}
        with pytest.raises(InvalidPromptsConfigError, match="mapping"):
            validate_prompts_config(config)

    def test_rejects_empty_registry_directory(self):
        """Empty registry.directory raises error."""
        config = {
            "prompts": {
                "registry": {"directory": ""},
                "system": {"active_role": "react_analyst", "active_version": "1.0.0"},
                "selection_mode": "fixed",
            }
        }
        with pytest.raises(InvalidPromptsConfigError, match="directory"):
            validate_prompts_config(config)


# ------------------------------------------------------------------
# T023: Content resolution tests
# ------------------------------------------------------------------

class TestConfigContentResolution:
    """Content-resolution errors allow startup with baseline fallback (not startup failure)."""

    @pytest.fixture
    def valid_config(self) -> dict:
        """A structurally valid prompts config with a non-existent version."""
        return {
            "prompts": {
                "registry": {"directory": "src/prompts", "refresh_window_seconds": 300},
                "system": {"active_role": "react_analyst", "active_version": "9.9.9"},
                "selection_mode": "fixed",
            }
        }

    def test_content_resolution_falls_back_on_unknown_version(self, tmp_path, valid_config):
        """Non-existent version — loader falls back with WARN, does not block startup."""
        # Create a baseline asset so fallback has a target
        from core.prompt_types import SelectionTuple
        asset_dir = tmp_path / "system"
        asset_dir.mkdir(parents=True, exist_ok=True)
        asset_md = asset_dir / "react_analyst.md"
        asset_md.write_text(
            "---\nname: test\nversion: 1.0.0\nagent_role: react_analyst\n"
            "status: active\nvariant: baseline\nlocale: en\nparity_group: ''\n---\nContent\n",
            encoding="utf-8",
        )
        valid_config["prompts"]["registry"]["directory"] = str(tmp_path)

        loader = PromptAssetLoader(
            prompt_root=tmp_path,
            config=valid_config,
        )
        sel = SelectionTuple(agent_role="react_analyst", requested_version="9.9.9")
        result = loader.resolve(sel)
        assert result.fallback_used is True
        assert result.prompt_version == "1.0.0"  # baseline fallback
        assert "9.9.9" in result.degraded_reason

    def test_content_resolution_succeeds_on_valid_version(self, tmp_path, valid_config):
        """Existing version — clean resolution with no fallback."""
        from core.prompt_types import SelectionTuple
        asset_dir = tmp_path / "system"
        asset_dir.mkdir(parents=True, exist_ok=True)
        asset_md = asset_dir / "react_analyst.md"
        asset_md.write_text(
            "---\nname: baseline\nversion: 1.0.0\nagent_role: react_analyst\n"
            "status: active\nvariant: baseline\nlocale: en\nparity_group: ''\n---\nContent\n",
            encoding="utf-8",
        )
        valid_config["prompts"]["registry"]["directory"] = str(tmp_path)
        valid_config["prompts"]["system"]["active_version"] = "1.0.0"

        loader = PromptAssetLoader(
            prompt_root=tmp_path,
            config=valid_config,
        )
        sel = SelectionTuple(agent_role="react_analyst", requested_version="1.0.0")
        result = loader.resolve(sel)
        assert result.fallback_used is False
        assert result.prompt_version == "1.0.0"
