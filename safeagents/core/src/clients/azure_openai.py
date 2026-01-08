"""
Shared OpenAI client utilities for SafeAgents.
Ensures consistent client creation across frameworks and assessment.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


def get_openai_config() -> Dict[str, Any]:
    """
    Get OpenAI configuration from environment variables.
    Used by both frameworks and assessment modules.

    Returns:
        dict: Configuration dictionary with OpenAI settings

    Raises:
        ValueError: If required environment variables are not set
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
    openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))

    if not openai_api_key:
        raise ValueError(
            "OpenAI environment variable OPENAI_API_KEY is not set properly in the `.env`."
        )

    config = {
        "api_key": openai_api_key,
        "model": openai_model_name,
        "temperature": openai_temperature,
        "model_capabilities": {
            "function_calling": True,
            "json_output": True,
            "vision": True,
            "structured_output": True,
        },
    }
    return config


def get_openai_client_sync():
    """
    Create a synchronous OpenAI client for assessment/evaluation.
    Uses the same configuration as frameworks.

    Returns:
        OpenAI: Synchronous OpenAI client
    """
    from openai import OpenAI

    config = get_openai_config()

    client = OpenAI(
        api_key=config["api_key"],
    )

    return client


def get_openai_client_async():
    """
    Create an async OpenAI client.
    Uses the same configuration as frameworks.

    Returns:
        AsyncOpenAI: Async OpenAI client
    """
    from openai import AsyncOpenAI

    config = get_openai_config()

    client = AsyncOpenAI(
        api_key=config["api_key"],
    )

    return client


# ============ 兼容性别名（可选，方便过渡）============
get_azure_config = get_openai_config
get_azure_openai_client_sync = get_openai_client_sync
get_azure_openai_client_async = get_openai_client_async
