"""
Database setup and migration script.

§10.2 clean-slate migration: Use --clean-slate to drop and recreate
sessions, conversations, and agent_checkpoints collections.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from src.data.schema.schema_manager import SchemaManager
from src.utils.config_loader import ConfigLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("db_setup")

# Collections affected by the STM domain model refactor (§10.2)
STM_COLLECTIONS = ["sessions", "conversations", "agent_checkpoints"]


def drop_stm_collections(connection_string: str, database_name: str) -> bool:
    """Drop STM-related collections for clean-slate migration (§10.2).

    WARNING: This permanently deletes all data in sessions, conversations,
    and agent_checkpoints collections.
    """
    from pymongo import MongoClient
    try:
        client = MongoClient(connection_string)
        db = client[database_name]
        for name in STM_COLLECTIONS:
            if name in db.list_collection_names():
                logger.warning(f"Dropping collection '{name}' (clean-slate migration)")
                db.drop_collection(name)
            else:
                logger.info(f"Collection '{name}' does not exist, skipping drop")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Error dropping STM collections: {e}")
        return False

def setup_database(config=None, clean_slate: bool = False):
    """Set up the database schema.
    
    Args:
        config: Application config dict. Loaded from environment if None.
        clean_slate: If True, drop STM collections before recreation (§10.2).
    """
    # Load configuration
    if config is None:
        # Load from environment variables
        load_dotenv()
        config = ConfigLoader.load_config()
    
    # Get MongoDB connection details
    mongodb_config = config.get('database', {}).get('mongodb', {})
    connection_string = mongodb_config.get('connection_string', os.getenv('MONGODB_URI'))
    database_name = mongodb_config.get('database_name', os.getenv('MONGODB_DB_NAME', 'stock_assistant'))
    
    if not connection_string:
        logger.error("MongoDB connection string not provided")
        return False
    
    # Clean-slate migration: drop STM collections first (§10.2)
    if clean_slate:
        logger.warning("=== CLEAN-SLATE MIGRATION: Dropping STM collections ===")
        if not drop_stm_collections(connection_string, database_name):
            logger.error("Failed to drop STM collections — aborting")
            return False
        logger.info("STM collections dropped successfully")
        
    # Initialize schema manager
    logger.info(f"Setting up database schema for '{database_name}'")
    schema_manager = SchemaManager(connection_string, database_name)
    
    # Setup all collections
    success = schema_manager.setup_all_collections()
    
    if success:
        logger.info("Database setup completed successfully")
    else:
        logger.error("Database setup failed")
        
    return success

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Set up MongoDB database schema")
    parser.add_argument(
        "--uri", 
        help="MongoDB connection URI (overrides config)",
        default=None
    )
    parser.add_argument(
        "--db", 
        help="MongoDB database name (overrides config)",
        default=None
    )
    parser.add_argument(
        "--clean-slate",
        action="store_true",
        help="Drop sessions, conversations, and agent_checkpoints before recreation (§10.2)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Override config with command line arguments if provided
    config = ConfigLoader.load_config()
    
    if args.uri or args.db:
        if 'database' not in config:
            config['database'] = {}
        if 'mongodb' not in config['database']:
            config['database']['mongodb'] = {}
            
        if args.uri:
            config['database']['mongodb']['connection_string'] = args.uri
        if args.db:
            config['database']['mongodb']['database_name'] = args.db
    
    # Run setup
    success = setup_database(config, clean_slate=args.clean_slate)
    sys.exit(0 if success else 1)