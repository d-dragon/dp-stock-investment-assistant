"""
Configuration loader utility with environment variable support.
"""

import os
import yaml
import logging
from typing import Dict, Any, Union
from pathlib import Path
from dotenv import load_dotenv


class ConfigLoader:
    """Utility class for loading configuration files with environment variable override support."""
    
    @staticmethod
    def load_config(config_path: str = None, load_env: bool = True) -> Dict[str, Any]:
        """Load configuration from YAML file with environment variable overrides.
        
        Args:
            config_path: Path to config file. If None, uses default path.
            load_env: Whether to load .env file and apply environment variable overrides.
            
        Returns:
            Configuration dictionary with environment variable overrides applied
        """
        logger = logging.getLogger(__name__)
        
        # Load .env file if requested
        if load_env:
            ConfigLoader._load_env_file()
        
        if config_path is None:
            # Default config path
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"
        
        try:
            if not os.path.exists(config_path):
                logger.warning(f"Config file not found at {config_path}, using defaults with env overrides")
                config = ConfigLoader._get_default_config()
            else:
                with open(config_path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {config_path}")
            
            # Apply environment variable overrides
            if load_env:
                config = ConfigLoader._apply_env_overrides(config)
                logger.info("Environment variable overrides applied")
            
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.info("Using default configuration with env overrides")
            config = ConfigLoader._get_default_config()
            if load_env:
                config = ConfigLoader._apply_env_overrides(config)
            return config
    
    @staticmethod
    def _load_env_file() -> None:
        """Load environment variables from .env file."""
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / ".env"
        
        if env_path.exists():
            load_dotenv(env_path)
            logging.getLogger(__name__).info(f"Loaded environment variables from {env_path}")
        else:
            logging.getLogger(__name__).debug("No .env file found, using system environment variables only")
    
    @staticmethod
    def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration.
        
        Args:
            config: Base configuration dictionary
            
        Returns:
            Configuration with environment variable overrides applied
        """
        env_mappings = {
            # OpenAI settings
            'OPENAI_API_KEY': ('openai', 'api_key'),
            'OPENAI_MODEL': ('openai', 'model'),
            'OPENAI_MAX_TOKENS': ('openai', 'max_tokens'),
            'OPENAI_TEMPERATURE': ('openai', 'temperature'),
            # Unified model section (new)
            'MODEL_PROVIDER': ('model', 'provider'),
            'MODEL_NAME': ('model', 'name'),
            'MODEL_TEMPERATURE': ('model', 'temperature'),
            'MODEL_MAX_TOKENS': ('model', 'max_tokens'),
            'MODEL_ALLOW_FALLBACK': ('model', 'allow_fallback'),
            'MODEL_FALLBACK_ORDER': ('model', 'fallback_order'),  # comma-separated
            'MODEL_DEBUG_PROMPT': ('model', 'debug_prompt'),
            # Grok specific (placeholder)
            'GROK_API_KEY': ('model', 'grok', 'api_key'),
            'GROK_MODEL': ('model', 'grok', 'model'),
            
            # Financial APIs
            'ALPHA_VANTAGE_API_KEY': ('financial_apis', 'alpha_vantage', 'api_key'),
            'ALPHA_VANTAGE_ENABLED': ('financial_apis', 'alpha_vantage', 'enabled'),
            'YAHOO_FINANCE_ENABLED': ('financial_apis', 'yahoo_finance', 'enabled'),
            
            # App settings
            'APP_LOG_LEVEL': ('app', 'log_level'),
            'APP_CACHE_ENABLED': ('app', 'cache_enabled'),
            'APP_MAX_HISTORY': ('app', 'max_history'),
            
            # Analysis settings
            'ANALYSIS_DEFAULT_PERIOD': ('analysis', 'default_period'),
            'ANALYSIS_DEFAULT_INTERVAL': ('analysis', 'default_interval'),
            
            # Export settings
            'EXPORT_DEFAULT_FORMAT': ('export', 'default_format'),
            'EXPORT_OUTPUT_DIRECTORY': ('export', 'output_directory'),
            'EXPORT_INCLUDE_CHARTS': ('export', 'include_charts'),
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                ConfigLoader._set_nested_value(config, config_path, ConfigLoader._convert_env_value(env_value))
        
        return config
    
    @staticmethod
    def _set_nested_value(config: Dict[str, Any], path: tuple, value: Any) -> None:
        """Set a nested value in the configuration dictionary.
        
        Args:
            config: Configuration dictionary to modify
            path: Tuple representing the nested path (e.g., ('openai', 'api_key'))
            value: Value to set
        """
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    @staticmethod
    def _convert_env_value(value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate Python type.
        
        Args:
            value: String value from environment variable
            
        Returns:
            Converted value with appropriate type
        """
        # Handle boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Handle numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # handle list (fallback order)
        if "," in value:
            parts = [p.strip() for p in value.split(",")]
            if all(parts):
                return parts
        # Return as string if no conversion possible
        return value
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'openai': {
                'api_key': '',
                'model': 'gpt-4',
                'max_tokens': 2000,
                'temperature': 0.7
            },
            'model': {  # new unified model config
                'provider': 'openai',
                'name': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 2000,
                'allow_fallback': True,
                'fallback_order': ['openai', 'grok'],
                'debug_prompt': False,
                'grok': {
                    'api_key': '',
                    'model': 'grok-beta'
                }
            },
            'financial_apis': {
                'yahoo_finance': {
                    'enabled': True
                },
                'alpha_vantage': {
                    'api_key': '',
                    'enabled': False
                }
            },
            'app': {
                'log_level': 'INFO',
                'cache_enabled': True,
                'max_history': 100
            },
            'analysis': {
                'default_period': '1y',
                'default_interval': '1d',
                'sectors_to_track': [
                    'Technology',
                    'Healthcare', 
                    'Financial',
                    'Energy'
                ]
            },
            'export': {
                'default_format': 'pdf',
                'output_directory': 'reports',
                'include_charts': True
            }
        }
    
    @staticmethod
    def get_config_value(config: Dict[str, Any], path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.
        
        Args:
            config: Configuration dictionary
            path: Dot-separated path to the value (e.g., 'openai.api_key')
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        current = config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """Validate that required configuration values are present.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        logger = logging.getLogger(__name__)
        required_paths = [
            'openai.api_key',
            'openai.model'
        ]
        
        is_valid = True
        for path in required_paths:
            value = ConfigLoader.get_config_value(config, path)
            if not value or (isinstance(value, str) and value.strip() == ''):
                logger.warning(f"Required configuration missing or empty: {path}")
                is_valid = False
        
        return is_valid
