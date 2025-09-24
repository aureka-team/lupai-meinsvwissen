from typing import Any
from functools import lru_cache

from qdrant_client.models import Record
from langgraph.runtime import get_runtime
from pydantic_ai.mcp import MCPServerStreamableHTTP

from multi_agents.graph import Node
from common.logger import get_logger

from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.mcp.utils import process_tool_call
from lupai_mw.llm_agents import RetrievalAssistant, RetrievalAssistantDeps
from lupai_mw.multi_agent.schema import (
    StateSchema,
    Context,
    RelevantChunk,
)

from lupai_mw.mcp.server import get_text_chunk_

from .utils import send_status, get_azure_gpt_model


logger = get_logger(__name__)


def get_retrieval_assistant(provider: str, mcp_dsn: str) -> RetrievalAssistant:
    mcp = MCPServerStreamableHTTP(
        url=mcp_dsn,
        process_tool_call=process_tool_call,
    )

    if provider == "azure":
        return RetrievalAssistant(
            model=get_azure_gpt_model(),
            mcp_servers=[mcp],
        )

    return RetrievalAssistant(mcp_servers=[mcp])


@lru_cache()
def get_mcp(mcp_dsn: str) -> MCPServerStreamableHTTP:
    return MCPServerStreamableHTTP(
        url=mcp_dsn,
        process_tool_call=process_tool_call,
    )


def get_relevant_chunk(record: Record) -> RelevantChunk:
    payload = record.payload
    assert payload is not None

    return RelevantChunk(
        text=payload["page_content"],
        title=payload["metadata"]["title"],
        category_title=payload["metadata"]["category_title"],
        topics=payload["metadata"]["topics"],
        url=payload["metadata"]["url"],
        chunk_id=payload["metadata"]["chunk_id"],
    )


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running retriever_assistant...")

    runtime = get_runtime(Context)
    runtime_context = runtime.context

    await send_status(
        context=runtime_context,
        status="retriever_assistant",
    )

    user_context = state.user_context
    assert user_context is not None

    mcp = get_mcp(mcp_dsn=runtime_context.mcp_dsn)
    assistant = RetrievalAssistant(
        message_history_length=4,
        mongodb_message_history=MongoDBMessageHistory(
            session_id=state.session_id
        ),
        read_only_message_history=True,
        mcp_servers=[mcp],
    )

    async with assistant.agent:
        assistant_output = await assistant.generate(
            user_prompt=f"User query: {state.query}",
            agent_deps=RetrievalAssistantDeps(
                retriever_metadata_fields=runtime_context.retriever_metadata_fields,
                user_context=user_context,
            ),
        )

    relevant_chunk_ids = assistant_output.relevant_chunk_ids
    logger.info(f"relevant_chunk_ids: {relevant_chunk_ids}")

    chunk_records = (
        get_text_chunk_(chunk_id=chunk_id) for chunk_id in relevant_chunk_ids
    )

    relevant_chunks = [
        get_relevant_chunk(record=chunk_record)
        for chunk_record in chunk_records
        if chunk_record is not None
    ]

    if not len(relevant_chunks):
        prev_relevant_chunks = state.relevant_chunks
        logger.info(f"prev_relevant_chunks: {len(prev_relevant_chunks)}")

        if not len(prev_relevant_chunks):
            language = state.language
            assert language is not None

            # NOTE: In case relevant chunks were never set.
            return {
                "assistant_response": runtime_context.no_answer_messages[
                    language
                ],
            }

        # NOTE: Preserve the previous chunks in case no new chunks are found.
        return {}

    return {
        "relevant_chunks": relevant_chunks,
    }


retriever_assistant = Node(
    name="retriever_assistant",
    run=run,
)
