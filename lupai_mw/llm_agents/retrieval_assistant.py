from pydantic import BaseModel, StrictStr, Field

from pydantic_ai import ToolOutput
from pydantic_ai.models import Model
from pydantic_ai.mcp import MCPServer

from llm_agents.meta.interfaces import LLMAgent
from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.conf import llm_agents
from lupai_mw.meta.schema import UserContext


class RetrievalAssistantDeps(BaseModel):
    user_context: UserContext
    retriever_metadata_fields: list[StrictStr]


class RetrievalAssistantOutput(BaseModel):
    relevant_chunk_ids: list[StrictStr] = Field(
        description="List of relevant `chunk_id`.",
        default=[],
    )


class RetrievalAssistant(
    LLMAgent[RetrievalAssistantDeps, RetrievalAssistantOutput]
):
    def __init__(
        self,
        conf_path=f"{llm_agents.__path__[0]}/retrieval-assistant.yaml",
        mcp_servers: list[MCPServer] = [],
        max_concurrency: int = 10,
        message_history_length: int = 4,
        mongodb_message_history: MongoDBMessageHistory | None = None,
        read_only_message_history: bool = True,
        model: Model | None = None,
        retries: int = 3,
    ):
        super().__init__(
            conf_path=conf_path,
            deps_type=RetrievalAssistantDeps,
            output_type=ToolOutput(RetrievalAssistantOutput),  # type: ignore
            model=model,
            mcp_servers=mcp_servers,
            max_concurrency=max_concurrency,
            message_history_length=message_history_length,
            mongodb_message_history=mongodb_message_history,
            read_only_message_history=read_only_message_history,
            retries=retries,
        )
