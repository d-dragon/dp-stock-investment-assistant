@echo off
echo Installing Flask dependencies for API server...
pip install flask flask-cors flask-socketio python-socketio

echo.
echo Flask dependencies installed successfully!
echo You can now run the API server with: python src/web/api_server.py
