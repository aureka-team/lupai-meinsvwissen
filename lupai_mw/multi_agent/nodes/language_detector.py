from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger

from llm_agents.agents import LanguageDetector
from lupai_mw.multi_agent.schema import StateSchema

from .utils import get_ionos_model_


logger = get_logger(__name__)


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running language_detector...")

    ld = LanguageDetector(
        model=get_ionos_model_(model_name="meta-llama/Llama-3.3-70B-Instruct")
    )

    ld_output = await ld.generate(user_prompt=state.query)

    return {
        "language": ld_output.language.name,
    }


language_detector = Node(
    name="language_detector",
    run=run,
)
