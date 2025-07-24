from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.llm_experts import Assistant, AssistantInput
from lupai.multi_agent.schema import StateSchema, ConfigSchema

from .utils import get_chunk_metadata, socket_send


logger = get_logger(__name__)


async def run(state: StateSchema, config: ConfigSchema) -> StateSchema:
    logger.info("running assistant...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="assitant",
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

    assistant = Assistant(mongodb_chat_history=conf["history"])
    intent_instructions = conf["intents"]["instructions"][state.intent]
    assistant_output = await assistant.async_generate(
        expert_input=AssistantInput(
            text_chunks=text_chunks,
            query_text=state.query,
            output_language=state.language.language_name,
            intent_instructions=intent_instructions,
            user_context=state.user_context,
        )
    )

    answer = assistant_output.response
    return {
        "assistant_response": {
            "answer": answer,
            "answer_found": False if answer is None else True,
        },
    }


assistant = Node(
    name="assistant",
    run=run,
)
