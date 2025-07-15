"""
Main entry point for the DP Stock-Investment Assistant.
"""

from core.agent import StockAgent
from core.data_manager import DataManager
from utils.config_loader import ConfigLoader
import logging


def setup_logging(level="INFO"):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main function to run the stock investment assistant."""
    try:
        # Load configuration
        config = ConfigLoader.load_config()
        
        # Setup logging
        setup_logging(config.get('app', {}).get('log_level', 'INFO'))
        logger = logging.getLogger(__name__)
        
        logger.info("Starting DP Stock-Investment Assistant...")
        
        # Initialize data manager
        data_manager = DataManager(config)
        
        # Initialize the stock agent
        agent = StockAgent(config, data_manager)
        
        # Start the interactive session
        agent.run_interactive()
        
    except Exception as e:
        logging.error(f"Error starting application: {e}")
        raise


if __name__ == "__main__":
    main()
