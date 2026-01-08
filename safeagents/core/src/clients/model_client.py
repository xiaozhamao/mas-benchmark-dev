import os


class ModelConfig:
    """
    The config params of Model initialization.
    """
    api_key: str = None
    model_name: str = None
    temperature: float = 0.0


class Model:
    """
    The underlying LLM to use for generating responses and actions in an Agent.
    """

    def __init__(self, config: ModelConfig, client, framework: str):
        """
        Use other class methods to create objects of this class. Avoid direct instantiation.
        """
        self.config = config
        self.client = client
        self.framework = framework

    @classmethod
    def from_openai_for_autogen(cls, config: ModelConfig):
        """
        Create a Model instance using OpenAI for Autogen framework.
        """
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        chat_completion_kwargs = {
            "api_key": config.api_key,
            "model": config.model_name,
            "temperature": config.temperature,
            "model_capabilities": {
                "function_calling": True,
                "json_output": True,
                "vision": True,
                "structured_output": True,
            },
        }
        model_client = OpenAIChatCompletionClient(**chat_completion_kwargs)

        framework = "Autogen"

        return cls(config, model_client, framework)

    # 兼容性别名
    @classmethod
    def from_azure_openai_for_autogen(cls, config: ModelConfig):
        """
        Compatibility alias for from_openai_for_autogen.
        """
        return cls.from_openai_for_autogen(config)

    def get_client(self):
        return self.client
