from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema
from lupai.llm_experts import (
    AdditionalContextDecider,
    AdditionalContextDeciderInput,
)

from .utils import get_chunk_metadata, socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    conf = config["configurable"]
    logger.info("running clarification_decider...")

    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="clarification_decider",
        ),
        websocket=conf["websocket"],
    )

    if state.intent in {"Translation", "Explain"}:
        return {
            "clarification_needed": False,
        }

    text_chunks = [
        {
            "chunk_id": retriever_item.chunk_id,
            "text": retriever_item.text,
            "chunk_metadata": get_chunk_metadata(
                retriever_item=retriever_item,
                chunk_props=conf["wv"]["chunk_props"],
            ),
        }
        for retriever_item in state.retriever_items
    ]

    clarification_decider = AdditionalContextDecider()
    clarification_decider_output = await clarification_decider.async_generate(
        expert_input=AdditionalContextDeciderInput(
            text_chunks=text_chunks,
            query_text=state.query,
            user_context=state.user_context,
        )
    )

    return {
        "clarification_needed": clarification_decider_output.additional_context_needed
    }


clarification_decider = Node(
    name="clarification_decider",
    run=run,
)
