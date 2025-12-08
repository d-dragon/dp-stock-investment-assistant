"""Logging utilities for service and repository layers."""

from __future__ import annotations

import logging
from typing import Optional


class LoggingMixin:
    """Mixin that injects a logger into subclasses."""

    def __init__(self, *, logger: Optional[logging.Logger] = None) -> None:
        self._logger = logger or self._build_logger()

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def _build_logger(self) -> logging.Logger:
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return logging.getLogger(name)

    def bind_logger(self, logger: logging.Logger) -> None:
        self._logger = logger
