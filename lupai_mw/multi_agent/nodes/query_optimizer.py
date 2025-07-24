from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema
from lupai.llm_experts import ImproveQuery, ImproveQueryInput

from .utils import socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running query_optimizer...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="query_optimizer",
        ),
        websocket=conf["websocket"],
    )

    improve_query_expert = ImproveQuery()
    query = state.query
    improve_query_expert_output = await improve_query_expert.async_generate(
        expert_input=ImproveQueryInput(
            query_text=query,
            user_context=state.user_context,
            output_language=state.language.language_name,
        )
    )

    improved_query = improve_query_expert_output.improved_query
    if improved_query is None:
        return {
            "improved_query": None,
        }

    language = state.language.language_name
    return {
        "improved_query": {
            "query": improved_query,
            "warning": conf["messages"]["improved_query_warning"][language],
        }
    }


query_optimizer = Node(
    name="query_optimizer",
    run=run,
)
