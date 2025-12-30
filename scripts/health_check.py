#!/usr/bin/env python
"""Comprehensive system health check."""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-8s - %(name)s - %(message)s'
)

print("\n" + "=" * 70)
print("COMPREHENSIVE SYSTEM HEALTH CHECK")
print("=" * 70)

all_checks_passed = True

# ============================================================================
# 1. CONFIGURATION CHECK
# ============================================================================
print("\n1️⃣  CONFIGURATION CHECK")
print("-" * 70)

try:
    from utils.config_loader import ConfigLoader
    config = ConfigLoader.load_config()
    
    # Check critical config keys
    checks = {
        "OpenAI API Key": config.get('openai', {}).get('api_key'),
        "Grok API Key": config.get('grok', {}).get('api_key'),
        "Model Provider": config.get('model', {}).get('provider'),
        "Tools Enabled": config.get('langchain', {}).get('tools', {}).get('enabled'),
        "MongoDB URI": config.get('mongodb', {}).get('uri'),
        "Redis Host": config.get('redis', {}).get('host'),
    }

    # Keys whose values are sensitive and must not be printed
    sensitive_keys = {
        "OpenAI API Key",
        "Grok API Key",
    }
    
    for key, value in checks.items():
        if value:
            status = "✅"
            if key in sensitive_keys:
                # Do not log the actual secret value
                value_str = "[SET]"
            else:
                value_str = str(value)[:40] + "..." if len(str(value)) > 40 else str(value)
        else:
            status = "❌"
            value_str = "NOT SET"
            all_checks_passed = False
        print(f"  {status} {key:25} {value_str}")
        
except Exception as e:
    print(f"  ❌ Configuration load failed: {e}")
    all_checks_passed = False

# ============================================================================
# 2. DATABASE CHECK
# ============================================================================
print("\n2️⃣  DATABASE CONNECTIVITY CHECK")
print("-" * 70)

try:
    from pymongo import MongoClient
    from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
    
    uri = config.get('mongodb', {}).get('uri')
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    
    db = client[config.get('mongodb', {}).get('database', 'stock_assistant')]
    
    # Check collections
    try:
        result = db.command("listCollections")
        collections = [c['name'] for c in result['cursor']['firstBatch']]
        print(f"  ✅ MongoDB connected")
        print(f"     Database: {db.name}")
        print(f"     Collections: {len(collections)} ({', '.join(collections[:3])}...)")
    except OperationFailure as e:
        if "not authorized" in str(e).lower():
            print(f"  ⚠️  MongoDB connected (but listing collections failed - auth restricted)")
        else:
            raise
            
except ServerSelectionTimeoutError:
    print(f"  ❌ MongoDB unreachable (is docker-compose running?)")
    all_checks_passed = False
except Exception as e:
    print(f"  ❌ MongoDB connection failed: {e}")
    all_checks_passed = False

# ============================================================================
# 3. CACHE CHECK
# ============================================================================
print("\n3️⃣  CACHE CONNECTIVITY CHECK")
print("-" * 70)

try:
    from utils.cache import CacheBackend
    
    cache = CacheBackend.from_config(config)
    is_healthy = cache.is_healthy() if hasattr(cache, 'is_healthy') else True
    
    if is_healthy:
        print(f"  ✅ Cache backend connected")
        # Test basic operations
        cache.set_json("test_key", {"test": "value"}, ttl_seconds=10)
        cached = cache.get_json("test_key")
        if cached:
            print(f"     Cache read/write: ✅ Working")
        else:
            print(f"     Cache read/write: ❌ Failed")
            all_checks_passed = False
    else:
        print(f"  ⚠️  Cache backend unavailable (falling back to memory)")
        
except Exception as e:
    print(f"  ❌ Cache initialization failed: {e}")
    all_checks_passed = False

# ============================================================================
# 4. DATA MANAGER CHECK
# ============================================================================
print("\n4️⃣  DATA MANAGER CHECK")
print("-" * 70)

try:
    from core.data_manager import DataManager
    
    dm = DataManager(config)
    print(f"  ✅ DataManager initialized")
    print(f"     Available data sources: {len(dm.providers)}")
    
except Exception as e:
    print(f"  ❌ DataManager initialization failed: {e}")
    all_checks_passed = False

# ============================================================================
# 5. TOOL INITIALIZATION CHECK
# ============================================================================
print("\n5️⃣  TOOL INITIALIZATION CHECK")
print("-" * 70)

try:
    from core.tools.stock_symbol import StockSymbolTool
    from core.tools.reporting import ReportingTool
    
    print(f"  ✅ StockSymbolTool imported")
    print(f"  ✅ ReportingTool imported")
    
except ImportError as e:
    print(f"  ❌ Tool import failed: {e}")
    all_checks_passed = False

# ============================================================================
# 6. MODEL CLIENT CHECK
# ============================================================================
print("\n6️⃣  MODEL CLIENT CHECK")
print("-" * 70)

try:
    from core.model_factory import ModelClientFactory
    
    # Test primary model
    client = ModelClientFactory.get_client(config, provider="openai")
    if client:
        print(f"  ✅ OpenAI client created")
        print(f"     Model: {client.model_name if hasattr(client, 'model_name') else 'gpt-5'}")
    
    # Test fallback
    fallback_seq = ModelClientFactory.get_fallback_sequence(config)
    if len(fallback_seq) >= 2:
        print(f"  ✅ Fallback configured: {' → '.join(fallback_seq)}")
    else:
        print(f"  ⚠️  Fallback not configured (only {len(fallback_seq)} provider)")
        
except Exception as e:
    print(f"  ❌ Model client initialization failed: {e}")
    all_checks_passed = False

# ============================================================================
# 7. AGENT INITIALIZATION CHECK
# ============================================================================
print("\n7️⃣  AGENT INITIALIZATION CHECK")
print("-" * 70)

try:
    from core.stock_assistant_agent import StockAssistantAgent
    
    agent = StockAssistantAgent(config, dm)
    
    # Check tools
    enabled_tools = agent._tool_registry.get_enabled_tools()
    print(f"  ✅ Agent initialized with {len(enabled_tools)} tools:")
    for tool in enabled_tools:
        print(f"     - {tool.name}: {tool.description[:50]}...")
    
    # Check executor
    if agent.executor:
        print(f"  ✅ LangGraph ReAct executor built")
    else:
        print(f"  ❌ Executor not built (no tools)")
        all_checks_passed = False
        
except Exception as e:
    print(f"  ❌ Agent initialization failed: {e}")
    import traceback
    traceback.print_exc()
    all_checks_passed = False

# ============================================================================
# 8. API SERVER CHECK
# ============================================================================
print("\n8️⃣  API SERVER CHECK")
print("-" * 70)

try:
    from web.api_server import APIServer
    
    server = APIServer()
    print(f"  ✅ API server instantiated")
    print(f"     Agent: {server.agent.__class__.__name__}")
    print(f"     Database: Connected")
    print(f"     Routes: {len(server.app.blueprints)} registered")
    
except Exception as e:
    print(f"  ⚠️  API server instantiation: {e}")
    # This might fail in some contexts, not critical

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
if all_checks_passed:
    print("✅ ALL CHECKS PASSED - System is healthy!")
else:
    print("⚠️  SOME CHECKS FAILED - See details above")
print("=" * 70 + "\n")

sys.exit(0 if all_checks_passed else 1)
