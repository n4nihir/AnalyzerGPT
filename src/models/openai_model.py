from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.config.constants import OPENAI_MODEL

def get_openai_model_client():
    openai_model_client = OpenAIChatCompletionClient(
        model = OPENAI_MODEL
    )

    return openai_model_client