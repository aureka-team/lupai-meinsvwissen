from agents.graph import Node
from common.logger import get_logger

from rage.meta.interfaces import RetrieverOutputItem
from lupai.meta.data_models.api import SocketOutput
from lupai.llm_experts import Reranker, RerankerInput
from lupai.multi_agent.schema import StateSchema, ConfigSchema

from .utils import (
    get_retriever,
    get_wv_collections,
    socket_send,
)


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running retriever...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="retriever",
        ),
        websocket=conf["websocket"],
    )

    wv_collections = get_wv_collections(location=conf["location"])
    retriever = get_retriever()

    query_text = (
        state.query
        if state.improved_query is None
        else state.improved_query.query
    )

    retriever_items = await retriever.retrieve(
        collection_names=wv_collections,
        query_text=query_text,
        query_language=state.language.language_code,
        query_properties=conf["wv"]["query_props"],
        return_properties=conf["wv"]["return_props"],
        translate_query=state.language.translate_query,
    )

    logger.info(f"retriever_items => {len(retriever_items)}")
    if not len(retriever_items):
        return {
            "retriever_items": [],
        }

    # TODO: Move reranker to a node
    retriever_filter = Reranker()
    retriever_filter_output = await retriever_filter.async_generate(
        expert_input=RerankerInput(
            query_text=query_text,
            user_context=state.user_context,
            text_chunks=[
                {
                    "text": item.text,
                    "chunk_id": item.chunk_id,
                }
                for item in retriever_items
            ],
        )
    )

    relevant_chunk_ids = set(retriever_filter_output.relevant_chunk_ids)
    relevant_items = [
        item for item in retriever_items if item.chunk_id in relevant_chunk_ids
    ]

    logger.info(f"relevant_items => {len(relevant_items)}")
    return {
        "retriever_items": [
            RetrieverOutputItem(**(item.model_dump() | {"chunk_id": idx}))
            for idx, item in enumerate(relevant_items, start=1)
        ]
    }


retriever = Node(
    name="retriever",
    run=run,
)
