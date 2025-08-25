from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from langgraph.runtime import get_runtime

from lupai_mw.multi_agent.schema import State, Context
from lupai_mw.llm_agents import (
    SensitiveTopicDetector,
    SensitiveTopicDetectorDeps,
)

from .utils import get_azure_gpt_model


logger = get_logger(__name__)


def get_sensitive_topic_detector(provider: str) -> SensitiveTopicDetector:
    if provider == "azure":
        return SensitiveTopicDetector(model=get_azure_gpt_model())

    return SensitiveTopicDetector()


async def run(state: State) -> dict[str, Any]:
    logger.info("running sensitive_topic_detector...")

    runtime = get_runtime(Context)
    runtime_context = runtime.context

    sd = get_sensitive_topic_detector(provider=runtime_context.provider)
    sd_output = await sd.generate(
        user_prompt=f"Query: {state.query}",
        agent_deps=SensitiveTopicDetectorDeps(
            sensitive_topics=runtime_context.sensitive_topics
        ),
    )

    return {
        "sensitive_topic": sd_output.sensitive_topic,
    }


sensitive_topic_detector = Node(
    name="sensitive_topic_detector",
    run=run,
)
