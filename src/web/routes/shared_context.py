"""Shared context dataclass for HTTP route blueprints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Optional, Tuple, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from logging import Logger
    from flask import Flask
    from core.agent import StockAgent
    from core.model_registry import OpenAIModelRegistry
    from services.factory import ServiceFactory
    from services.user_service import UserService
    from services.chat_service import ChatService


@dataclass(frozen=True)
class APIRouteContext:
    """
    Immutable context object passed to all route factory functions.
    
    Contains all dependencies needed by HTTP route blueprints, following
    the frozen dataclass dependency injection pattern documented in
    backend-python.instructions.md.
    """
    app: "Flask"
    agent: "StockAgent"
    config: Mapping[str, Any]
    logger: "Logger"
    # Chat-related dependencies (prefer using chat_service instead of individual functions)
    chat_service: Optional["ChatService"] = None
    # Legacy function references (deprecated, use chat_service instead)
    stream_chat_response: Optional[Callable[[str, Optional[str]], Iterable[str]]] = None
    extract_meta: Optional[Callable[[str], Tuple[str, str, bool]]] = None
    strip_fallback_prefix: Optional[Callable[[str], str]] = None
    get_timestamp: Optional[Callable[[], str]] = None
    # Other services
    model_registry: Optional["OpenAIModelRegistry"] = None
    set_active_model: Optional[Callable[[str, str], Dict[str, Any]]] = None
    service_factory: Optional["ServiceFactory"] = None
    user_service: Optional["UserService"] = None
