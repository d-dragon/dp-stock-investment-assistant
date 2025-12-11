"""
MongoDB Safe Patterns
=====================

Demonstrates safe MongoDB patterns for the repository layer.

Key Patterns:
1. Safe collection discovery with fallback
2. ObjectId handling and normalization
3. MongoGenericRepository usage
4. Health check implementation

Reference: backend-python.instructions.md § Database Layer - MongoDB
Related: examples/troubleshooting/mongodb_unauthorized_fallback.py
"""

from pymongo import MongoClient
from pymongo.errors import OperationFailure
from bson import ObjectId
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# PATTERN 1: Safe Collection Discovery
# ============================================================================

def safe_collection_exists(db, collection_name: str) -> bool:
    """
    Check if collection exists with fallback for restricted users.
    
    Pattern: Use db.command() instead of list_collection_names()
    """
    try:
        result = db.command("listCollections", filter={"name": collection_name})
        collections = [c['name'] for c in result['cursor']['firstBatch']]
        return collection_name in collections
    
    except OperationFailure as e:
        if "not authorized" in str(e).lower():
            logger.warning(f"Cannot verify collection '{collection_name}' exists (permission denied)")
            # Assume it exists if known from schema
            known_collections = [
                'users', 'workspaces', 'watchlists', 'portfolios',
                'market_data', 'symbols', 'fundamental_analysis'
            ]
            return collection_name in known_collections
        raise


# ============================================================================
# PATTERN 2: ObjectId Handling
# ============================================================================

