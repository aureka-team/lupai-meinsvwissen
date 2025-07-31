from pydantic_ai.models import Model
from pydantic_ai import PromptedOutput
from pydantic import BaseModel, StrictStr, Field

from lupai_mw.conf import llm_agents
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
        conf_path: str = f"{list(llm_agents.__path__)[0]}/sensitive_detector.yaml",
        model: Model | None = None,
        retries: int = 1,
    ):
        super().__init__(
            conf_path=conf_path,
            deps_type=SensitiveDetectorDeps,
            output_type=PromptedOutput(SensitiveDetectorOutput),
            model=model,
            retries=retries,
        )
