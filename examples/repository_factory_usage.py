"""
Example usage of RepositoryFactory for centralized repository management.

This example demonstrates how to use the new RepositoryFactory to create
and manage repository instances throughout the application.
"""

from utils.config_loader import ConfigLoader
from data.repositories.factory import RepositoryFactory


def example_basic_usage():
    """Basic usage: Create factory and get repositories."""
    
    # Load configuration
    config = ConfigLoader.load_config()
    
    # Create factory instance (parses config once)
    factory = RepositoryFactory(config)
    
    # Get repository instances
    user_repo = factory.get_user_repository()
    symbol_repo = factory.get_symbol_repository()
    workspace_repo = factory.get_workspace_repository()
    
    if user_repo and symbol_repo and workspace_repo:
        # Use repositories
        print("✓ All repositories initialized successfully")
        
        # Example: Search for users
        users = user_repo.search_by_name("John", limit=5)
        print(f"Found {len(users)} users matching 'John'")
        
        # Example: Get tracked symbols
        tracked_symbols = symbol_repo.get_tracked_symbols(limit=10)
        print(f"Found {tracked_symbols} tracked symbols")
    else:
        print("✗ Failed to initialize repositories")


def example_service_pattern():
    """Service pattern: Encapsulate factory in service class."""
    
    class WorkspaceService:
        """Service that orchestrates multiple repositories."""
        
        def __init__(self, config):
            """Initialize service with repositories."""
            factory = RepositoryFactory(config)
            self.workspace_repo = factory.get_workspace_repository()
            self.session_repo = factory.get_session_repository()
            self.user_repo = factory.get_user_repository()
        
        def create_workspace_with_default_session(self, user_id, workspace_name):
            """Create workspace and initialize default session."""
            if not all([self.workspace_repo, self.session_repo, self.user_repo]):
                raise RuntimeError("Repositories not initialized")
            
            # Verify user exists
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return None, "User not found"
            
            # Create workspace
            workspace_data = {
                "user_id": user_id,
                "name": workspace_name,
                "description": f"Workspace for {user.get('name', 'user')}",
                "status": "active"
            }
            workspace_id = self.workspace_repo.create(workspace_data)
            
            if not workspace_id:
                return None, "Failed to create workspace"
            
            # Create default session
            session_data = {
                "workspace_id": workspace_id,
                "title": "Default Session",
                "status": "open"
            }
            session_id = self.session_repo.create(session_data)
            
            return {
                "workspace_id": workspace_id,
                "session_id": session_id
            }, None
    
    # Usage
    config = ConfigLoader.load_config()
    service = WorkspaceService(config)
    
    # Example user ID
    user_id = "507f1f77bcf86cd799439011"
    result, error = service.create_workspace_with_default_session(
        user_id, 
        "Tech Stock Analysis"
    )
    
    if error:
        print(f"✗ Error: {error}")
    else:
        print(f"✓ Created workspace: {result['workspace_id']}")
        print(f"✓ Created session: {result['session_id']}")


