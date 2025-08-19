from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.multi_agent.schema import State
from lupai_mw.llm_agents import Assistant, AssistantDeps, ContextChunk


logger = get_logger(__name__)


async def run(state: State) -> dict[str, Any]:
    logger.info("running assistant...")

    assistant = Assistant(
        message_history_length=10,
        mongodb_message_history=MongoDBMessageHistory(
            session_id=state.session_id
        ),
    )

    async with assistant.agent:
        language = state.language
        assert language is not None

        assistant_output = await assistant.generate(
            user_prompt=state.query,
            agent_deps=AssistantDeps(
                output_language=language,
                context_chunks=[
                    ContextChunk(**cc.model_dump())
                    for cc in state.relevant_chunks
                ],
            ),
        )

    return {
        "assistant_response": assistant_output.answer,
    }


assistant = Node(
    name="assistant",
    run=run,
)
