from typing import Callable
from common.cache import RedisCache

from pydantic_ai.models import Model
from pydantic_ai import PromptedOutput
from pydantic import BaseModel, StrictStr, Field
from pydantic_extra_types.language_code import LanguageName

from lupai_mw.conf import llm_agents
from pydantic_ai.mcp import MCPServer
from llm_agents.meta.interfaces import LLMAgent


class AssistantDeps(BaseModel):
    output_language: LanguageName


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


class Assistant(LLMAgent[AssistantDeps, AssistantOutput]):
    def __init__(
        self,
        conf_path: str = f"{list(llm_agents.__path__)[0]}/assistant.yaml",
        model: Model | None = None,
        mcp_servers: list[MCPServer] = [],
        retries: int = 1,
        max_concurrency: int = 10,
        message_history_length: int = 10,
        history_processors: list[Callable] | None = None,
        cache: RedisCache | None = None,
    ):
        super().__init__(
            conf_path=conf_path,
            deps_type=AssistantDeps,
            output_type=PromptedOutput(AssistantOutput),
            model=model,
            mcp_servers=mcp_servers,
            retries=retries,
            max_concurrency=max_concurrency,
            message_history_length=message_history_length,
            history_processors=history_processors,
            cache=cache,
        )
