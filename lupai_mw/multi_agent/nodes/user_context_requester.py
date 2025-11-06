from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger

from langgraph.runtime import get_runtime
from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.llm_agents import UserContextRequester, UserContextRequesterDeps
from lupai_mw.multi_agent.schema import StateSchema, Context

from .utils import send_status, get_azure_gpt_model


logger = get_logger(__name__)


def get_intent_detector(provider: str, session_id: str) -> UserContextRequester:
    if provider == "azure":
        return UserContextRequester(
            model=get_azure_gpt_model(),
            mongodb_message_history=MongoDBMessageHistory(
                session_id=session_id
            ),
        )

    return UserContextRequester(
        mongodb_message_history=MongoDBMessageHistory(session_id=session_id),
    )


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running user_context_requester...")
    runtime = get_runtime(Context)
    runtime_context = runtime.context

    await send_status(
        context=runtime_context,
        status="user_context_requester",
    )

    ucr = UserContextRequester(
        mongodb_message_history=MongoDBMessageHistory(
            session_id=state.session_id
        ),
    )

    user_context = state.user_context
    assert user_context is not None

    language = state.language
    assert language is not None

    uce_output = await ucr.generate(
        user_prompt=state.query,
        agent_deps=UserContextRequesterDeps(
            user_context=user_context,
            output_language=language,
        ),
    )

    information_request = uce_output.information_request
    return {
        "assistant_response": information_request,
        "user_context_request": information_request,
        "is_request": False,
    }


user_context_requester = Node(
    name="user_context_requester",
    run=run,
)
