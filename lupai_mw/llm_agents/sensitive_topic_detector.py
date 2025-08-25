from pydantic_ai import ToolOutput
from pydantic_ai.models import Model
from pydantic import BaseModel, StrictStr, Field

from lupai_mw.conf import llm_agents
from llm_agents.meta.interfaces import LLMAgent


class SensitiveTopicDetectorDeps(BaseModel):
    sensitive_topics: list[StrictStr]


class SensitiveTopicDetectorOutput(BaseModel):
    sensitive_topic: StrictStr | None = Field(
        description="The detected sensitive topic.",
        default=None,
    )


class SensitiveTopicDetector(
    LLMAgent[SensitiveTopicDetectorDeps, SensitiveTopicDetectorOutput]
):
    def __init__(
        self,
        conf_path: str = f"{list(llm_agents.__path__)[0]}/sensitive_detector.yaml",
        model: Model | None = None,
        retries: int = 3,
    ):
        super().__init__(
            conf_path=conf_path,
            deps_type=SensitiveTopicDetectorDeps,
            output_type=ToolOutput(SensitiveTopicDetectorOutput),
            model=model,
            retries=retries,
        )
