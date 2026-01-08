import os
from dotenv import load_dotenv


class EnvironmentSetup:
    """
    Encapsulates the configuration and initialization of the environment in which the multi-agent system operates.
    """

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))
        self.framework = os.getenv("FRAMEWORK")
        self.exp_type = os.getenv("EXP_TYPE")

    def get_framework(self):
        return self.framework

    def get_exp_type(self):
        return self.exp_type

    def get_openai_config(self):
        return {
            "api_key": self.api_key,
            "model_name": self.model_name,
            "temperature": self.temperature,
        }

    # 兼容性别名
    def get_azure_config(self):
        """
        Compatibility alias for get_openai_config.
        Returns config in a format compatible with old Azure-style calls.
        """
        return {
            "api_key": self.api_key,
            "model_name": self.model_name,
            "temperature": self.temperature,
            # 以下为兼容性字段，映射到 OpenAI 配置
            "endpoint": None,
            "deployment": self.model_name,
            "api_version": None,
            "token_provider": None,
        }
