"""
Model Fallback Configuration and Debugging

Demonstrates how to configure and troubleshoot model fallback behavior
when the primary AI model fails.

Reference: backend-python.instructions.md § Model Factory > Fallback Support
"""

from typing import List
from unittest.mock import MagicMock


# ============================================================================
# STEP 1: Verify config.yaml Settings
# ============================================================================

def show_required_config():
    """Display required configuration for model fallback."""
    
    print("=" * 60)
    print("REQUIRED CONFIGURATION (config.yaml)")
    print("=" * 60)
    
    config_example = """
model:
  provider: openai             # Primary provider
  allow_fallback: true         # ← Must be true
  fallback_order:              # ← Must have 2+ providers
    - openai
    - grok

openai:
  api_key: ${OPENAI_API_KEY}   # From environment variable
  model: gpt-4

grok:
  api_key: ${GROK_API_KEY}     # Must be configured
  base_url: https://api.x.ai/v1
  model: grok-beta
    """
    
    print(config_example)
    
    print("\n✅ Checklist:")
    print("  [  ] model.allow_fallback = true")
    print("  [  ] model.fallback_order has 2+ providers")
    print("  [  ] All providers in fallback_order have API keys")
    print("  [  ] Environment variables set (OPENAI_API_KEY, GROK_API_KEY)")


# ============================================================================
# STEP 2: Test Fallback Sequence Retrieval
# ============================================================================

def test_fallback_sequence():
    """Test that fallback sequence is correctly retrieved from config."""
    
    print("\n" + "=" * 60)
    print("TEST FALLBACK SEQUENCE")
    print("=" * 60)
    
    # Simulate config loading and fallback sequence retrieval
    print("\nTest Script:")
    print("""
from core.model_factory import ModelClientFactory
from utils.config_loader import ConfigLoader

config = ConfigLoader.load_config()
sequence = ModelClientFactory.get_fallback_sequence(config)
print(f"Fallback sequence: {sequence}")

# Expected output: ["openai", "grok"]
# If empty list: Check config['model']['allow_fallback'] is true
    """)
    
    # Mock example
    mock_config = {
        'model': {
            'provider': 'openai',
            'allow_fallback': True,
            'fallback_order': ['openai', 'grok']
        }
    }
    
    # Simulate retrieval
    allow_fallback = mock_config.get('model', {}).get('allow_fallback', False)
    fallback_order = mock_config.get('model', {}).get('fallback_order', [])
    
    print(f"\nConfig values:")
    print(f"  allow_fallback: {allow_fallback}")
    print(f"  fallback_order: {fallback_order}")
    
    if allow_fallback and len(fallback_order) >= 2:
        print(f"\n✅ Fallback configured correctly: {fallback_order}")
    else:
        print(f"\n❌ Fallback NOT configured:")
        if not allow_fallback:
            print("  - allow_fallback is false")
        if len(fallback_order) < 2:
            print(f"  - fallback_order has only {len(fallback_order)} provider(s)")


# ============================================================================
# STEP 3: Check Agent Logs for Fallback Attempts
# ============================================================================

def show_expected_log_messages():
    """Display expected log messages when fallback is triggered."""
    
    print("\n" + "=" * 60)
    print("EXPECTED LOG MESSAGES")
    print("=" * 60)
    
    logs = [
        ("WARNING", "Primary model openai:gpt-4 failed: RateLimitError (429)"),
        ("INFO", "Attempting fallback to provider=grok model=grok-beta"),
        ("INFO", "Fallback successful with provider=grok"),
    ]
    
    print("\nWhen fallback works correctly, you should see:")
    for level, message in logs:
        print(f"  {level:8} - {message}")
    
    print("\nIf NO fallback messages appear:")
    print("  ❌ Check that StockAgent uses ModelClientFactory.get_fallback_sequence()")
    print("  ❌ Verify exception handling triggers fallback logic")
    print("  ❌ Ensure model provider API keys are valid")


# ============================================================================
# STEP 4: Clear Model Client Cache
# ============================================================================

def show_cache_clearing():
    """Show how to clear model client cache when switching providers."""
    
    print("\n" + "=" * 60)
    print("CLEAR MODEL CLIENT CACHE")
    print("=" * 60)
    
    print("\nModel clients are cached by key: {provider}:{model_name}")
    print("Examples: 'openai:gpt-4', 'grok:grok-beta'")
    
    print("\nClear all cached clients:")
    print("""
from core.model_factory import ModelClientFactory
ModelClientFactory.clear_cache()
    """)
    
    print("\nClear specific provider:")
    print("""
ModelClientFactory.clear_cache(provider="openai")
    """)
    
    print("\n✅ When to clear cache:")
    print("  - After changing API keys in config")
    print("  - When testing fallback behavior")
    print("  - After updating model names in config")


