"""
Stock Investment Agent - Main AI agent for handling user interactions.
"""

import logging
from typing import Dict, Any
from .ai_client import AIClient
from .data_manager import DataManager


class StockAgent:
    """Main agent class for the Stock Investment Assistant."""
    
    def __init__(self, config: Dict[str, Any], data_manager: DataManager):
        """Initialize the Stock Agent.
        
        Args:
            config: Configuration dictionary
            data_manager: Data manager instance
        """
        self.config = config
        self.data_manager = data_manager
        self.ai_client = AIClient(config)
        self.logger = logging.getLogger(__name__)
        
    def run_interactive(self):
        """Run the interactive session."""
        self.logger.info("Starting interactive session...")
        print("Welcome to DP Stock-Investment Assistant!")
        print("Type 'quit' or 'exit' to end the session.")
        print("Type 'help' for available commands.\n")
        
        while True:
            try:
                user_input = input("Stock Assistant> ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                elif user_input:
                    response = self._process_query(user_input)
                    print(f"\nAssistant: {response}\n")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error processing query: {e}")
                print(f"Error: {e}")
    
    def _process_query(self, query: str) -> str:
        """Process user query and return AI response.
        
        Args:
            query: User's question or command
            
        Returns:
            AI-generated response
        """
        try:
            # For now, pass the query directly to AI
            # TODO: Add data analysis, stock lookups, etc.
            response = self.ai_client.generate_response(query)
            return response
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error: {e}"
    
    def _show_help(self):
        """Show available commands."""
        help_text = """
Available commands:
- Ask any question about stocks, markets, or investments
- 'help' - Show this help message
- 'quit' or 'exit' - End the session

Examples:
- "What is the current price of AAPL?"
- "Analyze the tech sector performance"
- "Should I invest in renewable energy stocks?"
        """
        print(help_text)
