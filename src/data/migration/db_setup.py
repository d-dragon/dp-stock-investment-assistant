"""
Database setup and migration script.
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

def setup_database(config=None):
    """Set up the database schema"""
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
    success = setup_database(config)
    sys.exit(0 if success else 1)