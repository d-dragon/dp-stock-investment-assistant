"""
Unit Tests for MemoryConfig and ContentValidator (Tasks T011, T027)

Tests the MemoryConfig frozen dataclass with fail-fast validation
per FR-3.1.9 (externally configurable) and FR-3.1.10 (fail-fast validation).

Also tests ContentValidator for FR-3.1.7 (zero financial data) and
FR-3.1.8 (tool outputs as references only) compliance.

Test Strategy:
- Test default values load correctly
- Test valid custom values accepted
- Test each validation boundary (min/max) for all numeric parameters
- Test messages_to_keep < max_messages constraint
- Test collection name validation (non-empty strings)
- Test from_config() factory method
- Test disabled() factory method
- Test to_dict() serialization
- Verify error messages include parameter name and valid range
- Test ContentValidator detects prohibited financial patterns
- Test ContentValidator returns empty list for compliant content

Reference:
    - Spec: specs/spec-driven-development-pilot/plan.md § MemoryConfig Dataclass Pattern
    - Source: src/utils/memory_config.py
"""

import pytest
from utils.memory_config import MemoryConfig, ContentValidator, VALIDATION_RANGES


# ============================================================================
# Test Default Values
# ============================================================================

class TestDefaultValues:
    """Test MemoryConfig loads with correct default values."""
    
    def test_default_enabled_is_true(self):
        """Default enabled should be True."""
        config = MemoryConfig()
        assert config.enabled is True
    
    def test_default_summarize_threshold(self):
        """Default summarize_threshold should be 4000."""
        config = MemoryConfig()
        assert config.summarize_threshold == 4000
    
    def test_default_max_messages(self):
        """Default max_messages should be 50."""
        config = MemoryConfig()
        assert config.max_messages == 50
    
    def test_default_messages_to_keep(self):
        """Default messages_to_keep should be 10."""
        config = MemoryConfig()
        assert config.messages_to_keep == 10
    
    def test_default_max_content_size(self):
        """Default max_content_size should be 32768."""
        config = MemoryConfig()
        assert config.max_content_size == 32768
    
    def test_default_summary_max_length(self):
        """Default summary_max_length should be 500."""
        config = MemoryConfig()
        assert config.summary_max_length == 500
    
    def test_default_context_load_timeout_ms(self):
        """Default context_load_timeout_ms should be 500."""
        config = MemoryConfig()
        assert config.context_load_timeout_ms == 500
    
    def test_default_state_save_timeout_ms(self):
        """Default state_save_timeout_ms should be 50."""
        config = MemoryConfig()
        assert config.state_save_timeout_ms == 50
    
    def test_default_checkpoint_collection(self):
        """Default checkpoint_collection should be 'agent_checkpoints'."""
        config = MemoryConfig()
        assert config.checkpoint_collection == "agent_checkpoints"
    
    def test_default_conversations_collection(self):
        """Default conversations_collection should be 'conversations'."""
        config = MemoryConfig()
        assert config.conversations_collection == "conversations"


# ============================================================================
# Test Valid Custom Values
# ============================================================================

class TestValidCustomValues:
    """Test MemoryConfig accepts valid custom values."""
    
    def test_enabled_false_accepted(self):
        """enabled=False should be accepted."""
        config = MemoryConfig(enabled=False)
        assert config.enabled is False
    
    def test_all_valid_custom_values(self):
        """All parameters with valid custom values should be accepted."""
        config = MemoryConfig(
            enabled=False,
            summarize_threshold=5000,
            max_messages=100,
            messages_to_keep=20,
            max_content_size=16384,
            summary_max_length=800,
            context_load_timeout_ms=1000,
            state_save_timeout_ms=100,
            checkpoint_collection="custom_checkpoints",
            conversations_collection="custom_conversations",
        )
        
        assert config.enabled is False
        assert config.summarize_threshold == 5000
        assert config.max_messages == 100
        assert config.messages_to_keep == 20
        assert config.max_content_size == 16384
        assert config.summary_max_length == 800
        assert config.context_load_timeout_ms == 1000
        assert config.state_save_timeout_ms == 100
        assert config.checkpoint_collection == "custom_checkpoints"
        assert config.conversations_collection == "custom_conversations"


# ============================================================================
# Test Frozen Dataclass Immutability
# ============================================================================

class TestFrozenDataclass:
    """Test MemoryConfig is immutable (frozen dataclass)."""
    
    def test_cannot_modify_enabled(self):
        """Should not be able to modify enabled after creation."""
        config = MemoryConfig()
        with pytest.raises(AttributeError):
            config.enabled = False  # type: ignore
    
    def test_cannot_modify_summarize_threshold(self):
        """Should not be able to modify summarize_threshold after creation."""
        config = MemoryConfig()
        with pytest.raises(AttributeError):
            config.summarize_threshold = 5000  # type: ignore
    
    def test_cannot_add_new_attribute(self):
        """Should not be able to add new attributes after creation."""
        config = MemoryConfig()
        with pytest.raises(AttributeError):
            config.new_field = "value"  # type: ignore


