from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional, Tuple

try:
    import redis  # type: ignore
except Exception:
    redis = None  # optional


class CacheBackend:
    """
    Simple cache abstraction.
    - Tries Redis if available and reachable.
    - Falls back to in-memory cache with TTL if Redis is not available.
    """
    def __init__(self, redis_url: Optional[str] = None, *, logger=None, decode_responses: bool = True):
        self._logger = logger
        self._memory: Dict[str, Tuple[str, Optional[float]]] = {}  # key -> (str_value, expiry_epoch)
        self._redis = None

        if redis and redis_url:
            try:
                self._redis = redis.from_url(redis_url, decode_responses=decode_responses)
                self._redis.ping()
                if self._logger:
                    self._logger.info(f"Redis cache connected: {redis_url}")
            except Exception as exc:
                self._redis = None
                if self._logger:
                    self._logger.warning(f"Redis unavailable, using in-memory cache. reason={exc}")

    @classmethod
    def from_config(cls, config: Dict[str, Any], *, logger=None) -> "CacheBackend":
        url = (
            os.getenv("REDIS_URL")
            or (config.get("cache", {}) or {}).get("redis_url")
            or None
        )
        return cls(url, logger=logger)

    def is_available(self) -> bool:
        return self._redis is not None

    def ping(self) -> bool:
        if self._redis:
            try:
                self._redis.ping()
                return True
            except Exception:
                return False
        return True  # in-memory always "available"

    # ----- Raw get/set -----
    def get(self, key: str) -> Optional[str]:
        if self._redis:
            try:
                return self._redis.get(key)
            except Exception as exc:
                if self._logger:
                    self._logger.debug(f"Redis get failed key={key} reason={exc}")
        # memory
        val = self._memory.get(key)
        if not val:
            return None
        data, exp = val
        if exp is not None and time.time() > exp:
            self._memory.pop(key, None)
            return None
        return data

    def set(self, key: str, value: str, *, ttl_seconds: Optional[int] = None) -> None:
        if self._redis:
            try:
                if ttl_seconds is not None:
                    self._redis.setex(key, ttl_seconds, value)
                else:
                    self._redis.set(key, value)
                return
            except Exception as exc:
                if self._logger:
                    self._logger.debug(f"Redis set failed key={key} reason={exc}")
        # memory
        exp = (time.time() + ttl_seconds) if ttl_seconds else None
        self._memory[key] = (value, exp)

    def delete(self, key: str) -> None:
        if self._redis:
            try:
                self._redis.delete(key)
                return
            except Exception as exc:
                if self._logger:
                    self._logger.debug(f"Redis delete failed key={key} reason={exc}")
        self._memory.pop(key, None)

    # ----- JSON helpers -----
    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        raw = self.get(key)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception as exc:
            if self._logger:
                self._logger.debug(f"Cache get_json decode failed key={key} reason={exc}")
            return None

    def set_json(self, key: str, value: Dict[str, Any], *, ttl_seconds: Optional[int] = None) -> None:
        try:
            payload = json.dumps(value)
        except Exception as exc:
            if self._logger:
                self._logger.debug(f"Cache set_json encode failed key={key} reason={exc}")
            raise
        self.set(key, payload, ttl_seconds=ttl_seconds)