def normalize_document(doc: Optional[Dict], id_fields=("_id",)) -> Optional[Dict]:
    """
    Convert MongoDB document to JSON-safe format.
    
    Conversions:
    - ObjectId → string
    - datetime → ISO 8601 string
    - Recursive for nested structures
    
    Used in: src/utils/service_utils.py
    """
    if doc is None:
        return None
    
    if isinstance(doc, list):
        return [normalize_document(item, id_fields) for item in doc]
    
    if not isinstance(doc, dict):
        return doc
    
    result = {}
    for key, value in doc.items():
        # Convert ObjectId to string
        if key in id_fields and isinstance(value, ObjectId):
            result[key] = str(value)
        # Convert datetime to ISO string
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        # Recursively normalize nested dicts
        elif isinstance(value, dict):
            result[key] = normalize_document(value, id_fields)
        # Recursively normalize lists
        elif isinstance(value, list):
            result[key] = [normalize_document(item, id_fields) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    
    return result


def prepare_filter(filter_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare filter dict for MongoDB queries.
    
    Converts string IDs to ObjectId for _id queries.
    """
    if "_id" in filter_dict and isinstance(filter_dict["_id"], str):
        try:
            filter_dict["_id"] = ObjectId(filter_dict["_id"])
        except Exception:
            # Invalid ObjectId string - leave as is (will not match)
            pass
    return filter_dict


# ============================================================================
# PATTERN 3: MongoGenericRepository Base Class
# ============================================================================

class MongoGenericRepository:
    """
    Generic MongoDB repository with CRUD operations.
    
    Used in: src/data/repositories/mongodb_repository.py
    
    All domain repositories extend this base class.
    """
    
    def __init__(self, db, collection_name: str):
        self.db = db
        self.collection_name = collection_name
        self.collection = db[collection_name]
    
    def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict]:
        """Find single document."""
        filter_dict = prepare_filter(filter_dict)
        doc = self.collection.find_one(filter_dict)
        return normalize_document(doc) if doc else None
    
    def find_many(
        self,
        filter_dict: Dict[str, Any],
        *,
        limit: int = 100,
        skip: int = 0,
        sort: Optional[List] = None
    ) -> List[Dict]:
        """Find multiple documents."""
        filter_dict = prepare_filter(filter_dict)
        
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
        
        if sort:
            cursor = cursor.sort(sort)
        
        docs = list(cursor)
        return [normalize_document(doc) for doc in docs]
    
    def insert_one(self, document: Dict[str, Any]) -> str:
        """Insert document, return ID as string."""
        result = self.collection.insert_one(document)
        return str(result.inserted_id)
    
    def update_one(self, id: str, updates: Dict[str, Any]) -> Optional[Dict]:
        """Update document by ID, return updated document."""
        try:
            object_id = ObjectId(id)
        except Exception:
            return None
        
        result = self.collection.find_one_and_update(
            {"_id": object_id},
            {"$set": updates},
            return_document=True
        )
        
        return normalize_document(result) if result else None
    
    def delete_one(self, id: str) -> bool:
        """Delete document by ID."""
        try:
            object_id = ObjectId(id)
        except Exception:
            return False
        
        result = self.collection.delete_one({"_id": object_id})
        return result.deleted_count > 0
    
    def count(self, filter_dict: Dict[str, Any]) -> int:
        """Count documents matching filter."""
        filter_dict = prepare_filter(filter_dict)
        return self.collection.count_documents(filter_dict)
    
    def health_check(self) -> tuple:
        """
        Check repository health.
        
        Returns: (healthy: bool, details: dict)
        """
        try:
            # Verify collection exists
            exists = safe_collection_exists(self.db, self.collection_name)
            
            if not exists:
                return False, {
                    "component": f"{self.collection_name}_repository",
                    "error": f"Collection '{self.collection_name}' not found"
                }
            
            # Try to count documents (tests read permission)
            self.collection.count_documents({}, limit=1)
            
            return True, {
                "component": f"{self.collection_name}_repository",
                "status": "ready"
            }
        
        except Exception as e:
            return False, {
                "component": f"{self.collection_name}_repository",
                "error": str(e)
            }


# ============================================================================
# PATTERN 4: Domain Repository Example
# ============================================================================

class UserRepository(MongoGenericRepository):
    """
    Domain-specific repository extending base class.
    
    Adds domain-specific methods beyond CRUD.
    """
    
    def __init__(self, db):
        super().__init__(db, "users")
    
    def find_by_email(self, email: str) -> Optional[Dict]:
        """Find user by email address."""
        return self.find_one({"email": email})
    
    def search_users(self, query: str, *, limit: int = 10) -> List[Dict]:
        """Search users by name or email."""
        filter_dict = {
            "$or": [
                {"email": {"$regex": query, "$options": "i"}},
                {"name": {"$regex": query, "$options": "i"}}
            ]
        }
        return self.find_many(filter_dict, limit=limit)
    
    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        updates = {"last_login": datetime.utcnow()}
        result = self.update_one(user_id, updates)
        return result is not None


# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    print("=" * 80)
    print("MONGODB SAFE PATTERNS")
    print("=" * 80)
    
    # Demonstrate ObjectId normalization
    print("\n1. ObjectId Normalization:")
    print("-" * 80)
    
    sample_doc = {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "email": "test@example.com",
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
        "profile": {
            "_id": ObjectId("507f1f77bcf86cd799439012"),
            "bio": "Trader"
        }
    }
    
    normalized = normalize_document(sample_doc)
    print(f"   Original _id type: {type(sample_doc['_id'])}")
    print(f"   Normalized _id type: {type(normalized['_id'])}")
    print(f"   Normalized _id value: {normalized['_id']}")
    print(f"   Normalized datetime: {normalized['created_at']}")
    
    # Demonstrate filter preparation
    print("\n2. Filter Preparation (string → ObjectId):")
    print("-" * 80)
    
    filter_with_string = {"_id": "507f1f77bcf86cd799439011"}
    prepared = prepare_filter(filter_with_string.copy())
    
    print(f"   Original: {filter_with_string}")
    print(f"   Prepared: {prepared}")
    print(f"   Type: {type(prepared['_id'])}")
    
    # Demonstrate repository pattern
    print("\n3. Repository Pattern:")
    print("-" * 80)
    print("   MongoGenericRepository provides:")
    print("   - find_one(filter_dict) → Optional[Dict]")
    print("   - find_many(filter_dict, limit, skip, sort) → List[Dict]")
    print("   - insert_one(document) → str (ID)")
    print("   - update_one(id, updates) → Optional[Dict]")
    print("   - delete_one(id) → bool")
    print("   - count(filter_dict) → int")
    print("   - health_check() → (bool, dict)")
    
    print("\n4. Domain Repository Example:")
    print("-" * 80)
    print("   UserRepository(MongoGenericRepository):")
    print("   - Inherits all CRUD operations")
    print("   - Adds: find_by_email(email)")
    print("   - Adds: search_users(query)")
    print("   - Adds: update_last_login(user_id)")
    
    print("\n" + "=" * 80)
    print("KEY PATTERNS")
    print("=" * 80)
    print("✅ Use db.command('listCollections') with fallback for restricted users")
    print("✅ Normalize ObjectId → string and datetime → ISO in responses")
    print("✅ Prepare filters: convert string IDs to ObjectId for queries")
    print("✅ Extend MongoGenericRepository for domain repositories")
    print("✅ Implement health_check() in all repositories")
    print("=" * 80)