# ============================================================================
# Test summarize_threshold Validation
# ============================================================================

class TestSummarizeThresholdValidation:
    """Test summarize_threshold validation (valid: 1000-10000)."""
    
    def test_min_boundary_valid(self):
        """summarize_threshold=1000 (min boundary) should be valid."""
        config = MemoryConfig(summarize_threshold=1000)
        assert config.summarize_threshold == 1000
    
    def test_max_boundary_valid(self):
        """summarize_threshold=10000 (max boundary) should be valid."""
        config = MemoryConfig(summarize_threshold=10000)
        assert config.summarize_threshold == 10000
    
    def test_below_min_raises_error(self):
        """summarize_threshold=999 (below min) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(summarize_threshold=999)
        
        error_msg = str(exc_info.value)
        assert "summarize_threshold" in error_msg
        assert "999" in error_msg
        assert "1000" in error_msg
        assert "10000" in error_msg
        assert "below" in error_msg.lower()
    
    def test_above_max_raises_error(self):
        """summarize_threshold=10001 (above max) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(summarize_threshold=10001)
        
        error_msg = str(exc_info.value)
        assert "summarize_threshold" in error_msg
        assert "10001" in error_msg
        assert "above" in error_msg.lower()
    
    def test_zero_raises_error(self):
        """summarize_threshold=0 should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(summarize_threshold=0)
        
        assert "summarize_threshold" in str(exc_info.value)
    
    def test_negative_raises_error(self):
        """summarize_threshold=-100 should raise ValueError."""
        with pytest.raises(ValueError):
            MemoryConfig(summarize_threshold=-100)
    
    def test_non_integer_raises_error(self):
        """summarize_threshold='4000' (string) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(summarize_threshold="4000")  # type: ignore
        
        error_msg = str(exc_info.value)
        assert "summarize_threshold" in error_msg
        assert "integer" in error_msg.lower()


# ============================================================================
# Test max_messages Validation
# ============================================================================

class TestMaxMessagesValidation:
    """Test max_messages validation (valid: 10-200)."""
    
    def test_min_boundary_valid(self):
        """max_messages=10 (min boundary) should be valid."""
        # Also need messages_to_keep < 10
        config = MemoryConfig(max_messages=10, messages_to_keep=5)
        assert config.max_messages == 10
    
    def test_max_boundary_valid(self):
        """max_messages=200 (max boundary) should be valid."""
        config = MemoryConfig(max_messages=200)
        assert config.max_messages == 200
    
    def test_below_min_raises_error(self):
        """max_messages=9 (below min) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(max_messages=9, messages_to_keep=5)
        
        error_msg = str(exc_info.value)
        assert "max_messages" in error_msg
        assert "9" in error_msg
        assert "10" in error_msg
        assert "200" in error_msg
    
    def test_above_max_raises_error(self):
        """max_messages=201 (above max) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(max_messages=201)
        
        error_msg = str(exc_info.value)
        assert "max_messages" in error_msg
        assert "201" in error_msg


# ============================================================================
# Test messages_to_keep Validation
# ============================================================================

class TestMessagesToKeepValidation:
    """Test messages_to_keep validation (valid: 5-50, must be < max_messages)."""
    
    def test_min_boundary_valid(self):
        """messages_to_keep=5 (min boundary) should be valid."""
        config = MemoryConfig(messages_to_keep=5)
        assert config.messages_to_keep == 5
    
    def test_max_boundary_valid(self):
        """messages_to_keep=50 (max boundary) should be valid with high max_messages."""
        config = MemoryConfig(messages_to_keep=50, max_messages=100)
        assert config.messages_to_keep == 50
    
    def test_below_min_raises_error(self):
        """messages_to_keep=4 (below min) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(messages_to_keep=4)
        
        error_msg = str(exc_info.value)
        assert "messages_to_keep" in error_msg
        assert "4" in error_msg
        assert "5" in error_msg
        assert "50" in error_msg
    
    def test_above_max_raises_error(self):
        """messages_to_keep=51 (above max) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(messages_to_keep=51, max_messages=100)
        
        error_msg = str(exc_info.value)
        assert "messages_to_keep" in error_msg
        assert "51" in error_msg
    
    def test_equal_to_max_messages_raises_error(self):
        """messages_to_keep == max_messages should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(messages_to_keep=30, max_messages=30)
        
        error_msg = str(exc_info.value)
        assert "messages_to_keep" in error_msg
        assert "less than" in error_msg.lower()
        assert "max_messages" in error_msg
    
    def test_greater_than_max_messages_raises_error(self):
        """messages_to_keep > max_messages should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(messages_to_keep=40, max_messages=30)
        
        error_msg = str(exc_info.value)
        assert "messages_to_keep" in error_msg
        assert "less than" in error_msg.lower()


