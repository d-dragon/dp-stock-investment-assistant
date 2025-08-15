"""Factory for selecting appropriate model client based on configuration or overrides."""

from __future__ import annotations
from typing import Dict, Any, Optional
import logging
from .base_model_client import BaseModelClient
from .openai_model_client import OpenAIModelClient
from .grok_model_client import GrokModelClient


class ModelClientFactory:
    _CACHE: Dict[str, BaseModelClient] = {}

    @staticmethod
    def get_client(config: Dict[str, Any], *, provider: Optional[str] = None, model_name: Optional[str] = None) -> BaseModelClient:
        logger = logging.getLogger(__name__)

        # Determine provider
        provider_cfg = provider or config.get("model", {}).get("provider")
        if not provider_cfg:
            # Fallback: if legacy openai config present, assume openai
            provider_cfg = "openai" if "openai" in config else "openai"

        key = f"{provider_cfg}:{model_name or ''}"
        if key in ModelClientFactory._CACHE:
            return ModelClientFactory._CACHE[key]

        if provider_cfg == "openai":
            client = OpenAIModelClient(config)
        elif provider_cfg == "grok":
            client = GrokModelClient(config)
        else:
            raise ValueError(f"Unsupported model provider: {provider_cfg}")

        logger.info(f"Created model client provider={client.provider} model={client.model_name}")
        ModelClientFactory._CACHE[key] = client
        return client

    @staticmethod
    def get_fallback_sequence(config: Dict[str, Any]) -> list[str]:
        model_cfg = config.get("model", {})
        seq = model_cfg.get("fallback_order")
        if isinstance(seq, list) and seq:
            return seq
        # default generic fallback preference
        return ["openai", "grok"]