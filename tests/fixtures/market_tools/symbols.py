"""Vietnam symbol identity fixtures."""

from __future__ import annotations

from core.tools.normalization import CanonicalSymbolIdentity


FPT = CanonicalSymbolIdentity(symbol="FPT", exchange="HOSE", currency="VND", aliases=("HOSE:FPT",))
SHS = CanonicalSymbolIdentity(symbol="SHS", exchange="HNX", currency="VND", aliases=("HNX:SHS",))
BSR = CanonicalSymbolIdentity(symbol="BSR", exchange="UPCOM", currency="VND", aliases=("UPCOM:BSR",))
VNM = CanonicalSymbolIdentity(symbol="VNM", exchange="HOSE", currency="VND", aliases=("HOSE:VNM",))

SUPPORTED_SYMBOLS = {
    "FPT": FPT,
    "HOSE:FPT": FPT,
    "SHS": SHS,
    "HNX:SHS": SHS,
    "BSR": BSR,
    "UPCOM:BSR": BSR,
    "VNM": VNM,
    "HOSE:VNM": VNM,
}

AMBIGUOUS_TICKERS = {"ABC"}
