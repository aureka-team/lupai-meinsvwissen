from agents.graph import Node
from common.logger import get_logger

from rage.utils.language import async_get_language
from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema

from .utils import socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running language_detector...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="language_detector",
        ),
        websocket=conf["websocket"],
    )

    language = await async_get_language(query_text=state.query)
    language_name = language["language_name"]
    return {
        "language": {
            "language_code": language["language"],
            "language_name": language_name,
            "translate_query": language["translate_query"],
            "is_valid": language_name
            in conf["language_config"]["valid_languages"],
        }
    }


language_detector = Node(
    name="language_detector",
    run=run,
)
