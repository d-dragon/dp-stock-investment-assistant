"""Tests for src/utils/service_utils.py — management-route helpers."""

import pytest

from utils.service_utils import (
    ListParams,
    batched,
    management_error_response,
    normalize_document,
    parse_list_params,
)


# ---------------------------------------------------------------------------
# parse_list_params
# ---------------------------------------------------------------------------

class TestParseListParams:
    """Tests for the shared list query-parameter parser."""

    def test_defaults(self):
        result = parse_list_params({})
        assert result.limit == 25
        assert result.offset == 0
        assert result.status is None

    def test_custom_defaults(self):
        result = parse_list_params({}, default_limit=10, max_limit=50)
        assert result.limit == 10

    def test_explicit_values(self):
        result = parse_list_params({"limit": "30", "offset": "5"})
        assert result.limit == 30
        assert result.offset == 5

    def test_limit_clamped_to_max(self):
        result = parse_list_params({"limit": "999"})
        assert result.limit == 100

    def test_limit_clamped_to_min(self):
        result = parse_list_params({"limit": "0"})
        assert result.limit == 1

    def test_negative_limit_clamped(self):
        result = parse_list_params({"limit": "-5"})
        assert result.limit == 1

    def test_negative_offset_raises(self):
        with pytest.raises(ValueError, match="offset must be >= 0"):
            parse_list_params({"offset": "-10"})

    def test_non_numeric_limit_uses_default(self):
        result = parse_list_params({"limit": "abc"})
        assert result.limit == 25

    def test_non_numeric_offset_uses_default(self):
        result = parse_list_params({"offset": "xyz"})
        assert result.offset == 0

    def test_valid_status(self):
        result = parse_list_params(
            {"status": "active"},
            valid_statuses={"active", "closed", "archived"},
        )
        assert result.status == "active"

    def test_status_case_insensitive(self):
        result = parse_list_params(
            {"status": "Active"},
            valid_statuses={"active", "closed", "archived"},
        )
        assert result.status == "active"

    def test_invalid_status_ignored(self):
        result = parse_list_params(
            {"status": "deleted"},
            valid_statuses={"active", "closed", "archived"},
        )
        assert result.status is None

    def test_status_without_valid_set_passes_through(self):
        result = parse_list_params({"status": "anything"})
        assert result.status == "anything"

    def test_status_whitespace_stripped(self):
        result = parse_list_params(
            {"status": "  closed  "},
            valid_statuses={"active", "closed", "archived"},
        )
        assert result.status == "closed"

    def test_as_dict(self):
        result = parse_list_params({"limit": "10", "offset": "5", "status": "active"})
        d = result.as_dict()
        assert d == {"limit": 10, "offset": 5, "status": "active"}


# ---------------------------------------------------------------------------
# management_error_response
# ---------------------------------------------------------------------------

class TestManagementErrorResponse:
    """Tests for the JSON error envelope builder."""

    def test_minimal(self):
        body = management_error_response("Not found", 404)
        assert body == {"error": {"message": "Not found", "code": "NOT_FOUND"}}

    def test_with_code(self):
        body = management_error_response("Not found", 404, code="RESOURCE_NOT_FOUND")
        assert body["error"]["code"] == "RESOURCE_NOT_FOUND"

    def test_with_details(self):
        body = management_error_response(
            "Bad request", 400, details={"field": "name"}
        )
        assert body["error"]["details"] == {"field": "name"}

    def test_with_correlation_id(self):
        body = management_error_response(
            "Conflict", 409, correlation_id="abc-123"
        )
        assert body["error"]["correlation_id"] == "abc-123"

    def test_full_envelope(self):
        body = management_error_response(
            "Workspace not found",
            404,
            code="RESOURCE_NOT_FOUND",
            details={"entity": "workspace"},
            correlation_id="corr-1",
        )
        assert body == {
            "error": {
                "message": "Workspace not found",
                "code": "RESOURCE_NOT_FOUND",
                "details": {"entity": "workspace"},
                "correlation_id": "corr-1",
            }
        }
