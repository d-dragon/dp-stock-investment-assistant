"""
Configuration loader utility.
"""

import os
import yaml
import logging
from typing import Dict, Any
from pathlib import Path


class ConfigLoader:
    """Utility class for loading configuration files."""
    
    @staticmethod
    def load_config(config_path: str = None) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Args:
            config_path: Path to config file. If None, uses default path.
            
        Returns:
            Configuration dictionary
        """
        logger = logging.getLogger(__name__)
        
        if config_path is None:
            # Default config path
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"
        
        try:
            if not os.path.exists(config_path):
                logger.warning(f"Config file not found at {config_path}, using defaults")
                return ConfigLoader._get_default_config()
            
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                
            logger.info(f"Configuration loaded from {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.info("Using default configuration")
            return ConfigLoader._get_default_config()
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY', ''),
                'model': 'gpt-4',
                'max_tokens': 2000,
                'temperature': 0.7
            },
            'financial_apis': {
                'yahoo_finance': {
                    'enabled': True
                },
                'alpha_vantage': {
                    'api_key': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
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
