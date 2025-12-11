"""
Frozen Dataclass Context Pattern for Dependency Injection

Demonstrates why we use frozen=True and how it prevents accidental mutation.

Reference: backend-python.instructions.md § Flask API Patterns
"""

from dataclasses import dataclass, FrozenInstanceError
from typing import Any, Dict, Mapping


@dataclass(frozen=True)
class FrozenContext:
    """Immutable context - cannot be modified after creation."""
    config: Mapping[str, Any]
    data: Dict[str, Any]  # Note: Dict is mutable, but reference is frozen


@dataclass(frozen=False)
class MutableContext:
    """Regular dataclass - can be modified anywhere."""
    config: Dict[str, Any]
    data: Dict[str, Any]


def demonstrate_frozen_safety():
    """Show how frozen=True prevents bugs."""
    
    print("=" * 60)
    print("FROZEN CONTEXT PATTERN DEMONSTRATION")
    print("=" * 60)
    
    # Create frozen context
    frozen = FrozenContext(
        config={"api_key": "secret123", "timeout": 30},
        data={"count": 0}
    )
    
    print("\n1. Frozen context created:")
    print(f"   config: {frozen.config}")
    print(f"   data: {frozen.data}")
    
    # Try to reassign attribute (WILL FAIL)
    print("\n2. Attempting to reassign frozen.config...")
    try:
        frozen.config = {"new": "value"}  # type: ignore
        print("   ❌ Assignment succeeded (BAD!)")
    except FrozenInstanceError as e:
        print(f"   ✅ Assignment blocked: {e}")
    
    # Mutable data inside can still be modified (reference is frozen, not content)
    print("\n3. Modifying mutable dict inside frozen context...")
    frozen.data["count"] = 10  # This works (dict is mutable)
    print(f"   frozen.data: {frozen.data}")
    print("   ⚠️  Dict content CAN be modified (use Mapping[str, Any] for read-only)")
    
    # Compare with mutable context
    print("\n4. Creating mutable context for comparison...")
    mutable = MutableContext(
        config={"api_key": "secret123", "timeout": 30},
        data={"count": 0}
    )
    
    # Reassignment works (DANGEROUS in large codebase)
    print("\n5. Attempting to reassign mutable.config...")
    mutable.config = {"oops": "accidentally_replaced"}
    print(f"   ❌ Assignment succeeded: {mutable.config}")
    print("   This can cause hard-to-debug issues!")
    
    # Best practice: Use Mapping for truly immutable config
    print("\n6. BEST PRACTICE: Use Mapping[str, Any] for config")
    print("   - Frozen dataclass prevents attribute reassignment")
    print("   - Mapping type hint signals read-only intent")
    print("   - Combine both for maximum safety")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ frozen=True prevents: context.config = new_dict")
    print("⚠️  Does NOT prevent: context.data['key'] = value (if Dict)")
    print("✅ Use Mapping[str, Any] to signal read-only config")
    print("✅ Benefits: Thread-safe, prevents accidental mutation bugs")


def demonstrate_context_usage_in_blueprint():
    """Show how context is used in actual blueprint factories."""
    
    print("\n" + "=" * 60)
    print("BLUEPRINT FACTORY PATTERN")
    print("=" * 60)
    
    from flask import Blueprint, jsonify
    
    @dataclass(frozen=True)
    class RouteContext:
        """Matches APIRouteContext in src/web/routes/shared_context.py"""
        config: Mapping[str, Any]
        logger: Any  # logging.Logger
    
    def create_safe_blueprint(context: RouteContext) -> Blueprint:
        """
        Factory pattern ensures:
        1. Context cannot be reassigned
        2. Each blueprint gets consistent dependencies
        3. Testing is easy (just pass mock context)
        """
        bp = Blueprint("safe", __name__)
        
        # Unpack at function level (not in route handlers)
        config = context.config
        logger = context.logger
        
        @bp.route('/status')
        def status():
            # Access unpacked variables (closure)
            # Cannot accidentally do: context.config = something_else
            app_name = config.get("app_name", "Unknown")
            logger.info(f"Status check for {app_name}")
            return jsonify({"status": "ok", "app": app_name})
        
        return bp
    
    print("\n✅ Pattern enforces:")
    print("   1. Immutable dependency injection")
    print("   2. Clear dependency boundaries")
    print("   3. Easy testing with mock contexts")
    print("   4. Thread-safe blueprint creation")


if __name__ == "__main__":
    demonstrate_frozen_safety()
    demonstrate_context_usage_in_blueprint()
