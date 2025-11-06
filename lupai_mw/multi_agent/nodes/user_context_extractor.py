from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger

from langgraph.runtime import get_runtime

from lupai_mw.llm_agents import UserContextExtractor
from lupai_mw.multi_agent.schema import StateSchema, Context

from .utils import send_status, get_azure_gpt_model


logger = get_logger(__name__)


def get_intent_detector(provider: str) -> UserContextExtractor:
    if provider == "azure":
        return UserContextExtractor(model=get_azure_gpt_model())

    return UserContextExtractor()


def get_user_context(
    prev_user_context: dict,
    user_context: dict,
) -> dict:
    return prev_user_context | {
        k: v for k, v in user_context.items() if v is not None
    }


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running user_context_extractor...")

    runtime = get_runtime(Context)
    runtime_context = runtime.context

    await send_status(
        context=runtime_context,
        status="user_context_extractor",
    )

    uce = UserContextExtractor()
    uce_output = await uce.generate(
        user_prompt=f"User query: {state.query}",
    )

    prev_user_context = state.user_context
    user_context = uce_output.model_dump()

    if prev_user_context is None:
        return {
            "user_context": user_context,
        }

    return {
        "user_context": get_user_context(
            prev_user_context=prev_user_context.model_dump(),
            user_context=user_context,
        )
    }


user_context_extractor = Node(
    name="user_context_extractor",
    run=run,
    is_entry_point=True,
)
