"""Utility helpers shared across service implementations."""

from __future__ import annotations

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


def normalize_document(
    document: Dict[str, Any], *, id_fields: Sequence[str] = ("_id", "user_id", "workspace_id")
) -> Dict[str, Any]:
    """Return a shallow copy with common identifier fields coerced to strings."""
    normalized = dict(document or {})
    for key in id_fields:
        if key in normalized:
            normalized[key] = stringify_identifier(normalized[key])
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
