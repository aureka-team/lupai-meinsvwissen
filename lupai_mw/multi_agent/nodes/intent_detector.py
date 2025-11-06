from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from langgraph.runtime import get_runtime

from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.multi_agent.schema import StateSchema, Context
from lupai_mw.llm_agents import IntentDetector, IntentDetectorDeps, Intent

from .utils import send_status, get_azure_gpt_model


logger = get_logger(__name__)


def get_intent_detector(provider: str, session_id: str) -> IntentDetector:
    if provider == "azure":
        return IntentDetector(
            model=get_azure_gpt_model(),
            message_history_length=4,
            mongodb_message_history=MongoDBMessageHistory(
                session_id=session_id
            ),
            read_only_message_history=True,
        )

    return IntentDetector(
        message_history_length=4,
        mongodb_message_history=MongoDBMessageHistory(session_id=session_id),
        read_only_message_history=True,
    )


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running intent_detector...")

    runtime = get_runtime(Context)
    runtime_context = runtime.context

    await send_status(
        context=runtime_context,
        status="intent_detector",
    )

    intents = runtime_context.intents
    intents = [
        Intent(
            name=name,
            description=intents[name]["description"],
        )
        for name in intents.keys()
    ]

    int_det = IntentDetector(
        message_history_length=4,
        mongodb_message_history=MongoDBMessageHistory(
            session_id=state.session_id
        ),
        read_only_message_history=True,
    )

    int_det_output = await int_det.generate(
        user_prompt=f"User query: {state.query}",
        agent_deps=IntentDetectorDeps(
            intents=intents,
        ),
    )

    intent = int_det_output.intent
    logger.info(f"intent: {intent}")

    return {
        "intent": intent,
    }


intent_detector = Node(
    name="intent_detector",
    run=run,
    is_entry_point=True,
)
