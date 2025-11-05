from pydantic_ai import ToolOutput
from pydantic_ai.models import Model
from pydantic import BaseModel, Field, StrictStr

from common.cache import RedisCache
from lupai_mw.conf import llm_agents
from llm_agents.meta.interfaces import LLMAgent


class QueryCategory(BaseModel):
    name: StrictStr
    description: StrictStr


class QueryClassifierDeps(BaseModel):
    user_query: StrictStr
    categories: list[QueryCategory]


class QueryClassifierOutput(BaseModel):
    category: StrictStr | None = Field(
        description="The best-matching Category for the user query, or null if none apply.",
        default=None,
    )


class QueryClassifier(LLMAgent[QueryClassifierDeps, QueryClassifierOutput]):
    def __init__(
        self,
        conf_path: str = f"{list(llm_agents.__path__)[0]}/query-classifier.yaml",
        model: Model | None = None,
        max_concurrency: int = 10,
        cache: RedisCache | None = None,
        retries: int = 3,
    ):
        super().__init__(
            conf_path=conf_path,
            deps_type=QueryClassifierDeps,
            output_type=ToolOutput(QueryClassifierOutput),  # type: ignore
            model=model,
            max_concurrency=max_concurrency,
            cache=cache,
            retries=retries,
        )
