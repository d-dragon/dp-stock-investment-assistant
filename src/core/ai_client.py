"""
AI Client for interfacing with OpenAI's GPT API.
"""

import logging
from typing import Dict, Any, List, Optional, Generator
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

    def web_search_response(
        self, query: str, context: Optional[str] = None
    ) -> str:
        """Generate a response using OpenAI's web search capabilities.
        
        Args:
            query: User's search query
            context: Additional context for the AI
            
        Returns:
            Generated response from the AI
        """
        try:
            self.logger.info(f"Processing query: {query}")
            
            # Prepare the input for responses API
            input_content = f"{self._get_system_prompt(context)}\n\nUser query: {query}"
            
            # Use OpenAI's responses API with web search
            response = self.client.responses.create(
                model=self.model,
                input=input_content,
                tools=[{"type": "web_search_preview"}]
            )
            
            self.logger.info(f"Response type: {type(response)}")
            self.logger.info(f"Response output length: {len(response.output) if hasattr(response, 'output') else 'No output attr'}")
            
            if hasattr(response, 'output') and response.output:
                self.logger.info(f"Response has {len(response.output)} output items")
                
                # Iterate through all output items to find one with content
                for i, item in enumerate(response.output):
                    self.logger.info(f"Processing output item {i}: type={type(item)}")
                    self.logger.info(f"Item {i} attributes: {[attr for attr in dir(item) if not attr.startswith('_')]}")
                    
                    # Try to extract content from this item
                    extracted_content = self._extract_content_from_output_item(item, i)
                    if extracted_content:
                        self.logger.info(f"Successfully extracted content from item {i}")
                        return extracted_content
                
                # If no content found in any item, log all items for debugging
                self.logger.warning(f"No content found in any of the {len(response.output)} output items")
                for i, item in enumerate(response.output):
                    self.logger.warning(f"Item {i}: {type(item)}")
                    if hasattr(item, '__dict__'):
                        self.logger.warning(f"Item {i} dict: {item.__dict__}")
                    else:
                        self.logger.warning(f"Item {i} str: {str(item)[:200]}...")
                
                # Final fallback: convert first item to string
                if response.output:
                    self.logger.info(f"Using string conversion fallback on first item")
                    return str(response.output[0])
            
            # Final fallback
            self.logger.warning("No response content found, using fallback")
            return self.generate_response(query, context)
            
        except Exception as e:
            self.logger.error(f"Error in web search response: {e}")
            # Fallback to regular chat completion
            try:
                return self.generate_response(query, context)
            except Exception as fallback_error:
                self.logger.error(f"Fallback also failed: {fallback_error}")
                return f"Sorry, I encountered an error: {str(e)}"

    def web_search_response_streaming(
        self, query: str, context: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Generate a streaming web search response using OpenAI's API.
        
        Args:
            query: User's search query
            context: Additional context for the AI
            
        Yields:
            Response chunks as they are generated
        """
        try:
            self.logger.info(f"Processing streaming query: {query}")
            
            # Prepare the input for responses API
            input_content = f"{self._get_system_prompt(context)}\n\nUser query: {query}"
            
            # Use OpenAI's responses API with web search and streaming
            response = self.client.responses.create(
                model=self.model,
                input=input_content,
                tools=[{"type": "web_search_preview"}],
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
            
            # Stream the response chunks
            for chunk in response:
                self.logger.debug(f"Streaming chunk type: {type(chunk)}")
                
                if hasattr(chunk, 'output') and chunk.output:
                    for output in chunk.output:
                        content = self._extract_content_from_item(output)
                        if content:
                            yield content
                elif hasattr(chunk, 'choices') and chunk.choices:
                    # Fallback for different response format
                    for choice in chunk.choices:
                        if hasattr(choice, 'delta') and hasattr(choice.delta, 'content') and choice.delta.content:
                            yield choice.delta.content
            
        except Exception as e:
            self.logger.error(f"Error generating streaming web search response: {e}")
            # Fallback to streaming chat completion
            try:
                yield from self._generate_streaming_fallback(query, context)
            except Exception as fallback_error:
                self.logger.error(f"Streaming fallback also failed: {fallback_error}")
                yield f"Error: {str(e)}"

    def _extract_content_from_output_item(self, item, item_index: int) -> Optional[str]:
        """Extract content from a specific output item.
        
        Args:
            item: Output item object from response
            item_index: Index of the item for logging
            
        Returns:
            Extracted content string or None if no content found
        """
        try:
            # Based on API docs, check for content array first
            if hasattr(item, 'content') and item.content:
                self.logger.info(f"Item {item_index} has content: {type(item.content)}")
                
                if isinstance(item.content, list) and item.content:
                    # content is an array of content parts
                    for j, content_part in enumerate(item.content):
                        self.logger.info(f"Content part {j} type: {type(content_part)}")
                        self.logger.info(f"Content part {j} attributes: {[attr for attr in dir(content_part) if not attr.startswith('_')]}")
                        if hasattr(content_part, 'text') and content_part.text:
                            self.logger.info(f"Found text in content part {j}: {content_part.text[:100]}...")
                            return content_part.text
                
                elif isinstance(item.content, str) and item.content.strip():
                    self.logger.info(f"Content is string: {item.content[:100]}...")
                    return item.content
                
                elif hasattr(item.content, 'text') and item.content.text:
                    self.logger.info(f"Content has text: {item.content.text[:100]}...")
                    return item.content.text
            
            # Check for direct text attribute (OutputText object)
            if hasattr(item, 'text') and item.text:
                self.logger.info(f"Found direct text attribute: {item.text[:100]}...")
                return item.text
            
            # Check for message with content (assistant message format)
            if hasattr(item, 'message'):
                message = item.message
                self.logger.info(f"Found message attribute: {type(message)}")
                if hasattr(message, 'content'):
                    if isinstance(message.content, list) and message.content:
                        # Message content is array of content parts
                        for content_part in message.content:
                            if hasattr(content_part, 'text') and content_part.text:
                                return content_part.text
                    elif isinstance(message.content, str) and message.content.strip():
                        return message.content
                    elif hasattr(message.content, 'text') and message.content.text:
                        return message.content.text
            
            # Check if item has role and content (message format)
            if hasattr(item, 'role') and hasattr(item, 'content'):
                if isinstance(item.content, list) and item.content:
                    for content_part in item.content:
                        if hasattr(content_part, 'text') and content_part.text:
                            return content_part.text
                elif isinstance(item.content, str) and item.content.strip():
                    return item.content
            
            # Log available attributes for debugging
            self.logger.debug(f"Item {item_index} - no extractable content found")
            self.logger.debug(f"Available attributes: {[attr for attr in dir(item) if not attr.startswith('_')]}")
            
        except Exception as e:
            self.logger.error(f"Error extracting content from item {item_index}: {e}")
        
        return None

    def _extract_content_from_item(self, item) -> Optional[str]:
        """Extract content from a response item.
        
        Args:
            item: Response item object
            
        Returns:
            Extracted content string or None
        """
        if isinstance(item, dict):
            return item.get('content', item.get('text', ''))
        else:
            # Try different possible attributes
            if hasattr(item, 'content'):
                content = item.content
                if isinstance(content, str):
                    return content
                elif hasattr(content, 'text'):
                    return content.text
            elif hasattr(item, 'text'):
                return item.text
            elif hasattr(item, 'message'):
                message = item.message
                if hasattr(message, 'content'):
                    return message.content
        
        return None

    def _generate_streaming_fallback(
        self, query: str, context: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Generate streaming response using regular chat completion as fallback.
        
        Args:
            query: User's question or prompt
            context: Additional context for the AI
            
        Yields:
            Response chunks as they are generated
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
            
            # Make streaming API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"Error in streaming fallback: {e}")
            yield f"Error: {str(e)}"

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
