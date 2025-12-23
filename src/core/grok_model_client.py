"""Grok (xAI) model client implementing BaseModelClient.

Uses OpenAI SDK with xAI's compatible API endpoint.
Reference: https://docs.x.ai/docs/guides/migration

xAI API is fully compatible with OpenAI SDK - just change base_url to https://api.x.ai/v1
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Generator
import logging
from openai import OpenAI
from .base_model_client import BaseModelClient

# xAI API constants
XAI_BASE_URL = "https://api.x.ai/v1"
XAI_DEFAULT_MODEL = "grok-4-1-fast-reasoning"
XAI_DEFAULT_TIMEOUT = 3600  # xAI recommends 3600s for reasoning models


class GrokModelClient(BaseModelClient):
    """
    Grok model client using OpenAI SDK with xAI's API endpoint.
    
    xAI API is OpenAI SDK compatible. Per xAI docs:
    "If you can use either SDKs, we recommend using OpenAI SDK for better stability."
    
    Supported models: grok-4, grok-4-1-fast-reasoning, grok-3, grok-3-mini
    Note: Grok 4 models don't support presencePenalty, frequencyPenalty, stop params.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Get configuration from nested grok config or top-level
        model_cfg = config.get("model", {})
        grok_cfg = model_cfg.get("grok", {}) or config.get("grok", {})
        
        # API key (required for actual calls, but allow init without for fallback setup)
        self._api_key = (
            grok_cfg.get("api_key") or 
            config.get("grok", {}).get("api_key")
        )
        
        # Model configuration - prioritize grok-specific settings over generic model settings
        # All values come from config (loaded from .env via config_loader)
        self._model = (
            grok_cfg.get("model") or 
            model_cfg.get("name") or 
            XAI_DEFAULT_MODEL
        )
        self._base_url = grok_cfg.get("base_url") or XAI_BASE_URL
        
        # Type conversion for env vars (they come as strings from .env)
        self._timeout = self._to_int(grok_cfg.get("timeout"), XAI_DEFAULT_TIMEOUT)
        self._max_tokens = self._to_int(grok_cfg.get("max_tokens"), 2000)
        self._temperature = self._to_float(grok_cfg.get("temperature"), 0.7)
        
        # Initialize OpenAI client with xAI endpoint (lazy init if no key)
        self._client: Optional[OpenAI] = None
        if self._api_key:
            self._init_client()
        else:
            self.logger.warning("Grok API key missing; client will raise if invoked.")
        
        self.logger.info(
            f"GrokModelClient initialized model={self._model} "
            f"base_url={self._base_url} timeout={self._timeout}s"
        )
    
    def _init_client(self) -> None:
        """Initialize OpenAI client with xAI configuration."""
        self._client = OpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._timeout,
        )
    
    @staticmethod
    def _to_int(value: Any, default: int) -> int:
        """Convert value to int with fallback to default."""
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def _to_float(value: Any, default: float) -> float:
        """Convert value to float with fallback to default."""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _ensure_client(self) -> OpenAI:
        """Ensure client is initialized, raise if not configured."""
        if self._client is None:
            if not self._api_key:
                raise ValueError(
                    "Grok API key not configured. "
                    "Set GROK_API_KEY or XAI_API_KEY environment variable."
                )
            self._init_client()
        return self._client

    @property
    def provider(self) -> str:
        return "grok"

    @property
    def model_name(self) -> str:
        return self._model
    
    def _system_prompt(self, context: Optional[str] = None) -> str:
        """Build system prompt for Grok."""
        # xAI's recommended system prompt style
        base = (
            "You are Grok, a highly intelligent AI assistant specializing in "
            "stock market analysis. Provide clear, factual insights with a touch "
            "of wit. Include a disclaimer that this is not financial advice."
        )
        if context:
            return f"{base}\n\nContext: {context}"
        return base

    def generate(self, prompt: str, *, context: Optional[str] = None) -> str:
        """
        Generate a response using Grok model.
        
        Uses OpenAI SDK chat completions with xAI endpoint.
        Note: Does not use frequency_penalty, presence_penalty, stop params
        (unsupported by Grok 4 reasoning models).
        """
        client = self._ensure_client()
        
        try:
            messages = [
                {"role": "system", "content": self._system_prompt(context)},
                {"role": "user", "content": prompt},
            ]
            
            response = client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
            )
            
            content = response.choices[0].message.content
            
            # Log usage stats if available (Grok includes reasoning_tokens)
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                self.logger.debug(
                    f"Grok usage: prompt={usage.prompt_tokens} "
                    f"completion={usage.completion_tokens} "
                    f"total={usage.total_tokens}"
                )
            
            return content or ""
            
        except Exception as e:
            self.logger.error(f"Grok generation error: {e}")
            raise

    def generate_stream(
        self, prompt: str, *, context: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Stream a response using Grok model with SSE.
        
        Uses OpenAI SDK streaming with xAI endpoint.
        Chunks follow SSE format with delta.content.
        """
        client = self._ensure_client()
        
        try:
            messages = [
                {"role": "system", "content": self._system_prompt(context)},
                {"role": "user", "content": prompt},
            ]
            
            response = client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                stream=True,
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"Grok streaming error: {e}")
            yield f"[error] {e}"