# ============================================================================
# Test max_content_size Validation
# ============================================================================

class TestMaxContentSizeValidation:
    """Test max_content_size validation (valid: 1024-65536)."""
    
    def test_min_boundary_valid(self):
        """max_content_size=1024 (min boundary) should be valid."""
        config = MemoryConfig(max_content_size=1024)
        assert config.max_content_size == 1024
    
    def test_max_boundary_valid(self):
        """max_content_size=65536 (max boundary) should be valid."""
        config = MemoryConfig(max_content_size=65536)
        assert config.max_content_size == 65536
    
    def test_below_min_raises_error(self):
        """max_content_size=1023 (below min) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(max_content_size=1023)
        
        error_msg = str(exc_info.value)
        assert "max_content_size" in error_msg
        assert "1023" in error_msg
        assert "1024" in error_msg
        assert "65536" in error_msg
    
    def test_above_max_raises_error(self):
        """max_content_size=65537 (above max) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(max_content_size=65537)
        
        error_msg = str(exc_info.value)
        assert "max_content_size" in error_msg
        assert "65537" in error_msg


# ============================================================================
# Test summary_max_length Validation
# ============================================================================

class TestSummaryMaxLengthValidation:
    """Test summary_max_length validation (valid: 100-2000)."""
    
    def test_min_boundary_valid(self):
        """summary_max_length=100 (min boundary) should be valid."""
        config = MemoryConfig(summary_max_length=100)
        assert config.summary_max_length == 100
    
    def test_max_boundary_valid(self):
        """summary_max_length=2000 (max boundary) should be valid."""
        config = MemoryConfig(summary_max_length=2000)
        assert config.summary_max_length == 2000
    
    def test_below_min_raises_error(self):
        """summary_max_length=99 (below min) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(summary_max_length=99)
        
        error_msg = str(exc_info.value)
        assert "summary_max_length" in error_msg
        assert "99" in error_msg
        assert "100" in error_msg
        assert "2000" in error_msg
    
    def test_above_max_raises_error(self):
        """summary_max_length=2001 (above max) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(summary_max_length=2001)
        
        error_msg = str(exc_info.value)
        assert "summary_max_length" in error_msg
        assert "2001" in error_msg


# ============================================================================
# Test context_load_timeout_ms Validation
# ============================================================================

class TestContextLoadTimeoutValidation:
    """Test context_load_timeout_ms validation (valid: 100-5000)."""
    
    def test_min_boundary_valid(self):
        """context_load_timeout_ms=100 (min boundary) should be valid."""
        config = MemoryConfig(context_load_timeout_ms=100)
        assert config.context_load_timeout_ms == 100
    
    def test_max_boundary_valid(self):
        """context_load_timeout_ms=5000 (max boundary) should be valid."""
        config = MemoryConfig(context_load_timeout_ms=5000)
        assert config.context_load_timeout_ms == 5000
    
    def test_below_min_raises_error(self):
        """context_load_timeout_ms=99 (below min) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(context_load_timeout_ms=99)
        
        error_msg = str(exc_info.value)
        assert "context_load_timeout_ms" in error_msg
        assert "99" in error_msg
        assert "100" in error_msg
        assert "5000" in error_msg
    
    def test_above_max_raises_error(self):
        """context_load_timeout_ms=5001 (above max) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(context_load_timeout_ms=5001)
        
        error_msg = str(exc_info.value)
        assert "context_load_timeout_ms" in error_msg
        assert "5001" in error_msg


# ============================================================================
# Test state_save_timeout_ms Validation
# ============================================================================

class TestStateSaveTimeoutValidation:
    """Test state_save_timeout_ms validation (valid: 10-500)."""
    
    def test_min_boundary_valid(self):
        """state_save_timeout_ms=10 (min boundary) should be valid."""
        config = MemoryConfig(state_save_timeout_ms=10)
        assert config.state_save_timeout_ms == 10
    
    def test_max_boundary_valid(self):
        """state_save_timeout_ms=500 (max boundary) should be valid."""
        config = MemoryConfig(state_save_timeout_ms=500)
        assert config.state_save_timeout_ms == 500
    
    def test_below_min_raises_error(self):
        """state_save_timeout_ms=9 (below min) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(state_save_timeout_ms=9)
        
        error_msg = str(exc_info.value)
        assert "state_save_timeout_ms" in error_msg
        assert "9" in error_msg
        assert "10" in error_msg
        assert "500" in error_msg
    
    def test_above_max_raises_error(self):
        """state_save_timeout_ms=501 (above max) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(state_save_timeout_ms=501)
        
        error_msg = str(exc_info.value)
        assert "state_save_timeout_ms" in error_msg
        assert "501" in error_msg


