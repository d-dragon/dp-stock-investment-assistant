"""Services for managing OpenAI model metadata and caching."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - library should exist in runtime, but tests may mock
    OpenAI = None  # type: ignore


class OpenAIModelRegistry:
    """Handles retrieval and caching of OpenAI model catalog data."""

    SUPPORTED_CACHE_KEY = "model:supported:openai"
    ACTIVE_CACHE_KEY = "model:active:openai"

    def __init__(self, config: Dict[str, Any], cache_repository=None):
        self.config = config
        self.cache_repository = cache_repository
        self.logger = logging.getLogger(__name__)

        model_cfg = config.get("model", {}) if isinstance(config, dict) else {}
        provider_cfg = model_cfg.get("openai", {}) if isinstance(model_cfg, dict) else {}
        legacy_cfg = config.get("openai", {}) if isinstance(config, dict) else {}

        self._api_key = provider_cfg.get("api_key") or legacy_cfg.get("api_key")
        self._client: Optional[OpenAI] = None
        ttl = model_cfg.get("catalog_cache_ttl") if isinstance(model_cfg, dict) else None
        self.cache_ttl_seconds = int(ttl) if isinstance(ttl, (int, float)) and ttl > 0 else 3600

    @property
    def is_configured(self) -> bool:
        """Return True when the registry can reach OpenAI for live refreshes."""
        return self._api_key is not None and OpenAI is not None

    def get_supported_models(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Return supported OpenAI models, optionally forcing a live refresh."""
        if not force_refresh:
            cached = self._get_cached_models()
            if cached:
                result = dict(cached)
                result["source"] = "cache"
                result["active_model"] = result.get("active_model") or self.get_active_model()
                return result

        if not self.is_configured:
            cached = self._get_cached_models()
            if cached:
                result = dict(cached)
                result["source"] = "cache"
                result["active_model"] = result.get("active_model") or self.get_active_model()
                return result
            raise RuntimeError("OpenAI API key is not configured; cannot refresh model catalog")

        result = self.refresh_supported_models()
        result["source"] = "live"
        return result

    def refresh_supported_models(self) -> Dict[str, Any]:
        """Fetch supported models from OpenAI and update cache."""
        payload = self._fetch_models_from_openai()
        if self.cache_repository:
            self.cache_repository.cache_supported_models("openai", payload, expire_seconds=self.cache_ttl_seconds)
        payload_with_meta = dict(payload)
        payload_with_meta["active_model"] = self.get_active_model()
        return payload_with_meta

    def is_supported_model(self, model_name: str) -> bool:
        """Return True if the provided model id exists in the catalog."""
        listing = self.get_supported_models(force_refresh=False)
        if self._model_in_listing(model_name, listing.get("models", [])):
            return True
        if not self.is_configured:
            return False
        refreshed = self.refresh_supported_models()
        return self._model_in_listing(model_name, refreshed.get("models", []))

    def record_active_model(self, model_name: str) -> None:
        """Persist the active model selection in cache when available."""
        if self.cache_repository:
            self.cache_repository.cache_active_model("openai", model_name)

    def get_active_model(self) -> Optional[str]:
        """Retrieve the active OpenAI model selection."""
        cached = None
        if self.cache_repository:
            cached = self.cache_repository.get_cached_active_model("openai")
        if cached:
            return cached
        model_cfg = self.config.get("model", {}) if isinstance(self.config, dict) else {}
        if model_cfg.get("provider") not in (None, "openai"):
            return None
        return model_cfg.get("name")

    # -------- Internal helpers --------
    def _get_cached_models(self) -> Optional[Dict[str, Any]]:
        if not self.cache_repository:
            return None
        return self.cache_repository.get_cached_supported_models("openai")

    def _fetch_models_from_openai(self) -> Dict[str, Any]:
        client = self._get_client()
        response = client.models.list()
        items = getattr(response, "data", response)
        serialized = [self._serialize_model(item) for item in items]
        return {
            "models": serialized,
            "refreshed_at": datetime.now(timezone.utc).isoformat(timespec="seconds")
        }

    def _get_client(self) -> OpenAI:
        if self._client is None:
            if not self.is_configured:
                raise RuntimeError("OpenAI client unavailable (missing dependency or API key)")
            self._client = OpenAI(api_key=self._api_key)
        return self._client

    @staticmethod
    def _serialize_model(model_obj: Any) -> Dict[str, Any]:
        candidates = [
            getattr(model_obj, "model_dump", None),
            getattr(model_obj, "dict", None),
            getattr(model_obj, "to_dict", None),
        ]
        for fn in candidates:
            if callable(fn):
                try:
                    data = fn()
                    if isinstance(data, dict):
                        return data
                except TypeError:
                    continue
        # Fallback: gather common attributes
        fields = {}
        for attr in ("id", "object", "created", "owned_by", "root", "parent"):
            if hasattr(model_obj, attr):
                fields[attr] = getattr(model_obj, attr)
        permissions = getattr(model_obj, "permission", None)
        if permissions is not None:
            try:
                fields["permission"] = list(permissions)
            except TypeError:
                fields["permission"] = permissions
        return fields

    @staticmethod
    def _model_in_listing(model_name: str, models: List[Dict[str, Any]]) -> bool:
        for item in models:
            if isinstance(item, dict) and item.get("id") == model_name:
                return True
        return False