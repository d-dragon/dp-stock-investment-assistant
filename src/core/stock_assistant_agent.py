"""
Stock Assistant Agent with LangGraph ReAct Pattern.

Implements a ReAct (Reasoning + Acting) agent that uses LangGraph tools
for stock-related queries. Replaces the legacy StockAgent with a modern
tool-orchestrated architecture.
Migration Note (v1.0):
    Migrated from `langgraph.prebuilt.create_react_agent` (deprecated in
    LangGraph v1.0) to `langchain.agents.create_agent`. Key API change:
    `prompt=` parameter renamed to `system_prompt=`.
Reference: .github/instructions/backend-python.instructions.md § Model Factory
"""

from __future__ import annotations

import asyncio
import logging
import pathlib
import re
import time
from typing import Any, Dict, Generator, List, Mapping, Optional

import yaml

try:
    from langchain.agents import create_agent  # type: ignore
except ImportError:
    try:
        from langgraph.prebuilt import create_react_agent

        def create_agent(*, model, tools, system_prompt, checkpointer=None, name=None):
            """Compatibility wrapper for older LangChain/LangGraph stacks."""
            kwargs = {}
            if checkpointer is not None:
                kwargs["checkpointer"] = checkpointer
            if name is not None:
                kwargs["name"] = name
            return create_react_agent(
                model=model,
                tools=tools,
                prompt=system_prompt,
                **kwargs,
            )
    except ImportError:
        def create_agent(*, model, tools, system_prompt, checkpointer=None, name=None):
            """Defer missing optional dependency failure to agent construction time."""
            raise ImportError(
                "No compatible agent constructor found. Install a supported "
                "LangChain/LangGraph version that provides either "
                "langchain.agents.create_agent or langgraph.prebuilt.create_react_agent."
            )
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI

from .data_manager import DataManager
from .langchain_adapter import build_prompt
from .model_factory import ModelClientFactory
from .prompt_asset_loader import PromptAssetLoader
from .prompt_assembler import PromptAssembler
from .prompt_types import PromptSelection, SelectionTuple
from .routes import StockQueryRoute
from .tools.registry import ToolRegistry, get_tool_registry
from .types import AgentResponse, ResponseStatus, TokenUsage, ToolCall


TICKER_REGEX = re.compile(r"\b[A-Z]{1,5}\b")


