from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger

from lupai_mw.llm_agents import Assistant
from lupai_mw.multi_agent.schema import StateSchema


logger = get_logger(__name__)


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running assistant...")

    assitant = Assistant()
    assitant_output = await assitant.generate(user_prompt=state.query)

    return {
        "assistant_response": assitant_output.answer,
    }


assistant = Node(
    name="assistant",
    run=run,
)
