from pydantic import BaseModel, StrictStr, Field
from pydantic_extra_types.language_code import LanguageName

from pydantic_ai import ToolOutput
from pydantic_ai.mcp import MCPServer

from llm_agents.meta.interfaces import LLMAgent
from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.conf import llm_agents


class ContextChunk(BaseModel):
    text: StrictStr
    title: StrictStr
    category_title: StrictStr | None = None
    topics: list[StrictStr] = []
    chunk_id: StrictStr


class AssistantDeps(BaseModel):
    output_language: LanguageName
    context_chunks: list[ContextChunk]


class AssistantOutput(BaseModel):
    answer: StrictStr | None = Field(
        description="The assistant's answer to the user query.",
        default=None,
    )


class Assistant(LLMAgent[AssistantDeps, AssistantOutput]):
    def __init__(
        self,
        conf_path=f"{llm_agents.__path__[0]}/assistant.yaml",
        mcp_servers: list[MCPServer] = [],
        message_history_length: int = 10,
        mongodb_message_history: MongoDBMessageHistory | None = None,
    ):
        super().__init__(
            conf_path=conf_path,
            deps_type=AssistantDeps,
            output_type=ToolOutput(AssistantOutput),
            mcp_servers=mcp_servers,
            message_history_length=message_history_length,
            mongodb_message_history=mongodb_message_history,
        )
