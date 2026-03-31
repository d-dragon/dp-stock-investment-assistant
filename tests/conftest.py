"""Pytest configuration and fixtures.

Coverage non-regression (NFR-6.1.3):
    The coverage floor is tracked in ``pytest.ini`` as a comment.
    Run ``pytest tests/ --cov=src --cov-fail-under=56 -q`` to enforce.
    Update the threshold after coverage improves to ratchet upward.
"""

import os
import sys
from typing import Dict

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


def _to_wsgi_header_name(header_name: str) -> str:
    """Convert an HTTP header key to Flask/Werkzeug environ format."""
    return f"HTTP_{header_name.upper().replace('-', '_')}"


@pytest.fixture
def management_headers() -> Dict[str, str]:
    """Default headers required by strict management routes in tests."""
    return {"X-User-ID": "user-1"}


@pytest.fixture
def apply_management_headers(management_headers):
    """Return a helper that applies required management headers to a test client."""

    def _apply(client):
        for key, value in management_headers.items():
            client.environ_base[_to_wsgi_header_name(key)] = value
        return client

    return _apply
