Notes:

This is a small development convenience to allow the existing main.py call to pass allow_unsafe_werkzeug. For production, run the app with a real WSGI server (gunicorn/uvicorn) instead of Flask's built-in server.
If your APIServer implementation does not expose a Flask app as self.app, adapt the patch to access whatever attribute holds the Flask application instance (commonly app, application, or flask_app).

src/services/
├── __init__.py
├── workspace_service.py      # Orchestrates workspaces, sessions, watchlists
├── portfolio_service.py      # Manages portfolios, positions, trades
├── analysis_service.py       # Coordinates analyses, reports, ideas
├── notification_service.py   # Handles alerts and notifications
└── user_service.py           # User management and preferences

Service pattern
@bp.route('/api/workspace/<workspace_id>')
def get_workspace(workspace_id):
    workspace_service = get_workspace_service()  # From DI
    overview = workspace_service.get_workspace_overview(workspace_id)
    return jsonify(overview)

    
 Service Layer Tests
Unit tests with mocked repositories
Integration tests with real database (test environment)

Key Design Patterns
Service Layer - Business logic orchestration above repositories
Dependency Injection - Via factory with explicit wiring
Protocol-Based Dependency Injection
Health Checks - Standardized dependency health reporting
Smart Caching - TTL-based with targeted invalidation
Async Support - Async wrappers for blocking operations
Streaming APIs - Generator-based batching for large datasets
Input Validation - Early validation with descriptive ValueError exceptions
SOLID principles

Architecture Layer

API Routes (Flask)     
↓
Service Layer (NEW - Business Logic)    
↓
Repository Layer (Data Access)    
↓
MongoDB / Redis