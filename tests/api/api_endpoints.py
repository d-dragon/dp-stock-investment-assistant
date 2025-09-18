import json
import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from web.routes.api_routes import create_api_blueprint, APIRouteContext

@pytest.fixture
def mock_context():
    """Fixture to create a mocked APIRouteContext."""
    app = Flask(__name__)
    agent = MagicMock()
    config = {
        'model': {'provider': 'openai', 'name': 'gpt-4'},
        'financial_apis': {
            'yahoo_finance': {'enabled': True},
            'alpha_vantage': {'enabled': False}
        }
    }
    logger = MagicMock()
    stream_chat_response = MagicMock(return_value=['data: {"chunk": "test"}\n\n'])
    extract_meta = MagicMock(return_value=('openai', 'gpt-4', False))
    strip_fallback_prefix = MagicMock(return_value='clean response')
    get_timestamp = MagicMock(return_value='2025-09-16T12:34:56Z')
    
    return APIRouteContext(
        app=app,
        agent=agent,
        config=config,
        logger=logger,
        stream_chat_response=stream_chat_response,
        extract_meta=extract_meta,
        strip_fallback_prefix=strip_fallback_prefix,
        get_timestamp=get_timestamp
    )

@pytest.fixture
def client(mock_context):
    """Fixture to create a test client for the blueprint."""
    blueprint = create_api_blueprint(mock_context)
    app = mock_context.app
    app.register_blueprint(blueprint, url_prefix='/api')
    return app.test_client()

def test_health_check(client):
    """Test GET /api/health."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {'status': 'healthy', 'message': 'Stock Investment Assistant API is running'}

def test_chat_non_streaming_success(client, mock_context):
    """Test POST /api/chat (non-streaming)."""
    mock_context.agent.process_query.return_value = 'raw response'
    payload = {'message': 'Test query', 'stream': False}
    response = client.post('/api/chat', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    assert data['response'] == 'clean response'
    mock_context.agent.process_query.assert_called_once_with('Test query', provider=None)

def test_chat_streaming(client, mock_context):
    """Test POST /api/chat (streaming)."""
    payload = {'message': 'Test query', 'stream': True}
    response = client.post('/api/chat', json=payload)
    assert response.status_code == 200
    assert response.mimetype == 'text/event-stream'
    # Check if streaming generator is called
    mock_context.stream_chat_response.assert_called_once_with('Test query', None)

def test_chat_missing_message(client):
    """Test POST /api/chat with missing message."""
    payload = {}
    response = client.post('/api/chat', json=payload)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data == {'error': 'Message is required'}

def test_chat_empty_message(client):
    """Test POST /api/chat with empty message."""
    payload = {'message': ''}
    response = client.post('/api/chat', json=payload)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data == {'error': 'Message cannot be empty'}

def test_chat_with_provider_override(client, mock_context):
    """Test POST /api/chat with provider override."""
    mock_context.agent.process_query.return_value = 'raw response'
    payload = {'message': 'Test query', 'provider': 'anthropic'}
    response = client.post('/api/chat', json=payload)
    assert response.status_code == 200
    mock_context.agent.process_query.assert_called_once_with('Test query', provider='anthropic')

def test_chat_internal_error(client, mock_context):
    """Test POST /api/chat with internal error."""
    mock_context.agent.process_query.side_effect = Exception('Test error')
    payload = {'message': 'Test query'}
    response = client.post('/api/chat', json=payload)
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data == {'error': 'Internal server error'}

def test_get_config(client, mock_context):
    """Test GET /api/config."""
    response = client.get('/api/config')
    assert response.status_code == 200
    data = json.loads(response.data)
    expected = {
        'model': {'provider': 'openai', 'name': 'gpt-4'},
        'features': {'yahoo_finance': True, 'alpha_vantage': False}
    }
    assert data == expected