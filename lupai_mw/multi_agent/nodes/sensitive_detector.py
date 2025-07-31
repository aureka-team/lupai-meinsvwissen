from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from langgraph.runtime import get_runtime

from lupai_mw.multi_agent.schema import StateSchema, ContextSchema
from lupai_mw.llm_agents import SensitiveDetector, SensitiveDetectorDeps

from .utils import get_ionos_model_


logger = get_logger(__name__)


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running sensitive_detector...")

    runtime = get_runtime(ContextSchema)
    sensitive_topics = dict(runtime.context)["sensitive_topics"]

    sd = SensitiveDetector(
        model=get_ionos_model_(model_name="meta-llama/Llama-3.3-70B-Instruct")
    )

    sd_output = await sd.generate(
        user_prompt=f"Query: {state.query}",
        agent_deps=SensitiveDetectorDeps(sensitive_topics=sensitive_topics),
    )

    return {
        "sensitive_topic": sd_output.sensitive_topic,
    }


sensitive_detector = Node(
    name="sensitive_detector",
    run=run,
)
