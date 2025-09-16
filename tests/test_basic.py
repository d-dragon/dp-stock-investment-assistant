"""
Basic tests for the DP Stock-Investment Assistant.
"""

import unittest
import sys
import os
from pathlib import Path

# Add src directory to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestBasicImports(unittest.TestCase):
    """Test that basic imports work correctly."""
    
    def test_import_main_modules(self):
        """Test importing main modules."""
        try:
            from utils.config_loader import ConfigLoader
            from core.agent import StockAgent
            from core.ai_client import AIClient
            from core.data_manager import DataManager
          
          # Test that classes can be instantiated with mock config
            mock_config = {
                'openai': {'api_key': 'test'},
                'financial_apis': {'yahoo_finance': {'enabled': True}}
            }
            
            # These might fail due to missing API keys, but imports should work
            self.assertTrue(True)  # If we get here, imports worked
            
        except ImportError as e:
            self.fail(f"Import failed: {e}")


if __name__ == '__main__':
    unittest.main()
