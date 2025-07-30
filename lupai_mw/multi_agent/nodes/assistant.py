from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger
from pydantic_ai.mcp import MCPServerStreamableHTTP

from lupai_mw.llm_agents import Assistant
from lupai_mw.mcp.utils import process_tool_call
from lupai_mw.multi_agent.schema import StateSchema


logger = get_logger(__name__)


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running assistant...")

    mcp = MCPServerStreamableHTTP(
        url="http://lupai-mw-mcp:8000/mcp",
        process_tool_call=process_tool_call,
    )

    assitant = Assistant(mcp_servers=[mcp])
    async with assitant.agent:
        assitant_output = await assitant.generate(user_prompt=state.query)

    return {
        "assistant_response": assitant_output.answer,
    }


assistant = Node(
    name="assistant",
    run=run,
)
