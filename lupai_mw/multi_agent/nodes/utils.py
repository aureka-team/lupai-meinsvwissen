from functools import lru_cache
from pydantic_ai.models.openai import OpenAIModel

from llm_agents.utils.ionos import get_ionos_model


@lru_cache(maxsize=1)
def get_ionos_model_() -> OpenAIModel:
    return get_ionos_model(model_name="meta-llama/Llama-3.3-70B-Instruct")
