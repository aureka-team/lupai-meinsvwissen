from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema

from .utils import socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running clarification_checkpoint...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="clarification_checkpoint",
        ),
        websocket=conf["websocket"],
    )

    return {
        "clarification_request": None,
        "user_context": {
            "origin_country": state.user_context.origin_country,
            "time_in_germany": state.user_context.time_in_germany,
            "age": state.user_context.age,
            "extra_context": state.query,
        },
    }


clarification_checkpoint = Node(
    name="clarification_checkpoint",
    run=run,
)
