"""
Flask API server for Stock Investment Assistant.
Provides REST API endpoints for the React frontend.
"""

import logging
import json
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os
import time
from datetime import datetime, timezone

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.agent import StockAgent
from core.data_manager import DataManager
from core.model_factory import ModelClientFactory  # new import
from utils.config_loader import ConfigLoader


class APIServer:
    """Flask API server for the Stock Investment Assistant."""
    
    def __init__(self, app=None, *args, **kwargs):
        """Initialize the API server."""
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'your-secret-key-here'
        
        # Enable CORS for React frontend
        CORS(self.app, origins=["http://localhost:3000"])
        
        # Initialize SocketIO for real-time communication
        self.socketio = SocketIO(self.app, cors_allowed_origins="http://localhost:3000")
        
        # Load configuration and initialize agent
        self.config = ConfigLoader.load_config()
        self.data_manager = DataManager(self.config)
        self.agent = StockAgent(self.config, self.data_manager)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Register routes
        self._register_routes()
        self._register_socketio_events()
    
    def _register_routes(self):
        """Register API routes."""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'message': 'Stock Investment Assistant API is running'
            })
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """Chat endpoint for stock investment queries."""
            try:
                data = request.get_json()
                if not data or 'message' not in data:
                    return jsonify({'error': 'Message is required'}), 400

                user_message = data['message'].strip()
                if not user_message:
                    return jsonify({'error': 'Message cannot be empty'}), 400

                # Optional provider override (JSON > query param)
                provider_override = data.get('provider') or request.args.get('provider')
                stream = data.get('stream', False)

                if stream:
                    return Response(
                        stream_with_context(self._stream_chat_response(user_message, provider_override)),
                        mimetype='text/event-stream',
                        headers={
                            'Cache-Control': 'no-cache',
                            'Connection': 'keep-alive',
                            'Access-Control-Allow-Origin': '*'
                        }
                    )
                else:
                    raw_response = self.agent._process_query(user_message, provider=provider_override)
                    provider_used, model_used, fallback_flag = self._extract_meta(raw_response)
                    response_clean = self._strip_fallback_prefix(raw_response)

                    return jsonify({
                        'response': response_clean,
                        'provider': provider_used,
                        'model': model_used,
                        'fallback': fallback_flag,
                        'timestamp': self._get_timestamp()
                    })

            except Exception as e:
                self.logger.error(f"Error in chat endpoint: {e}")
                return jsonify({'error': f'Internal server error: {str(e)}'}), 500

        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """Get safe configuration info (no sensitive data)."""
            model_cfg = self.config.get('model', {})
            legacy = self.config.get('openai', {})
            safe_config = {
                'model': {
                    'provider': model_cfg.get('provider') or 'openai',
                    'name': model_cfg.get('name') or legacy.get('model') or 'gpt-4'
                },
                'features': {
                    'yahoo_finance': self.config.get('financial_apis', {}).get('yahoo_finance', {}).get('enabled', False),
                    'alpha_vantage': self.config.get('financial_apis', {}).get('alpha_vantage', {}).get('enabled', False)
                }
            }
            return jsonify(safe_config)
    
    def _register_socketio_events(self):
        """Register SocketIO events for real-time communication."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            self.logger.info('Client connected')
            emit('status', {'message': 'Connected to Stock Investment Assistant'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            self.logger.info('Client disconnected')
        
        @self.socketio.on('chat_message')
        def handle_chat_message(data):
            """Handle real-time chat messages."""
            try:
                message = data.get('message', '').strip()
                provider_override = data.get('provider')
                if not message:
                    emit('error', {'message': 'Message cannot be empty'})
                    return

                raw_response = self.agent._process_query(message, provider=provider_override)
                provider_used, model_used, fallback_flag = self._extract_meta(raw_response)
                response_clean = self._strip_fallback_prefix(raw_response)

                emit('chat_response', {
                    'response': response_clean,
                    'provider': provider_used,
                    'model': model_used,
                    'fallback': fallback_flag,
                    'timestamp': self._get_timestamp()
                })
            except Exception as e:
                self.logger.error(f"Error in chat_message handler: {e}")
                emit('error', {'message': f'Error processing message: {str(e)}'})

    def _stream_chat_response(self, user_message, provider_override=None):
        """Stream chat response in real-time (SSE)."""
        try:
            self.logger.info(f"Starting streaming response for: {user_message}")
            # Send an initial metadata event
            client = ModelClientFactory.get_client(self.config, provider=provider_override) if provider_override else self.agent._select_client(None)
            meta = {
                'event': 'meta',
                'provider': client.provider,
                'model': client.model_name
            }
            yield f"data: {json.dumps(meta)}\n\n"

            chunk_count = 0
            full_text_parts = []
            for chunk in self.agent.process_query_streaming(user_message, provider=provider_override):
                if chunk:
                    chunk_count += 1
                    full_text_parts.append(chunk)
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            # After streaming, analyze fallback prefix (non-stream fallback could have occurred)
            full_text = "".join(full_text_parts)
            provider_used, model_used, fallback_flag = self._extract_meta(full_text)
            completion_payload = {
                'event': 'done',
                'fallback': fallback_flag,
                'provider': provider_used,
                'model': model_used
            }
            yield f"data: {json.dumps(completion_payload)}\n\n"
            yield "data: [DONE]\n\n"
            self.logger.info(f"Streaming complete chunks={chunk_count}")
        except Exception as e:
            self.logger.error(f"Error in streaming response: {e}")
            error_data = json.dumps({'error': str(e)})
            yield f"data: {error_data}\n\n"

    # -------- Helper metadata parsing --------
    def _extract_meta(self, raw: str):
        """
        Inspect response for fallback prefix pattern: [fallback:provider]
        Returns (provider, model, fallback_flag)
        """
        fallback_flag = False
        provider = self.config.get('model', {}).get('provider', 'openai')
        model = self.config.get('model', {}).get('name') or self.config.get('openai', {}).get('model', 'gpt-4')

        if raw.startswith("[fallback:"):
            fallback_flag = True
            try:
                closing = raw.find("]")
                tag = raw[1:closing]  # fallback:provider
                provider = tag.split(":", 1)[1]
            except Exception:
                pass
        return provider, model, fallback_flag

    def _strip_fallback_prefix(self, raw: str) -> str:
        if raw.startswith("[fallback:"):
            closing = raw.find("]")
            if closing != -1:
                return raw[closing + 1:].lstrip()
        return raw

    def _get_timestamp(self) -> str:
        """Return current UTC timestamp as ISO 8601 string (Z suffix)."""
        return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False, **kwargs):
        """
        Run the underlying server. Use SocketIO's runner so WebSocket support works locally.
        """
        self.logger.info(f"Starting API server on {host}:{port}")
        # Do NOT forward unknown kwargs to werkzeug.run_simple (causes TypeError).
        # Use socketio.run so local `python src/main.py` serves both HTTP and SocketIO.
        self.socketio.run(self.app, host=host, port=port, debug=debug)


def main():
    """Main function to run the API server."""
    logging.basicConfig(level=logging.INFO)
    
    server = APIServer()
    print("🚀 Starting Stock Investment Assistant API Server...")
    print("📡 API will be available at: http://localhost:5000")
    print("🔗 React app should connect to: http://localhost:5000")
    print("💬 WebSocket endpoint: ws://localhost:5000")
    
    server.run()


if __name__ == '__main__':
    main()
