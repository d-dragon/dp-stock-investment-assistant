"""
Basic Flask Blueprint Pattern Example

Demonstrates the minimal blueprint creation pattern with APIRouteContext
dependency injection as documented in backend-python.instructions.md.

Usage:
    python examples/flask_blueprints/basic_blueprint.py
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

from flask import Blueprint, Flask, jsonify, request

if TYPE_CHECKING:
    from logging import Logger


@dataclass(frozen=True)
class APIRouteContext:
    """Immutable context for HTTP route blueprints."""
    app: "Flask"
    config: Mapping[str, Any]
    logger: "Logger"


def create_example_blueprint(context: APIRouteContext) -> Blueprint:
    """
    Factory function that creates a blueprint with dependency injection.
    
    Pattern:
    - Blueprint created inside factory function
    - Context unpacked at function level
    - Route handlers are closures with access to context
    - Returns configured blueprint ready for registration
    """
    blueprint = Blueprint("example", __name__)
    config = context.config
    logger = context.logger.getChild("example")
    
    @blueprint.route('/hello', methods=['GET'])
    def hello():
        """Simple GET endpoint."""
        name = request.args.get('name', 'World')
        logger.info(f"Hello request received: name={name}")
        return jsonify({"message": f"Hello, {name}!"}), 200
    
    @blueprint.route('/data', methods=['POST'])
    def create_data():
        """POST endpoint with JSON body validation."""
        data = request.get_json()
        
        # Validate required fields
        if not data or 'value' not in data:
            logger.warning("Invalid request: missing 'value' field")
            return jsonify({"error": "'value' field is required"}), 400
        
        # Process data (in real app, delegate to service)
        result = {"id": "123", "value": data['value'], "status": "created"}
        logger.info(f"Data created: {result}")
        
        return jsonify(result), 201
    
    @blueprint.route('/config', methods=['GET'])
    def get_config():
        """Endpoint demonstrating config access."""
        # Access config from context (read-only via Mapping)
        app_name = config.get('app', {}).get('name', 'Unknown')
        return jsonify({"app_name": app_name}), 200
    
    return blueprint


def register_blueprint_example(app: Flask, context: APIRouteContext) -> None:
    """
    Registration pattern used in src/web/api_server.py.
    
    Pattern:
    - Create blueprint from context
    - Register with app using url_prefix
    - All routes automatically prefixed (/api/hello, /api/data, /api/config)
    """
    blueprint = create_example_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")


if __name__ == "__main__":
    import logging
    
    # Demo setup
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    app = Flask(__name__)
    context = APIRouteContext(
        app=app,
        config={"app": {"name": "Example App"}},
        logger=logger,
    )
    
    register_blueprint_example(app, context)
    
    print("Blueprint registered successfully!")
    print("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    print("\nRun with: flask run")
    print("Test with: curl http://localhost:5000/api/hello?name=Alice")
