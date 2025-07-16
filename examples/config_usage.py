"""
Example usage of the enhanced ConfigLoader with environment variables.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.config_loader import ConfigLoader


def main():
    """Example of how to use the enhanced configuration loader."""
    
    # Load configuration with environment variable overrides
    config = ConfigLoader.load_config()
    
    # Validate configuration
    if not ConfigLoader.validate_config(config):
        print("⚠️  Configuration validation failed - some required values are missing")
    
    # Access configuration values using dot notation
    openai_key = ConfigLoader.get_config_value(config, 'openai.api_key', 'not-set')
    model = ConfigLoader.get_config_value(config, 'openai.model', 'gpt-3.5-turbo')
    log_level = ConfigLoader.get_config_value(config, 'app.log_level', 'INFO')
    
    print("🔧 Configuration loaded successfully!")
    print(f"📡 OpenAI API Key: {'***' + openai_key[-4:] if len(openai_key) > 4 else 'not-set'}")
    print(f"🤖 Model: {model}")
    print(f"📝 Log Level: {log_level}")
    
    # Print full configuration (be careful not to log sensitive data in production)
    print("\n📋 Full Configuration Structure:")
    for section, values in config.items():
        print(f"  {section}:")
        if isinstance(values, dict):
            for key, value in values.items():
                if 'key' in key.lower() and isinstance(value, str) and len(value) > 4:
                    # Mask sensitive keys
                    print(f"    {key}: ***{value[-4:]}")
                else:
                    print(f"    {key}: {value}")
        else:
            print(f"    {values}")


if __name__ == "__main__":
    main()
