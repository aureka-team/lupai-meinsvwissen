from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema
from lupai.llm_experts import ImproveAnswer, ImproveAnswerInput


from .utils import get_chunk_metadata, socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running answer_improver...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="answer_improver",
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

    improve_answer = ImproveAnswer()
    answer = state.assistant_response.answer
    # intent_instructions = conf["intents"]["instructions"][state.intent]
    improve_answer_output = await improve_answer.async_generate(
        expert_input=ImproveAnswerInput(
            query_text=state.query,
            user_context=state.user_context,
            text_chunks=text_chunks,
            output_language=state.language.language_name,
            # intent_instructions=intent_instructions,
            assistant_answer=state.assistant_response.answer,
        )
    )

    return {
        "assistant_response": {
            "answer": answer,
            "answer_found": state.assistant_response.answer_found,
            "improved_answer": improve_answer_output.improved_answer,
        }
    }


answer_improver = Node(
    name="answer_improver",
    run=run,
)
