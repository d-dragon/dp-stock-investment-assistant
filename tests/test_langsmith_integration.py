"""
LangSmith Studio Integration Tests

Tests the bootstrap module and LangGraph agent loading mechanism
to ensure Studio integration works correctly.

Reference: .github/copilot-instructions.md § Testing with pytest
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def clean_sys_path():
    """Restore sys.path after test to prevent pollution."""
    original_path = sys.path.copy()
    yield
    sys.path[:] = original_path


@pytest.fixture
def mock_config():
    """Minimal config for agent creation."""
    return {
        'model': {
            'provider': 'openai',
            'allow_fallback': False
        },
        'openai': {
            'api_key': 'test-key',
            'model': 'gpt-4'
        },
        'mongodb': {
            'uri': 'mongodb://localhost:27017',
            'database': 'test_db'
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 1
        }
    }


# ============================================================================
# PATH SETUP TESTS
# ============================================================================

class TestBootstrapPathSetup:
    """Test bootstrap module's sys.path manipulation."""
    
    def test_bootstrap_adds_src_to_path(self, clean_sys_path):
        """Test that bootstrap module adds src directory to sys.path."""
        # Get expected src path
        project_root = Path(__file__).resolve().parent.parent
        src_path = str(project_root / "src")
        
        # Remove src from path if present (simulate LangGraph context)
        sys.path = [p for p in sys.path if src_path not in p]
        
        # Import bootstrap module
        from core import langgraph_bootstrap
        
        # Verify src is now in path
        assert src_path in sys.path, f"Expected {src_path} in sys.path"
    
    def test_bootstrap_path_setup_is_idempotent(self, clean_sys_path):
        """Test that calling path setup multiple times doesn't duplicate."""
        from core.langgraph_bootstrap import _setup_python_path
        
        initial_count = len(sys.path)
        
        # Call multiple times
        _setup_python_path()
        _setup_python_path()
        _setup_python_path()
        
        # Should only add once
        src_count = sum(1 for p in sys.path if 'src' in p and 'site-packages' not in p)
        assert src_count <= 2, "Path setup should be idempotent"


# ============================================================================
# IMPORT CHAIN TESTS
# ============================================================================

class TestBootstrapImportChain:
    """Test that bootstrap correctly imports project modules."""
    
    def test_bootstrap_imports_stock_assistant(self):
        """Test that bootstrap can import stock_assistant_agent module."""
        # This tests the full import chain works
        from core import langgraph_bootstrap
        
        # Verify the module has the expected function
        assert hasattr(langgraph_bootstrap, 'get_agent')
        assert callable(langgraph_bootstrap.get_agent)
    
    def test_bootstrap_exports_agent(self):
        """Test that bootstrap exports an agent graph."""
        from core import langgraph_bootstrap
        
        # The bootstrap should export 'agent' at module level
        assert hasattr(langgraph_bootstrap, 'agent')
        
        # Should be a compiled graph (CompiledGraph or similar)
        agent = langgraph_bootstrap.agent
        assert agent is not None


# ============================================================================
# AGENT CREATION TESTS
# ============================================================================

class TestAgentCreation:
    """Test agent creation through bootstrap."""
    
    @patch('core.stock_assistant_agent.ConfigLoader')
    @patch('core.stock_assistant_agent.DataManager')
    @patch('core.stock_assistant_agent.get_langgraph_agent')
    def test_create_agent_with_mocks(
        self,
        mock_get_agent,
        mock_dm_class,
        mock_config_loader,
        mock_config
    ):
        """Test agent creation with mocked dependencies."""
        # Setup mocks
        mock_config_loader.load_config.return_value = mock_config
        mock_dm_instance = MagicMock()
        mock_dm_class.return_value = mock_dm_instance
        mock_graph = MagicMock()
        mock_get_agent.return_value = mock_graph
        
        # Import and create agent
        from core.stock_assistant_agent import create_stock_assistant_agent
        
        # Call with explicit config to avoid actual config loading
        result = create_stock_assistant_agent(mock_config)
        
        # Verify DataManager was created
        mock_dm_class.assert_called_once()
        
        # Verify graph was requested
        mock_get_agent.assert_called_once()
    
    def test_create_agent_factory_function_exists(self):
        """Test that factory function is importable."""
        from core.stock_assistant_agent import create_stock_assistant_agent
        
        assert callable(create_stock_assistant_agent)


# ============================================================================
# LANGGRAPH.JSON VALIDATION TESTS
# ============================================================================

class TestLangGraphConfig:
    """Test langgraph.json configuration validity."""
    
    def test_langgraph_json_exists(self):
        """Test that langgraph.json exists at project root."""
        project_root = Path(__file__).resolve().parent.parent
        config_path = project_root / "langgraph.json"
        
        assert config_path.exists(), f"langgraph.json should exist at {config_path}"
    
    def test_langgraph_json_points_to_bootstrap(self):
        """Test that langgraph.json references bootstrap module."""
        import json
        
        project_root = Path(__file__).resolve().parent.parent
        config_path = project_root / "langgraph.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Check graphs section
        assert 'graphs' in config, "langgraph.json should have 'graphs' section"
        
        graphs = config['graphs']
        assert 'stock_assistant' in graphs, "Should have 'stock_assistant' graph"
        
        # Should point to bootstrap module
        graph_path = graphs['stock_assistant']
        assert 'langgraph_bootstrap.py' in graph_path, \
            f"Graph should reference bootstrap module, got: {graph_path}"
    
    def test_bootstrap_module_path_valid(self):
        """Test that the bootstrap module path in config is valid."""
        import json
        
        project_root = Path(__file__).resolve().parent.parent
        config_path = project_root / "langgraph.json"
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Parse graph path (format: "./path/to/module.py:attribute")
        graph_spec = config['graphs']['stock_assistant']
        
        if ':' in graph_spec:
            module_path, attr = graph_spec.rsplit(':', 1)
        else:
            module_path = graph_spec
            attr = 'agent'
        
        # Remove leading ./ if present
        if module_path.startswith('./'):
            module_path = module_path[2:]
        
        # Verify file exists
        full_path = project_root / module_path
        assert full_path.exists(), f"Bootstrap module should exist at {full_path}"


# ============================================================================
# INTEGRATION SMOKE TEST
# ============================================================================

class TestBootstrapIntegration:
    """Integration tests for full bootstrap flow."""
    
    def test_bootstrap_module_loads_without_error(self):
        """Smoke test: bootstrap module should load without exceptions."""
        try:
            from core import langgraph_bootstrap
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
        
        assert success, f"Bootstrap module should load cleanly: {error}"
    
    def test_project_imports_work_after_bootstrap(self):
        """Test that project imports work after bootstrap path setup."""
        # Load bootstrap first
        from core import langgraph_bootstrap
        
        # These imports should work because bootstrap set up the path
        from core.data_manager import DataManager
        from utils.config_loader import ConfigLoader
        from data.repositories.factory import RepositoryFactory
        
        # Verify they're the right types
        assert hasattr(DataManager, '__init__')
        assert hasattr(ConfigLoader, 'load_config')
        assert hasattr(RepositoryFactory, '__init__')


# ============================================================================
# RUNNING TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
