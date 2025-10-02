from pydantic_ai import ToolOutput
from pydantic import BaseModel, StrictStr, Field

from llm_agents.meta.interfaces import LLMAgent
from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.conf import llm_agents
from lupai_mw.meta.schema import SensitiveTopic


class SensitiveTopicDeps(BaseModel):
    sensitive_topics: list[SensitiveTopic]


class SensitiveTopicOutput(BaseModel):
    sensitive_topic: StrictStr | None = Field(
        description="The detected sensitive topic.",
        default=None,
    )


class SensitiveTopicDetector(
    LLMAgent[SensitiveTopicDeps, SensitiveTopicOutput]
):
    def __init__(
        self,
        conf_path=f"{llm_agents.__path__[0]}/sensitive-topic-detector.yaml",
        max_concurrency: int = 10,
        message_history_length: int = 4,
        mongodb_message_history: MongoDBMessageHistory | None = None,
        read_only_message_history: bool = True,
        retries: int = 3,
    ):
        super().__init__(
            conf_path=conf_path,
            deps_type=SensitiveTopicDeps,
            output_type=ToolOutput(SensitiveTopicOutput),  # type: ignore
            max_concurrency=max_concurrency,
            message_history_length=message_history_length,
            mongodb_message_history=mongodb_message_history,
            read_only_message_history=read_only_message_history,
            retries=retries,
        )
