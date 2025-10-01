from typing import Literal
from pydantic_ai import ToolOutput
from pydantic import BaseModel, Field

from llm_agents.meta.interfaces import LLMAgent
from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.conf import llm_agents


class UserContextExtractorOutput(BaseModel):
    student_or_teacher: Literal["student", "teacher"] | None = Field(
        description="Indicates whether the person is a student or a teacher.",
        default=None,
    )


class UserContextExtractor(LLMAgent[None, UserContextExtractorOutput]):
    def __init__(
        self,
        conf_path=f"{llm_agents.__path__[0]}/user-context-extractor.yaml",
        message_history_length: int = 4,
        mongodb_message_history: MongoDBMessageHistory | None = None,
        retries: int = 3,
    ):
        super().__init__(
            conf_path=conf_path,
            output_type=ToolOutput(UserContextExtractorOutput),  # type: ignore
            message_history_length=message_history_length,
            mongodb_message_history=mongodb_message_history,
            retries=retries,
        )
