from pydantic import BaseModel, StrictStr, Field

from common.cache import RedisCache

from lupai.conf import llm_agents
from llm_agents.meta.interfaces import LLMAgent


class OrganizationExtractorOutput(BaseModel):
    organizations: list[StrictStr] = Field(
        description="List of organizations extracted from the provided text.",
        default=[],
    )


class OrganizationExtractor(LLMAgent[None, OrganizationExtractorOutput]):
    def __init__(
        self,
        conf_path=f"{llm_agents.__path__[0]}/organization-extractor.yaml",
        max_concurrency: int = 10,
        cache: RedisCache = None,
    ):
        super().__init__(
            conf_path=conf_path,
            deps_type=None,
            output_type=OrganizationExtractorOutput,
            max_concurrency=max_concurrency,
            cache=cache,
        )
