from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema
from lupai.llm_experts import SensitiveTopic, SensitiveTopicInput

from .utils import socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running sensitive_topic_detector...")
    conf = config["configurable"]

    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="sensitive_topic_detector",
        ),
        websocket=conf["websocket"],
    )

    sensitive_topic_expert = SensitiveTopic()
    sensitive_topic_output = await sensitive_topic_expert.async_generate(
        expert_input=SensitiveTopicInput(
            query_text=state.query,
            topics=conf["sensitive_topics"]["topics"],
        )
    )

    sensitive_topic = sensitive_topic_output.sensitive_topic
    if sensitive_topic is None:
        return {
            "sensitive_topic": None,
        }

    language = state.language.language_name
    warning = conf["sensitive_topics"]["warnings"][sensitive_topic]
    warning_text = conf["sensitive_topics"]["translations"][warning][language]

    return {
        "sensitive_topic": {
            "topic": sensitive_topic,
            "warning": warning_text,
        },
    }


sensitive_topic_detector = Node(
    name="sensitive_topic_detector",
    run=run,
)
