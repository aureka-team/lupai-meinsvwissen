from pydantic_ai import ToolOutput
from pydantic_ai.models import Model
from pydantic_extra_types.language_code import LanguageName
from pydantic import (
    BaseModel,
    StrictStr,
    Field,
)

from llm_agents.meta.interfaces import LLMAgent
from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.conf import llm_agents
from lupai_mw.meta.schema import UserContext


class UserContextRequesterDeps(BaseModel):
    user_context: UserContext
    output_language: LanguageName


class UserContextRequesterOutput(BaseModel):
    information_request: StrictStr = Field(
        description="Request to the user, asking for additional context information.",
    )


class UserContextRequester(
    LLMAgent[UserContextRequesterDeps, UserContextRequesterOutput]
):
    def __init__(
        self,
        conf_path=f"{llm_agents.__path__[0]}/user-context-requester.yaml",
        mongodb_message_history: MongoDBMessageHistory | None = None,
        message_history_length: int = 10,
        retries: int = 3,
        model: Model | None = None,
    ):
        super().__init__(
            conf_path=conf_path,
            model=model,
            deps_type=UserContextRequesterDeps,
            output_type=ToolOutput(UserContextRequesterOutput),  # type: ignore
            mongodb_message_history=mongodb_message_history,
            message_history_length=message_history_length,
            retries=retries,
        )
