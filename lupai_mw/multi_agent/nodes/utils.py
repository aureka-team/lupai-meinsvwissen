import os
import asyncio

from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.azure import AzureProvider

from lupai_mw.multi_agent.schema import Context


FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT")
FOUNDRY_API_VERSION = os.getenv("FOUNDRY_API_VERSION")
FOUNDRY_API_KEY = os.getenv("FOUNDRY_API_KEY")


def get_azure_gpt_model(
    model_name: str = "Llama-4-Maverick-17B-128E-Instruct-FP8",
) -> Model:
    return OpenAIModel(
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

    await websocket.send_json({"status": status})
    await asyncio.sleep(1e-6)
