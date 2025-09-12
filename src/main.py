"""
Main entry point for the DP Stock-Investment Assistant.
"""

from core.agent import StockAgent
from core.data_manager import DataManager
from utils.config_loader import ConfigLoader
from web.api_server import APIServer
import logging
import sys
import argparse


def setup_logging(level="INFO"):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main function to run the stock investment assistant."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='DP Stock Investment Assistant')
        parser.add_argument('--mode', choices=['cli', 'web', 'both'], default='web',
                          help='Run mode: cli (interactive CLI), web (API server), or both')
        parser.add_argument('--host', default='0.0.0.0', help='API server host')
        parser.add_argument('--port', type=int, default=5000, help='API server port')
        args = parser.parse_args()
        
        # Load configuration
        config = ConfigLoader.load_config()
        
        # Setup logging
        setup_logging(config.get('app', {}).get('log_level', 'INFO'))
        logger = logging.getLogger(__name__)
        
        logger.info("Starting DP Stock-Investment Assistant...")
        
        if args.mode == 'web' or args.mode == 'both':
            # Start the web API server
            logger.info("Starting API server for React frontend...")
            server = APIServer()
            print("🚀 Starting Stock Investment Assistant API Server...")
            print(f"📡 API will be available at: http://{args.host}:{args.port}")
            print("🔗 React app should connect to: http://localhost:5000")
            print("💬 WebSocket endpoint: ws://localhost:5000")
            
            if args.mode == 'both':
                # Start server in a separate thread for both modes
                import threading
                server_thread = threading.Thread(target=lambda: server.run(host=args.host, port=args.port, debug=False))
                server_thread.daemon = True
                server_thread.start()
                
                # Also run CLI mode
                logger.info("Starting interactive CLI mode...")
                data_manager = DataManager(config)
                agent = StockAgent(config, data_manager)
                agent.run_interactive()
            else:
                # Run only web server
                server.run(host=args.host, port=args.port, debug=True)
                
        elif args.mode == 'cli':
            # Run only CLI mode
            logger.info("Starting interactive CLI mode...")
            data_manager = DataManager(config)
            agent = StockAgent(config, data_manager)
            agent.run_interactive()
        
    except Exception as e:
        logging.error(f"Error starting application: {e}")
        raise


if __name__ == "__main__":
    main()
