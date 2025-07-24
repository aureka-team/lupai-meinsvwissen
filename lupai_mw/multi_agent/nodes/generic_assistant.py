from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.llm_experts import GenericAssistant, GenericAssistantInput
from lupai.multi_agent.schema import StateSchema, ConfigSchema

from .utils import socket_send


logger = get_logger(__name__)


async def run(state: StateSchema, config: ConfigSchema) -> StateSchema:
    logger.info("running generic_assistant...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="generic_assistant",
        ),
        websocket=conf["websocket"],
    )

    ga = GenericAssistant(mongodb_chat_history=conf["history"])
    assistant_output = await ga.async_generate(
        expert_input=GenericAssistantInput(
            query_text=state.query,
        )
    )

    answer = assistant_output.response
    return {
        "assistant_response": {
            "answer": answer,
            "answer_found": True,
            "improved_answer": answer,
        },
    }


generic_assistant = Node(
    name="generic_assistant",
    run=run,
)
