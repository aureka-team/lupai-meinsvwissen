from pydantic import BaseModel, StrictStr, Field
from pydantic_extra_types.language_code import LanguageName

from pydantic_ai import ToolOutput
from pydantic_ai.models import Model
from pydantic_ai.mcp import MCPServer

from llm_agents.meta.interfaces import LLMAgent
from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.conf import llm_agents
from lupai_mw.meta.schema import UserContext


class ContextChunk(BaseModel):
    text: StrictStr
    title: StrictStr | None = None
    topics: list[StrictStr] = []


class AssistantDeps(BaseModel):
    intent_instructions: StrictStr
    output_language: LanguageName
    user_context: UserContext
    context_chunks: list[ContextChunk]


class AssistantOutput(BaseModel):
    response: StrictStr | None = Field(
        description="The assistant's response.",
        default=None,
    )


class Assistant(LLMAgent[AssistantDeps, AssistantOutput]):
    def __init__(
        self,
        conf_path=f"{llm_agents.__path__[0]}/assistant.yaml",
        mcp_servers: list[MCPServer] = [],
        max_concurrency: int = 10,
        message_history_length: int = 10,
        mongodb_message_history: MongoDBMessageHistory | None = None,
        model: Model | None = None,
        retries: int = 3,
    ):
        super().__init__(
            conf_path=conf_path,
            deps_type=AssistantDeps,
            output_type=ToolOutput(AssistantOutput),  # type: ignore
            model=model,
            mcp_servers=mcp_servers,
            max_concurrency=max_concurrency,
            message_history_length=message_history_length,
            mongodb_message_history=mongodb_message_history,
            retries=retries,
        )
