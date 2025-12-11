"""
Cache Patterns and Best Practices

Demonstrates cache key helpers, TTL strategies, and invalidation patterns
used throughout the service layer.

Reference: backend-python.instructions.md § Cache Backend, § Cache Invalidation Patterns
"""

import random
import threading
import time
from typing import Any, Dict, Optional

# Mock CacheBackend for demonstration
class MockCache:
    """Simple in-memory cache for demonstration."""
    def __init__(self):
        self.data = {}
        self.expiry = {}
    
    def get_json(self, key: str) -> Optional[Dict]:
        if key in self.data:
            if key in self.expiry and time.time() > self.expiry[key]:
                del self.data[key]
                del self.expiry[key]
                return None
            return self.data[key]
        return None
    
    def set_json(self, key: str, value: Dict, ttl_seconds: int = 300) -> None:
        self.data[key] = value
        self.expiry[key] = time.time() + ttl_seconds
    
    def delete(self, key: str) -> None:
        self.data.pop(key, None)
        self.expiry.pop(key, None)


# ============================================================================
# PATTERN 1: Cache Key Helpers (Private Methods)
# ============================================================================

class WorkspaceServiceCacheExample:
    """Demonstrates cache key pattern used in services."""
    
    # TTL constants as class attributes
    WORKSPACE_CACHE_TTL = 300  # 5 minutes
    WORKSPACE_LIST_CACHE_TTL = 180  # 3 minutes
    
    def __init__(self, cache: Optional[MockCache] = None):
        self.cache = cache
    
    def _workspace_cache_key(self, workspace_id: str) -> str:
        """
        Generate cache key for single workspace.
        
        Pattern: <entity>:<id>
        """
        return f"workspace:{workspace_id}"
    
    def _workspace_list_cache_key(self, user_id: str, filters: str = "") -> str:
        """
        Generate cache key for workspace lists.
        
        Pattern: <entity>_list:<owner_id>:<filters_hash>
        """
        filter_suffix = f":{filters}" if filters else ""
        return f"workspace_list:{user_id}{filter_suffix}"
    
    def get_workspace(self, workspace_id: str, *, use_cache: bool = True) -> Optional[Dict]:
        """Fetch workspace with caching."""
        cache_key = self._workspace_cache_key(workspace_id)
        
        # Check cache first
        if use_cache and self.cache:
            cached = self.cache.get_json(cache_key)
            if cached:
                return cached
        
        # Simulate database fetch
        workspace = {"id": workspace_id, "name": "Test Workspace"}
        
        # Populate cache
        if use_cache and self.cache:
            self.cache.set_json(cache_key, workspace, ttl_seconds=self.WORKSPACE_CACHE_TTL)
        
        return workspace
    
    def invalidate_workspace(self, workspace_id: str) -> None:
        """
        Invalidate all cached data for a workspace.
        
        Call this when workspace data is updated.
        """
        if not self.cache:
            return
        
        self.cache.delete(self._workspace_cache_key(workspace_id))
        # Could also invalidate related list caches here


# ============================================================================
# PATTERN 2: TTL Strategy by Data Type
# ============================================================================

def demonstrate_ttl_strategies():
    """Show different TTL values for different data types."""
    print("=" * 60)
    print("TTL STRATEGY BY DATA TYPE")
    print("=" * 60)
    
    ttl_config = {
        "price_data": 60,           # 1 minute (high volatility)
        "historical_data": 3600,    # 1 hour (stable historical)
        "fundamental_data": 86400,  # 24 hours (quarterly updates)
        "technical_data": 900,      # 15 minutes (recalculated frequently)
        "reports": 43200,           # 12 hours (generated reports)
        "user_profile": 300,        # 5 minutes (balance freshness/load)
        "symbol_metadata": 86400,   # 24 hours (rarely changes)
    }
    
    print("\nRecommended TTL values:")
    for data_type, ttl in ttl_config.items():
        hours = ttl / 3600
        minutes = ttl / 60
        if hours >= 1:
            print(f"  {data_type:20} {ttl:6}s ({hours:.1f} hours)")
        else:
            print(f"  {data_type:20} {ttl:6}s ({minutes:.0f} minutes)")
    
    print("\n✅ Guidelines:")
    print("  - Real-time data: 30-60 seconds")
    print("  - User-facing data: 3-5 minutes")
    print("  - Reference data: 1-24 hours")
    print("  - Use jitter (+/- 10%) to prevent mass expiry")


# ============================================================================
# PATTERN 3: Cache Invalidation on Updates
# ============================================================================

class UserServiceCacheExample:
    """Demonstrates cache invalidation patterns."""
    
    USER_CACHE_TTL = 300
    PROFILE_CACHE_TTL = 180
    DASHBOARD_CACHE_TTL = 120
    
    def __init__(self, cache: Optional[MockCache] = None):
        self.cache = cache
    
    def _user_cache_key(self, user_id: str) -> str:
        return f"user:{user_id}"
    
    def _profile_cache_key(self, user_id: str) -> str:
        return f"user_profile:{user_id}"
    
    def _dashboard_cache_key(self, user_id: str) -> str:
        return f"user_dashboard:{user_id}"
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict:
        """
        Update user and invalidate related caches.
        
        Pattern: Write-through cache invalidation
        """
        # Simulate database update
        user = {"id": user_id, **updates}
        
        # Invalidate all related caches
        self.invalidate_user_cache(user_id)
        
        return user
    
    def invalidate_user_cache(self, user_id: str) -> None:
        """
        Invalidate all cached data for a user.
        
        Pattern: Clear all entity-related cache keys
        """
        if not self.cache:
            return
        
        # Clear all user-related caches
        self.cache.delete(self._user_cache_key(user_id))
        self.cache.delete(self._profile_cache_key(user_id))
        self.cache.delete(self._dashboard_cache_key(user_id))
        
        print(f"✅ Invalidated all caches for user {user_id}")