# ============================================================================
# Test Collection Name Validation
# ============================================================================

class TestCollectionNameValidation:
    """Test MongoDB collection name validation (non-empty strings)."""
    
    def test_valid_checkpoint_collection(self):
        """Valid checkpoint_collection name should be accepted."""
        config = MemoryConfig(checkpoint_collection="my_checkpoints")
        assert config.checkpoint_collection == "my_checkpoints"
    
    def test_valid_conversations_collection(self):
        """Valid conversations_collection name should be accepted."""
        config = MemoryConfig(conversations_collection="my_conversations")
        assert config.conversations_collection == "my_conversations"
    
    def test_empty_checkpoint_collection_raises_error(self):
        """Empty checkpoint_collection should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(checkpoint_collection="")
        
        error_msg = str(exc_info.value)
        assert "checkpoint_collection" in error_msg
        assert "non-empty" in error_msg.lower()
    
    def test_empty_conversations_collection_raises_error(self):
        """Empty conversations_collection should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(conversations_collection="")
        
        error_msg = str(exc_info.value)
        assert "conversations_collection" in error_msg
        assert "non-empty" in error_msg.lower()
    
    def test_whitespace_only_checkpoint_collection_raises_error(self):
        """Whitespace-only checkpoint_collection should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(checkpoint_collection="   ")
        
        error_msg = str(exc_info.value)
        assert "checkpoint_collection" in error_msg
        assert "non-empty" in error_msg.lower() or "blank" in error_msg.lower()
    
    def test_whitespace_only_conversations_collection_raises_error(self):
        """Whitespace-only conversations_collection should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(conversations_collection="\t\n")
        
        error_msg = str(exc_info.value)
        assert "conversations_collection" in error_msg
    
    def test_non_string_checkpoint_collection_raises_error(self):
        """Non-string checkpoint_collection should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(checkpoint_collection=123)  # type: ignore
        
        error_msg = str(exc_info.value)
        assert "checkpoint_collection" in error_msg
        assert "string" in error_msg.lower()
    
    def test_non_string_conversations_collection_raises_error(self):
        """Non-string conversations_collection should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(conversations_collection=None)  # type: ignore
        
        error_msg = str(exc_info.value)
        assert "conversations_collection" in error_msg


# ============================================================================
# Test enabled Validation
# ============================================================================

class TestEnabledValidation:
    """Test enabled field validation (boolean)."""
    
    def test_enabled_true_valid(self):
        """enabled=True should be valid."""
        config = MemoryConfig(enabled=True)
        assert config.enabled is True
    
    def test_enabled_false_valid(self):
        """enabled=False should be valid."""
        config = MemoryConfig(enabled=False)
        assert config.enabled is False
    
    def test_enabled_string_raises_error(self):
        """enabled='true' (string) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(enabled="true")  # type: ignore
        
        error_msg = str(exc_info.value)
        assert "enabled" in error_msg
        assert "boolean" in error_msg.lower()
    
    def test_enabled_int_raises_error(self):
        """enabled=1 (integer) should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(enabled=1)  # type: ignore
        
        error_msg = str(exc_info.value)
        assert "enabled" in error_msg


# ============================================================================
# Test from_config() Factory Method
# ============================================================================

