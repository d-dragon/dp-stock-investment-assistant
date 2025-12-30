"""
Flask API Route Testing Patterns

Demonstrates comprehensive testing patterns for Flask API routes,
including test client usage, request/response validation, error handling,
and mock integration.

Reference: backend-python.instructions.md § Testing > Testing Flask API Routes
"""

import pytest
import json
from typing import Any, Dict
from unittest.mock import MagicMock, patch
from flask import Flask, Blueprint, jsonify, request


# ============================================================================
# EXAMPLE FLASK ROUTES (for testing)
# ============================================================================

def create_test_app(mock_agent=None, mock_service=None) -> Flask:
    """
    Create Flask app for testing.
    
    Args:
        mock_agent: Optional mock agent for chat routes
        mock_service: Optional mock service for data routes
    
    Returns:
        Configured Flask app with test routes
    """
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy", "service": "test-api"}), 200
    
    # Chat route with agent dependency
    @app.route('/api/chat', methods=['POST'])
    def chat():
        data = request.get_json()
        
        # Validate required fields
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Process with agent
        if mock_agent is None:
            return jsonify({"error": "Service unavailable"}), 503
        
        try:
            response = mock_agent.process_query(message)
            provider = data.get('provider', 'openai')
            
            return jsonify({
                "response": response,
                "provider": provider,
                "model": "gpt-4"
            }), 200
        
        except Exception as e:
            app.logger.error(f"Chat error: {e}")
            return jsonify({"error": "Failed to process message"}), 500
    
    # Data route with service dependency
    @app.route('/api/users/<user_id>', methods=['GET'])
    def get_user(user_id: str):
        if mock_service is None:
            return jsonify({"error": "Service unavailable"}), 503
        
        try:
            user = mock_service.get_user(user_id)
            
            if user is None:
                return jsonify({"error": "User not found"}), 404
            
            return jsonify(user), 200
        
        except Exception as e:
            app.logger.error(f"Get user error: {e}")
            return jsonify({"error": "Failed to retrieve user"}), 500
    
    # Update route with validation
    @app.route('/api/users/<user_id>', methods=['PUT'])
    def update_user(user_id: str):
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        if mock_service is None:
            return jsonify({"error": "Service unavailable"}), 503
        
        try:
            updated_user = mock_service.update_user(user_id, data)
            
            if updated_user is None:
                return jsonify({"error": "User not found"}), 404
            
            return jsonify(updated_user), 200
        
        except ValueError as e:
            app.logger.error(f"Validation error updating user {user_id}: {e}")
            return jsonify({"error": "Invalid user data"}), 400
        except Exception as e:
            app.logger.error(f"Update user error: {e}")
            return jsonify({"error": "Failed to update user"}), 500
    
    return app


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_agent():
    """Mock agent for chat routes."""
    agent = MagicMock()
    agent.process_query.return_value = "This is a test response from the agent"
    return agent


@pytest.fixture
def mock_user_service():
    """Mock user service for data routes."""
    service = MagicMock()
    
    # Default behavior
    service.get_user.return_value = {
        "_id": "user123",
        "email": "test@example.com",
        "name": "Test User"
    }
    
    service.update_user.return_value = {
        "_id": "user123",
        "email": "test@example.com",
        "name": "Updated User"
    }
    
    return service


@pytest.fixture
def app_with_agent(mock_agent):
    """Flask app with mock agent."""
    return create_test_app(mock_agent=mock_agent)


@pytest.fixture
def app_with_service(mock_user_service):
    """Flask app with mock service."""
    return create_test_app(mock_service=mock_user_service)


@pytest.fixture
def app_with_both(mock_agent, mock_user_service):
    """Flask app with both mocks."""
    return create_test_app(mock_agent=mock_agent, mock_service=mock_user_service)


@pytest.fixture
def client(app_with_both):
    """Flask test client."""
    return app_with_both.test_client()


# ============================================================================
# TESTS: HEALTH CHECK ENDPOINT
# ============================================================================

def test_health_endpoint_returns_200(client):
    """Test /api/health returns 200 status code."""
    response = client.get('/api/health')
    assert response.status_code == 200


def test_health_endpoint_returns_json(client):
    """Test /api/health returns JSON content type."""
    response = client.get('/api/health')
    assert response.content_type == 'application/json'


def test_health_endpoint_returns_healthy_status(client):
    """Test /api/health returns expected status."""
    response = client.get('/api/health')
    data = response.get_json()
    
    assert data['status'] == 'healthy'
    assert data['service'] == 'test-api'


# ============================================================================
# TESTS: CHAT ENDPOINT - SUCCESS CASES
# ============================================================================

