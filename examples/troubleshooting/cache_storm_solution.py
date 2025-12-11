"""
Cache Storm Prevention with Threading Lock and TTL Jitter

Demonstrates the thundering herd problem and solution using threading.Lock
to prevent multiple concurrent requests from fetching the same uncached data.

Reference: backend-python.instructions.md § Pitfalls > Cache Miss Storms
"""

import random
import threading
import time
from typing import Any, Dict, Optional


# ============================================================================
# PROBLEM: Cache Miss Storm (Thundering Herd)
# ============================================================================

class CacheStormProblem:
    """Demonstrates the cache storm problem WITHOUT protection."""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.fetch_count = 0  # Track how many times we hit the database
    
    def get_data(self, key: str) -> Dict:
        """Fetch data WITHOUT storm protection."""
        cache_key = f"data:{key}"
        
        # Check cache
        if cache_key in self.cache:
            print(f"  [Thread {threading.current_thread().name}] Cache HIT")
            return self.cache[cache_key]
        
        # Cache miss - fetch from database
        print(f"  [Thread {threading.current_thread().name}] Cache MISS → fetching from database")
        self.fetch_count += 1
        time.sleep(0.5)  # Simulate expensive database query
        
        data = {"key": key, "value": f"expensive_result_{self.fetch_count}"}
        
        # Store in cache
        self.cache[cache_key] = data
        return data


def demonstrate_cache_storm():
    """Show cache storm with 10 concurrent requests."""
    print("=" * 60)
    print("PROBLEM: CACHE MISS STORM")
    print("=" * 60)
    
    service = CacheStormProblem()
    
    print("\n🔥 Simulating 10 concurrent requests for uncached data...")
    
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(service.get_data, "critical_data") for _ in range(10)]
        results = [f.result() for f in futures]
    
    print(f"\n❌ RESULT: Database fetched {service.fetch_count} times")
    print("   Problem: All 10 threads hit database simultaneously!")
    print("   Impact: Database overload, slow response, wasted resources")


# ============================================================================
# SOLUTION: Lock-Based Protection with TTL Jitter
# ============================================================================

class CacheStormSolution:
    """
    Prevents cache storm using threading.Lock pattern.
    
    Key improvements:
    1. Lock per cache key (only blocks competing requests)
    2. Double-check cache after acquiring lock
    3. TTL jitter to prevent synchronized expiry
    """
    
    BASE_TTL = 300  # 5 minutes base TTL
    _fetch_locks: Dict[str, threading.Lock] = {}  # Class-level lock dictionary
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_expiry: Dict[str, float] = {}
        self.fetch_count = 0
    
    def get_data(self, key: str, *, use_cache: bool = True) -> Dict:
        """
        Fetch data WITH storm protection.
        
        Pattern:
        1. Check cache first (no lock needed)
        2. Acquire lock if cache miss
        3. Double-check cache (another thread may have populated)
        4. Fetch only if still missing (only one thread does this)
        5. Add TTL jitter to prevent mass expiry
        """
        cache_key = f"data:{key}"
        
        # Step 1: Check cache first (fast path, no lock)
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                print(f"  [Thread {threading.current_thread().name}] Cache HIT")
                return cached
        
        # Step 2: Cache miss - get or create lock for this key
        lock = self._fetch_locks.setdefault(key, threading.Lock())
        
        # Step 3: Acquire lock (only competing threads wait here)
        with lock:
            # Step 4: Double-check cache after acquiring lock
            if use_cache:
                cached = self._get_from_cache(cache_key)
                if cached:
                    print(f"  [Thread {threading.current_thread().name}] Cache HIT after lock (another thread populated)")
                    return cached
            
            # Step 5: Only one thread reaches here - fetch from database
            print(f"  [Thread {threading.current_thread().name}] Cache MISS → fetching from database (ONLY ONE THREAD)")
            self.fetch_count += 1
            time.sleep(0.5)  # Simulate expensive database query
            
            data = {"key": key, "value": f"expensive_result_{self.fetch_count}"}
            
            # Step 6: Store in cache with TTL jitter
            if use_cache:
                jitter = random.randint(0, 60)  # 0-60 seconds
                ttl = self.BASE_TTL + jitter
                self._set_in_cache(cache_key, data, ttl)
                print(f"  [Thread {threading.current_thread().name}] Cached with TTL={ttl}s (base={self.BASE_TTL}s + jitter={jitter}s)")
            
            return data
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get from cache, checking expiry."""
        if key in self.cache:
            if time.time() < self.cache_expiry.get(key, 0):
                return self.cache[key]
            else:
                # Expired - clean up
                del self.cache[key]
                del self.cache_expiry[key]
        return None
    
    def _set_in_cache(self, key: str, value: Dict, ttl_seconds: int) -> None:
        """Store in cache with expiry."""
        self.cache[key] = value
        self.cache_expiry[key] = time.time() + ttl_seconds


def demonstrate_cache_storm_solution():
    """Show cache storm protection with locks."""
    print("\n" + "=" * 60)
    print("SOLUTION: LOCK-BASED PROTECTION")
    print("=" * 60)
    
    service = CacheStormSolution()
    
    print("\n✅ Simulating 10 concurrent requests with protection...")
    
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(service.get_data, "critical_data") for _ in range(10)]
        results = [f.result() for f in futures]
    
    print(f"\n✅ RESULT: Database fetched {service.fetch_count} time(s)")
    print("   Solution: Only ONE thread fetched, others waited for cache!")
    print("   Impact: Database protected, faster response, efficient resources")


# ============================================================================
# ALTERNATIVE: Cache Warming on Initialization
# ============================================================================

def demonstrate_cache_warming():
    """Show cache warming to prevent cold start storms."""
    print("\n" + "=" * 60)
    print("ALTERNATIVE: CACHE WARMING")
    print("=" * 60)
    
    print("\nPre-populate frequently accessed data on service startup:")
    print("""
