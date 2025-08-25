from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from langgraph.runtime import get_runtime

from lupai_mw.llm_agents import LanguageDetector
from lupai_mw.multi_agent.schema import State, Context

from .utils import get_azure_gpt_model


logger = get_logger(__name__)


def get_language_detector(provider: str) -> LanguageDetector:
    if provider == "azure":
        return LanguageDetector(model=get_azure_gpt_model())

    return LanguageDetector()


async def run(state: State) -> dict[str, Any]:
    logger.info("running language_detector...")

    runtime = get_runtime(Context)
    runtime_context = runtime.context

    ld = get_language_detector(provider=runtime_context.provider)
    ld_output = await ld.generate(user_prompt=state.query)

    return {
        "language": ld_output.language.name,
    }


language_detector = Node(
    name="language_detector",
    run=run,
)
