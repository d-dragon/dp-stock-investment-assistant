"""
Clear all Python-level caches and Redis to force fresh configuration loading.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("CLEARING ALL CACHES")
print("=" * 60)

# 1. Clear ModelClientFactory cache
print("\n1. Clearing ModelClientFactory._CACHE...")
try:
    from core.model_factory import ModelClientFactory
    ModelClientFactory._CACHE.clear()
    print("   ✓ ModelClientFactory._CACHE cleared")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 2. Clear langchain_adapter cache
print("\n2. Clearing langchain_adapter._PROMPT_CACHE...")
try:
    from core import langchain_adapter
    langchain_adapter._PROMPT_CACHE.clear()
    print("   ✓ langchain_adapter._PROMPT_CACHE cleared")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 3. Clear Redis and in-memory cache
print("\n3. Clearing CacheBackend (Redis + in-memory)...")
try:
    from utils.cache import CacheBackend
    from utils.config_loader import ConfigLoader
    
    config = ConfigLoader.load_config()
    cache = CacheBackend.from_config(config)
    
    # Clear all OpenAI config keys
    cache_keys = ["openai_config:api_key", "openai_config:model", "openai_config:model_name", 
                  "openai_config:temperature", "openai_config:max_tokens"]
    
    for key in cache_keys:
        cache.delete(key)
        print(f"   ✓ Deleted {key}")
    
    # Also flush in-memory dict directly
    cache._memory.clear()
    print("   ✓ In-memory cache dict cleared")
    
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("✓ ALL CACHES CLEARED")
print("=" * 60)
print("\nNow restart your app:")
print("  python src/main.py --mode cli")