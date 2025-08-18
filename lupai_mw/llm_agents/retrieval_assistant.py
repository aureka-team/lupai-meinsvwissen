from pydantic import BaseModel, StrictStr, Field

from pydantic_ai import ToolOutput
from pydantic_ai.mcp import MCPServer

from llm_agents.meta.interfaces import LLMAgent

from lupai_mw.conf import llm_agents


class RetrievalAssistantOutput(BaseModel):
    relevant_chunk_ids: list[StrictStr] = Field(
        description="List of relevant `chunk_id`.",
        default=[],
    )


class RetrievalAssistant(LLMAgent[None, RetrievalAssistantOutput]):
    def __init__(
        self,
        conf_path=f"{llm_agents.__path__[0]}/retrieval-assistant.yaml",
        mcp_servers: list[MCPServer] = [],
        max_concurrency: int = 10,
    ):
        super().__init__(
            conf_path=conf_path,
            output_type=ToolOutput(RetrievalAssistantOutput),
            mcp_servers=mcp_servers,
            max_concurrency=max_concurrency,
        )
