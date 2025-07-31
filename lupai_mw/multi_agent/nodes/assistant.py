from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from pydantic_ai.mcp import MCPServerStreamableHTTP

from lupai_mw.mcp.utils import process_tool_call
from lupai_mw.llm_agents import Assistant, AssistantDeps
from lupai_mw.multi_agent.schema import StateSchema, RelevantChunk

from lupai_mw.mcp.server import get_text_chunk

from .utils import get_ionos_model_


logger = get_logger(__name__)


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running assistant...")

    mcp = MCPServerStreamableHTTP(
        url="http://lupai-mw-mcp:8000/mcp",
        process_tool_call=process_tool_call,
    )

    assitant = Assistant(
        model=get_ionos_model_(
            model_name="meta-llama/Meta-Llama-3.1-405B-Instruct-FP8"
        ),
        mcp_servers=[mcp],
    )

    async with assitant.agent:
        assitant_output = await assitant.generate(
            user_prompt=state.query,
            agent_deps=AssistantDeps(output_language=state.language),  # type: ignore
        )

    relevant_chunks = (
        get_text_chunk(
            collection=relevant_chunk.collection,
            chunk_id=relevant_chunk.chunk_id,
        )
        for relevant_chunk in assitant_output.relevant_chunks
    )

    relevant_chunks = [
        RelevantChunk(**rc.model_dump())
        for rc in relevant_chunks
        if rc is not None
    ]

    return {
        "assistant_response": assitant_output.answer,
        "relevant_chunks": relevant_chunks,
    }


assistant = Node(
    name="assistant",
    run=run,
)
