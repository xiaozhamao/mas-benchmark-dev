"""
Client factory for creating framework-specific clients.
This module standardizes client creation across different frameworks.
"""

from typing import Any, Dict
from .framework_types import Framework


class ClientFactory:
    """
    Factory class for creating framework-specific clients.
    Standardizes client creation and configuration across frameworks.
    """

    @staticmethod
    def create_client(framework: Framework, llm_config: Dict[str, Any]) -> Any:
        """
        Create a framework-specific client.

        Args:
            framework: The framework type
            llm_config: LLM configuration dictionary

        Returns:
            Framework-specific client instance

        Raises:
            ValueError: If framework is not supported
        """
        if framework == Framework.AUTOGEN:
            return ClientFactory._create_autogen_client(llm_config)
        elif framework == Framework.LANGGRAPH:
            return ClientFactory._create_langgraph_client(llm_config)
        elif framework == Framework.OPENAI_AGENTS:
            return ClientFactory._create_openai_agents_client(llm_config)
        else:
            raise ValueError(f"Unsupported framework: {framework}")

    @staticmethod
    def _create_autogen_client(llm_config: Dict[str, Any]) -> Any:
        """
        Create Autogen framework client.

        Args:
            llm_config: LLM configuration dictionary

        Returns:
            OpenAIChatCompletionClient instance
        """
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        autogen_config = {
            "api_key": llm_config["api_key"],
            "model": llm_config["model"],
            "temperature": llm_config.get("temperature", 0),
        }

        return OpenAIChatCompletionClient(**autogen_config)

    @staticmethod
    def _create_langgraph_client(llm_config: Dict[str, Any]) -> Any:
        """
        Create LangGraph framework client.

        Args:
            llm_config: LLM configuration dictionary

        Returns:
            ChatOpenAI instance
        """
        from langchain_openai import ChatOpenAI

        langgraph_config = {
            "api_key": llm_config["api_key"],
            "model": llm_config["model"],
            "temperature": llm_config.get("temperature", 0),
        }

        return ChatOpenAI(**langgraph_config)

    @staticmethod
    def _create_openai_agents_client(llm_config: Dict[str, Any]) -> Any:
        """
        Create OpenAI Agents framework client.
        Also sets up global OpenAI Agents configuration.

        Args:
            llm_config: LLM configuration dictionary

        Returns:
            AsyncOpenAI instance
        """
        import httpx
        import json
        from openai import AsyncOpenAI
        from agents import set_default_openai_api, set_default_openai_client, set_tracing_disabled
        from ....logger import logger

        # Create httpx client with event hooks for logging
        async def log_request(request: httpx.Request):
            """Log outgoing request to OpenAI API."""
            if "/chat/completions" in str(request.url):
                try:
                    body = json.loads(request.content.decode())
                    logger.info(f"OpenAI API Request: {json.dumps(body, indent=2, ensure_ascii=False)}")
                except Exception as e:
                    logger.debug(f"Could not log request body: {e}")

        async def log_response(response: httpx.Response):
            """Log incoming response from OpenAI API."""
            if "/chat/completions" in str(response.url):
                try:
                    body = json.loads(response.content.decode())
                    logger.info(f"OpenAI API Response: {json.dumps(body, indent=2, ensure_ascii=False)}")
                except Exception as e:
                    logger.debug(f"Could not log response body: {e}")

        http_client = httpx.AsyncClient(
            event_hooks={
                "request": [log_request],
                "response": [log_response]
            }
        )

        client = AsyncOpenAI(
            api_key=llm_config["api_key"],
            http_client=http_client
        )

        # Set global defaults for OpenAI Agents framework
        set_default_openai_api("chat_completions")
        set_default_openai_client(client, False)
        set_tracing_disabled(disabled=True)

        return client

    @staticmethod
    def bind_tools_for_framework(client: Any, framework: Framework, tools: list,
                                   parallel_tool_calls: bool = True) -> Any:
        """
        Bind tools to a client in a framework-specific way.

        Args:
            client: The client instance
            framework: The framework type
            tools: List of tools to bind
            parallel_tool_calls: Whether to allow parallel tool calls

        Returns:
            Client with tools bound (framework-dependent)
        """
        if framework == Framework.LANGGRAPH:
            # LangGraph uses bind_tools method
            return client.bind_tools(tools, parallel_tool_calls=parallel_tool_calls)
        elif framework == Framework.AUTOGEN:
            # Autogen handles tools differently (passed to agents, not bound to client)
            return client
        elif framework == Framework.OPENAI_AGENTS:
            # OpenAI Agents handles tools at agent level
            return client
        else:
            return client
