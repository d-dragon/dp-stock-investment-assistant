"""Tests for LangChain Tools Module.

Comprehensive test coverage for:
- CachingTool base class
- ToolRegistry singleton
- StockSymbolTool
- ReportingTool
- TradingViewTool

Reference: .github/instructions/testing.instructions.md § Protocol-Based Mocking
"""

import hashlib
import json
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Any, Dict


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_cache():
    """Mock CacheBackend for testing."""
    cache = MagicMock()
    cache.get_json.return_value = None  # Default: cache miss
    cache.set_json.return_value = True
    cache.ping.return_value = True
    cache.is_available.return_value = True
    return cache


@pytest.fixture
def mock_data_manager():
    """Mock DataManager for testing."""
    manager = MagicMock()
    manager.get_stock_info.return_value = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "current_price": 175.50,
        "previous_close": 174.25,
        "market_cap": 2750000000000,
        "pe_ratio": 28.5,
        "dividend_yield": 0.005,
        "sector": "Technology",
        "industry": "Consumer Electronics",
    }
    return manager


@pytest.fixture
def mock_symbol_repository():
    """Mock SymbolRepository for testing."""
    repo = MagicMock()
    repo.get_by_symbol.return_value = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_type": "stock",
        "classification": {
            "sector": "Technology",
            "industry": "Consumer Electronics",
        },
        "listing": {
            "exchange": "NASDAQ",
        },
    }
    repo.search_by_name.return_value = [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "asset_type": "stock",
            "listing": {"exchange": "NASDAQ"},
        },
        {
            "symbol": "APLE",
            "name": "Apple Hospitality REIT",
            "asset_type": "stock",
            "listing": {"exchange": "NYSE"},
        },
    ]
    return repo


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset tool registry before each test."""
    from src.core.tools.registry import reset_tool_registry
    reset_tool_registry()
    yield
    reset_tool_registry()


# ============================================================================
# CachingTool Base Class Tests
# ============================================================================

class TestCachingTool:
    """Tests for CachingTool abstract base class."""
    
    def test_caching_tool_is_abstract(self):
        """Test that CachingTool cannot be instantiated directly."""
        from src.core.tools.base import CachingTool
        
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            CachingTool()
    
    def test_concrete_tool_requires_execute(self):
        """Test that subclass must implement _execute."""
        from src.core.tools.base import CachingTool
        
        class IncompleteTool(CachingTool):
            name: str = "incomplete"
            description: str = "Missing _execute"
        
        with pytest.raises(TypeError, match="_execute"):
            IncompleteTool()
    
    def test_concrete_tool_creation(self, mock_cache):
        """Test creating a concrete CachingTool subclass."""
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "A test tool"
            
            def _execute(self, **kwargs):
                return {"result": kwargs.get("query", "default")}
        
        tool = TestTool(cache=mock_cache, cache_ttl_seconds=120)
        
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.cache_ttl_seconds == 120
        assert tool.enable_cache is True
        assert tool.cache is mock_cache
    
    def test_cache_key_generation(self, mock_cache):
        """Test that cache keys are deterministic."""
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {"result": "test"}
        
        tool = TestTool(cache=mock_cache)
        
        # Same inputs should produce same key
        key1 = tool._generate_cache_key(query="test", limit=10)
        key2 = tool._generate_cache_key(query="test", limit=10)
        assert key1 == key2
        
        # Different inputs should produce different keys
        key3 = tool._generate_cache_key(query="different", limit=10)
        assert key1 != key3
        
        # Key format: tool:{name}:{hash}
        assert key1.startswith("tool:test_tool:")
    
    def test_cached_run_cache_hit(self, mock_cache):
        """Test _cached_run returns cached result on cache hit."""
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {"result": "fresh"}
        
        # Setup cache hit
        mock_cache.get_json.return_value = {"result": "cached"}
        
        tool = TestTool(cache=mock_cache)
        result, was_cached = tool._cached_run(query="test")
        
        assert was_cached is True
        assert result == {"result": "cached"}
        mock_cache.get_json.assert_called_once()
    
    def test_cached_run_cache_miss(self, mock_cache):
        """Test _cached_run executes and caches on cache miss."""
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {"result": "fresh"}
        
        # Setup cache miss
        mock_cache.get_json.return_value = None
        
        tool = TestTool(cache=mock_cache)
        result, was_cached = tool._cached_run(query="test")
        
        assert was_cached is False
        assert result == {"result": "fresh"}
        mock_cache.set_json.assert_called_once()
    
    def test_run_returns_result(self, mock_cache):
        """Test _run executes tool and returns result."""
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return f"Result: {kwargs.get('query')}"
        
        tool = TestTool(cache=mock_cache)
        result = tool._run(query="hello")
        
        assert result == "Result: hello"
    
    def test_run_without_cache(self):
        """Test tool works without cache configured."""
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {"result": kwargs.get("query")}
        
        tool = TestTool(cache=None, enable_cache=False)
        result = tool._run(query="test")
        
        assert result == {"result": "test"}
    
    @pytest.mark.asyncio
    async def test_arun_wraps_sync(self, mock_cache):
        """Test _arun wraps synchronous execution."""
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {"result": "async_wrapped"}
        
        tool = TestTool(cache=mock_cache)
        result = await tool._arun(query="test")
        
        assert result == {"result": "async_wrapped"}
    
    def test_create_tool_call(self, mock_cache):
        """Test create_tool_call returns proper ToolCall."""
        from src.core.tools.base import CachingTool
        from src.core.types import ToolCall
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {"result": "test"}
        
        tool = TestTool(cache=mock_cache)
        
        tool_call = tool.create_tool_call(
            input_args={"query": "test"},
            output={"result": "test"},
            cached=False,
            execution_time_ms=150.5,
        )
        
        assert isinstance(tool_call, ToolCall)
        assert tool_call.name == "test_tool"
        assert tool_call.input == {"query": "test"}
        assert tool_call.output == {"result": "test"}
        assert tool_call.cached is False
        assert tool_call.execution_time_ms == 150.5
    
    def test_health_check_healthy(self, mock_cache):
        """Test health_check returns healthy when cache available."""
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {}
        
        tool = TestTool(cache=mock_cache)
        healthy, details = tool.health_check()
        
        assert healthy is True
        assert details["component"] == "tool:test_tool"
        assert details["cache_enabled"] is True
        assert details["cache_available"] is True
        assert details["status"] == "ready"
    
    def test_health_check_no_cache(self):
        """Test health_check when cache not configured."""
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {}
        
        tool = TestTool(cache=None)
        healthy, details = tool.health_check()
        
        assert healthy is True
        assert details["cache_available"] is False


# ============================================================================
# ToolRegistry Tests
# ============================================================================

class TestToolRegistry:
    """Tests for ToolRegistry singleton."""
    
    def test_singleton_pattern(self):
        """Test that get_instance returns same instance."""
        from src.core.tools.registry import ToolRegistry
        
        registry1 = ToolRegistry.get_instance()
        registry2 = ToolRegistry.get_instance()
        
        assert registry1 is registry2
    
    def test_register_tool(self, mock_cache):
        """Test registering a tool."""
        from src.core.tools.registry import ToolRegistry
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {}
        
        registry = ToolRegistry.get_instance()
        tool = TestTool(cache=mock_cache)
        
        registry.register(tool)
        
        assert registry.get("test_tool") is tool
        assert registry.is_enabled("test_tool") is True
    
    def test_register_duplicate_raises(self, mock_cache):
        """Test registering duplicate tool raises ValueError."""
        from src.core.tools.registry import ToolRegistry
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {}
        
        registry = ToolRegistry.get_instance()
        tool = TestTool(cache=mock_cache)
        
        registry.register(tool)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(tool)
    
    def test_register_with_replace(self, mock_cache):
        """Test registering with replace=True overwrites."""
        from src.core.tools.registry import ToolRegistry
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {}
        
        registry = ToolRegistry.get_instance()
        tool1 = TestTool(cache=mock_cache, cache_ttl_seconds=60)
        tool2 = TestTool(cache=mock_cache, cache_ttl_seconds=120)
        
        registry.register(tool1)
        registry.register(tool2, replace=True)
        
        assert registry.get("test_tool").cache_ttl_seconds == 120
    
    def test_unregister_tool(self, mock_cache):
        """Test unregistering a tool."""
        from src.core.tools.registry import ToolRegistry
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {}
        
        registry = ToolRegistry.get_instance()
        tool = TestTool(cache=mock_cache)
        
        registry.register(tool)
        assert registry.unregister("test_tool") is True
        assert registry.get("test_tool") is None
    
    def test_unregister_nonexistent(self):
        """Test unregistering nonexistent tool returns False."""
        from src.core.tools.registry import ToolRegistry
        
        registry = ToolRegistry.get_instance()
        assert registry.unregister("nonexistent") is False
    
    def test_set_enabled(self, mock_cache):
        """Test enabling/disabling tools."""
        from src.core.tools.registry import ToolRegistry
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            
            def _execute(self, **kwargs):
                return {}
        
        registry = ToolRegistry.get_instance()
        tool = TestTool(cache=mock_cache)
        
        registry.register(tool, enabled=True)
        assert registry.is_enabled("test_tool") is True
        
        registry.set_enabled("test_tool", False)
        assert registry.is_enabled("test_tool") is False
    
    def test_list_all_and_names(self, mock_cache):
        """Test list_all and list_names methods."""
        from src.core.tools.registry import ToolRegistry
        from src.core.tools.base import CachingTool
        
        class Tool1(CachingTool):
            name: str = "tool1"
            description: str = "Tool 1"
            def _execute(self, **kwargs): return {}
        
        class Tool2(CachingTool):
            name: str = "tool2"
            description: str = "Tool 2"
            def _execute(self, **kwargs): return {}
        
        registry = ToolRegistry.get_instance()
        registry.register(Tool1(cache=mock_cache))
        registry.register(Tool2(cache=mock_cache))
        
        all_tools = registry.list_all()
        names = registry.list_names()
        
        assert len(all_tools) == 2
        assert set(names) == {"tool1", "tool2"}
    
    def test_get_enabled_disabled_tools(self, mock_cache):
        """Test filtering enabled/disabled tools."""
        from src.core.tools.registry import ToolRegistry
        from src.core.tools.base import CachingTool
        
        class Tool1(CachingTool):
            name: str = "enabled_tool"
            description: str = "Enabled"
            def _execute(self, **kwargs): return {}
        
        class Tool2(CachingTool):
            name: str = "disabled_tool"
            description: str = "Disabled"
            def _execute(self, **kwargs): return {}
        
        registry = ToolRegistry.get_instance()
        registry.register(Tool1(cache=mock_cache), enabled=True)
        registry.register(Tool2(cache=mock_cache), enabled=False)
        
        enabled = registry.get_enabled_tools()
        disabled = registry.get_disabled_tools()
        
        assert len(enabled) == 1
        assert enabled[0].name == "enabled_tool"
        assert len(disabled) == 1
        assert disabled[0].name == "disabled_tool"
    
    def test_clear(self, mock_cache):
        """Test clearing registry."""
        from src.core.tools.registry import ToolRegistry
        from src.core.tools.base import CachingTool
        
        class TestTool(CachingTool):
            name: str = "test_tool"
            description: str = "Test"
            def _execute(self, **kwargs): return {}
        
        registry = ToolRegistry.get_instance()
        registry.register(TestTool(cache=mock_cache))
        
        registry.clear()
        
        assert len(registry.list_all()) == 0
    
    def test_health_check(self, mock_cache):
        """Test registry health_check aggregates tool health."""
        from src.core.tools.registry import ToolRegistry
        from src.core.tools.base import CachingTool
        
        class HealthyTool(CachingTool):
            name: str = "healthy"
            description: str = "Healthy tool"
            def _execute(self, **kwargs): return {}
        
        registry = ToolRegistry.get_instance()
        registry.register(HealthyTool(cache=mock_cache))
        
        all_healthy, details = registry.health_check()
        
        assert all_healthy is True
        assert "healthy" in details["tools"]
        assert details["total_tools"] == 1


# ============================================================================
# StockSymbolTool Tests
# ============================================================================

class TestStockSymbolTool:
    """Tests for StockSymbolTool."""
    
    def test_get_info_from_data_manager(self, mock_cache, mock_data_manager):
        """Test get_info retrieves data from DataManager."""
        from src.core.tools.stock_symbol import StockSymbolTool
        
        tool = StockSymbolTool(
            data_manager=mock_data_manager,
            cache=mock_cache,
        )
        
        result = tool._run(action="get_info", symbol="AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["source"] == "yahoo_finance"
        assert result["current_price"] == 175.50
        assert result["sector"] == "Technology"
    
    def test_get_info_fallback_to_repository(
        self, mock_cache, mock_symbol_repository
    ):
        """Test get_info falls back to repository when DataManager fails."""
        from src.core.tools.stock_symbol import StockSymbolTool
        
        failing_manager = MagicMock()
        failing_manager.get_stock_info.side_effect = Exception("API Error")
        
        tool = StockSymbolTool(
            data_manager=failing_manager,
            symbol_repository=mock_symbol_repository,
            cache=mock_cache,
        )
        
        result = tool._run(action="get_info", symbol="AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["source"] == "mongodb"
        assert result["name"] == "Apple Inc."
    
    def test_get_info_no_data_sources(self, mock_cache):
        """Test get_info returns error when no data sources."""
        from src.core.tools.stock_symbol import StockSymbolTool
        
        tool = StockSymbolTool(cache=mock_cache)
        
        result = tool._run(action="get_info", symbol="AAPL")
        
        assert "error" in result
        assert result["source"] == "none"
    
    def test_get_info_requires_symbol(
        self, mock_cache, mock_data_manager
    ):
        """Test get_info raises ValueError when symbol missing."""
        from src.core.tools.stock_symbol import StockSymbolTool
        
        tool = StockSymbolTool(
            data_manager=mock_data_manager,
            cache=mock_cache,
        )
        
        with pytest.raises(ValueError, match="symbol.*required"):
            tool._run(action="get_info")
    
    def test_search_symbols(self, mock_cache, mock_symbol_repository):
        """Test search action returns matching symbols."""
        from src.core.tools.stock_symbol import StockSymbolTool
        
        tool = StockSymbolTool(
            symbol_repository=mock_symbol_repository,
            cache=mock_cache,
        )
        
        result = tool._run(action="search", query="Apple", limit=5)
        
        assert result["query"] == "Apple"
        assert result["source"] == "mongodb"
        assert result["count"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["symbol"] == "AAPL"
    
    def test_search_requires_query(self, mock_cache, mock_symbol_repository):
        """Test search raises ValueError when query missing."""
        from src.core.tools.stock_symbol import StockSymbolTool
        
        tool = StockSymbolTool(
            symbol_repository=mock_symbol_repository,
            cache=mock_cache,
        )
        
        with pytest.raises(ValueError, match="query.*required"):
            tool._run(action="search")
    
    def test_unknown_action_raises(self, mock_cache):
        """Test unknown action raises ValueError."""
        from src.core.tools.stock_symbol import StockSymbolTool
        
        tool = StockSymbolTool(cache=mock_cache)
        
        with pytest.raises(ValueError, match="Unknown action"):
            tool._run(action="invalid_action")
    
    def test_convenience_methods(
        self, mock_cache, mock_data_manager, mock_symbol_repository
    ):
        """Test get_info() and search() convenience methods."""
        from src.core.tools.stock_symbol import StockSymbolTool
        
        tool = StockSymbolTool(
            data_manager=mock_data_manager,
            symbol_repository=mock_symbol_repository,
            cache=mock_cache,
        )
        
        info = tool.get_info("AAPL")
        assert info["symbol"] == "AAPL"
        
        search_result = tool.search("Apple", limit=5)
        assert search_result["query"] == "Apple"
    
    def test_health_check_with_data_source(
        self, mock_cache, mock_data_manager
    ):
        """Test health_check returns healthy with data source."""
        from src.core.tools.stock_symbol import StockSymbolTool
        
        tool = StockSymbolTool(
            data_manager=mock_data_manager,
            cache=mock_cache,
        )
        
        healthy, details = tool.health_check()
        
        assert healthy is True
        assert details["has_data_source"] is True
        assert details["data_manager_available"] is True
    
    def test_health_check_no_data_source(self, mock_cache):
        """Test health_check returns unhealthy without data source."""
        from src.core.tools.stock_symbol import StockSymbolTool
        
        tool = StockSymbolTool(cache=mock_cache)
        
        healthy, details = tool.health_check()
        
        assert healthy is False
        assert details["has_data_source"] is False


# ============================================================================
# ReportingTool Tests
# ============================================================================

class TestReportingTool:
    """Tests for ReportingTool scaffold."""
    
    def test_generate_symbol_report(self, mock_cache):
        """Test symbol report generation."""
        from src.core.tools.reporting import ReportingTool
        
        tool = ReportingTool(cache=mock_cache)
        
        result = tool._run(report_type="symbol", symbol="AAPL")
        
        assert result["report_type"] == "symbol"
        assert result["symbol"] == "AAPL"
        assert "markdown" in result
        assert "# Stock Analysis Report: AAPL" in result["markdown"]
        assert result["status"] == "scaffold"
    
    def test_generate_portfolio_report(self, mock_cache):
        """Test portfolio report generation."""
        from src.core.tools.reporting import ReportingTool
        
        tool = ReportingTool(cache=mock_cache)
        
        result = tool._run(report_type="portfolio", portfolio_id="my_portfolio")
        
        assert result["report_type"] == "portfolio"
        assert result["portfolio_id"] == "my_portfolio"
        assert "markdown" in result
        assert "# Portfolio Overview Report" in result["markdown"]
    
    def test_generate_market_report(self, mock_cache):
        """Test market report generation."""
        from src.core.tools.reporting import ReportingTool
        
        tool = ReportingTool(cache=mock_cache)
        
        result = tool._run(report_type="market")
        
        assert result["report_type"] == "market"
        assert "markdown" in result
        assert "# Market Summary Report" in result["markdown"]
    
    def test_symbol_report_requires_symbol(self, mock_cache):
        """Test symbol report raises ValueError when symbol missing."""
        from src.core.tools.reporting import ReportingTool
        
        tool = ReportingTool(cache=mock_cache)
        
        with pytest.raises(ValueError, match="symbol.*required"):
            tool._run(report_type="symbol")
    
    def test_unknown_report_type_raises(self, mock_cache):
        """Test unknown report type raises ValueError."""
        from src.core.tools.reporting import ReportingTool
        
        tool = ReportingTool(cache=mock_cache)
        
        with pytest.raises(ValueError, match="Unknown report_type"):
            tool._run(report_type="invalid_type")
    
    def test_convenience_methods(self, mock_cache):
        """Test convenience methods for report generation."""
        from src.core.tools.reporting import ReportingTool
        
        tool = ReportingTool(cache=mock_cache)
        
        symbol_report = tool.generate_symbol_report("AAPL")
        assert symbol_report["symbol"] == "AAPL"
        
        portfolio_report = tool.generate_portfolio_report("my_portfolio")
        assert portfolio_report["portfolio_id"] == "my_portfolio"
        
        market_report = tool.generate_market_report()
        assert market_report["report_type"] == "market"
    
    def test_default_cache_ttl(self, mock_cache):
        """Test ReportingTool has longer default TTL."""
        from src.core.tools.reporting import ReportingTool
        
        tool = ReportingTool(cache=mock_cache)
        
        assert tool.cache_ttl_seconds == 600  # 10 minutes


# ============================================================================
# TradingViewTool Tests
# ============================================================================

class TestTradingViewTool:
    """Tests for TradingViewTool placeholder."""
    
    def test_execute_raises_not_implemented(self, mock_cache):
        """Test _execute raises NotImplementedError."""
        from src.core.tools.tradingview import TradingViewTool
        
        tool = TradingViewTool(cache=mock_cache)
        
        with pytest.raises(NotImplementedError, match="Phase 2"):
            tool._run(action="get_chart_url", symbol="AAPL")
    
    def test_convenience_methods_raise(self, mock_cache):
        """Test convenience methods raise NotImplementedError."""
        from src.core.tools.tradingview import TradingViewTool
        
        tool = TradingViewTool(cache=mock_cache)
        
        with pytest.raises(NotImplementedError):
            tool.get_chart_url("AAPL")
        
        with pytest.raises(NotImplementedError):
            tool.get_widget("AAPL")
        
        with pytest.raises(NotImplementedError):
            tool.get_analysis("AAPL")
    
    def test_health_check_returns_healthy(self, mock_cache):
        """Test placeholder is always 'healthy'."""
        from src.core.tools.tradingview import TradingViewTool
        
        tool = TradingViewTool(cache=mock_cache)
        
        healthy, details = tool.health_check()
        
        assert healthy is True
        assert details["implementation_status"] == "placeholder"
        assert details["phase"] == "Phase 2"


# ============================================================================
# Module Import Tests
# ============================================================================

class TestModuleImports:
    """Tests for module-level imports and exports."""
    
    def test_all_exports_available(self):
        """Test all expected exports are available."""
        from src.core.tools import (
            CachingTool,
            ToolRegistry,
            get_tool_registry,
            reset_tool_registry,
            StockSymbolTool,
            ReportingTool,
            TradingViewTool,
        )
        
        assert CachingTool is not None
        assert ToolRegistry is not None
        assert callable(get_tool_registry)
        assert callable(reset_tool_registry)
        assert StockSymbolTool is not None
        assert ReportingTool is not None
        assert TradingViewTool is not None
    
    def test_get_tool_registry_returns_singleton(self):
        """Test get_tool_registry returns singleton instance."""
        from src.core.tools import get_tool_registry, ToolRegistry
        
        registry1 = get_tool_registry()
        registry2 = ToolRegistry.get_instance()
        
        assert registry1 is registry2
    
    def test_reset_tool_registry_clears_instance(self, mock_cache):
        """Test reset_tool_registry clears and creates new instance."""
        from src.core.tools import (
            get_tool_registry,
            reset_tool_registry,
            StockSymbolTool,
        )
        
        registry1 = get_tool_registry()
        registry1.register(StockSymbolTool(cache=mock_cache))
        
        reset_tool_registry()
        
        registry2 = get_tool_registry()
        assert len(registry2.list_all()) == 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestToolsIntegration:
    """Integration tests for tools working together."""
    
    def test_register_all_tools(
        self, mock_cache, mock_data_manager, mock_symbol_repository
    ):
        """Test registering all tools in registry."""
        from src.core.tools import (
            get_tool_registry,
            StockSymbolTool,
            ReportingTool,
            TradingViewTool,
        )
        
        registry = get_tool_registry()
        
        # Register all tools
        registry.register(StockSymbolTool(
            data_manager=mock_data_manager,
            symbol_repository=mock_symbol_repository,
            cache=mock_cache,
        ))
        registry.register(ReportingTool(cache=mock_cache))
        registry.register(TradingViewTool(cache=mock_cache))
        
        assert len(registry.list_all()) == 3
        assert set(registry.list_names()) == {"stock_symbol", "reporting", "tradingview"}
    
    def test_tool_caching_across_calls(
        self, mock_cache, mock_data_manager
    ):
        """Test that caching works across multiple calls."""
        from src.core.tools.stock_symbol import StockSymbolTool
        
        tool = StockSymbolTool(
            data_manager=mock_data_manager,
            cache=mock_cache,
            cache_ttl_seconds=60,
        )
        
        # First call - cache miss
        mock_cache.get_json.return_value = None
        result1 = tool._run(action="get_info", symbol="AAPL")
        
        # Simulate cache hit for second call
        mock_cache.get_json.return_value = result1
        result2, was_cached = tool._cached_run(action="get_info", symbol="AAPL")
        
        assert was_cached is True
        assert result1 == result2
        
        # Verify cache was checked
        assert mock_cache.get_json.call_count >= 2
