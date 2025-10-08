from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from langgraph.runtime import get_runtime

from lupai_mw.llm_agents import LanguageDetector
from lupai_mw.multi_agent.schema import StateSchema, Context

from .utils import get_azure_gpt_model, send_status


logger = get_logger(__name__)


def get_language_detector(provider: str) -> LanguageDetector:
    if provider == "azure":
        return LanguageDetector(model=get_azure_gpt_model())

    return LanguageDetector()


async def run(state: StateSchema) -> dict[str, Any]:
    # NOTE: Language is detected only at the start of the conversation.
    if state.language is not None:
        return {}

    logger.info("running language_detector...")
    runtime = get_runtime(Context)
    runtime_context = runtime.context

    await send_status(
        context=runtime_context,
        status="language_detector",
    )

    ld = get_language_detector(provider=runtime_context.provider)
    ld_output = await ld.generate(user_prompt=f"User Query: {state.query}")

    language = ld_output.language.name
    logger.info(f"language: {language}")

    return {
        "language": language,
    }


language_detector = Node(
    name="language_detector",
    run=run,
    is_entry_point=True,
)
