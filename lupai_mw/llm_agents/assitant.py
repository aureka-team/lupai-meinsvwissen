from typing import Callable
from pydantic import BaseModel, StrictStr, Field

from common.cache import RedisCache

from lupai.conf import llm_agents
from pydantic_ai.mcp import MCPServer
from llm_agents.meta.interfaces import LLMAgent


class RelevantChunk(BaseModel):
    chunk_id: StrictStr = Field(
        description="The `chunk_id` of the retrieved chunk."
    )

    source_name: StrictStr = Field(
        description="The `source_name` of the retrieved chunk."
    )

    source_author: StrictStr = Field(
        description="The `source_author` of the retrieved chunk."
    )


class AssistantOutput(BaseModel):
    answer: StrictStr | None = Field(
        description="The assistant's answer to the user question.",
        default=None,
    )

    relevant_chunks: list[RelevantChunk] = Field(
        description="List of the chunks used to generate your the answer.",
        default=[],
    )


class Assistant(LLMAgent[None, AssistantOutput]):
    def __init__(
        self,
        conf_path=f"{llm_agents.__path__[0]}/assistant.yaml",
        mcp_servers: list[MCPServer] = [],
        max_concurrency: int = 10,
        message_history_length: int = 10,
        history_processors: list[Callable] | None = None,
        cache: RedisCache = None,
    ):
        super().__init__(
            conf_path=conf_path,
            deps_type=None,
            output_type=AssistantOutput,
            mcp_servers=mcp_servers,
            max_concurrency=max_concurrency,
            message_history_length=message_history_length,
            history_processors=history_processors,
            cache=cache,
        )
