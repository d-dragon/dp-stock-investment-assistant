"""OpenAI model client implementing BaseModelClient."""

from __future__ import annotations
import logging
from typing import Dict, Any, Optional, Generator
from openai import OpenAI
from .base_model_client import BaseModelClient
from utils.cache import CacheBackend


class OpenAIModelClient(BaseModelClient):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize cache backend
        self.cache = CacheBackend.from_config(config, logger=self.logger)

        # Backward compatibility: accept either config['model'] or legacy config['openai']
        openai_cfg = config.get("openai", {})
        model_cfg = config.get("model", {})

        # Get configuration with cache-first approach
        self._api_key = self._get_config_value("api_key", model_cfg, openai_cfg)
        if not self._api_key:
            raise ValueError("OpenAI API key missing (expected in openai.api_key or model.openai.api_key)")

        self._model = self._get_config_value("model", model_cfg, openai_cfg, default=None)  # No hardcoded default; rely on config
        if not self._model:
            raise ValueError("OpenAI model name missing (expected in model.name or openai.model)")
        self._temperature = self._get_config_value("temperature", model_cfg, openai_cfg, default=0.7)
        self._max_tokens = self._get_config_value("max_tokens", model_cfg, openai_cfg, default=2000)

        self.client = OpenAI(api_key=self._api_key)
        self.logger.info(f"OpenAIModelClient initialized model={self._model}")

    def _get_config_value(self, key: str, model_cfg: Dict[str, Any], openai_cfg: Dict[str, Any], default: Any = None) -> Any:
        """
        Get configuration value - check config first, THEN cache (development-friendly).
        Priority: config -> Redis cache -> default
        """
        # Fallback to config with precedence: explicit model.* overrides legacy openai.*
        if key == "api_key":
            value = model_cfg.get("openai", {}).get("api_key") or openai_cfg.get("api_key") or default
        elif key == "model":
            value = model_cfg.get("name") or openai_cfg.get("model") or default
        else:
            value = model_cfg.get(key, openai_cfg.get(key, default))
        
        # Only use cache if config value is missing
        if value is None:
            cache_key = f"openai_config:{key}" if key != "model" else "openai_config:model_name"
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                self.logger.debug(f"Retrieved {key} from cache (config missing)")
                if key in ["temperature"]:
                    return float(cached_value)
                elif key in ["max_tokens"]:
                    return int(cached_value)
                return cached_value
    
        return value

    def update_config_in_cache(self, key: str, value: Any, *, ttl_seconds: int = 3600) -> None:
        """
        Update a configuration value in cache.
        """
        if key == "model":
            cache_key = "openai_config:model_name"
        else:
            cache_key = f"openai_config:{key}"
        self.cache.set(cache_key, str(value), ttl_seconds=ttl_seconds)
        self.logger.info(f"Updated {key} in cache")

    def clear_config_cache(self) -> None:
        """
        Clear all cached configuration values.
        """
        config_keys = ["api_key", "model", "temperature", "max_tokens"]
        for key in config_keys:
            if key == "model":
                cache_key = "openai_config:model_name"
            else:
                cache_key = f"openai_config:{key}"
            self.cache.delete(cache_key)
        self.logger.info("Cleared OpenAI configuration cache")

    @property
    def provider(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    def supports_web_search(self) -> bool:
        return True  # using responses API with web_search_preview tool

    def _system_prompt(self, context: Optional[str]) -> str:
        base = (
            "You are a helpful AI assistant specializing in stock market analysis. "
            "Provide clear, factual insights; include a disclaimer that this is not financial advice."
        )
        return base + (f"\nContext: {context}" if context else "")

    def generate(self, prompt: str, *, context: Optional[str] = None) -> str:
        try:
            messages = [
                {"role": "system", "content": self._system_prompt(context)},
                {"role": "user", "content": prompt},
            ]
            resp = self.client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_completion_tokens=self._max_tokens,
            )
            return resp.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI generation error: {e}")
            raise

    def generate_with_search(self, prompt: str, *, context: Optional[str] = None) -> str:
        # Use responses API to leverage web_search_preview tool; fallback to plain chat on failure
        try:
            input_content = f"{self._system_prompt(context)}\n\nUser query: {prompt}"
            resp = self.client.responses.create(
                model=self._model,
                input=input_content,
                tools=[{"type": "web_search_preview"}],
                max_output_tokens=self._max_tokens,
            )
            # Attempt extraction
            if hasattr(resp, "output") and resp.output:
                for item in resp.output:
                    txt = self._extract(item)
                    if txt:
                        return txt
            return self.generate(prompt, context=context)
        except Exception as e:
            self.logger.warning(f"web_search path failed, fallback to chat: {e}")
            return self.generate(prompt, context=context)

    def generate_stream(self, prompt: str, *, context: Optional[str] = None) -> Generator[str, None, None]:
        try:
            messages = [
                {"role": "system", "content": self._system_prompt(context)},
                {"role": "user", "content": prompt},
            ]
            resp = self.client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_completion_tokens=self._max_tokens,
                stream=True,
            )
            for chunk in resp:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            self.logger.error(f"OpenAI streaming error: {e}")
            # Emit single error chunk
            yield f"[error] {e}"

    def _extract(self, item) -> Optional[str]:
        try:
            if hasattr(item, "content"):
                content = item.content
                if isinstance(content, list):
                    for part in content:
                        if hasattr(part, "text") and part.text:
                            return part.text
                elif isinstance(content, str):
                    return content
                elif hasattr(content, "text"):
                    return content.text
            if hasattr(item, "text") and item.text:
                return item.text
        except Exception:
            pass
        return None