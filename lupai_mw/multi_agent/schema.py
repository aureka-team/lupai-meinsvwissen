from typing import Literal
from fastapi import WebSocket

from pydantic import BaseModel, StrictStr, ConfigDict
from pydantic_extra_types.language_code import LanguageName

from common.logger import get_logger

from lupai_mw.meta.schema import UserContext, Domain  # , SensitiveTopic


logger = get_logger(__name__)


class Context(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mcp_dsn: StrictStr
    provider: Literal["openai", "azure"]
    valid_languages: list[LanguageName]
    retriever_metadata_fields: list[StrictStr]
    # sensitive_topics: list[SensitiveTopic]
    domains: list[Domain]
    domain_translations: dict
    invalid_language_warning: StrictStr
    no_answer_messages: dict[str, str]
    invalid_domain_messages: dict[str, str]
    intents: dict[str, dict[str, str]]
    intent_instructions: dict[str, str]
    websocket: WebSocket | None = None


class RelevantChunk(BaseModel):
    text: StrictStr
    title: StrictStr
    topics: list[StrictStr] = []
    url: StrictStr
    chunk_id: StrictStr


class StateSchema(BaseModel):
    session_id: StrictStr
    query: StrictStr
    domain: StrictStr | None = None
    intent: StrictStr | None = None
    user_context: UserContext | None = None

    # FIXME: Why is this not properly saved and restored if it is a boolean?
    user_context_request: StrictStr | None = None

    language: LanguageName | None = None
    assistant_response: StrictStr | None = None
    relevant_chunks: list[RelevantChunk] = []
