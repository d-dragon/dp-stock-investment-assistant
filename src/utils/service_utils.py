"""Utility helpers shared across service implementations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, List, Sequence, TypeVar

try:  # optional dependency in tests
    from bson import ObjectId  # type: ignore
except Exception:  # pragma: no cover - bson is available in runtime env
    ObjectId = None  # type: ignore

T = TypeVar("T")


def stringify_identifier(value: Any) -> Any:
    """Convert ObjectId (or similar) values to simple strings for JSON serialization."""
    if ObjectId is not None and isinstance(value, ObjectId):
        return str(value)
    return value


def serialize_value(value: Any) -> Any:
    """Convert MongoDB types to JSON-serializable values."""
    if ObjectId is not None and isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    return value


def normalize_document(
    document: Dict[str, Any], *, id_fields: Sequence[str] = ("_id", "user_id", "workspace_id")
) -> Dict[str, Any]:
    """Return a copy with common identifier fields and datetime objects coerced to JSON-safe types."""
    normalized = {}
    for key, value in (document or {}).items():
        if key in id_fields:
            normalized[key] = stringify_identifier(value)
        else:
            normalized[key] = serialize_value(value)
    return normalized


def batched(iterable: Iterable[T], size: int) -> Iterator[List[T]]:
    """Yield items from *iterable* in fixed-size lists (last batch may be smaller)."""
    if size <= 0:
        raise ValueError("Batch size must be positive")

    chunk: List[T] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