# ============================================================================
# PATTERN 4: Cache Storm Prevention with Lock + Jitter
# ============================================================================

class CacheStormPreventionExample:
    """Demonstrates cache storm prevention with threading.Lock and TTL jitter."""
    
    BASE_TTL = 300  # 5 minutes
    _fetch_locks: Dict[str, threading.Lock] = {}
    
    def __init__(self, cache: Optional[MockCache] = None):
        self.cache = cache
    
    def get_expensive_data(self, key: str, *, use_cache: bool = True) -> Dict:
        """
        Fetch expensive data with cache storm prevention.
        
        Problem: Many concurrent requests hit uncached data simultaneously
        Solution: Use lock to ensure only one thread fetches
        """
        cache_key = f"expensive:{key}"
        
        # Check cache first
        if use_cache and self.cache:
            cached = self.cache.get_json(cache_key)
            if cached:
                return cached
        
        # Get or create lock for this key
        lock = self._fetch_locks.setdefault(key, threading.Lock())
        
        with lock:
            # Double-check cache after acquiring lock
            if use_cache and self.cache:
                cached = self.cache.get_json(cache_key)
                if cached:  # Another thread populated cache
                    return cached
            
            # Only one thread reaches here - fetch from source
            print(f"⏳ Fetching expensive data for key={key} (only one thread does this)")
            time.sleep(0.5)  # Simulate expensive operation
            data = {"key": key, "value": "expensive_result"}
            
            if use_cache and self.cache:
                # Add jitter to TTL to prevent synchronized expiry
                jitter = random.randint(0, 60)  # 0-60 seconds
                ttl = self.BASE_TTL + jitter
                self.cache.set_json(cache_key, data, ttl_seconds=ttl)
                print(f"✅ Cached with TTL={ttl}s (base={self.BASE_TTL}s + jitter={jitter}s)")
            
            return data


# ============================================================================
# PATTERN 5: Cache Warming on Service Initialization
# ============================================================================

class CacheWarmingExample:
    """Demonstrates cache warming to prevent cold start issues."""
    
    def __init__(self, cache: Optional[MockCache] = None):
        self.cache = cache
        self._warm_critical_caches()
    
    def _warm_critical_caches(self) -> None:
        """
        Pre-populate frequently accessed data on service startup.
        
        Use for:
        - Reference data (symbol lists, categories)
        - Default configurations
        - Popular user data (top 10% active users)
        """
        if not self.cache:
            return
        
        print("🔥 Warming critical caches...")
        
        # Example: Warm symbol metadata cache
        critical_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        for symbol in critical_symbols:
            data = {"symbol": symbol, "name": f"{symbol} Corp", "sector": "Technology"}
            self.cache.set_json(f"symbol:{symbol}", data, ttl_seconds=3600)
        
        print(f"✅ Warmed {len(critical_symbols)} symbol caches")


# ============================================================================
# DEMONSTRATIONS
# ============================================================================

def demonstrate_cache_patterns():
    """Run all cache pattern demonstrations."""
    
    print("=" * 60)
    print("CACHE PATTERNS DEMONSTRATION")
    print("=" * 60)
    
    cache = MockCache()
    
    # Pattern 1: Cache Key Helpers
    print("\n1. CACHE KEY HELPERS")
    print("-" * 60)
    service = WorkspaceServiceCacheExample(cache)
    ws = service.get_workspace("ws123")
    print(f"Fetched workspace: {ws}")
    ws_cached = service.get_workspace("ws123")
    print(f"Fetched from cache: {ws_cached}")
    
    # Pattern 2: TTL Strategies
    print("\n2. TTL STRATEGIES")
    print("-" * 60)
    demonstrate_ttl_strategies()
    
    # Pattern 3: Cache Invalidation
    print("\n3. CACHE INVALIDATION")
    print("-" * 60)
    user_service = UserServiceCacheExample(cache)
    user_service.update_user("user123", {"name": "Alice"})
    
    # Pattern 4: Cache Storm Prevention
    print("\n4. CACHE STORM PREVENTION")
    print("-" * 60)
    storm_service = CacheStormPreventionExample(cache)
    
    # Simulate 5 concurrent requests
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(storm_service.get_expensive_data, "critical_data") for _ in range(5)]
        results = [f.result() for f in futures]
    print(f"All requests completed, cache hit count: {len([r for r in results if r])}")
    
    # Pattern 5: Cache Warming
    print("\n5. CACHE WARMING")
    print("-" * 60)
    warming_service = CacheWarmingExample(cache)
    
    print("\n" + "=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("✅ Use consistent cache key patterns: <entity>:<id>")
    print("✅ Set TTL based on data volatility")
    print("✅ Invalidate caches on data updates")
    print("✅ Prevent cache storms with locks + jitter")
    print("✅ Warm critical caches on startup")


if __name__ == "__main__":
    demonstrate_cache_patterns()
