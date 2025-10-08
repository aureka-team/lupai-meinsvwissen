from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from langgraph.runtime import get_runtime
from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.multi_agent.schema import StateSchema, Context
from lupai_mw.llm_agents import Assistant, AssistantDeps, ContextChunk

from .utils import get_azure_gpt_model, send_status


logger = get_logger(__name__)


def get_assistant(provider: str, session_id: str) -> Assistant:
    if provider == "azure":
        return Assistant(
            model=get_azure_gpt_model(),
            message_history_length=10,
            mongodb_message_history=MongoDBMessageHistory(
                session_id=session_id
            ),
        )

    return Assistant(
        message_history_length=10,
        mongodb_message_history=MongoDBMessageHistory(session_id=session_id),
    )


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running assistant...")

    runtime = get_runtime(Context)
    runtime_context = runtime.context

    await send_status(
        context=runtime_context,
        status="assistant",
    )

    user_context = state.user_context
    assert user_context is not None

    language = state.language
    assert language is not None

    context_chunks = [
        ContextChunk(**cc.model_dump()) for cc in state.relevant_chunks
    ]

    logger.info(f"context_chunks: {len(context_chunks)}")
    intent = state.intent
    assert intent is not None

    intent_instructions = runtime_context.intent_instructions[
        runtime_context.intents[intent]["instructions"]
    ]

    assistant = get_assistant(
        provider=runtime_context.provider,
        session_id=state.session_id,
    )

    async with assistant.agent:
        language = state.language
        assert language is not None

        assistant_output = await assistant.generate(
            user_prompt=state.query,
            agent_deps=AssistantDeps(
                intent_instructions=intent_instructions,
                output_language=language,
                user_context=user_context,
                context_chunks=context_chunks,
            ),
        )

    assistant_response = assistant_output.response
    if state.sensitive_topic is not None:
        sensitive_topic_message = (
            runtime_context.sensitive_topic_messages["victim"][language]
            if state.user_is_victim
            else runtime_context.sensitive_topic_messages["victimizer"][
                language
            ]
        )

        assistant_response = (
            f"{assistant_response}\n\n{sensitive_topic_message}"
        )

    return {
        "assistant_response": assistant_response,
    }


assistant = Node(
    name="assistant",
    run=run,
)