def example_flask_route_integration():
    """Flask route integration: Use factory in route handlers."""
    
    from flask import Blueprint, jsonify, request
    
    # Assume app_factory provides config
    def create_api_routes(config):
        """Create API routes with repository access."""
        
        api_bp = Blueprint('api', __name__)
        
        # Create factory once at blueprint creation
        factory = RepositoryFactory(config)
        
        @api_bp.route('/api/users/<user_id>/workspaces', methods=['GET'])
        def get_user_workspaces(user_id):
            """Get all workspaces for a user."""
            workspace_repo = factory.get_workspace_repository()
            
            if not workspace_repo:
                return jsonify({"error": "Repository not available"}), 500
            
            try:
                workspaces = workspace_repo.get_by_user_id(user_id, limit=50)
                return jsonify({
                    "user_id": user_id,
                    "workspaces": workspaces,
                    "count": len(workspaces)
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @api_bp.route('/api/symbols/search', methods=['GET'])
        def search_symbols():
            """Search symbols by name or ticker."""
            symbol_repo = factory.get_symbol_repository()
            
            if not symbol_repo:
                return jsonify({"error": "Repository not available"}), 500
            
            query = request.args.get('q', '')
            if not query:
                return jsonify({"error": "Query parameter 'q' required"}), 400
            
            try:
                # Try exact ticker match first
                exact_match = symbol_repo.get_by_symbol(query.upper())
                if exact_match:
                    return jsonify({"results": [exact_match], "count": 1})
                
                # Fall back to name search
                results = symbol_repo.search_by_name(query, limit=10)
                return jsonify({"results": results, "count": len(results)})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @api_bp.route('/api/portfolios/<portfolio_id>/positions', methods=['GET'])
        def get_portfolio_positions(portfolio_id):
            """Get positions for a portfolio with enriched symbol data."""
            portfolio_repo = factory.get_portfolio_repository()
            symbol_repo = factory.get_symbol_repository()
            
            if not all([portfolio_repo, symbol_repo]):
                return jsonify({"error": "Repositories not available"}), 500
            
            try:
                # Get portfolio
                portfolio = portfolio_repo.get_by_id(portfolio_id)
                if not portfolio:
                    return jsonify({"error": "Portfolio not found"}), 404
                
                # Enrich positions with symbol data
                positions = portfolio.get('positions', [])
                enriched_positions = []
                
                for position in positions:
                    symbol_id = position.get('symbol_id')
                    if symbol_id:
                        symbol_data = symbol_repo.get_by_id(symbol_id)
                        position['symbol_data'] = symbol_data
                    enriched_positions.append(position)
                
                return jsonify({
                    "portfolio_id": portfolio_id,
                    "name": portfolio.get('name'),
                    "positions": enriched_positions,
                    "count": len(enriched_positions)
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        return api_bp


def example_dependency_injection():
    """Dependency injection: Pass repositories to classes."""
    
    class SymbolAnalyzer:
        """Analyzes symbols using repository data."""
        
        def __init__(self, symbol_repo, portfolio_repo):
            """Inject repository dependencies."""
            self.symbol_repo = symbol_repo
            self.portfolio_repo = portfolio_repo
        
        def analyze_symbol_exposure(self, symbol_id):
            """Analyze how many portfolios hold this symbol."""
            symbol = self.symbol_repo.get_by_id(symbol_id)
            if not symbol:
                return None
            
            # Find portfolios containing this symbol
            # (This would require a proper query in real implementation)
            all_portfolios = self.portfolio_repo.get_all(limit=1000)
            
            holding_portfolios = [
                p for p in all_portfolios
                if any(pos.get('symbol_id') == symbol_id 
                      for pos in p.get('positions', []))
            ]
            
            return {
                "symbol": symbol.get('symbol'),
                "name": symbol.get('name'),
                "portfolios_count": len(holding_portfolios),
                "portfolios": [p.get('name') for p in holding_portfolios]
            }
    
    # Usage
    config = ConfigLoader.load_config()
    factory = RepositoryFactory(config)
    
    # Create analyzer with injected dependencies
    analyzer = SymbolAnalyzer(
        symbol_repo=factory.get_symbol_repository(),
        portfolio_repo=factory.get_portfolio_repository()
    )
    
    # Use analyzer
    symbol_id = "507f1f77bcf86cd799439011"
    analysis = analyzer.analyze_symbol_exposure(symbol_id)
    
    if analysis:
        print(f"Symbol: {analysis['symbol']} ({analysis['name']})")
        print(f"Held in {analysis['portfolios_count']} portfolios")


def example_legacy_compatibility():
    """Demonstrate backward compatibility with legacy static methods."""
    
    config = ConfigLoader.load_config()
    
    # Old way (still works for MongoDBStockDataRepository)
    stock_repo = RepositoryFactory.create_mongo_repository(config)
    cache_repo = RepositoryFactory.create_cache_repository(config)
    stock_service = RepositoryFactory.create_stock_data_service(config)
    
    print("✓ Legacy static methods still work")
    
    # New way (recommended for new code)
    factory = RepositoryFactory(config)
    user_repo = factory.get_user_repository()
    symbol_repo = factory.get_symbol_repository()
    
    print("✓ New instance methods work alongside legacy methods")


if __name__ == "__main__":
    print("=== Repository Factory Usage Examples ===\n")
    
    print("1. Basic Usage:")
    try:
        example_basic_usage()
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n2. Service Pattern:")
    try:
        example_service_pattern()
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n3. Dependency Injection:")
    try:
        example_dependency_injection()
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n4. Legacy Compatibility:")
    try:
        example_legacy_compatibility()
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n=== Examples Complete ===")
