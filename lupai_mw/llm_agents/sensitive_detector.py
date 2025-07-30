from typing import Callable
from pydantic import BaseModel, StrictStr, Field

from common.cache import RedisCache

from lupai_mw.conf import llm_agents
from pydantic_ai.mcp import MCPServer
from llm_agents.meta.interfaces import LLMAgent


class SensitiveDetectorDeps(BaseModel):
    sensitive_topics: list[StrictStr]


class SensitiveDetectorOutput(BaseModel):
    sensitive_topic: StrictStr | None = Field(
        description="The detected sensitive topic.",
        default=None,
    )


class SensitiveDetector(
    LLMAgent[SensitiveDetectorDeps, SensitiveDetectorOutput]
):
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
            deps_type=SensitiveDetectorDeps,
            output_type=SensitiveDetectorOutput,
            mcp_servers=mcp_servers,
            max_concurrency=max_concurrency,
            message_history_length=message_history_length,
            history_processors=history_processors,
            cache=cache,
        )
