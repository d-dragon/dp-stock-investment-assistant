from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional, Tuple, TYPE_CHECKING

import requests
from flask import Blueprint, jsonify, request

if TYPE_CHECKING:
    from logging import Logger
    from flask import Flask
    from core.agent import StockAgent

from .api_routes import APIRouteContext  # reuse shared context
from utils.cache import CacheBackend

CACHE_KEY = "openai:models:list"
DEFAULT_TTL_SECONDS = 3600


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _get_openai_api_key(config: Mapping[str, Any]) -> Optional[str]:
    # Priority: ENV > config.openai.api_key > config.model.api_key
    import os
    return os.getenv("OPENAI_API_KEY") or (config.get("openai", {}) or {}).get("api_key") or (config.get("model", {}) or {}).get("api_key")


def _fetch_openai_models(api_key: str, *, timeout: float = 15.0) -> Dict[str, Any]:
    # https://platform.openai.com/docs/api-reference/models/list
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()
    models = []
    for item in (payload.get("data") or []):
        models.append(
            {
                "id": item.get("id"),
                "created": item.get("created"),
                "owned_by": item.get("owned_by"),
                "object": item.get("object"),
            }
        )
    return {"models": models, "fetched_at": _iso_utc_now(), "source": "openai"}


def create_models_blueprint(context: APIRouteContext) -> Blueprint:
    """
    Endpoints:
    - GET /api/models/openai?refresh=true|false
    - POST /api/models/openai/refresh
    - GET /api/models/openai/selected
    - POST /api/models/openai/select
    """
    blueprint = Blueprint("models", __name__)
    config = context.config
    logger = context.logger
    agent = context.agent
    set_active_model = context.set_active_model

    cache = CacheBackend.from_config(config, logger=logger)
    ttl_seconds = int((config.get("cache", {}) or {}).get("ttl_seconds", DEFAULT_TTL_SECONDS))

    def get_models(refresh: bool = False) -> Tuple[Dict[str, Any], bool]:
        """
        Returns: (payload, cached_flag)
        payload: {"models": [...], "fetched_at": "...", "source": "openai"|"cache"}
        """
        if not refresh:
            cached = cache.get_json(CACHE_KEY)
            if cached:
                cached["source"] = "cache"
                logger.info("models.list cache-hit", extra={"cached": True, "count": len(cached.get("models", []))})
                return cached, True

        api_key = _get_openai_api_key(config)
        if not api_key:
            raise RuntimeError("Missing OpenAI API key")
        t0 = time.perf_counter()
        fresh = _fetch_openai_models(api_key)
        dt = (time.perf_counter() - t0) * 1000.0
        logger.info("models.list fetched", extra={"cached": False, "count": len(fresh.get("models", [])), "ms": round(dt, 2)})
        cache.set_json(CACHE_KEY, fresh, ttl_seconds=ttl_seconds)
        return fresh, False

    @blueprint.route("/models/openai", methods=["GET"])
    def list_openai_models():
        refresh = str(request.args.get("refresh", "false")).lower() in ("1", "true", "yes")
        logger.debug("GET /api/models/openai", extra={"refresh": refresh})
        try:
            payload, cached = get_models(refresh=refresh)
            response = {
                "models": payload.get("models", []),
                "fetched_at": payload.get("fetched_at"),
                "source": payload.get("source", "cache" if cached else "openai"),
                "cached": cached,
            }
            logger.debug("models.list response", extra={"cached": cached, "count": len(response["models"])})
            return jsonify(response)
        except requests.HTTPError as http_err:
            logger.error("OpenAI models fetch failed", extra={"error": str(http_err)})
            return jsonify({"error": f"OpenAI error: {http_err}"}), 502
        except Exception as exc:
            logger.error("Error listing models", extra={"error": str(exc)})
            return jsonify({"error": str(exc)}), 500

    @blueprint.route("/models/openai/refresh", methods=["POST"])
    def refresh_openai_models():
        logger.debug("POST /api/models/openai/refresh")
        try:
            payload, _ = get_models(refresh=True)
            response = {
                "models": payload.get("models", []),
                "fetched_at": payload.get("fetched_at"),
                "source": "openai",
                "cached": False,
            }
            logger.info("models.refresh success", extra={"count": len(response["models"])})
            return jsonify(response)
        except requests.HTTPError as http_err:
            logger.error("OpenAI models refresh failed", extra={"error": str(http_err)})
            return jsonify({"error": f"OpenAI error: {http_err}"}), 502
        except Exception as exc:
            logger.error("Error refreshing models", extra={"error": str(exc)})
            return jsonify({"error": str(exc)}), 500

    @blueprint.route("/models/openai/selected", methods=["GET"])
    def get_selected_model():
        logger.debug("GET /api/models/openai/selected")
        model_cfg = config.get("model", {}) or {}
        res = {
            "provider": model_cfg.get("provider") or "openai",
            "name": model_cfg.get("name") or (config.get("openai", {}) or {}).get("model") or "gpt-4",
        }
        logger.debug("models.selected", extra=res)
        return jsonify(res)

    @blueprint.route("/models/openai/select", methods=["POST"])
    def select_model():
        data = request.get_json(silent=True) or {}
        provider = (data.get("provider") or "openai").strip() or "openai"
        name = (data.get("name") or "").strip()
        logger.debug("POST /api/models/openai/select", extra={"provider": provider, "model_name": name})
        try:
            if not name:
                return jsonify({"error": "Field 'name' is required"}), 400

            # Optional: validate exists in cache (advisory)
            cached = cache.get_json(CACHE_KEY)
            if cached and cached.get("models"):
                ids = {m.get("id") for m in cached["models"] if isinstance(m, dict)}
                if name not in ids:
                    logger.info("models.select name not in cache", extra={"model_name": name, "advisory": True})

            # Apply selection
            if set_active_model:
                result = set_active_model(provider, name)
                logger.info("models.select applied via context", extra={"provider": provider, "model_name": name})
            elif hasattr(agent, "set_active_model"):
                agent.set_active_model(provider=provider, name=name)
                logger.info("models.select applied via agent", extra={"provider": provider, "model_name": name})
            else:
                # Fallback: mutate config, best-effort to refresh underlying client
                cfg_model = config.setdefault("model", {})
                cfg_model["provider"] = provider
                cfg_model["name"] = name
                logger.info("models.select applied to config", extra={"provider": provider, "model_name": name})
                try:
                    from core.model_factory import ModelClientFactory
                    agent._client = ModelClientFactory.get_client(config, provider=provider)
                except Exception as e:
                    logger.error("Failed to update agent client after select", extra={"error": str(e)})

            # Persist in config
            cfg_model = config.setdefault("model", {})
            cfg_model["provider"] = provider
            cfg_model["name"] = name

            return jsonify({"provider": provider, "name": name})
        except Exception as exc:
            logger.error("Error selecting model", extra={"error": str(exc), "provider": provider, "model_name": name, "traceback": True}, exc_info=True)
            return jsonify({"error": str(exc)}), 500

    return blueprint