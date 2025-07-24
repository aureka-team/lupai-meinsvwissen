from datetime import datetime
from agents.graph import Node
from common.logger import get_logger

from lupai.multi_agent.schema import StateSchema, ConfigSchema
from lupai.meta.data_models.api import SocketOutput, UserContext
from lupai.llm_experts import UserContextExtractor, UserContextExtractorInput

from .utils import socket_send


logger = get_logger(__name__)


async def run(state: StateSchema, config: ConfigSchema):
    logger.info("running user_context_extractor...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="user_context_extractor",
        ),
        websocket=conf["websocket"],
    )

    uce = UserContextExtractor()
    uce_output = await uce.async_generate(
        expert_input=UserContextExtractorInput(
            query_text=state.query,
            current_date=datetime.now().strftime("%B %d, %Y"),
        )
    )

    return {
        "user_context": UserContext(
            origin_country=uce_output.origin_country,
            time_in_germany=uce_output.time_in_germany,
            age=uce_output.age,
        ),
    }


user_context_extractor = Node(
    name="user_context_extractor",
    run=run,
)
