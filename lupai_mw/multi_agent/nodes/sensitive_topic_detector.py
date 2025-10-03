from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from langgraph.runtime import get_runtime

from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.multi_agent.schema import StateSchema, Context
from lupai_mw.llm_agents import SensitiveTopicDetector, SensitiveTopicDeps

from .utils import send_status


logger = get_logger(__name__)


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running sensitive_topic_detector...")

    runtime = get_runtime(Context)
    runtime_context = runtime.context

    await send_status(
        context=runtime_context,
        status="sensitive_topic_detector",
    )

    st_det = SensitiveTopicDetector(
        message_history_length=4,
        mongodb_message_history=MongoDBMessageHistory(
            session_id=state.session_id
        ),
        read_only_message_history=True,
    )

    st_det_output = await st_det.generate(
        user_prompt=f"User query: {state.query}",
        agent_deps=SensitiveTopicDeps(
            sensitive_topics=runtime_context.sensitive_topics,
        ),
    )

    sensitive_topic = st_det_output.sensitive_topic
    logger.info(f"sensitive_topic: {sensitive_topic}")

    return {
        "sensitive_topic": sensitive_topic,
        "user_is_victim": st_det_output.user_is_victim,
    }


sensitive_topic_detector = Node(
    name="sensitive_topic_detector",
    run=run,
    is_entry_point=True,
)
