from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger

from lupai_mw.multi_agent.schema import StateSchema


logger = get_logger(__name__)


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running aggregator...")

    return {}


aggregator = Node(
    name="aggregator",
    run=run,
    is_finish_point=True,
)
