"""
MongoDB Unauthorized Fallback Pattern
=====================================

Problem: User lacks 'listCollections' permission in restrictive MongoDB setups
Symptom: pymongo.errors.OperationFailure: not authorized on stock_assistant to execute command { listCollections: 1 }
Solution: Use db.command() with try/except fallback to known schema

Reference: backend-python.instructions.md § Database Layer - MongoDB
Related: backend-python.instructions.md § Pitfalls and Gotchas #4
"""

from pymongo import MongoClient
from pymongo.errors import OperationFailure
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# PROBLEM: Direct listCollections Call
# ============================================================================

def bad_collection_discovery(db):
    """
    ❌ BAD: Uses list_collection_names() which may raise Unauthorized.
    
    Fails in environments where user lacks listCollections permission.
    """
    try:
        collections = db.list_collection_names()
        return collections
    except OperationFailure as e:
        # This will crash the application
        logger.error(f"Unauthorized: {e}")
        raise


# ============================================================================
# SOLUTION: Safe Collection Discovery with Fallback
# ============================================================================

def safe_collection_discovery(db):
    """
    ✅ GOOD: Uses db.command() with fallback to known schema.
    
    Gracefully handles Unauthorized by falling back to application schema.
    """
    try:
        # Try using MongoDB command (more reliable than list_collection_names)
        result = db.command("listCollections")
        collections = [c['name'] for c in result['cursor']['firstBatch']]
        logger.info(f"Discovered {len(collections)} collections via listCollections command")
        return collections
    
    except OperationFailure as e:
        if "not authorized" in str(e).lower():
            logger.warning(
                "User lacks listCollections permission; using known schema. "
                "This is expected in restrictive authentication setups."
            )
            # Fallback to known collections from application schema
            known_collections = get_known_collections()
            logger.info(f"Using {len(known_collections)} known collections from schema")
            return known_collections
        else:
            # Re-raise for other operation failures (network, etc.)
            raise


def get_known_collections():
    """
    Returns known collection names from application schema.
    
    This list should match collections created by db_setup.py migration script.
    """
    return [
        # User & Auth
        'users',
        'user_profiles',
        'user_preferences',
        'accounts',
        'sessions',
        'groups',
        
        # Workspaces & Organization
        'workspaces',
        'watchlists',
        'portfolios',
        'positions',
        
        # Market Data
        'market_data',  # Time-series collection
        'symbols',
        'market_snapshots',
        'technical_indicators',
        
        # Analysis & Reports
        'fundamental_analysis',
        'analyses',
        'reports',
        'investment_reports',
        
        # Investment Management
        'investment_ideas',
        'investment_styles',
        'strategies',
        'rules_policies',
        'trades',
        
        # Collaboration
        'chats',
        'notes',
        'tasks',
        'notifications',
        'news_events',
    ]


# ============================================================================
# PRACTICAL USAGE: Repository Factory Pattern
# ============================================================================

