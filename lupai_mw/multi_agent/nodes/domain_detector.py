from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from langgraph.runtime import get_runtime

from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.meta.schema import Domain
from lupai_mw.multi_agent.schema import StateSchema, Context
from lupai_mw.llm_agents import DomainDetector, DomainDetectorDeps

from .utils import send_status


logger = get_logger(__name__)


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running domain_detector...")

    runtime = get_runtime(Context)
    runtime_context = runtime.context

    await send_status(
        context=runtime_context,
        status="domain_detector",
    )

    domains = [Domain(**d.model_dump()) for d in runtime_context.domains]

    dd = DomainDetector(
        message_history_length=4,
        mongodb_message_history=MongoDBMessageHistory(
            session_id=state.session_id
        ),
        read_only_message_history=True,
    )

    dd_output = await dd.generate(
        user_prompt=f"User query: {state.query}",
        agent_deps=DomainDetectorDeps(
            previous_domain=state.domain,
            domains=domains,
        ),
    )

    domain = dd_output.domain
    logger.info(f"domain: {domain}")

    return {
        "domain": domain,
    }


domain_detector = Node(
    name="domain_detector",
    run=run,
    is_entry_point=True,
)
