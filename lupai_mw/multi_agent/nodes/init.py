from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger

from lupai_mw.multi_agent.schema import State


logger = get_logger(__name__)


async def run(state: State) -> dict[str, Any]:
    logger.info("running init...")

    return {}


init = Node(
    name="init",
    run=run,
    is_entry_point=True,
)
