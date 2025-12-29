#!/usr/bin/env python3
"""Debug script to find where the API key mismatch is coming from."""

import os
import sys

print("=" * 80)
print("DEBUG: API KEY SOURCE INVESTIGATION")
print("=" * 80)

# Step 1: Check .env before loading it
print("\n[Step 1] Checking .env file content:")
print("-" * 80)
with open('.env', 'r') as f:
    for line in f:
        if 'OPENAI_API_KEY' in line:
            # Show just the first and last 20 chars
            parts = line.split('=')
            if len(parts) == 2:
                key_value = parts[1].strip()
                print(f"FILE:  OPENAI_API_KEY={key_value[:20]}...{key_value[-20:]}")

# Step 2: Load .env
print("\n[Step 2] Loading .env with dotenv:")
print("-" * 80)
from dotenv import load_dotenv
load_dotenv()

env_key_raw = os.getenv('OPENAI_API_KEY', '')
print(f"MEMRY: OPENAI_API_KEY={env_key_raw[:20]}...{env_key_raw[-20:]}")

# Step 3: Load ConfigLoader
print("\n[Step 3] Loading ConfigLoader:")
print("-" * 80)
from utils.config_loader import ConfigLoader

# Trace the loading steps
print("Calling ConfigLoader.load_config()...")
config = ConfigLoader.load_config()

config_key = config.get('openai', {}).get('api_key', '')
print(f"CONFIG: openai.api_key={config_key[:20]}...{config_key[-20:]}")

# Step 4: Compare
print("\n[Step 4] Comparison:")
print("-" * 80)

if env_key_raw == config_key:
    print("✅ MATCH: .env and loaded config are IDENTICAL")
elif config_key == "your-openai-api-key-here":
    print("❌ ERROR: ConfigLoader loaded placeholder, not from .env")
    print("   This means .env env var was NOT applied")
else:
    print("❌ MISMATCH: .env and loaded config are DIFFERENT")
    print(f"\nDETAILS:")
    print(f"  From .env:    {env_key_raw[:30]}...{env_key_raw[-20:]}")
    print(f"  From config:  {config_key[:30]}...{config_key[-20:]}")
    
    # Try to identify the mystery key
    if 'usYTqinoFaZs' in config_key:
        print("\n  ⚠️  WARNING: Detected 'usYTqinoFaZs' key (from docs/previous investigation)")
        print("  This key should NOT be loaded from anywhere!")
        print("  Check for: cached Python modules, previous environment state, etc.")

# Step 5: Check environment override mode
print("\n[Step 5] ConfigLoader Override Mode:")
print("-" * 80)
override_mode = os.getenv('CONFIG_ENV_OVERRIDE_MODE', 'default')
print(f"CONFIG_ENV_OVERRIDE_MODE: {override_mode}")
print(f"APP_ENV: {os.getenv('APP_ENV', 'not set')}")

print("\n" + "=" * 80)
print("END DEBUG")
print("=" * 80)
