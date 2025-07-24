from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema
from lupai.llm_experts import DomainShift, DomainShiftInput

from .utils import socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running domain_shift_detector...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="domain_shift_detector",
        ),
        websocket=conf["websocket"],
    )

    domain_shift_expert = DomainShift(mongodb_chat_history=conf["history"])
    domain_shift_output = await domain_shift_expert.async_generate(
        expert_input=DomainShiftInput(
            query_text=state.query,
            previous_domain=state.domain.domain,
        )
    )

    domain_shifted = domain_shift_output.domain_shifted
    return {"domain_shifted": domain_shifted}


domain_shift_detector = Node(
    name="domain_shift_detector",
    run=run,
)
