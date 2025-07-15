"""
AI Client for interfacing with OpenAI's GPT API.
"""

import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI


class AIClient:
    """Client for OpenAI API interactions."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the AI client.
        
        Args:
            config: Configuration dictionary containing OpenAI settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        openai_config = config.get('openai', {})
        api_key = openai_config.get('api_key')
        
        if not api_key:
            raise ValueError("OpenAI API key not found in configuration")
            
        self.client = OpenAI(api_key=api_key)
        self.model = openai_config.get('model', 'gpt-4')
        self.max_tokens = openai_config.get('max_tokens', 2000)
        self.temperature = openai_config.get('temperature', 0.7)
        
        self.logger.info(f"AI Client initialized with model: {self.model}")
    
    def generate_response(self, query: str, context: Optional[str] = None) -> str:
        """Generate a response using OpenAI's API.
        
        Args:
            query: User's question or prompt
            context: Additional context for the AI
            
        Returns:
            Generated response from the AI
        """
        try:
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt(context)
                },
                {
                    "role": "user", 
                    "content": query
                }
            ]
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error generating AI response: {e}")
            raise
    
    def _get_system_prompt(self, context: Optional[str] = None) -> str:
        """Get the system prompt for the AI.
        
        Args:
            context: Additional context to include
            
        Returns:
            System prompt string
        """
        base_prompt = """You are a helpful AI assistant specializing in stock market analysis and investment advice. 
        You provide clear, accurate, and actionable insights about stocks, market trends, and investment strategies.
        
        Key guidelines:
        - Always remind users that you provide information, not financial advice
        - Be factual and base responses on sound financial principles
        - Suggest users consult with financial advisors for major decisions
        - Use clear, accessible language
        """
        
        if context:
            return f"{base_prompt}\n\nAdditional context: {context}"
        
        return base_prompt
