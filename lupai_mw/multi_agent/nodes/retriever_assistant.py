from typing import Any

from qdrant_client.models import Record
from langgraph.runtime import get_runtime
from pydantic_ai.mcp import MCPServerStreamableHTTP

from multi_agents.graph import Node
from common.logger import get_logger

from lupai_mw.mcp.utils import process_tool_call
from lupai_mw.llm_agents import RetrievalAssistant
from lupai_mw.multi_agent.schema import (
    StateSchema,
    ContextSchema,
    RelevantChunk,
)

from lupai_mw.mcp.server import _get_text_chunk


logger = get_logger(__name__)


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

    runtime = get_runtime(ContextSchema)
    runtime_context = runtime.context

    mcp = MCPServerStreamableHTTP(
        url=runtime_context.mcp_dsn,
        process_tool_call=process_tool_call,
    )

    assistant = RetrievalAssistant(mcp_servers=[mcp])
    async with assistant.agent:
        assistant_output = await assistant.generate(
            user_prompt=f"User query: {state.query}"
        )

    relevant_chunk_ids = assistant_output.relevant_chunk_ids
    logger.info(f"relevant_chunk_ids: {relevant_chunk_ids}")
    # NOTE: Preserve the previous chunks in case no new chunks are found.
    if not len(relevant_chunk_ids):
        return {}

    chunk_records = (
        _get_text_chunk(chunk_id=chunk_id) for chunk_id in relevant_chunk_ids
    )

    relevant_chunks = [
        get_relevant_chunk(record=chunk_record)
        for chunk_record in chunk_records
        if chunk_record is not None
    ]

    return {
        "relevant_chunks": relevant_chunks,
    }


retriever_assistant = Node(
    name="retriever_assistant",
    run=run,
)
