Notes:

This is a small development convenience to allow the existing main.py call to pass allow_unsafe_werkzeug. For production, run the app with a real WSGI server (gunicorn/uvicorn) instead of Flask's built-in server.
If your APIServer implementation does not expose a Flask app as self.app, adapt the patch to access whatever attribute holds the Flask application instance (commonly app, application, or flask_app).