class WorkspaceService:
    def __init__(self, cache=None):
        self.cache = cache
        self._warm_critical_caches()
    
    def _warm_critical_caches(self):
        '''Warm cache for top 10% active users.'''
        if not self.cache:
            return
        
        # Fetch frequently accessed workspaces
        popular_workspace_ids = get_popular_workspaces()
        
        for ws_id in popular_workspace_ids:
            workspace = self._fetch_from_db(ws_id)
            self.cache.set_json(f'workspace:{ws_id}', workspace, ttl=300)
    """)
    
    print("\n✅ Benefits:")
    print("  - Prevents cold start cache storms")
    print("  - Improves first-request latency")
    print("  - Good for reference data (symbols, categories)")


# ============================================================================
# BEST PRACTICES SUMMARY
# ============================================================================

def show_best_practices():
    """Display cache storm prevention best practices."""
    print("\n" + "=" * 60)
    print("BEST PRACTICES")
    print("=" * 60)
    
    practices = [
        ("Use Lock per Key", "self._fetch_locks.setdefault(key, threading.Lock())"),
        ("Double-Check Pattern", "Check cache again after acquiring lock"),
        ("TTL Jitter", "Add random 0-60s to TTL to prevent synchronized expiry"),
        ("Cache Warming", "Pre-populate critical data on service initialization"),
        ("Request Coalescing", "Single lock ensures only one fetch per key"),
        ("Monitor Cache Hits", "Track hit/miss ratio to identify storm patterns"),
    ]
    
    for i, (practice, detail) in enumerate(practices, 1):
        print(f"\n{i}. {practice}")
        print(f"   {detail}")


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CACHE STORM PREVENTION")
    print("=" * 60)
    print("\nThe 'thundering herd' problem occurs when many concurrent requests")
    print("hit uncached data simultaneously, overwhelming the database.\n")
    
    # Show the problem
    demonstrate_cache_storm()
    
    # Show the solution
    demonstrate_cache_storm_solution()
    
    # Show alternative approach
    demonstrate_cache_warming()
    
    # Best practices
    show_best_practices()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ Use threading.Lock to prevent concurrent fetches")
    print("✅ Double-check cache after acquiring lock")
    print("✅ Add TTL jitter (0-60s) to prevent synchronized expiry")
    print("✅ Warm critical caches on service initialization")
    print("✅ Monitor cache metrics to detect storm patterns")
    
    print("\n📖 Reference: backend-python.instructions.md")
    print("   § Pitfalls and Gotchas > Cache Miss Storms")