class TestFromConfig:
    """Test MemoryConfig.from_config() factory method."""
    
    def test_empty_config_uses_defaults(self):
        """Empty config should use all default values."""
        config = MemoryConfig.from_config({})
        
        assert config.enabled is True
        assert config.summarize_threshold == 4000
        assert config.max_messages == 50
        assert config.messages_to_keep == 10
    
    def test_missing_langchain_section_uses_defaults(self):
        """Missing 'langchain' section should use defaults."""
        config_dict = {"other_section": {}}
        config = MemoryConfig.from_config(config_dict)
        
        assert config.enabled is True
        assert config.summarize_threshold == 4000
    
    def test_missing_memory_section_uses_defaults(self):
        """Missing 'memory' section under 'langchain' should use defaults."""
        config_dict = {"langchain": {"other": {}}}
        config = MemoryConfig.from_config(config_dict)
        
        assert config.enabled is True
        assert config.summarize_threshold == 4000
    
    def test_full_config_loads_all_values(self):
        """Full config should load all custom values."""
        config_dict = {
            "langchain": {
                "memory": {
                    "enabled": False,
                    "summarize_threshold": 5000,
                    "max_messages": 100,
                    "messages_to_keep": 20,
                    "max_content_size": 16384,
                    "summary_max_length": 800,
                    "context_load_timeout_ms": 1000,
                    "state_save_timeout_ms": 100,
                    "checkpoint_collection": "custom_checkpoints",
                    "conversations_collection": "custom_conversations",
                }
            }
        }
        config = MemoryConfig.from_config(config_dict)
        
        assert config.enabled is False
        assert config.summarize_threshold == 5000
        assert config.max_messages == 100
        assert config.messages_to_keep == 20
        assert config.max_content_size == 16384
        assert config.summary_max_length == 800
        assert config.context_load_timeout_ms == 1000
        assert config.state_save_timeout_ms == 100
        assert config.checkpoint_collection == "custom_checkpoints"
        assert config.conversations_collection == "custom_conversations"
    
    def test_partial_config_uses_defaults_for_missing(self):
        """Partial config should use defaults for missing values."""
        config_dict = {
            "langchain": {
                "memory": {
                    "enabled": False,
                    "summarize_threshold": 5000,
                }
            }
        }
        config = MemoryConfig.from_config(config_dict)
        
        assert config.enabled is False
        assert config.summarize_threshold == 5000
        assert config.max_messages == 50  # Default
        assert config.messages_to_keep == 10  # Default
    
    def test_from_config_validates_values(self):
        """from_config() should validate values and raise ValueError."""
        config_dict = {
            "langchain": {
                "memory": {
                    "summarize_threshold": 500,  # Below min of 1000
                }
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig.from_config(config_dict)
        
        assert "summarize_threshold" in str(exc_info.value)
    
    def test_from_config_none_values_use_defaults(self):
        """None values in config should use defaults."""
        config_dict = {
            "langchain": {
                "memory": {
                    "enabled": None,
                    "summarize_threshold": None,
                }
            }
        }
        config = MemoryConfig.from_config(config_dict)
        
        # None values should be skipped, using defaults
        assert config.enabled is True
        assert config.summarize_threshold == 4000


# ============================================================================
# Test disabled() Factory Method
# ============================================================================

class TestDisabledFactory:
    """Test MemoryConfig.disabled() factory method."""
    
    def test_disabled_returns_enabled_false(self):
        """disabled() should return config with enabled=False."""
        config = MemoryConfig.disabled()
        assert config.enabled is False
    
    def test_disabled_uses_default_values(self):
        """disabled() should use default values for other fields."""
        config = MemoryConfig.disabled()
        
        assert config.summarize_threshold == 4000
        assert config.max_messages == 50
        assert config.messages_to_keep == 10
        assert config.checkpoint_collection == "agent_checkpoints"
        assert config.conversations_collection == "conversations"
    
    def test_disabled_is_immutable(self):
        """disabled() config should be immutable."""
        config = MemoryConfig.disabled()
        
        with pytest.raises(AttributeError):
            config.enabled = True  # type: ignore


# ============================================================================
# Test to_dict() Serialization
# ============================================================================

class TestToDict:
    """Test MemoryConfig.to_dict() serialization."""
    
    def test_to_dict_includes_all_fields(self):
        """to_dict() should include all configuration fields."""
        config = MemoryConfig()
        result = config.to_dict()
        
        expected_keys = {
            "enabled",
            "summarize_threshold",
            "max_messages",
            "messages_to_keep",
            "max_content_size",
            "summary_max_length",
            "context_load_timeout_ms",
            "state_save_timeout_ms",
            "checkpoint_collection",
            "conversations_collection",
        }
        
        assert set(result.keys()) == expected_keys
    
    def test_to_dict_returns_correct_values(self):
        """to_dict() should return correct values."""
        config = MemoryConfig(
            enabled=False,
            summarize_threshold=5000,
            max_messages=100,
            messages_to_keep=20,
        )
        result = config.to_dict()
        
        assert result["enabled"] is False
        assert result["summarize_threshold"] == 5000
        assert result["max_messages"] == 100
        assert result["messages_to_keep"] == 20
    
    def test_to_dict_returns_dict_type(self):
        """to_dict() should return a dictionary."""
        config = MemoryConfig()
        result = config.to_dict()
        
        assert isinstance(result, dict)
    
    def test_to_dict_is_serializable(self):
        """to_dict() result should be JSON-serializable."""
        import json
        
        config = MemoryConfig()
        result = config.to_dict()
        
        # Should not raise
        json_str = json.dumps(result)
        assert json_str is not None


# ============================================================================
# Test VALIDATION_RANGES Constant
# ============================================================================

class TestValidationRanges:
    """Test VALIDATION_RANGES constant is correctly defined."""
    
    def test_validation_ranges_has_expected_keys(self):
        """VALIDATION_RANGES should have all expected parameter keys."""
        expected_keys = {
            "summarize_threshold",
            "max_messages",
            "messages_to_keep",
            "max_content_size",
            "summary_max_length",
            "context_load_timeout_ms",
            "state_save_timeout_ms",
        }
        
        assert set(VALIDATION_RANGES.keys()) == expected_keys
    
    def test_validation_ranges_values_are_tuples(self):
        """VALIDATION_RANGES values should be (min, max) tuples."""
        for key, value in VALIDATION_RANGES.items():
            assert isinstance(value, tuple), f"{key} should be tuple"
            assert len(value) == 2, f"{key} should have 2 elements"
            assert isinstance(value[0], int), f"{key} min should be int"
            assert isinstance(value[1], int), f"{key} max should be int"
    
    def test_validation_ranges_min_less_than_max(self):
        """VALIDATION_RANGES min should always be less than max."""
        for key, (min_val, max_val) in VALIDATION_RANGES.items():
            assert min_val < max_val, f"{key}: min ({min_val}) >= max ({max_val})"
    
    def test_summarize_threshold_range(self):
        """summarize_threshold range should be (1000, 10000)."""
        assert VALIDATION_RANGES["summarize_threshold"] == (1000, 10000)
    
    def test_max_messages_range(self):
        """max_messages range should be (10, 200)."""
        assert VALIDATION_RANGES["max_messages"] == (10, 200)
    
    def test_messages_to_keep_range(self):
        """messages_to_keep range should be (5, 50)."""
        assert VALIDATION_RANGES["messages_to_keep"] == (5, 50)
    
    def test_max_content_size_range(self):
        """max_content_size range should be (1024, 65536)."""
        assert VALIDATION_RANGES["max_content_size"] == (1024, 65536)
    
    def test_summary_max_length_range(self):
        """summary_max_length range should be (100, 2000)."""
        assert VALIDATION_RANGES["summary_max_length"] == (100, 2000)
    
    def test_context_load_timeout_ms_range(self):
        """context_load_timeout_ms range should be (100, 5000)."""
        assert VALIDATION_RANGES["context_load_timeout_ms"] == (100, 5000)
    
    def test_state_save_timeout_ms_range(self):
        """state_save_timeout_ms range should be (10, 500)."""
        assert VALIDATION_RANGES["state_save_timeout_ms"] == (10, 500)


# ============================================================================
# Test Error Message Quality
# ============================================================================

class TestErrorMessageQuality:
    """Test error messages are actionable per FR-3.1.10."""
    
    def test_error_includes_parameter_name(self):
        """Error message should include parameter name."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(summarize_threshold=500)
        
        assert "summarize_threshold" in str(exc_info.value)
    
    def test_error_includes_invalid_value(self):
        """Error message should include the invalid value."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(max_messages=5)
        
        assert "5" in str(exc_info.value)
    
    def test_error_includes_valid_range(self):
        """Error message should include valid range."""
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(context_load_timeout_ms=50)
        
        error_msg = str(exc_info.value)
        assert "100" in error_msg  # min
        assert "5000" in error_msg  # max
    
    def test_error_indicates_below_or_above(self):
        """Error message should indicate if value is below or above range."""
        # Test below
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(state_save_timeout_ms=5)
        assert "below" in str(exc_info.value).lower()
        
        # Test above
        with pytest.raises(ValueError) as exc_info:
            MemoryConfig(state_save_timeout_ms=600)
        assert "above" in str(exc_info.value).lower()


# ============================================================================
# Test Boolean Edge Cases
# ============================================================================

class TestBooleanEdgeCases:
    """Test edge cases for boolean type validation."""
    
    def test_boolean_true_as_int_zero_raises_error(self):
        """enabled=0 should raise ValueError (not treated as False)."""
        # Note: In Python, bool is subclass of int, so isinstance(True, int) is True
        # The implementation should explicitly check for bool type
        with pytest.raises(ValueError):
            MemoryConfig(enabled=0)  # type: ignore
    
    def test_enabled_none_raises_error(self):
        """enabled=None should raise ValueError."""
        with pytest.raises(ValueError):
            MemoryConfig(enabled=None)  # type: ignore


# ============================================================================
# Test Combination Constraints
# ============================================================================

class TestCombinationConstraints:
    """Test constraints that involve multiple parameters."""
    
    def test_messages_to_keep_at_boundary_with_max_messages_at_boundary(self):
        """Test messages_to_keep=50 with max_messages=51 (edge case)."""
        config = MemoryConfig(messages_to_keep=50, max_messages=51)
        assert config.messages_to_keep == 50
        assert config.max_messages == 51
    
    def test_messages_to_keep_at_min_with_max_messages_at_min(self):
        """Test messages_to_keep=5 with max_messages=10 (both at minimum)."""
        config = MemoryConfig(messages_to_keep=5, max_messages=10)
        assert config.messages_to_keep == 5
        assert config.max_messages == 10
    
    def test_all_parameters_at_minimum_valid(self):
        """All parameters at minimum boundaries should be valid."""
        config = MemoryConfig(
            summarize_threshold=1000,
            max_messages=10,
            messages_to_keep=5,
            max_content_size=1024,
            summary_max_length=100,
            context_load_timeout_ms=100,
            state_save_timeout_ms=10,
        )
        
        assert config.summarize_threshold == 1000
        assert config.max_messages == 10
        assert config.messages_to_keep == 5
    
    def test_all_parameters_at_maximum_valid(self):
        """All parameters at maximum boundaries should be valid (except messages_to_keep constraint)."""
        config = MemoryConfig(
            summarize_threshold=10000,
            max_messages=200,
            messages_to_keep=50,  # Must be < max_messages, so use 50 (max for this field)
            max_content_size=65536,
            summary_max_length=2000,
            context_load_timeout_ms=5000,
            state_save_timeout_ms=500,
        )
        
        assert config.summarize_threshold == 10000
        assert config.max_messages == 200
        assert config.messages_to_keep == 50


# ============================================================================
# ContentValidator Tests (Task T027)
# ============================================================================

class TestContentValidatorDollarAmounts:
    """Test ContentValidator detects dollar amount patterns."""
    
    def test_detects_simple_dollar_amount(self):
        """Should detect $150."""
        violations = ContentValidator.scan_prohibited_patterns("The stock is $150")
        assert "$150" in violations
    
    def test_detects_dollar_with_decimals(self):
        """Should detect $150.00."""
        violations = ContentValidator.scan_prohibited_patterns("Price is $150.00")
        assert "$150.00" in violations
    
    def test_detects_dollar_with_commas(self):
        """Should detect $1,234.56."""
        violations = ContentValidator.scan_prohibited_patterns("Market cap $1,234.56")
        assert "$1,234.56" in violations
    
    def test_detects_large_dollar_amount(self):
        """Should detect $1,234,567.89."""
        violations = ContentValidator.scan_prohibited_patterns("Revenue: $1,234,567.89")
        assert "$1,234,567.89" in violations
    
    def test_detects_multiple_dollar_amounts(self):
        """Should detect multiple dollar amounts."""
        content = "Stock went from $100 to $150"
        violations = ContentValidator.scan_prohibited_patterns(content)
        assert "$100" in violations
        assert "$150" in violations


class TestContentValidatorPercentages:
    """Test ContentValidator detects percentage patterns."""
    
    def test_detects_simple_percentage(self):
        """Should detect 15%."""
        violations = ContentValidator.scan_prohibited_patterns("Yield is 15%")
        assert "15%" in violations
    
    def test_detects_decimal_percentage(self):
        """Should detect 15.5%."""
        violations = ContentValidator.scan_prohibited_patterns("Growth rate 15.5%")
        assert "15.5%" in violations
    
    def test_detects_negative_percentage(self):
        """Should detect -3.2%."""
        violations = ContentValidator.scan_prohibited_patterns("Stock fell -3.2%")
        assert "-3.2%" in violations
    
    def test_detects_hundred_percent(self):
        """Should detect 100%."""
        violations = ContentValidator.scan_prohibited_patterns("Utilization at 100%")
        assert "100%" in violations


class TestContentValidatorPERatios:
    """Test ContentValidator detects P/E ratio patterns."""
    
    def test_detects_pe_with_slash(self):
        """Should detect P/E 25."""
        violations = ContentValidator.scan_prohibited_patterns("The P/E 25 is high")
        assert any("25" in v for v in violations)
    
    def test_detects_pe_without_slash(self):
        """Should detect PE 25.5."""
        violations = ContentValidator.scan_prohibited_patterns("PE 25.5 indicates")
        assert any("25.5" in v for v in violations)
    
    def test_detects_pe_ratio_text(self):
        """Should detect P/E ratio 30."""
        violations = ContentValidator.scan_prohibited_patterns("P/E ratio 30 is average")
        assert any("30" in v for v in violations)
    
    def test_detects_pe_ratio_with_colon(self):
        """Should detect PE ratio: 25."""
        violations = ContentValidator.scan_prohibited_patterns("PE ratio: 25")
        assert any("25" in v for v in violations)


class TestContentValidatorPriceContext:
    """Test ContentValidator detects price context patterns."""
    
    def test_detects_price_at(self):
        """Should detect 'price at' patterns."""
        violations = ContentValidator.scan_prohibited_patterns("price at 150.00")
        assert len(violations) > 0
    
    def test_detects_trading_at(self):
        """Should detect 'trading at' patterns."""
        violations = ContentValidator.scan_prohibited_patterns("AAPL trading at 175.50")
        assert len(violations) > 0
    
    def test_detects_priced_at(self):
        """Should detect 'priced at' patterns."""
        violations = ContentValidator.scan_prohibited_patterns("stock priced at $50")
        assert len(violations) > 0


class TestContentValidatorMarketCap:
    """Test ContentValidator detects market cap patterns."""
    
    def test_detects_market_cap_billions(self):
        """Should detect market cap $500B."""
        violations = ContentValidator.scan_prohibited_patterns("market cap $500B")
        assert len(violations) > 0
    
    def test_detects_market_cap_trillions(self):
        """Should detect market cap $1.5T."""
        violations = ContentValidator.scan_prohibited_patterns("market cap: $1.5T")
        assert len(violations) > 0


class TestContentValidatorEPS:
    """Test ContentValidator detects EPS patterns."""
    
    def test_detects_eps_dollar(self):
        """Should detect EPS $1.50."""
        violations = ContentValidator.scan_prohibited_patterns("EPS $1.50")
        assert len(violations) > 0
    
    def test_detects_eps_with_colon(self):
        """Should detect EPS: 2.30."""
        violations = ContentValidator.scan_prohibited_patterns("EPS: 2.30")
        assert len(violations) > 0


class TestContentValidatorDividend:
    """Test ContentValidator detects dividend yield patterns."""
    
    def test_detects_dividend_yield_percent(self):
        """Should detect dividend yield 2.5%."""
        violations = ContentValidator.scan_prohibited_patterns("dividend yield 2.5%")
        assert len(violations) > 0
    
    def test_detects_yield_percent(self):
        """Should detect yield: 3%."""
        violations = ContentValidator.scan_prohibited_patterns("yield: 3%")
        assert len(violations) > 0


class TestContentValidatorCompliant:
    """Test ContentValidator returns empty list for compliant content."""
    
    def test_empty_string_is_compliant(self):
        """Empty string should return no violations."""
        violations = ContentValidator.scan_prohibited_patterns("")
        assert violations == []
    
    def test_none_like_empty_is_compliant(self):
        """None converted to empty should be handled gracefully."""
        # Empty string should not raise
        violations = ContentValidator.scan_prohibited_patterns("")
        assert violations == []
    
    def test_simple_question_is_compliant(self):
        """Simple user question should be compliant."""
        violations = ContentValidator.scan_prohibited_patterns("What is AAPL?")
        assert violations == []
    
    def test_stock_symbol_only_is_compliant(self):
        """Stock symbol mention should be compliant."""
        violations = ContentValidator.scan_prohibited_patterns("User asked about AAPL trends")
        assert violations == []
    
    def test_general_analysis_request_is_compliant(self):
        """General analysis request should be compliant."""
        content = "Can you analyze the technical indicators for MSFT?"
        violations = ContentValidator.scan_prohibited_patterns(content)
        assert violations == []
    
    def test_tool_reference_is_compliant(self):
        """Tool reference without data should be compliant."""
        content = "Called get_stock_price tool for AAPL"
        violations = ContentValidator.scan_prohibited_patterns(content)
        assert violations == []


class TestContentValidatorIsCompliant:
    """Test ContentValidator.is_compliant() convenience method."""
    
    def test_is_compliant_returns_true_for_clean_content(self):
        """is_compliant() should return True for content without violations."""
        assert ContentValidator.is_compliant("User asked about AAPL")
    
    def test_is_compliant_returns_false_for_violations(self):
        """is_compliant() should return False for content with violations."""
        assert not ContentValidator.is_compliant("AAPL price is $150")
    
    def test_is_compliant_returns_true_for_empty_string(self):
        """is_compliant() should return True for empty string."""
        assert ContentValidator.is_compliant("")


class TestContentValidatorEdgeCases:
    """Test ContentValidator edge cases and deduplication."""
    
    def test_removes_duplicate_violations(self):
        """Should not return duplicate violations."""
        content = "Price $150, again $150"
        violations = ContentValidator.scan_prohibited_patterns(content)
        # Count occurrences of $150
        count = sum(1 for v in violations if v == "$150")
        assert count == 1
    
    def test_multiple_different_patterns(self):
        """Should detect multiple different violation types."""
        content = "AAPL at $150 with P/E 25 and yield 2.5%"
        violations = ContentValidator.scan_prohibited_patterns(content)
        # Should have dollar, P/E, and percentage violations
        assert len(violations) >= 3
