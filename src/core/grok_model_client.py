"""Grok (xAI) model client placeholder implementing BaseModelClient.

NOTE: Replace stub implementations with actual API integration when available.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Generator
import logging
from .base_model_client import BaseModelClient


class GrokModelClient(BaseModelClient):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        model_cfg = config.get("model", {})
        grok_cfg = model_cfg.get("grok", {})  # nested provider-specific section
        self._api_key = grok_cfg.get("api_key") or config.get("grok", {}).get("api_key")
        self._model = model_cfg.get("name") or grok_cfg.get("model") or "grok-beta"
        if not self._api_key:
            # Keep non-fatal so user can still run OpenAI; raise only if actually used
            self.logger.warning("Grok API key missing; Grok client will raise if invoked.")
        self.logger.info(f"GrokModelClient initialized model={self._model} (stub)")

    @property
    def provider(self) -> str:
        return "grok"

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, prompt: str, *, context: Optional[str] = None) -> str:
        if not self._api_key:
            raise ValueError("Grok API key not configured.")
        # Placeholder logic
        return f"[Grok STUB] Would process prompt: {prompt[:60]}..."

    def generate_stream(self, prompt: str, *, context: Optional[str] = None) -> Generator[str, None, None]:
        if not self._api_key:
            yield "[error] Grok API key not configured."
            return
        # Simple fake streaming
        text = self.generate(prompt, context=context)
        for token in text.split():
            yield token + " "