from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.llm_experts import TopicDetector, TopicDetectorInput
from lupai.multi_agent.schema import StateSchema, ConfigSchema

from .utils import socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running topic_detector...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="topic_detector",
        ),
        websocket=conf["websocket"],
    )

    queries = state.queries
    queries = queries if queries is not None else []
    queries.append(state.query)

    topic_detector = TopicDetector()
    topic_detector_output = await topic_detector.async_generate(
        expert_input=TopicDetectorInput(
            query_history=queries,
            topics=conf["topics"],
        )
    )

    return {
        "topics": topic_detector_output.topics,
        "queries": queries,
    }


topic_detector = Node(
    name="topic_detector",
    run=run,
)
