from web.api_server import APIServer

# Create the APIServer and expose the Flask WSGI app as `app` for gunicorn
server = APIServer()
# APIServer must expose the Flask application instance as `self.app`.
# If your implementation names it differently, adjust accordingly.
app = server.app
socketio = server.socketio