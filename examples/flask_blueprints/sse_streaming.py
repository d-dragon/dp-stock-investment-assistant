"""
Server-Sent Events (SSE) Streaming Pattern

Demonstrates SSE implementation for real-time streaming responses,
commonly used for AI chat streaming endpoints.

Reference: backend-python.instructions.md § Server-Sent Events (SSE) for Streaming
"""

import json
import time
from flask import Flask, Response, request, stream_with_context

# SSE headers required for proper streaming
SSE_HEADERS = {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',  # Adjust for production
    'X-Accel-Buffering': 'no',  # Disable nginx buffering
}


def create_streaming_app() -> Flask:
    """Create Flask app with SSE streaming endpoints."""
    app = Flask(__name__)
    
    @app.route('/api/stream/simple', methods=['GET'])
    def stream_simple():
        """
        Simple SSE stream example.
        
        Client code:
            const eventSource = new EventSource('/api/stream/simple');
            eventSource.onmessage = (event) => {
                console.log(event.data);
            };
        """
        def generate():
            for i in range(10):
                # SSE format: "data: <json>\n\n"
                yield f"data: {json.dumps({'count': i, 'message': f'Chunk {i}'})}\n\n"
                time.sleep(0.5)  # Simulate processing delay
        
        return Response(generate(), mimetype='text/event-stream', headers=SSE_HEADERS)
    
    @app.route('/api/stream/chat', methods=['POST'])
    def stream_chat():
        """
        SSE streaming for AI chat responses.
        
        Mimics the pattern in src/web/routes/ai_chat_routes.py.
        """
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return {'error': 'Message is required'}, 400
        
        def generate():
            """Generator function for streaming chunks."""
            try:
                # Simulate AI token-by-token generation
                response_text = f"AI response to: {message}"
                words = response_text.split()
                
                for word in words:
                    chunk_data = {
                        'chunk': word + ' ',
                        'done': False
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                    time.sleep(0.1)  # Simulate model latency
                
                # Send completion event
                yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
                
            except Exception as e:
                # Error handling: send error event
                error_data = {'error': str(e), 'done': True}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        # stream_with_context ensures request context is available in generator
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers=SSE_HEADERS
        )
    
    @app.route('/api/stream/multiline', methods=['GET'])
    def stream_multiline():
        """
        SSE with multiline messages using event types.
        
        Client code:
            eventSource.addEventListener('progress', (event) => {
                console.log('Progress:', JSON.parse(event.data));
            });
        """
        def generate():
            # Send named events
            yield f"event: start\ndata: {json.dumps({'timestamp': time.time()})}\n\n"
            
            for i in range(5):
                progress = {'step': i, 'total': 5, 'percent': (i / 5) * 100}
                yield f"event: progress\ndata: {json.dumps(progress)}\n\n"
                time.sleep(0.5)
            
            yield f"event: complete\ndata: {json.dumps({'status': 'done'})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream', headers=SSE_HEADERS)
    
    return app


def demonstrate_sse_patterns():
    """Show SSE implementation patterns and best practices."""
    print("=" * 60)
    print("SERVER-SENT EVENTS (SSE) STREAMING PATTERNS")
    print("=" * 60)
    
    print("\n1. BASIC SSE FORMAT")
    print("   data: <message>\\n\\n")
    print("   - Double newline terminates event")
    print("   - 'data:' prefix is required")
    
    print("\n2. JSON SSE FORMAT (recommended)")
    print("   data: {\"key\": \"value\"}\\n\\n")
    print("   - Client parses with JSON.parse(event.data)")
    
    print("\n3. NAMED EVENTS")
    print("   event: myevent\\n")
    print("   data: <message>\\n\\n")
    print("   - Client: eventSource.addEventListener('myevent', ...)")
    
    print("\n4. REQUIRED HEADERS")
    for key, value in SSE_HEADERS.items():
        print(f"   {key}: {value}")
    
    print("\n5. ERROR HANDLING")
    print("   - Wrap generator in try-except")
    print("   - Send error as final event: {'error': ..., 'done': true}")
    print("   - Log errors with exc_info=True")
    
    print("\n6. FLASK PATTERNS")
    print("   ✅ Use stream_with_context() for request context access")
    print("   ✅ Return Response(generator(), mimetype='text/event-stream')")
    print("   ✅ Yield strings in 'data: ...\\n\\n' format")
    print("   ❌ Don't buffer responses (set X-Accel-Buffering: no)")
    
    print("\n7. CLIENT RECONNECTION")
    print("   - Browser auto-reconnects on connection drop")
    print("   - Send 'id: <event_id>' for resume support")
    print("   - Client sends Last-Event-ID header on reconnect")
    
    print("\n" + "=" * 60)
    print("TESTING SSE ENDPOINTS")
    print("=" * 60)
    print("\n# Using curl:")
    print("curl -N http://localhost:5000/api/stream/simple")
    print("\n# Using httpie:")
    print("http --stream GET http://localhost:5000/api/stream/simple")
    print("\n# Using JavaScript:")
    print("const es = new EventSource('/api/stream/simple');")
    print("es.onmessage = e => console.log(JSON.parse(e.data));")


if __name__ == "__main__":
    demonstrate_sse_patterns()
    
    print("\n" + "=" * 60)
    print("DEMO APP CREATED")
    print("=" * 60)
    print("\nRun with:")
    print("  set FLASK_APP=examples.flask_blueprints.sse_streaming:create_streaming_app")
    print("  flask run")
    print("\nTest endpoints:")
    print("  GET  /api/stream/simple")
    print("  POST /api/stream/chat")
    print("  GET  /api/stream/multiline")