class MongoRepositoryFactory:
    """
    Example repository factory using safe collection discovery.
    
    Used in: src/data/repositories/factory.py
    """
    
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self._repositories = {}
        self._available_collections = None
    
    def get_available_collections(self):
        """Get available collections with safe fallback."""
        if self._available_collections is None:
            self._available_collections = safe_collection_discovery(self.db)
        return self._available_collections
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists (safe for restricted users)."""
        return collection_name in self.get_available_collections()
    
    def get_user_repository(self):
        """Get user repository, ensuring collection exists."""
        if not self.collection_exists('users'):
            logger.warning("Collection 'users' not found; it may need migration")
        
        if 'user_repo' not in self._repositories:
            from data.repositories.user_repository import UserRepository
            self._repositories['user_repo'] = UserRepository(self.db)
        
        return self._repositories['user_repo']


# ============================================================================
# SCHEMA SETUP: Migration Script Pattern
# ============================================================================

def setup_collections_with_safe_check(db):
    """
    Example migration script using safe collection discovery.
    
    Used in: src/data/migration/db_setup.py
    """
    existing_collections = safe_collection_discovery(db)
    logger.info(f"Found existing collections: {existing_collections}")
    
    # Define collections to create
    collections_to_create = [
        ('users', {'validator': {'$jsonSchema': {...}}}),
        ('workspaces', {'validator': {'$jsonSchema': {...}}}),
        # ... more collections
    ]
    
    for collection_name, options in collections_to_create:
        if collection_name in existing_collections:
            logger.info(f"Collection '{collection_name}' already exists, skipping")
        else:
            logger.info(f"Creating collection '{collection_name}'")
            db.create_collection(collection_name, **options)


# ============================================================================
# HEALTH CHECK: Service Integration
# ============================================================================

def mongodb_health_check(db):
    """
    Health check for MongoDB connection (safe for restricted users).
    
    Used in: BaseService._dependency_health(), RepositoryFactory.health_check()
    """
    try:
        # Use ping command (requires minimal permissions)
        db.command("ping")
        
        # Optional: Verify collection accessibility (graceful failure)
        try:
            collections = safe_collection_discovery(db)
            return True, {
                "component": "mongodb",
                "status": "ready",
                "collections": len(collections)
            }
        except Exception as e:
            # Even if collection discovery fails, ping succeeded
            logger.warning(f"Collection discovery failed but DB is reachable: {e}")
            return True, {
                "component": "mongodb",
                "status": "ready",
                "warning": "Limited collection visibility"
            }
    
    except Exception as e:
        return False, {
            "component": "mongodb",
            "status": "error",
            "error": str(e)
        }


# ============================================================================
# CONFIGURATION: Grant Permissions (MongoDB Admin)
# ============================================================================

def show_mongodb_permission_fix():
    """
    MongoDB commands to grant listCollections permission.
    
    Run this in MongoDB shell or via admin user to fix the root cause.
    """
    mongo_commands = """
    // Connect as admin
    use admin
    
    // Create custom role with listCollections action
    db.createRole({
        role: "appReadWrite",
        privileges: [
            {
                resource: { db: "stock_assistant", collection: "" },
                actions: [
                    "find", "insert", "update", "remove",
                    "listCollections",  // ← Add this action
                    "listIndexes"
                ]
            }
        ],
        roles: []
    })
    
    // Grant role to existing user
    use stock_assistant
    db.grantRolesToUser("app_user", ["appReadWrite"])
    
    // Verify permissions
    db.runCommand({ connectionStatus: 1, showPrivileges: true })
    """
    
    print("MongoDB Permission Fix Commands:")
    print(mongo_commands)


# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    print("=" * 80)
    print("MongoDB Unauthorized Fallback Pattern Demonstration")
    print("=" * 80)
    
    # Simulated scenarios
    class SimulatedDB:
        """Mock database for demonstration."""
        
        def __init__(self, authorized: bool):
            self.authorized = authorized
        
        def command(self, cmd):
            if cmd == "listCollections":
                if not self.authorized:
                    raise OperationFailure("not authorized on stock_assistant to execute command { listCollections: 1 }")
                
                return {
                    'cursor': {
                        'firstBatch': [
                            {'name': 'users'},
                            {'name': 'workspaces'},
                            {'name': 'market_data'},
                        ]
                    }
                }
            elif cmd == "ping":
                return {'ok': 1}
    
    print("\n1. Authorized User (listCollections works):")
    print("-" * 80)
    authorized_db = SimulatedDB(authorized=True)
    collections = safe_collection_discovery(authorized_db)
    print(f"   Discovered collections: {collections}")
    
    print("\n2. Restricted User (listCollections fails, fallback to schema):")
    print("-" * 80)
    restricted_db = SimulatedDB(authorized=False)
    collections = safe_collection_discovery(restricted_db)
    print(f"   Using known collections: {collections[:5]}... (showing first 5)")
    
    print("\n3. Health Check (works even with restricted permissions):")
    print("-" * 80)
    healthy, details = mongodb_health_check(restricted_db)
    print(f"   Healthy: {healthy}")
    print(f"   Details: {details}")
    
    print("\n4. MongoDB Permission Fix (for administrators):")
    print("-" * 80)
    show_mongodb_permission_fix()
    
    print("\n" + "=" * 80)
    print("Key Takeaways:")
    print("=" * 80)
    print("✅ Always use db.command('listCollections') with try/except fallback")
    print("✅ Fallback to known schema list from db_setup.py migration")
    print("✅ Warn in logs but don't crash the application")
    print("✅ Health checks should still pass even with restricted permissions")
    print("✅ Document required permissions in README for production setup")
    print("=" * 80)
