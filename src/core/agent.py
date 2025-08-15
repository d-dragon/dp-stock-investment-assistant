"""
Stock Investment Agent - Main AI agent for handling user interactions.
Refactored to support multi-model architecture via ModelClientFactory & LangChain prompt.
"""

import logging
import re
from typing import Dict, Any, Optional, Generator, List

from .model_factory import ModelClientFactory
from .data_manager import DataManager
from .langchain_adapter import build_prompt


TICKER_REGEX = re.compile(r"\b[A-Z]{1,5}\b")


class StockAgent:
    """Main agent class for the Stock Investment Assistant (multi-model)."""

    def __init__(self, config: Dict[str, Any], data_manager: DataManager):
        self.config = config
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)

        # Preload default client (lazy if needed)
        self._client = ModelClientFactory.get_client(config)

    # -------- Public interactive loop (unchanged UX) --------
    def run_interactive(self):
        self.logger.info("Starting interactive session...")
        print("Welcome to DP Stock-Investment Assistant!")
        print("Type 'quit' or 'exit' to end the session.")
        print("Type 'help' for available commands.\n")

        while True:
            try:
                user_input = input("Stock Assistant> ").strip()
                if user_input.lower() in ["quit", "exit"]:
                    print("Goodbye!")
                    break
                elif user_input.lower() == "help":
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

    # -------- Core processing --------
    def _process_query(self, query: str, *, provider: Optional[str] = None) -> str:
        try:
            tickers = self._extract_tickers(query)
            prompt = build_prompt(query, {}, tickers)
            client = self._select_client(provider)

            # Fast path: if simple price/info request & tickers
            if tickers and self._looks_like_price_request(query):
                enriched = self._build_quick_price_context(tickers)
                prompt = build_prompt(query, enriched, tickers)

            # Prefer web search if provider supports & query seems news-related
            if client.supports_web_search() and self._looks_like_news_query(query):
                return client.generate_with_search(prompt)

            return client.generate(prompt)
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error: {e}"

    def _process_query_non_streaming(self, query: str) -> str:
        return self._process_query(query)

    def process_query_streaming(self, query: str, *, provider: Optional[str] = None) -> Generator[str, None, None]:
        try:
            tickers = self._extract_tickers(query)
            prompt = build_prompt(query, {}, tickers)
            client = self._select_client(provider)
            for chunk in client.generate_stream(prompt):
                yield chunk
        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
            yield f"Sorry, I encountered an error: {e}"

    # -------- Helper methods --------
    def _select_client(self, provider: Optional[str]):
        if provider:
            return ModelClientFactory.get_client(self.config, provider=provider)
        return self._client

    def _extract_tickers(self, text: str) -> List[str]:
        raw = TICKER_REGEX.findall(text.upper())
        # Basic filtering; could integrate with DataManager for validation
        return list({t for t in raw if 1 < len(t) <= 5})

    def _looks_like_price_request(self, query: str) -> bool:
        q = query.lower()
        return any(k in q for k in ["price", "quote", "current", "close"])

    def _looks_like_news_query(self, query: str) -> bool:
        q = query.lower()
        return any(k in q for k in ["news", "headline", "latest", "market"])

    def _build_quick_price_context(self, tickers: List[str]) -> Dict[str, Any]:
        ctx = {"prices": []}
        for t in tickers[:4]:
            info = self.data_manager.get_stock_info(t)
            if info:
                ctx["prices"].append(
                    {
                        "symbol": t,
                        "price": info.get("current_price"),
                        "prev_close": info.get("previous_close"),
                        "pe": info.get("pe_ratio"),
                    }
                )
        return ctx

    def _show_help(self):
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