def test_chat_endpoint_processes_message(app_with_agent, mock_agent):
    """Test /api/chat processes valid message."""
    client = app_with_agent.test_client()
    
    response = client.post('/api/chat', json={
        'message': 'What is the price of AAPL?',
        'provider': 'openai'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'response' in data
    assert data['response'] == "This is a test response from the agent"
    assert data['provider'] == 'openai'
    assert data['model'] == 'gpt-4'
    
    # Verify agent was called
    mock_agent.process_query.assert_called_once_with('What is the price of AAPL?')


def test_chat_endpoint_uses_default_provider(app_with_agent, mock_agent):
    """Test /api/chat uses default provider when not specified."""
    client = app_with_agent.test_client()
    
    response = client.post('/api/chat', json={
        'message': 'Test message'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['provider'] == 'openai'  # Default


def test_chat_endpoint_strips_whitespace(app_with_agent, mock_agent):
    """Test /api/chat strips leading/trailing whitespace from message."""
    client = app_with_agent.test_client()
    
    response = client.post('/api/chat', json={
        'message': '  Test message  '
    })
    
    assert response.status_code == 200
    
    # Verify whitespace was stripped before calling agent
    mock_agent.process_query.assert_called_once_with('Test message')


# ============================================================================
# TESTS: CHAT ENDPOINT - VALIDATION ERRORS
# ============================================================================

def test_chat_endpoint_requires_message_field(app_with_agent):
    """Test /api/chat returns 400 when message field missing."""
    client = app_with_agent.test_client()
    
    response = client.post('/api/chat', json={})
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert 'error' in data
    assert 'required' in data['error'].lower()


def test_chat_endpoint_rejects_empty_message(app_with_agent):
    """Test /api/chat returns 400 when message is empty."""
    client = app_with_agent.test_client()
    
    response = client.post('/api/chat', json={
        'message': '   '  # Only whitespace
    })
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert 'error' in data
    assert 'empty' in data['error'].lower()


def test_chat_endpoint_requires_json_body(app_with_agent):
    """Test /api/chat returns 400 when request body is not JSON."""
    client = app_with_agent.test_client()
    
    response = client.post('/api/chat', data='not json')
    
    assert response.status_code == 400


# ============================================================================
# TESTS: CHAT ENDPOINT - ERROR HANDLING
# ============================================================================

def test_chat_endpoint_returns_503_when_agent_unavailable():
    """Test /api/chat returns 503 when agent is None."""
    app = create_test_app(mock_agent=None)  # No agent
    client = app.test_client()
    
    response = client.post('/api/chat', json={
        'message': 'Test message'
    })
    
    assert response.status_code == 503
    data = response.get_json()
    
    assert 'error' in data
    assert 'unavailable' in data['error'].lower()


def test_chat_endpoint_returns_500_on_agent_exception(app_with_agent, mock_agent):
    """Test /api/chat returns 500 when agent raises exception."""
    client = app_with_agent.test_client()
    
    # Make agent raise exception
    mock_agent.process_query.side_effect = RuntimeError("Agent processing failed")
    
    response = client.post('/api/chat', json={
        'message': 'Test message'
    })
    
    assert response.status_code == 500
    data = response.get_json()
    
    assert 'error' in data
    assert 'failed' in data['error'].lower()
    
    # Exception details should NOT be exposed to client
    assert 'RuntimeError' not in str(data)


# ============================================================================
# TESTS: USER ENDPOINT - SUCCESS CASES
# ============================================================================

def test_get_user_returns_user_data(app_with_service, mock_user_service):
    """Test /api/users/<id> returns user data."""
    client = app_with_service.test_client()
    
    response = client.get('/api/users/user123')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['_id'] == 'user123'
    assert data['email'] == 'test@example.com'
    assert data['name'] == 'Test User'
    
    # Verify service was called with correct ID
    mock_user_service.get_user.assert_called_once_with('user123')


def test_update_user_updates_and_returns_user(app_with_service, mock_user_service):
    """Test PUT /api/users/<id> updates user and returns updated data."""
    client = app_with_service.test_client()
    
    update_data = {"name": "New Name"}
    response = client.put('/api/users/user123', json=update_data)
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['name'] == 'Updated User'
    
    # Verify service was called with correct parameters
    mock_user_service.update_user.assert_called_once_with('user123', update_data)


# ============================================================================
# TESTS: USER ENDPOINT - ERROR CASES
# ============================================================================

def test_get_user_returns_404_when_user_not_found(app_with_service, mock_user_service):
    """Test /api/users/<id> returns 404 when user doesn't exist."""
    client = app_with_service.test_client()
    
    # Make service return None
    mock_user_service.get_user.return_value = None
    
    response = client.get('/api/users/nonexistent')
    
    assert response.status_code == 404
    data = response.get_json()
    
    assert 'error' in data
    assert 'not found' in data['error'].lower()


def test_update_user_returns_404_when_user_not_found(app_with_service, mock_user_service):
    """Test PUT /api/users/<id> returns 404 when user doesn't exist."""
    client = app_with_service.test_client()
    
    # Make service return None
    mock_user_service.update_user.return_value = None
    
    response = client.put('/api/users/nonexistent', json={"name": "Test"})
    
    assert response.status_code == 404


def test_update_user_returns_400_on_validation_error(app_with_service, mock_user_service):
    """Test PUT /api/users/<id> returns 400 when service raises ValueError."""
    client = app_with_service.test_client()
    
    # Make service raise ValueError
    mock_user_service.update_user.side_effect = ValueError("Invalid email format")
    
    response = client.put('/api/users/user123', json={"email": "invalid"})
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert 'error' in data
    assert 'Invalid email format' in data['error']


def test_update_user_requires_json_body(app_with_service):
    """Test PUT /api/users/<id> returns 400 when body missing."""
    client = app_with_service.test_client()
    
    response = client.put('/api/users/user123')
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert 'error' in data
    assert 'required' in data['error'].lower()


# ============================================================================
# TESTS: SERVICE AVAILABILITY
# ============================================================================

def test_routes_return_503_when_service_unavailable():
    """Test routes return 503 when dependencies are None."""
    app = create_test_app(mock_agent=None, mock_service=None)
    client = app.test_client()
    
    # Chat route
    response = client.post('/api/chat', json={'message': 'test'})
    assert response.status_code == 503
    
    # User route
    response = client.get('/api/users/user123')
    assert response.status_code == 503


# ============================================================================
# TESTS: CONTENT TYPE VALIDATION
# ============================================================================

def test_endpoints_return_json_content_type(client):
    """Test all endpoints return JSON content type."""
    # Health check
    response = client.get('/api/health')
    assert 'application/json' in response.content_type
    
    # Chat
    response = client.post('/api/chat', json={'message': 'test'})
    assert 'application/json' in response.content_type
    
    # Get user
    response = client.get('/api/users/user123')
    assert 'application/json' in response.content_type


# ============================================================================
# BEST PRACTICES DEMONSTRATION
# ============================================================================

def demonstrate_api_testing_best_practices():
    """Display API testing best practices."""
    
    print("=" * 60)
    print("FLASK API ROUTE TESTING BEST PRACTICES")
    print("=" * 60)
    
    practices = [
        {
            "practice": "Use Test Client",
            "pattern": "client = app.test_client()",
            "benefit": "Simulates HTTP requests without running server"
        },
        {
            "practice": "Mock Dependencies",
            "pattern": "@pytest.fixture def mock_agent(): return MagicMock()",
            "benefit": "Isolate route logic from external dependencies"
        },
        {
            "practice": "Test Success Paths",
            "pattern": "test_chat_endpoint_processes_message",
            "benefit": "Verify happy path functionality"
        },
        {
            "practice": "Test Validation Errors",
            "pattern": "test_chat_endpoint_requires_message_field",
            "benefit": "Ensure proper input validation"
        },
        {
            "practice": "Test Error Handling",
            "pattern": "test_chat_endpoint_returns_500_on_agent_exception",
            "benefit": "Verify graceful error handling"
        },
        {
            "practice": "Test Status Codes",
            "pattern": "assert response.status_code == 200",
            "benefit": "Validate HTTP semantics"
        },
        {
            "practice": "Test Response Format",
            "pattern": "data = response.get_json(); assert 'response' in data",
            "benefit": "Verify response structure"
        },
        {
            "practice": "Verify Mock Calls",
            "pattern": "mock_agent.process_query.assert_called_once_with('message')",
            "benefit": "Ensure dependencies called correctly"
        },
    ]
    
    for i, item in enumerate(practices, 1):
        print(f"\n{i}. {item['practice']}")
        print(f"   Pattern: {item['pattern']}")
        print(f"   Benefit: {item['benefit']}")


if __name__ == "__main__":
    print("Flask API Route Testing Patterns")
    print("=" * 60)
    print("\nDemonstrates comprehensive testing patterns for Flask API")
    print("routes using test client, mocks, and pytest fixtures.\n")
    
    demonstrate_api_testing_best_practices()
    
    print("\n" + "=" * 60)
    print("TEST COVERAGE CHECKLIST")
    print("=" * 60)
    print("✅ Success cases: Valid requests return expected responses")
    print("✅ Validation errors: Missing/invalid inputs return 400")
    print("✅ Not found errors: Non-existent resources return 404")
    print("✅ Server errors: Exceptions return 500 with safe messages")
    print("✅ Service unavailable: Missing dependencies return 503")
    print("✅ Content type: All responses are JSON")
    print("✅ Mock verification: Dependencies called with correct params")
    print("✅ Security: No internal details exposed in error responses")
    
    print("\n📖 Reference: backend-python.instructions.md")
    print("   § Testing with pytest > Testing Flask API Routes")
