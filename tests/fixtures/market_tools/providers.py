"""Provider posture fixtures."""

from __future__ import annotations

from core.tools.market_data import default_vietnam_provider_descriptors


PROVIDERS = default_vietnam_provider_descriptors()

VIETNAM_FIRST_PROVIDER_IDS = (
    "hose_official",
    "hnx_official",
    "vsdc",
    "fiingroup",
    "vietstock",
    "cafef",
    "vnstock",
)

INTERNATIONAL_FALLBACK_PROVIDER_IDS = ("yahoo_fallback",)
VISUALIZATION_PROVIDER_IDS = ("tradingview",)
BLOCKED_PUBLIC_WEB_PROVIDER_IDS = ("vietstock", "cafef", "vnstock")
