from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from langgraph.runtime import get_runtime
from pydantic_ai.mcp import MCPServer, MCPServerStreamableHTTP

from lupai_mw.mcp.utils import process_tool_call
from lupai_mw.llm_agents import Assistant, AssistantDeps
from lupai_mw.multi_agent.schema import (
    StateSchema,
    ContextSchema,
    RelevantChunk,
)

from lupai_mw.mcp.server import get_text_chunk

from .utils import get_ionos_model_


logger = get_logger(__name__)


def get_assitant(provider: str, mcp: MCPServer) -> Assistant:
    match provider:
        case "openai":
            return Assistant(mcp_servers=[mcp])
        case "ionos":
            return Assistant(
                model=get_ionos_model_(
                    model_name="meta-llama/Meta-Llama-3.1-405B-Instruct-FP8"
                ),
                mcp_servers=[mcp],
            )

        case _:
            return Assistant(mcp_servers=[mcp])


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running assistant...")

    runtime = get_runtime(ContextSchema)
    runtime_context = dict(runtime.context)

    mcp = MCPServerStreamableHTTP(
        url=runtime_context["mcp_dsn"],
        process_tool_call=process_tool_call,
    )

    assitant = get_assitant(
        provider=runtime_context["provider"],
        mcp=mcp,
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
