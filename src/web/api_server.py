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

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.agent import StockAgent
from core.data_manager import DataManager
from utils.config_loader import ConfigLoader


class APIServer:
    """Flask API server for the Stock Investment Assistant."""
    
    def __init__(self):
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
                
                # Check if streaming is requested
                stream = data.get('stream', False)
                
                if stream:
                    return Response(
                        stream_with_context(self._stream_chat_response(user_message)),
                        mimetype='text/event-stream',
                        headers={
                            'Cache-Control': 'no-cache',
                            'Connection': 'keep-alive',
                            'Access-Control-Allow-Origin': '*'
                        }
                    )
                else:
                    # Process the query using the agent (non-streaming)
                    response = self.agent._process_query_non_streaming(user_message)
                    
                    return jsonify({
                        'response': response,
                        'timestamp': self._get_timestamp()
                    })
                
            except Exception as e:
                self.logger.error(f"Error in chat endpoint: {e}")
                return jsonify({'error': f'Internal server error: {str(e)}'}), 500
        
        @self.app.route('/api/commands', methods=['GET'])
        def get_commands():
            """Get available commands."""
            commands = [
                {
                    'command': 'help',
                    'description': 'Show available commands'
                },
                {
                    'command': 'stock analysis',
                    'description': 'Ask questions about specific stocks',
                    'example': 'What is the current price of AAPL?'
                },
                {
                    'command': 'market trends',
                    'description': 'Get insights about market trends',
                    'example': 'How is the tech sector performing?'
                },
                {
                    'command': 'investment advice',
                    'description': 'Get investment guidance',
                    'example': 'Should I invest in renewable energy stocks?'
                }
            ]
            
            return jsonify({'commands': commands})
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """Get safe configuration info (no sensitive data)."""
            safe_config = {
                'model': self.config.get('openai', {}).get('model', 'gpt-4'),
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
                
                if not message:
                    emit('error', {'message': 'Message cannot be empty'})
                    return
                
                # Process the query
                response = self.agent._process_query(message)
                
                # Send response back to client
                emit('chat_response', {
                    'response': response,
                    'timestamp': self._get_timestamp()
                })
                
            except Exception as e:
                self.logger.error(f"Error in chat_message handler: {e}")
                emit('error', {'message': f'Error processing message: {str(e)}'})
    
    def _stream_chat_response(self, user_message):
        """Stream chat response in real-time."""
        try:
            self.logger.info(f"Starting streaming response for: {user_message}")
            # Stream response chunks in SSE format
            chunk_count = 0
            for chunk in self.agent.process_query_streaming(user_message):
                if chunk.strip():  # Only send non-empty chunks
                    chunk_count += 1
                    # Format as JSON for the frontend
                    chunk_data = json.dumps({'chunk': chunk})
                    yield f"data: {chunk_data}\n\n"
            
            # Send completion signal
            self.logger.info(f"Streaming complete. Sent {chunk_count} chunks.")
            yield f"data: [DONE]\n\n"
                
        except Exception as e:
            self.logger.error(f"Error in streaming response: {e}")
            error_data = json.dumps({'error': str(e)})
            yield f"data: {error_data}\n\n"
    
    def _get_timestamp(self):
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the Flask application."""
        self.logger.info(f"Starting API server on {host}:{port}")
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
