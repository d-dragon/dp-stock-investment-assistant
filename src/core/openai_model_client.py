"""OpenAI model client implementing BaseModelClient."""

from __future__ import annotations
import logging
from typing import Dict, Any, Optional, Generator
from openai import OpenAI
from .base_model_client import BaseModelClient


class OpenAIModelClient(BaseModelClient):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

        # Backward compatibility: accept either config['model'] or legacy config['openai']
        openai_cfg = config.get("openai", {})
        model_cfg = config.get("model", {})

        # Precedence: explicit model.* overrides legacy openai.*
        self._api_key = model_cfg.get("openai", {}).get("api_key") or openai_cfg.get("api_key")
        if not self._api_key:
            raise ValueError("OpenAI API key missing (expected in openai.api_key or model.openai.api_key)")

        self._model = model_cfg.get("name") or openai_cfg.get("model") or "gpt-4"
        self._temperature = model_cfg.get("temperature", openai_cfg.get("temperature", 0.7))
        self._max_tokens = model_cfg.get("max_tokens", openai_cfg.get("max_tokens", 2000))

        self.client = OpenAI(api_key=self._api_key)
        self.logger.info(f"OpenAIModelClient initialized model={self._model}")

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