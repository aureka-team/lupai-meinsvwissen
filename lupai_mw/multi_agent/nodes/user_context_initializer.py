from agents.graph import Node
from common.logger import get_logger


from lupai.multi_agent.schema import StateSchema, ConfigSchema


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running user_context_initializer...")

    conf = config["configurable"]
    return {
        "user_context": conf["user_context"],
    }


user_context_initializer = Node(
    name="user_context_initializer",
    run=run,
)
