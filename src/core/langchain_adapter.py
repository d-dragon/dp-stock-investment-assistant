"""Minimal LangChain integration (optional)."""

from __future__ import annotations
from typing import Optional, Dict, Any
import logging

try:
    from langchain.prompts import PromptTemplate
except ImportError:
    PromptTemplate = None  # graceful fallback

from .base_model_client import BaseModelClient


class PromptBuilder:
    """Wrapper around LangChain PromptTemplate with fallback."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        template_str = (
            "You are an investment analysis assistant.\n"
            "User query: {query}\n"
            "{ticker_section}"
            "Provide a concise, factual answer with a disclaimer."
        )
        if PromptTemplate:
            self.template = PromptTemplate.from_template(template_str)
        else:
            self.template = template_str

    def build(self, query: str, tickers: Optional[list[str]] = None) -> str:
        ticker_section = ""
        if tickers:
            ticker_section = f"Tickers referenced: {', '.join(tickers)}\n"
        if PromptTemplate:
            return self.template.format(query=query, ticker_section=ticker_section)
        return self.template.format(query=query, ticker_section=ticker_section)


def build_prompt(query: str, data: Dict[str, Any], tickers: list[str]) -> str:
    builder = PromptBuilder()
    return builder.build(query, tickers=tickers or [])