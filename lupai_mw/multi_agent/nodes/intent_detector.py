from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema
from lupai.llm_experts import IntentDetector, IntentDetectorInput

from .utils import socket_send


logger = get_logger(__name__)


async def run(state: StateSchema, config: ConfigSchema):
    logger.info("running intent_detector...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="intent_detector",
        ),
        websocket=conf["websocket"],
    )

    intent_expert = IntentDetector()
    intent_output = await intent_expert.async_generate(
        expert_input=IntentDetectorInput(
            query_text=state.query,
            intents=conf["intents"]["intents"],
        )
    )

    return {
        "intent": intent_output.intent,
    }


intent_detector = Node(
    name="intent_detector",
    run=run,
)
