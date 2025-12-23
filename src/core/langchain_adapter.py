"""Minimal LangChain integration (optional) with external prompt support."""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path

try:
    # LangChain 1.x: imports moved to langchain_core
    from langchain_core.prompts import PromptTemplate
except ImportError:
    try:
        # Fallback for older versions
        from langchain.prompts import PromptTemplate
    except ImportError:
        PromptTemplate = None  # graceful fallback

from .base_model_client import BaseModelClient


_PROMPT_CACHE: Dict[str, str] = {}
_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt_file(name: str) -> str:
    if name in _PROMPT_CACHE:
        return _PROMPT_CACHE[name]
    path = _PROMPTS_DIR / name
    if not path.exists():
        # fallback minimal
        content = "You are an investment analysis assistant."
    else:
        content = path.read_text(encoding="utf-8").strip()
    _PROMPT_CACHE[name] = content
    return content


class PromptBuilder:
    """Wrapper around LangChain PromptTemplate with fallback and external system prompt."""

    def __init__(self, system_filename: str = "system_stock_assistant-vn.txt"):
        self.logger = logging.getLogger(__name__)
        self.system_prompt = _load_prompt_file(system_filename)
        template_str = (
            "{system_prompt}\n"
            "User query: {query}\n"
            "{ticker_section}"
            "{data_section}"
            "Provide a concise, factual answer. Always append a brief disclaimer."
        )
        if PromptTemplate:
            self.template = PromptTemplate.from_template(template_str)
        else:
            self.template = template_str

    def build(
        self,
        query: str,
        tickers: Optional[List[str]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> str:
        ticker_section = ""
        if tickers:
            ticker_section = f"Tickers referenced: {', '.join(tickers)}\n"
        data_section = ""
        if data and data.get("prices"):
            lines = []
            for p in data["prices"][:6]:
                lines.append(
                    f"{p['symbol']}: price={p.get('price')} prev_close={p.get('prev_close')} PE={p.get('pe')}"
                )
            if lines:
                data_section = "Quick price snapshot:\n" + "\n".join(lines) + "\n"
        if PromptTemplate:
            return self.template.format(
                system_prompt=self.system_prompt,
                query=query,
                ticker_section=ticker_section,
                data_section=data_section,
            )
        return self.template.format(
            system_prompt=self.system_prompt,
            query=query,
            ticker_section=ticker_section,
            data_section=data_section,
        )


def build_prompt(query: str, data: Dict[str, Any], tickers: List[str]) -> str:
    builder = PromptBuilder()
    return builder.build(query=query, tickers=tickers or [], data=data or {})