class StockAssistantAgent:
    """ReAct-based agent for stock investment assistance.
    
    Uses LangChain's ReAct pattern to orchestrate tools for:
    - Stock price lookups
    - Technical analysis via TradingView
    - Report generation
    - General market queries
    
    The agent binds all enabled tools from ToolRegistry and lets the
    ReAct reasoning decide which tools to use for each query.
    
    Attributes:
        config: Application configuration dict
        data_manager: DataManager for fetching stock data
        logger: Logger instance
        cache: CacheBackend for model caching
        
    Example:
        >>> agent = StockAssistantAgent(config, data_manager)
        >>> response = agent.process_query("What is AAPL trading at?")
        >>> print(response)
        'AAPL is currently trading at $150.25...'
    """
    
    # System prompt for the ReAct agent
    # DEPRECATED: retained as fallback alias during M1 observation window;
    # remove after PS-04 verification when PromptAssetLoader is the
    # authoritative prompt source.
    REACT_SYSTEM_PROMPT = """You are a professional stock investment assistant.
You help users with stock analysis, price lookups, technical analysis, and investment research.

You have access to specialized tools for:
- Looking up stock symbols and price information
- Getting TradingView technical analysis charts
- Generating investment reports

When answering questions:
1. Use the appropriate tools when you need real-time data or analysis
2. Provide accurate, factual information based on tool outputs
3. Include relevant disclaimers for investment-related advice
4. Be concise but comprehensive in your responses

If you don't have a tool for a specific request, provide helpful general guidance based on your knowledge."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        data_manager: DataManager,
        *,
        tool_registry: Optional[ToolRegistry] = None,
        checkpointer: Optional[Any] = None,
        logger: Optional[logging.Logger] = None,
        prompt_asset_loader: Optional[PromptAssetLoader] = None,
        prompt_assembler: Optional[PromptAssembler] = None,
    ) -> None:
        """Initialize StockAssistantAgent.
        
        Args:
            config: Application configuration dict
            data_manager: DataManager instance for stock data
            tool_registry: Optional ToolRegistry (defaults to singleton)
            checkpointer: Optional LangGraph checkpointer for session memory (e.g., MongoDBSaver)
            logger: Optional logger instance
            prompt_asset_loader: Optional PromptAssetLoader for resolved prompt assets.
                When provided, the agent uses it as the authoritative prompt source (PS-04).
                When ``None``, falls back to ``_load_system_prompt()`` (pre-PS-04 transition).
            prompt_assembler: Optional PromptAssembler for route-aware prompt composition (M2 PS-08).
                When provided and ``route_contexts.enabled`` is ``True`` in config, the agent
                composes the system prompt through ``PromptAssembler.compile()`` instead of using
                the raw ``PromptSelection`` content.
        """
        self.config = config
        self.data_manager = data_manager
        self.logger = logger or logging.getLogger(__name__)
        self._checkpointer = checkpointer  # Store checkpointer for session-aware queries
        self._prompt_asset_loader = prompt_asset_loader
        self._prompt_assembler = prompt_assembler
        
        # Initialize cache backend
        from utils.cache import CacheBackend
        self.cache = CacheBackend.from_config(config, logger=self.logger)
        
        # Initialize tool registry
        self._tool_registry = tool_registry or get_tool_registry(logger=self.logger)
        
        # Initialize tools into the registry
        self._initialize_tools()
        
        # Preload default client (for model info)
        self._client = ModelClientFactory.get_client(self.config)
        
        # Load the system prompt
        if self._prompt_asset_loader is not None:
            # PS-04 path: use PromptAssetLoader as authoritative prompt source
            self._current_prompt = self._prompt_asset_loader.resolve(
                SelectionTuple(
                    agent_role="react_analyst",
                    selection_mode="fixed",
                    requested_version="1.0.0",
                )
            )
            self._prompt_content = (
                # Read the resolved asset content from disk
                pathlib.Path(__file__).parent.parent
                / "prompts"
                / self._current_prompt.selected_assets[0]
            ).read_text(encoding="utf-8")
            self.logger.info(
                "PromptAssetLoader resolved: %s v%s (%s) — fallback=%s",
                self._current_prompt.selected_assets[0],
                self._current_prompt.prompt_version,
                self._current_prompt.prompt_variant,
                self._current_prompt.fallback_used,
            )

            # M2 PS-08: Compose route-aware prompt via PromptAssembler
            self._current_route = StockQueryRoute.GENERAL_CHAT  # default until per-query
            self._compiled_prompt = None
            if self._prompt_assembler is not None:
                prompts_cfg = self.config.get("prompts", {})
                rc_cfg = prompts_cfg.get("route_contexts", {})
                if rc_cfg.get("enabled", False):
                    self._compiled_prompt = self._prompt_assembler.compile(
                        selection=self._current_prompt,
                        route=self._current_route,
                    )
                    self._prompt_content = self._compiled_prompt.compiled_text
                    self.logger.info(
                        "PromptAssembler compiled route-aware prompt: "
                        "route=%s, route_skill_used=%s",
                        self._current_route.value,
                        self._compiled_prompt.trace_metadata.get(
                            "route_skill_used", False
                        ),
                    )
                else:
                    self.logger.debug(
                        "PromptAssembler available but route_contexts not enabled"
                    )
        else:
            # Pre-PS-04 transition path: direct file read with inline fallback
            self._current_prompt, self._prompt_content = self._load_system_prompt()
            self._current_route = StockQueryRoute.GENERAL_CHAT
            self._compiled_prompt = None
        
        # Build the ReAct agent
        self._agent_executor = self._build_agent_executor()

    def _load_system_prompt(self) -> tuple[PromptSelection, str]:
        """Load the system prompt from the externalized prompt asset.

        Reads ``src/prompts/system/react_analyst.md``, parses frontmatter,
        and returns a ``(PromptSelection, content)`` tuple. Falls back to the
        hardcoded ``REACT_SYSTEM_PROMPT`` constant when the file is missing
        (pre-PS-04 safety net).

        Note:
            This is an intermediate step. Phase 4 (T019) replaces this
            method with ``PromptAssetLoader.resolve()``.
        """
        prompt_path = pathlib.Path(__file__).parent.parent / "prompts" / "system" / "react_analyst.md"
        try:
            text = prompt_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            self.logger.warning(
                "Prompt asset not found at %s. Falling back to inline REACT_SYSTEM_PROMPT.",
                prompt_path,
            )
            self.logger.warning(
                "REACT_SYSTEM_PROMPT is DEPRECATED — remove after PS-04 verification "
                "(PromptAssetLoader is the authoritative prompt source)."
            )
            return (
                PromptSelection(
                    selected_assets=["<inline>"],
                    prompt_version="0.0.0",
                    prompt_variant="inline_fallback",
                    selection_mode="fixed",
                    fallback_used=True,
                    degraded_reason=f"Prompt asset {prompt_path} not found",
                    trace_metadata={},
                ),
                self.REACT_SYSTEM_PROMPT,
            )

        # Split frontmatter from content
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) < 3:
                self.logger.warning(
                    "Malformed frontmatter in %s (missing closing ---). Falling back.",
                    prompt_path,
                )
                return (
                    PromptSelection(
                        selected_assets=["<inline>"],
                        prompt_version="0.0.0",
                        prompt_variant="inline_fallback",
                        selection_mode="fixed",
                        fallback_used=True,
                        degraded_reason=f"Malformed frontmatter in {prompt_path}",
                        trace_metadata={},
                    ),
                    self.REACT_SYSTEM_PROMPT,
                )
            raw_frontmatter = parts[1].strip()
            content = parts[2].strip()
        else:
            self.logger.warning(
                "No frontmatter delimiters in %s. Falling back.", prompt_path,
            )
            return (
                PromptSelection(
                    selected_assets=["<inline>"],
                    prompt_version="0.0.0",
                    prompt_variant="inline_fallback",
                    selection_mode="fixed",
                    fallback_used=True,
                    degraded_reason=f"No frontmatter in {prompt_path}",
                    trace_metadata={},
                ),
                self.REACT_SYSTEM_PROMPT,
            )

        # Parse YAML frontmatter
        try:
            frontmatter = yaml.safe_load(raw_frontmatter)
        except yaml.YAMLError as exc:
            self.logger.warning(
                "Failed to parse frontmatter in %s: %s. Falling back.", prompt_path, exc,
            )
            return (
                PromptSelection(
                    selected_assets=["<inline>"],
                    prompt_version="0.0.0",
                    prompt_variant="inline_fallback",
                    selection_mode="fixed",
                    fallback_used=True,
                    degraded_reason=f"Frontmatter parse error in {prompt_path}: {exc}",
                    trace_metadata={},
                ),
                self.REACT_SYSTEM_PROMPT,
            )

        if not isinstance(frontmatter, dict):
            self.logger.warning(
                "Frontmatter in %s is not a mapping. Falling back.", prompt_path,
            )
            return (
                PromptSelection(
                    selected_assets=["<inline>"],
                    prompt_version="0.0.0",
                    prompt_variant="inline_fallback",
                    selection_mode="fixed",
                    fallback_used=True,
                    degraded_reason=f"Invalid frontmatter type in {prompt_path}",
                    trace_metadata={},
                ),
                self.REACT_SYSTEM_PROMPT,
            )

        version = frontmatter.get("version", "0.0.0")
        variant = frontmatter.get("variant", "unknown")
        agent_role = frontmatter.get("agent_role", "unknown")

        self.logger.info(
            "Loaded prompt asset: %s v%s (%s) — role=%s",
            prompt_path.name, version, variant, agent_role,
        )

        trace_meta = {
            "prompt_version": version,
            "prompt_variant": variant,
            "prompt_selection_mode": "fixed",
            "agent_role": agent_role,
        }

        return (
            PromptSelection(
                selected_assets=["system/react_analyst.md"],
                prompt_version=version,
                prompt_variant=variant,
                selection_mode="fixed",
                fallback_used=False,
                degraded_reason=None,
                trace_metadata=trace_meta,
            ),
            content,
        )

    def _inject_prompt_metadata(self) -> Dict[str, Any]:
        """Build metadata dict from the resolved prompt selection.

        Returns a dict containing prompt identity fields suitable for
        inclusion in response metadata and LangSmith trace tags.

        Always populated regardless of LangSmith connectivity (M1-NFR-004).
        At M2 scope, also includes route context metadata when a
        ``CompiledPrompt`` is available.
        """
        meta = dict(self._current_prompt.trace_metadata) if self._current_prompt.trace_metadata else {}
        meta["prompt_version"] = self._current_prompt.prompt_version
        meta["prompt_variant"] = self._current_prompt.prompt_variant
        meta["prompt_selection_mode"] = self._current_prompt.selection_mode
        meta["fallback_used"] = self._current_prompt.fallback_used
        if self._current_prompt.fallback_used and self._current_prompt.degraded_reason:
            meta["degraded_reason"] = self._current_prompt.degraded_reason

        # M2 PS-08: Add route context metadata when CompiledPrompt is available
        if self._compiled_prompt is not None:
            tm = self._compiled_prompt.trace_metadata
            meta["route"] = tm.get("route", "")
            meta["route_skill_used"] = tm.get("route_skill_used", False)
            meta["selected_skills"] = tm.get("selected_skills", [])
            if "missing_route_skills" in tm:
                meta["missing_route_skills"] = tm["missing_route_skills"]

        # Add model provider/name from the current client
        try:
            client = self._client
            if hasattr(client, "_provider"):
                meta["model_provider"] = client._provider
            elif hasattr(client, "provider"):
                meta["model_provider"] = client.provider
            else:
                meta["model_provider"] = self.config.get("model_provider", "openai")

            if hasattr(client, "_model_name"):
                meta["model_name"] = client._model_name
            elif hasattr(client, "model_name"):
                meta["model_name"] = client.model_name
            else:
                meta["model_name"] = self.config.get("openai", {}).get("model", "gpt-4")
        except Exception:
            meta["model_provider"] = self.config.get("model_provider", "openai")
            meta["model_name"] = self.config.get("openai", {}).get("model", "gpt-4")

        return meta

    def _initialize_tools(self) -> None:
        """Initialize and register tools into the ToolRegistry.
        
        Loads all available tool implementations and registers them
        as enabled or disabled based on configuration.
        """
        try:
            from core.tools.stock_symbol import StockSymbolTool
            from core.tools.reporting import ReportingTool
            # from core.tools.tradingview import TradingViewTool  # Phase 2
            
            langchain_config = self.config.get('langchain', {})
            tools_config = langchain_config.get('tools', {})
            
            # Check if tools are globally enabled
            tools_enabled = tools_config.get('enabled', True)
            
            if not tools_enabled:
                self.logger.info("Tools globally disabled in configuration")
                return
            
            # Initialize and register StockSymbolTool
            try:
                stock_tool = StockSymbolTool(
                    data_manager=self.data_manager,
                    cache=self.cache,
                    logger=self.logger.getChild("stock_symbol_tool")
                )
                self._tool_registry.register(stock_tool, enabled=True)
            except Exception as e:
                self.logger.warning(f"Failed to initialize StockSymbolTool: {e}")
            
            # Initialize and register ReportingTool
            try:
                reporting_tool = ReportingTool(
                    data_manager=self.data_manager,
                    cache=self.cache,
                    logger=self.logger.getChild("reporting_tool")
                )
                self._tool_registry.register(reporting_tool, enabled=True)
            except Exception as e:
                self.logger.warning(f"Failed to initialize ReportingTool: {e}")
            
            # TradingViewTool - Phase 2
            # try:
            #     tradingview_tool = TradingViewTool(
            #         data_manager=self.data_manager,
            #         cache=self.cache,
            #         logger=self.logger.getChild("tradingview_tool")
            #     )
            #     self._tool_registry.register(tradingview_tool, enabled=False)  # Disabled for Phase 2
            # except Exception as e:
            #     self.logger.warning(f"Failed to initialize TradingViewTool: {e}")
            
            enabled_count = len(self._tool_registry.get_enabled_tools())
            self.logger.info(f"Tools initialized: {enabled_count} enabled, {len(self._tool_registry)} total")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize tools: {e}", exc_info=True)
    
    def _build_agent_executor(self):
        """Build LangGraph ReAct agent.
        
        Returns:
            CompiledStateGraph configured with enabled tools and optional checkpointer,
            or None if no tools are available.
        """
        # Get enabled tools from registry
        enabled_tools = self._tool_registry.get_enabled_tools()
        
        if not enabled_tools:
            self.logger.warning("No enabled tools found. Agent will run without tools.")
            return None
        
        tool_names = [tool.name for tool in enabled_tools]
        self.logger.info(f"Building ReAct agent with tools: {tool_names}")
        
        try:
            # Create LangChain ChatOpenAI model
            openai_config = self.config.get("openai", {})
            model_config = self.config.get("model", {})
            
            llm = ChatOpenAI(
                model=model_config.get("name") or openai_config.get("model", "gpt-4"),
                api_key=openai_config.get("api_key"),
                temperature=openai_config.get("temperature", 0.7),
            )
            
            # Create ReAct agent using langchain.agents.create_agent
            # Migrated from deprecated langgraph.prebuilt.create_react_agent (LangGraph v1.0)
            # Pass checkpointer if available for session-aware memory
            # Prompt source: externalized asset via self._current_prompt (M1 PS-04)
            system_prompt_text = self._prompt_content
            if self._current_prompt.fallback_used:
                self.logger.warning(
                    "Using inline fallback prompt — asset resolution failed: %s",
                    self._current_prompt.degraded_reason,
                )
            agent = create_agent(
                model=llm,
                tools=enabled_tools,
                system_prompt=system_prompt_text,
                checkpointer=self._checkpointer,  # None if not configured
                name="stock_assistant",
            )
            
            if self._checkpointer:
                self.logger.info("LangGraph ReAct agent built with checkpointer (session memory enabled)")
            else:
                self.logger.info("LangGraph ReAct agent built successfully (stateless mode)")
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to build ReAct agent: {e}")
            return None
    
    # -------- Public API (Compatible with StockAgent interface) --------
    
    def run_interactive(self) -> None:
        """Run interactive command-line session."""
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
    
    def process_query(
        self,
        query: str,
        *,
        provider: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> str:
        """Process a query and return complete response.
        
        Uses ReAct agent if available, falls back to legacy behavior otherwise.
        
        Args:
            query: User query to process
            provider: Optional provider override
            conversation_id: Conversation ID for STM memory (UUID v4).
                       When provided with a checkpointer, enables multi-turn
                       conversations with context recall.
            
        Returns:
            Complete response text
        """
        try:
            # Try ReAct agent first
            if self._agent_executor:
                return self._process_with_react(query, provider=provider, conversation_id=conversation_id)
            
            # Fallback to legacy processing
            return self._process_legacy(query, provider=provider)
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error: {e}"
    
    def process_query_streaming(
        self,
        query: str,
        *,
        provider: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """Process a query and stream response chunks.
        
        Uses astream_events() for proper tool call visibility during streaming.
        
        Args:
            query: User query to process
            provider: Optional provider override
            conversation_id: Conversation ID for STM memory (UUID v4).
                       When provided with a checkpointer, enables multi-turn
                       conversations with context recall.
            
        Yields:
            Response text chunks
        """
        try:
            # If we have a ReAct agent, use async streaming
            if self._agent_executor:
                # Run async streaming in sync context
                loop = asyncio.new_event_loop()
                try:
                    async_gen = self._stream_with_react_async(query, provider=provider, conversation_id=conversation_id)
                    while True:
                        try:
                            chunk = loop.run_until_complete(async_gen.__anext__())
                            yield chunk
                        except StopAsyncIteration:
                            break
                finally:
                    loop.close()
            else:
                # Fallback to legacy streaming
                yield from self._stream_legacy(query, provider=provider)
                
        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
            yield f"Sorry, I encountered an error: {e}"
    
    def process_query_structured(
        self,
        query: str,
        *,
        provider: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> AgentResponse:
        """Process a query and return structured AgentResponse.
        
        Returns full response with metadata, status, tool calls, and token usage.
        
        Args:
            query: User query to process
            provider: Optional provider override
            conversation_id: Conversation ID for STM memory (UUID v4).
            
        Returns:
            AgentResponse with content and metadata
        """
        start_time = time.time()
        tool_calls: List[ToolCall] = []
        
        try:
            if self._agent_executor:
                # Build invoke config for conversation memory
                invoke_config = None
                if conversation_id and self._checkpointer:
                    invoke_config = {"configurable": {"thread_id": conversation_id}}
                
                # Use LangGraph ReAct agent
                result = self._agent_executor.invoke(
                    {"messages": [HumanMessage(content=query)]},
                    config=invoke_config,
                )
                
                # Extract tool calls from messages
                messages = result.get("messages", [])
                content = ""
                
                for msg in messages:
                    # Tool messages contain tool call results
                    if hasattr(msg, 'type') and msg.type == 'tool':
                        tool_calls.append(ToolCall(
                            name=getattr(msg, 'name', 'unknown'),
                            input={"query": query},  # Simplified - actual input not preserved
                            output=str(msg.content) if hasattr(msg, 'content') else "",
                            execution_time_ms=None,
                        ))
                    # Get final AI response
                    elif isinstance(msg, AIMessage) and msg.content:
                        content = msg.content
                
                # Get model info
                client = self._select_client(provider)
                
                return AgentResponse.success(
                    content=content,
                    provider=client.provider,
                    model=client.model_name,
                    tool_calls=tuple(tool_calls),
                    metadata={
                        "execution_time_ms": (time.time() - start_time) * 1000,
                        "tools_used": len(tool_calls),
                    },
                )
            
            # Fallback to legacy
            content = self._process_legacy(query, provider=provider)
            client = self._select_client(provider)
            
            return AgentResponse.success(
                content=content,
                provider=client.provider,
                model=client.model_name,
            )
            
        except Exception as e:
            self.logger.error(f"Structured query error: {e}")
            client = self._select_client(provider)
            return AgentResponse.error(
                message=str(e),
                provider=client.provider if client else "unknown",
                model=client.model_name if client else "unknown",
            )
    
    # -------- ReAct Processing --------
    
    def _process_with_react(
        self,
        query: str,
        *,
        provider: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> str:
        """Process query using LangGraph ReAct agent.
        
        Args:
            query: User query
            provider: Optional provider override
            conversation_id: Conversation ID for STM memory.
                       Maps to LangGraph thread_id for checkpointing.
            
        Returns:
            Response text from agent
        """
        try:
            # Build invoke config — conversation_id IS the thread_id
            invoke_config = None
            if conversation_id and self._checkpointer:
                invoke_config = {"configurable": {"thread_id": conversation_id}}
                self.logger.debug(f"Conversation-aware query with thread_id: {conversation_id}")
            
            # Inject prompt metadata into LangSmith trace tags (M1-FR-011)
            # Wrap in try/except so LangSmith failures degrade silently (M1-NFR-004)
            try:
                prompt_meta = self._inject_prompt_metadata()
                trace_tags = {
                    "prompt_version": prompt_meta.get("prompt_version", ""),
                    "prompt_variant": prompt_meta.get("prompt_variant", ""),
                    "prompt_selection_mode": prompt_meta.get("prompt_selection_mode", ""),
                    "agent_role": "react_analyst",
                    "model_provider": prompt_meta.get("model_provider", ""),
                    "model_name": prompt_meta.get("model_name", ""),
                }
                if invoke_config is None:
                    invoke_config = {"configurable": {"tags": trace_tags}}
                else:
                    invoke_config.setdefault("configurable", {})["tags"] = trace_tags
            except Exception:
                # LangSmith unavailable — degrade silently (M1-NFR-004)
                self.logger.debug("Failed to inject LangSmith trace tags (non-critical)")
            
            # LangGraph agent uses messages format
            result = self._agent_executor.invoke(
                {"messages": [HumanMessage(content=query)]},
                config=invoke_config,
            )
            
            # Extract final AI response from messages
            messages = result.get("messages", [])
            
            # Log tool usage
            tool_messages = [m for m in messages if hasattr(m, 'type') and m.type == 'tool']
            if tool_messages:
                tools_used = [getattr(m, 'name', 'unknown') for m in tool_messages]
                self.logger.info(f"ReAct used tools: {tools_used}")
            
            # Get the last AI message as output
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) and msg.content:
                    return msg.content
            
            return "No response generated."
            
        except Exception as e:
            self.logger.warning(f"ReAct processing failed: {e}, falling back to legacy")
            return self._process_legacy(query, provider=provider)
    
    async def _stream_with_react_async(
        self,
        query: str,
        *,
        provider: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ):
        """Async stream using astream_events for tool visibility.
        
        Args:
            query: User query
            provider: Optional provider override
            conversation_id: Conversation ID for STM memory.
                       Maps to LangGraph thread_id for checkpointing.
            
        Yields:
            Response chunks with tool call notifications
        """
        try:
            # Build stream config — conversation_id IS the thread_id
            stream_config = None
            if conversation_id and self._checkpointer:
                stream_config = {"configurable": {"thread_id": conversation_id}}
                self.logger.debug(f"Conversation-aware streaming with thread_id: {conversation_id}")
            
            async for event in self._agent_executor.astream_events(
                {"messages": [HumanMessage(content=query)]},
                version="v2",
                config=stream_config,
            ):
                kind = event.get("event", "")
                
                # Handle different event types
                if kind == "on_chat_model_stream":
                    # LLM token
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        yield chunk.content
                        
                elif kind == "on_tool_start":
                    # Tool is starting
                    tool_name = event.get("name", "unknown")
                    yield f"\n[Using tool: {tool_name}...]\n"
                    
                elif kind == "on_tool_end":
                    # Tool completed
                    pass  # Output will come through LLM stream
                    
        except Exception as e:
            self.logger.error(f"Async streaming error: {e}")
            yield f"\n[Error: {e}]\n"
    
    # -------- Legacy Processing (Fallback) --------
    
    def _process_legacy(
        self,
        query: str,
        *,
        provider: Optional[str] = None,
    ) -> str:
        """Legacy processing without ReAct agent.
        
        Used as fallback when agent isn't available or fails.
        
        Args:
            query: User query
            provider: Optional provider override
            
        Returns:
            Response text
        """
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
    
    def _stream_legacy(
        self,
        query: str,
        *,
        provider: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """Legacy streaming without ReAct agent.
        
        Args:
            query: User query
            provider: Optional provider override
            
        Yields:
            Response chunks
        """
        tickers = self._extract_tickers(query)
        prompt = build_prompt(query, {}, tickers)
        
        if self.config.get("model", {}).get("debug_prompt"):
            yield "[DEBUG PROMPT START]\n" + prompt + "\n[DEBUG PROMPT END]\n"
        
        client = self._select_client(provider)
        
        try:
            for chunk in client.generate_stream(prompt):
                yield chunk
        except Exception as e:
            self.logger.warning(f"Primary streaming failed ({client.provider}): {e}")
            yield f"\n[notice] primary provider '{client.provider}' failed, attempting fallback...\n"
            text = self._generate_with_fallback(client, prompt, query, news=False)
            yield text
    
    # -------- Fallback Orchestration --------
    
    def _generate_with_fallback(
        self,
        client,
        prompt: str,
        query: str,
        *,
        news: bool,
    ) -> str:
        """Generate with fallback to other providers.
        
        Args:
            client: Primary model client
            prompt: Formatted prompt
            query: Original query
            news: Whether this is a news query
            
        Returns:
            Generated response text
        """
        allow = self.config.get("model", {}).get("allow_fallback", True)
        sequence = [client.provider]
        if allow:
            fb = ModelClientFactory.get_fallback_sequence(self.config)
            sequence += [p for p in fb if p not in sequence]
        
        last_error = None
        for provider in sequence:
            try:
                start = time.time()
                active_client = (
                    client if provider == client.provider 
                    else ModelClientFactory.get_client(self.config, provider=provider)
                )
                
                if news and active_client.supports_web_search():
                    result = active_client.generate_with_search(prompt)
                else:
                    result = active_client.generate(prompt)
                
                elapsed = (time.time() - start) * 1000
                self.logger.info(
                    f"gen_success provider={active_client.provider} "
                    f"model={active_client.model_name} ms={elapsed:.1f}"
                )
                
                if provider != client.provider:
                    result = f"[fallback:{provider}] {result}"
                return result
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"provider_fail provider={provider} error={e}")
                continue
        
        return f"All providers failed. Last error: {last_error}"
    
    # -------- Helper Methods --------
    
    def get_current_model_info(
        self,
        provider: Optional[str] = None,
    ) -> Dict[str, str]:
        """Get current model information.
        
        Args:
            provider: Optional provider override
            
        Returns:
            Dict with 'provider' and 'model' keys
        """
        client = self._select_client(provider)
        return {
            "provider": client.provider,
            "model": client.model_name,
        }
    
    def _select_client(self, provider: Optional[str]):
        """Select model client based on provider."""
        if provider:
            return ModelClientFactory.get_client(self.config, provider=provider)
        return self._client
    
    def _extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from text."""
        raw = TICKER_REGEX.findall(text.upper())
        return list({t for t in raw if 1 < len(t) <= 5})
    
    def _looks_like_price_request(self, query: str) -> bool:
        """Check if query is asking for price information."""
        q = query.lower()
        return any(k in q for k in ["price", "quote", "current", "close"])
    
    def _looks_like_news_query(self, query: str) -> bool:
        """Check if query is asking for news."""
        q = query.lower()
        return any(k in q for k in ["news", "headline", "latest", "market"])
    
    def _build_quick_price_context(self, tickers: List[str]) -> Dict[str, Any]:
        """Build quick price context for tickers."""
        ctx = {"prices": []}
        for t in tickers[:4]:
            info = self.data_manager.get_stock_info(t)
            if info:
                ctx["prices"].append({
                    "symbol": t,
                    "price": info.get("current_price"),
                    "prev_close": info.get("previous_close"),
                    "pe": info.get("pe_ratio"),
                })
        return ctx
    
    def set_default_model(
        self,
        provider: str,
        model_name: str,
    ) -> Dict[str, Any]:
        """Update the default client used for responses.
        
        Args:
            provider: Provider name (e.g., 'openai', 'grok')
            model_name: Model name (e.g., 'gpt-4')
            
        Returns:
            Dict with provider and model info
        """
        self.config.setdefault("model", {})
        self.config["model"]["provider"] = provider
        self.config["model"]["name"] = model_name
        
        ModelClientFactory.clear_cache(provider=provider)
        self._client = ModelClientFactory.get_client(
            self.config,
            provider=provider,
            model_name=model_name,
        )
        
        # Rebuild agent executor with new model
        self._agent_executor = self._build_agent_executor()
        
        return {
            "provider": provider,
            "model": self._client.model_name,
        }
    
    def set_active_model(
        self,
        *,
        provider: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        """Set the active model for responses.
        
        Args:
            provider: Optional provider to set
            name: Optional model name to set
        """
        model_cfg = self.config.setdefault("model", {})
        
        if provider:
            model_cfg["provider"] = provider
        if name:
            model_cfg["name"] = name
            self.cache.set("openai_config:model_name", name, ttl_seconds=3600)
            self.logger.debug(f"Updated cache for model name: {name}")
        
        # Invalidate old client
        ModelClientFactory.clear_cache(provider=model_cfg.get("provider") or "openai")
        
        effective_provider = model_cfg.get("provider")
        self._client = ModelClientFactory.get_client(
            self.config,
            provider=effective_provider,
            model_name=model_cfg.get("name"),
        )
        
        # Rebuild agent executor with new model
        self._agent_executor = self._build_agent_executor()
        
        self.logger.info(
            f"active_model provider={model_cfg.get('provider')} name={model_cfg.get('name')}"
        )
    
    def _show_help(self) -> None:
        """Show help text for interactive mode."""
        help_text = """
Available commands:
- Ask any question about stocks, markets, or investments
- Get stock prices: "What is AAPL trading at?"
- Technical analysis: "Show me TradingView chart for MSFT"
- Generate reports: "Create a report on TSLA"
- Type 'quit' or 'exit' to end the session
- Type 'help' to see this message

The assistant uses AI-powered tools to provide real-time data and analysis.
Always verify important financial decisions with a qualified advisor.
"""
        print(help_text)


# Alias for backward compatibility
StockAgent = StockAssistantAgent


# ============================================================================
# LangSmith Studio Integration
# ============================================================================

def create_stock_assistant_agent(config: Optional[Dict] = None):
    """
    Factory function for LangSmith Studio (langgraph.json).
    
    Creates a StockAssistantAgent instance and returns the underlying
    CompiledStateGraph for Studio visualization and debugging.
    
    Args:
        config: Optional configuration dict. If None, loads from ConfigLoader.
                Studio may pass runtime config overrides.
    
    Returns:
        CompiledStateGraph: The agent executor compatible with Studio
    
    Usage:
        # Studio imports via bootstrap: ./src/core/langgraph_bootstrap.py:agent
        # The bootstrap sets up sys.path for project imports
        
        # Manual/programmatic usage
        agent_graph = create_stock_assistant_agent()
        response = agent_graph.invoke({"messages": [("user", "What is AAPL?")]})
    """
    from utils.config_loader import ConfigLoader
    
    # Load base config
    if config is None:
        cfg = ConfigLoader.load_config()
    else:
        # Merge Studio runtime config with local config
        base_cfg = ConfigLoader.load_config()
        cfg = {**base_cfg, **config}
    
    # Import DataManager here to avoid circular imports with agent.py
    from core.data_manager import DataManager
    dm = DataManager(cfg)
    
    # Create agent instance
    agent_instance = StockAssistantAgent(cfg, dm)
    
    # Return the CompiledStateGraph (created by create_agent())
    return agent_instance._agent_executor


# Module-level export for direct usage (when src is in PYTHONPATH)
# For Studio, use langgraph_bootstrap.py which sets up the path first
agent = create_stock_assistant_agent()
