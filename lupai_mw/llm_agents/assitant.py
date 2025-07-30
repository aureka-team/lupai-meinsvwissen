from typing import Callable
from pydantic import BaseModel, StrictStr, Field

from common.cache import RedisCache

from lupai_mw.conf import llm_agents
from pydantic_ai.mcp import MCPServer
from llm_agents.meta.interfaces import LLMAgent


class RelevantChunk(BaseModel):
    chunk_id: StrictStr
    collection: StrictStr


class AssistantOutput(BaseModel):
    answer: StrictStr | None = Field(
        description="The assistant's answer to the user query.",
        default=None,
    )

    relevant_chunks: list[RelevantChunk] = Field(
        description="List of relevant chunks used to generate the answer.",
        default=[],
    )


class Assistant(LLMAgent[None, AssistantOutput]):
    def __init__(
        self,
        conf_path=f"{list(llm_agents.__path__)[0]}/assistant.yaml",
        mcp_servers: list[MCPServer] = [],
        max_concurrency: int = 10,
        message_history_length: int = 10,
        history_processors: list[Callable] | None = None,
        cache: RedisCache | None = None,
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
