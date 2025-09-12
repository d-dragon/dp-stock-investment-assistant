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
                    config = yaml.safe_load(file) or {}   # ensure dict even if YAML is empty
                logger.info(f"Configuration loaded from {config_path}")
            
            # Apply environment overlay (config.{env}.yaml)
            env_name = ConfigLoader._normalize_env_name(
                os.getenv("APP_ENV") or os.getenv("ENV") or os.getenv("STAGE") or "local"
            )
            try:
                env_overlay_path = Path(config_path).with_name(f"config.{env_name}.yaml")
                if env_overlay_path.exists():
                    with open(env_overlay_path, 'r', encoding='utf-8') as f:
                        env_overlay = yaml.safe_load(f) or {}
                    config = ConfigLoader._deep_merge(config, env_overlay)
                    logger.info(f"Applied environment overlay: {env_overlay_path.name}")
                else:
                    logger.debug(f"No environment overlay found for APP_ENV={env_name}")
            except Exception as ex:
                logger.warning(f"Failed to apply environment overlay for {env_name}: {ex}")

            # Apply environment variable overrides
            if load_env:
                config = ConfigLoader._apply_env_overrides(config)
                logger.info("Environment variable overrides applied")

            # Apply cloud secret provider overrides (e.g., Azure Key Vault) if configured
            try:
                config = ConfigLoader._apply_cloud_secret_overrides(config)
            except Exception as ex:
                logger.warning(f"Cloud secret overrides skipped due to error: {ex}")
            
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.info("Using default configuration with env overrides")
            config = ConfigLoader._get_default_config()
            if load_env:
                config = ConfigLoader._apply_env_overrides(config)
            try:
                config = ConfigLoader._apply_cloud_secret_overrides(config)
            except Exception:
                pass
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
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            # OpenAI settings
            'OPENAI_API_KEY': ('openai', 'api_key'),
            'OPENAI_MODEL': ('openai', 'model'),
            'OPENAI_MAX_TOKENS': ('openai', 'max_tokens'),
            'OPENAI_TEMPERATURE': ('openai', 'temperature'),
            # Unified model
            'MODEL_PROVIDER': ('model', 'provider'),
            'MODEL_NAME': ('model', 'name'),
            'MODEL_TEMPERATURE': ('model', 'temperature'),
            'MODEL_MAX_TOKENS': ('model', 'max_tokens'),
            'MODEL_ALLOW_FALLBACK': ('model', 'allow_fallback'),
            'MODEL_FALLBACK_ORDER': ('model', 'fallback_order'),
            'MODEL_DEBUG_PROMPT': ('model', 'debug_prompt'),
            # Grok specific
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
            # Analysis
            'ANALYSIS_DEFAULT_PERIOD': ('analysis', 'default_period'),
            'ANALYSIS_DEFAULT_INTERVAL': ('analysis', 'default_interval'),
            # Export
            'EXPORT_DEFAULT_FORMAT': ('export', 'default_format'),
            'EXPORT_OUTPUT_DIRECTORY': ('export', 'output_directory'),
            'EXPORT_INCLUDE_CHARTS': ('export', 'include_charts'),
            # Database: MongoDB
            'MONGODB_ENABLED': ('database', 'mongodb', 'enabled'),
            'MONGODB_URI': ('database', 'mongodb', 'connection_string'),
            'MONGODB_DB_NAME': ('database', 'mongodb', 'database_name'),
            'MONGODB_USERNAME': ('database', 'mongodb', 'username'),
            'MONGODB_PASSWORD': ('database', 'mongodb', 'password'),
            # Database: Redis
            'REDIS_ENABLED': ('database', 'redis', 'enabled'),
            'REDIS_HOST': ('database', 'redis', 'host'),
            'REDIS_PORT': ('database', 'redis', 'port'),
            'REDIS_DB': ('database', 'redis', 'db'),
            'REDIS_PASSWORD': ('database', 'redis', 'password'),
            'REDIS_SSL': ('database', 'redis', 'ssl'),
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
            'database': {
                'mongodb': {
                    'enabled': False,
                    'connection_string': '',
                    'database_name': '',
                    'username': '',
                    'password': ''
                },
                'redis': {
                    'enabled': False,
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0,
                    'password': '',
                    'ssl': False,
                    'ttl': {
                        'price_data': 60,
                        'historical_data': 3600,
                        'fundamental_data': 86400,
                        'technical_data': 900,
                        'reports': 43200
                    }
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
        """Validate required configuration values (provider-aware)."""
        logger = logging.getLogger(__name__)
        provider = (config.get('model') or {}).get('provider', 'openai')
        required_paths = []
        if provider == 'openai':
            required_paths = ['openai.api_key', 'openai.model']
        elif provider == 'grok':
            # keep light; avoid failing non-OpenAI local tests
            required_paths = ['model.grok.api_key', 'model.grok.model']

        is_valid = True
        for path in required_paths:
            value = ConfigLoader.get_config_value(config, path)
            if not value or (isinstance(value, str) and value.strip() == ''):
                logger.warning(f"Required configuration missing or empty: {path}")
                is_valid = False
        return is_valid

    @staticmethod
    def _normalize_env_name(env: str) -> str:
        e = (env or '').strip().lower()
        if e in ('dev', 'development', 'local'):
            return 'local'
        if e in ('k8s', 'k8s-local', 'local-k8s'):
            return 'k8s-local'
        if e in ('stage', 'stg', 'staging'):
            return 'staging'
        if e in ('prod', 'production'):
            return 'production'
        return e or 'local'

    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge override into base without mutating inputs."""
        result = dict(base) if isinstance(base, dict) else {}
        for k, v in (override or {}).items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = ConfigLoader._deep_merge(result[k], v)
            else:
                result[k] = v
        return result

    @staticmethod
    def _apply_cloud_secret_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
        """Optionally pull secrets from a cloud provider (Azure Key Vault if configured)."""
        # Activate if explicit or in staging/production
        env_name = ConfigLoader._normalize_env_name(os.getenv("APP_ENV") or "local")
        use_kv = os.getenv("USE_AZURE_KEYVAULT", "false").lower() in ("1", "true", "yes", "on") \
                 or env_name in ("staging", "production")
        if not use_kv:
            return config

        kv_uri = os.getenv("AZURE_KEYVAULT_URI")
        kv_name = os.getenv("KEYVAULT_NAME")
        if not kv_uri and kv_name:
            kv_uri = f"https://{kv_name}.vault.azure.net/"

        if not kv_uri:
            # Not configured
            return config

        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
        except Exception:
            logging.getLogger(__name__).info("Azure Key Vault SDK not available; skipping secret fetch")
            return config

        logger = logging.getLogger(__name__)
        try:
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=kv_uri, credential=credential)

            # Known secret mappings (extend as needed)
            mappings = {
                'OPENAI_API_KEY': ('openai', 'api_key'),
                'GROK_API_KEY': ('model', 'grok', 'api_key'),
                'ALPHA_VANTAGE_API_KEY': ('financial_apis', 'alpha_vantage', 'api_key'),
                'REDIS_PASSWORD': ('database', 'redis', 'password'),
                # If you store MongoDB password separately (when not embedding in URI)
                'MONGODB_PASSWORD': ('database', 'mongodb', 'password'),
            }

            for secret_name, path in mappings.items():
                try:
                    secret = client.get_secret(secret_name)
                    if secret and secret.value:
                        ConfigLoader._set_nested_value(config, path, secret.value)
                        logger.info(f"Applied secret from Key Vault: {secret_name}")
                except Exception as ex:
                    logger.debug(f"Secret {secret_name} not applied: {ex}")

        except Exception as ex:
            logger.warning(f"Failed to apply Azure Key Vault secrets: {ex}")

        return config
