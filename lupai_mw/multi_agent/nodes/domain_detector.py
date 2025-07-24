from agents.graph import Node
from common.logger import get_logger

from lupai.llm_experts import DomainDetector, DomainDetectorInput
from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema

from .utils import socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running domain_detector...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="domain_detector",
        ),
        websocket=conf["websocket"],
    )

    domain_detector = DomainDetector()
    domain_output = await domain_detector.async_generate(
        expert_input=DomainDetectorInput(
            query_text=state.query,
            domains=conf["domains"]["valid_domains"],
        )
    )

    domain = domain_output.domain
    return {
        "domain": {
            "domain": domain,
            "is_valid": domain is not None,
        }
    }


domain_detector = Node(
    name="domain_detector",
    run=run,
)
