import os
import asyncio

from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

from lupai_mw.multi_agent.schema import Context


FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT")
FOUNDRY_API_VERSION = os.getenv("FOUNDRY_API_VERSION")
FOUNDRY_API_KEY = os.getenv("FOUNDRY_API_KEY")


DISPLAY_MAP = {
    "domain_detector": "Analyzing query",
    "intent_detector": "Analyzing query",
    "language_detector": "Analyzing query",
    "user_context_extractor": "Analyzing query",
    "sensitive_topic_detector": "Analyzing query",
    "validation_checkpoint": "Analyzing query",
    "retriever_assistant": "Searching for sources",
    "user_context_requester": "Generating answer",
    "assistant": "Generating answer",
}


def get_azure_gpt_model(
    model_name: str = "Llama-4-Maverick-17B-128E-Instruct-FP8",
) -> Model:
    return OpenAIChatModel(
        model_name=model_name,
        provider=AzureProvider(
            azure_endpoint=FOUNDRY_ENDPOINT,
            api_version=FOUNDRY_API_VERSION,
            api_key=FOUNDRY_API_KEY,
        ),
    )


async def send_status(context: Context, status: str) -> None:
    websocket = context.websocket
    if websocket is None:
        return

    await websocket.send_json(
        {
            "status": status,
            "status_display": DISPLAY_MAP[status],
        }
    )

    await asyncio.sleep(1e-6)