# ============================================================================
# STEP 5: Test Fallback Manually
# ============================================================================

def show_manual_fallback_test():
    """Demonstrate manual fallback testing."""
    
    print("\n" + "=" * 60)
    print("MANUAL FALLBACK TEST")
    print("=" * 60)
    
    test_script = """
from core.agent import StockAgent
from core.data_manager import DataManager
from utils.config_loader import ConfigLoader

# Load config
config = ConfigLoader.load_config()
dm = DataManager(config)
agent = StockAgent(config, dm)

# Temporarily break primary provider (wrong API key)
config['openai']['api_key'] = 'invalid_key'

# This should trigger fallback to grok
try:
    response = agent.process_query("What is the price of AAPL?")
    print(f"✅ Response received (via fallback): {response[:100]}...")
except Exception as e:
    print(f"❌ Fallback failed: {e}")
    """
    
    print("\nTest script:")
    print(test_script)
    
    print("\n✅ Expected behavior:")
    print("  1. Primary model (openai) fails with invalid API key")
    print("  2. Agent logs 'Attempting fallback to provider=grok'")
    print("  3. Request succeeds with fallback model")
    
    print("\n❌ If fallback fails:")
    print("  - Check grok API key is valid")
    print("  - Verify grok configuration in config.yaml")
    print("  - Review agent logs for error details")


# ============================================================================
# STEP 6: Common Configuration Issues
# ============================================================================

def show_common_issues():
    """Display common fallback configuration issues."""
    
    print("\n" + "=" * 60)
    print("COMMON CONFIGURATION ISSUES")
    print("=" * 60)
    
    issues = [
        {
            "issue": "allow_fallback: false",
            "symptom": "Fallback never triggers, requests fail immediately",
            "fix": "Set model.allow_fallback: true in config.yaml"
        },
        {
            "issue": "fallback_order empty or single provider",
            "symptom": "get_fallback_sequence() returns empty list or [primary_only]",
            "fix": "Add 2+ providers to model.fallback_order: [openai, grok]"
        },
        {
            "issue": "Fallback provider API key missing",
            "symptom": "Fallback attempt fails with authentication error",
            "fix": "Set GROK_API_KEY environment variable or in .env"
        },
        {
            "issue": "Fallback provider not configured",
            "symptom": "KeyError when accessing config['grok']",
            "fix": "Add grok section to config.yaml with api_key, base_url, model"
        },
        {
            "issue": "Model client cache stale",
            "symptom": "Config changes not reflected, old API key used",
            "fix": "Call ModelClientFactory.clear_cache() after config changes"
        },
    ]
    
    for i, item in enumerate(issues, 1):
        print(f"\n{i}. {item['issue']}")
        print(f"   Symptom: {item['symptom']}")
        print(f"   Fix: {item['fix']}")


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MODEL FALLBACK DEBUGGING GUIDE")
    print("=" * 60)
    print("\nThis guide helps configure and troubleshoot AI model fallback")
    print("when the primary model fails (rate limits, API errors, etc.).\n")
    
    show_required_config()
    test_fallback_sequence()
    show_expected_log_messages()
    show_cache_clearing()
    show_manual_fallback_test()
    show_common_issues()
    
    print("\n" + "=" * 60)
    print("DEBUGGING CHECKLIST")
    print("=" * 60)
    print("[  ] 1. config.yaml has allow_fallback: true")
    print("[  ] 2. fallback_order lists 2+ providers")
    print("[  ] 3. All provider API keys configured")
    print("[  ] 4. get_fallback_sequence() returns expected list")
    print("[  ] 5. Agent logs show 'Attempting fallback' messages")
    print("[  ] 6. Model client cache cleared after config changes")
    print("[  ] 7. Manual test with broken primary succeeds via fallback")
    
    print("\n✅ Quick verification command:")
    print("""
python -c "
from core.model_factory import ModelClientFactory
from utils.config_loader import ConfigLoader
config = ConfigLoader.load_config()
print('Fallback enabled:', config.get('model', {}).get('allow_fallback'))
print('Fallback sequence:', ModelClientFactory.get_fallback_sequence(config))
"
    """)
