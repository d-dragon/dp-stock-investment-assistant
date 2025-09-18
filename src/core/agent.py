"""
Stock Investment Agent - Main AI agent for handling user interactions.
Refactored to support multi-model architecture via ModelClientFactory & LangChain prompt.
"""

import logging
import re
import time
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
                    response = self.process_query(user_input)
                    print(f"\nAssistant: {response}\n")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error processing query: {e}")
                print(f"Error: {e}")

    # -------- Core processing --------
    def process_query(self, query: str, *, provider: Optional[str] = None) -> str:
        try:
            tickers = self._extract_tickers(query)
            quick_ctx = {}
            if tickers and self._looks_like_price_request(query):
                quick_ctx = self._build_quick_price_context(tickers)

            prompt = build_prompt(query, quick_ctx, tickers)
            if self.config.get("model", {}).get("debug_prompt"):
                self.logger.debug(f"[PROMPT]\n{prompt}")

            client = self._select_client(provider)
            return self._generate_with_fallback(
                client=client,
                prompt=prompt,
                query=query,
                news=self._looks_like_news_query(query),
            )
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error: {e}"

    def process_query_streaming(self, query: str, *, provider: Optional[str] = None) -> Generator[str, None, None]:
        try:
            tickers = self._extract_tickers(query)
            prompt = build_prompt(query, {}, tickers)
            if self.config.get("model", {}).get("debug_prompt"):
                yield "[DEBUG PROMPT START]\n" + prompt + "\n[DEBUG PROMPT END]\n"
            client = self._select_client(provider)
            # Streaming only on primary; if fail, emit fallback note and retry non-stream
            try:
                for chunk in client.generate_stream(prompt):
                    yield chunk
            except Exception as e:
                self.logger.warning(f"Primary streaming failed ({client.provider}): {e}")
                yield f"\n[notice] primary provider '{client.provider}' failed, attempting fallback...\n"
                text = self._generate_with_fallback(client, prompt, query, news=False)
                yield text
        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
            yield f"Sorry, I encountered an error: {e}"

    # -------- Fallback orchestration --------
    def _generate_with_fallback(self, client, prompt: str, query: str, *, news: bool) -> str:
        allow = self.config.get("model", {}).get("allow_fallback", True)
        sequence = [client.provider]
        if allow:
            # append remaining fallback providers excluding current
            fb = ModelClientFactory.get_fallback_sequence(self.config)
            sequence += [p for p in fb if p not in sequence]

        last_error = None
        for provider in sequence:
            try:
                start = time.time()
                active_client = (
                    client if provider == client.provider else ModelClientFactory.get_client(self.config, provider=provider)
                )
                if news and active_client.supports_web_search():
                    result = active_client.generate_with_search(prompt)
                else:
                    result = active_client.generate(prompt)
                elapsed = (time.time() - start) * 1000
                self.logger.info(
                    f"gen_success provider={active_client.provider} model={active_client.model_name} ms={elapsed:.1f}"
                )
                if provider != client.provider:
                    result = f"[fallback:{provider}] {result}"
                return result
            except Exception as e:
                last_error = e
                self.logger.warning(f"provider_fail provider={provider} error={e}")
                continue
        return f"All providers failed. Last error: {last_error}"

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

    def set_default_model(self, provider: str, model_name: str) -> Dict[str, Any]:
        """Update the default client used for responses."""
        self.config.setdefault("model", {})
        self.config["model"]["provider"] = provider
        self.config["model"]["name"] = model_name
        ModelClientFactory.clear_cache(provider=provider)
        self._client = ModelClientFactory.get_client(self.config, provider=provider, model_name=model_name)
        return {
            "provider": provider,
            "model": self._client.model_name
        }

    def set_active_model(self, *, provider: Optional[str], name: Optional[str]) -> None:
        """
        Update the active provider/model for subsequent requests.
        """
        model_cfg = self.config.setdefault("model", {})
        if provider:
            model_cfg["provider"] = provider
        if name:
            model_cfg["name"] = name
        effective_provider = model_cfg.get("provider")
        # Recreate underlying client with updated config
        self._client = ModelClientFactory.get_client(self.config, provider=effective_provider)
        self.logger.info(f"active_model provider={model_cfg.get('provider')} name={model_cfg.get('name')}")

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

