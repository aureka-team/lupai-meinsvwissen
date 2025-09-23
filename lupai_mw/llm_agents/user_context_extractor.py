from pydantic_ai import ToolOutput

from llm_agents.meta.interfaces import LLMAgent
from llm_agents.message_history import MongoDBMessageHistory

from lupai_mw.conf import llm_agents
from lupai_mw.meta.schema import UserContext


class UserContextExtractorOutput(UserContext):
    pass


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
