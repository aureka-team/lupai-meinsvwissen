from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema
from lupai.llm_experts import AdditionalContext, AdditionalContextInput

from .utils import get_chunk_metadata, socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    conf = config["configurable"]
    if not conf["with_clarification"]:
        return {
            "clarification_request": None,
            "assistant_response": {
                "answer": None,
                "answer_found": False,
            },
        }

    logger.info("running clarification_requester...")
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="clarification_requester",
        ),
        websocket=conf["websocket"],
    )

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

    clarification_requester = AdditionalContext(
        mongodb_chat_history=conf["history"]
    )

    clarification_output = await clarification_requester.async_generate(
        expert_input=AdditionalContextInput(
            text_chunks=text_chunks,
            query_text=state.query,
            output_language=state.language.language_name,
            user_context=state.user_context,
        )
    )

    clarification_request = clarification_output.additional_context_request
    return {
        "assistant_response": {
            "answer": clarification_request,
            "answer_found": False,
            "improved_answer": clarification_request,
        },
        "clarification_request": clarification_request,
        "is_clarification": True,
    }


clarification_requester = Node(
    name="clarification_requester",
    run=run,
)
