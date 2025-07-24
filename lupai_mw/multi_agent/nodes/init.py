from agents.graph import Node
from common.logger import get_logger

from lupai.multi_agent.schema import StateSchema, ConfigSchema


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running init...")

    return {
        "clarification_request_needed": False,
        "is_final_response": False,
        "is_clarification": False,
    }


init = Node(
    name="init",
    run=run,
)
