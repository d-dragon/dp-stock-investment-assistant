"""Utility helpers shared across service implementations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Set, TypeVar

try:  # optional dependency in tests
    from bson import ObjectId  # type: ignore
except Exception:  # pragma: no cover - bson is available in runtime env
    ObjectId = None  # type: ignore

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Management-route query-parameter parsing
# ---------------------------------------------------------------------------

class ListParams:
    """Parsed and validated list query parameters."""

    __slots__ = ("limit", "offset", "status")

    def __init__(self, limit: int, offset: int, status: Optional[str]) -> None:
        self.limit = limit
        self.offset = offset
        self.status = status

    def as_dict(self) -> Dict[str, Any]:
        return {"limit": self.limit, "offset": self.offset, "status": self.status}


def parse_list_params(
    request_args: Dict[str, str],
    *,
    default_limit: int = 25,
    max_limit: int = 100,
    valid_statuses: Optional[Set[str]] = None,
) -> ListParams:
    """Parse ``limit``, ``offset``, and ``status`` from Flask *request.args*.

    Returns a :class:`ListParams` with validated values.

    * ``limit`` values outside ``[1, max_limit]`` are clamped silently.
    * Explicitly negative ``offset`` raises :class:`ValueError` so callers
      can translate it into a 400 response.
    * Unknown ``status`` values are ignored (reset to ``None``).
    """
    # --- limit ---
    try:
        limit = int(request_args.get("limit", default_limit))
    except (TypeError, ValueError):
        limit = default_limit
    limit = max(1, min(limit, max_limit))

    # --- offset ---
    try:
        offset = int(request_args.get("offset", 0))
    except (TypeError, ValueError):
        offset = 0
    if offset < 0:
        raise ValueError("offset must be >= 0")

    # --- status ---
    raw_status = request_args.get("status")
    if raw_status is not None:
        raw_status = raw_status.strip().lower()
    if valid_statuses and raw_status not in valid_statuses:
        raw_status = None

    return ListParams(limit=limit, offset=offset, status=raw_status)


def paginate_response(
    items: Sequence[Dict[str, Any]],
    total: int,
    limit: int,
    offset: int,
) -> Dict[str, Any]:
    """Build the standard management-API list envelope.

    Every paginated list endpoint returns the same shape::

        {"items": [...], "total": N, "limit": N, "offset": N}
    """
    return {
        "items": list(items),
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def management_error_response(
    message: str,
    status_code: int,
    *,
    code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a JSON error dict matching the chat error envelope pattern.

    Standard ``code`` values aligned with HTTP semantics:

    * ``VALIDATION_ERROR`` – 400 Bad Request
    * ``FORBIDDEN``        – 403 Forbidden
    * ``NOT_FOUND``        – 404 Not Found
    * ``CONFLICT``         – 409 Conflict
    * ``INTERNAL_ERROR``   – 500 Internal Server Error

    Returns a dict ``{"error": {...}}`` so callers can
    do ``return jsonify(body), status`` directly.
    """
    if code is None:
        code = _STATUS_TO_ERROR_CODE.get(status_code, "INTERNAL_ERROR")
    error_body: Dict[str, Any] = {"message": message, "code": code}
    if details is not None:
        error_body["details"] = details
    if correlation_id is not None:
        error_body["correlation_id"] = correlation_id
    return {"error": error_body}


# Maps HTTP status codes to canonical error codes.
_STATUS_TO_ERROR_CODE: Dict[int, str] = {
    400: "VALIDATION_ERROR",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    500: "INTERNAL_ERROR",
}


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
