from functools import lru_cache
from pydantic_ai.models.openai import OpenAIModel

from llm_agents.utils.ionos import get_ionos_model


@lru_cache(maxsize=1)
def get_ionos_model_(model_name: str) -> OpenAIModel:
    return get_ionos_model(model_name=model_name)
