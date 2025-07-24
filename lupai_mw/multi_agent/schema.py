from fastapi import WebSocket
from typing import Literal
from pydantic_extra_types.language_code import LanguageAlpha2, LanguageName
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from pydantic import (
    BaseModel,
    StrictStr,
    StrictBool,
    Field,
    ConfigDict,
    PositiveInt,
)

from common.logger import get_logger
from rage.meta.interfaces import RetrieverOutputItem

from lupai.llm_experts import Intent
from lupai.loaders import Organization
from lupai.meta.data_models.api import UserContext


logger = get_logger(__name__)


class WV(BaseModel):
    chunk_props: set[StrictStr] = Field(frozen=True)
    query_props: list[StrictStr] = Field(frozen=True)
    return_props: list[StrictStr] = Field(frozen=True)


class SensitiveTopics(BaseModel):
    topics: list[StrictStr] = Field(frozen=True)
    warnings: dict[StrictStr, StrictStr] = Field(frozen=True)
    translations: dict[StrictStr, dict] = Field(frozen=True)


class Domain(BaseModel):
    domain: StrictStr
    description: StrictStr


class Domains(BaseModel):
    valid_domains: list[Domain] = Field(
        alias="valid-domains",
        frozen=True,
    )

    translations: dict[StrictStr, dict] = Field(frozen=True)


class Intents(BaseModel):
    intents: list[Intent] = Field(frozen=True)
    instructions: dict[StrictStr, StrictStr] = Field(frozen=True)


class Messages(BaseModel):
    no_retrieve_answer: dict[LanguageName, StrictStr] = Field(
        alias="no-retrieve-answer",
        frozen=True,
    )

    improved_query_warning: dict[LanguageName, StrictStr] = Field(
        alias="improved-query-warning",
        frozen=True,
    )

    invalid_domain_answer: dict[LanguageName, StrictStr] = Field(
        alias="invalid-domain-answer",
        frozen=True,
    )


class LanguageConfig(BaseModel):
    valid_languages: set[StrictStr]
    invalid_language_warning: StrictStr


class ImmigrationLawChange(BaseModel):
    title: StrictStr
    changes: StrictStr


class ToneGuideline(BaseModel):
    title: StrictStr
    guideline: StrictStr


class Topic(BaseModel):
    topic: StrictStr
    description: StrictStr


class ConfigSchema(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    location: Literal["Berlin", "Germany"] = Field(
        default="Berlin",
        frozen=True,
    )

    user_context: UserContext | None = Field(frozen=True, default=None)
    wv: WV
    sensitive_topics: SensitiveTopics
    domains: Domains
    intents: Intents
    messages: Messages
    history: MongoDBChatMessageHistory | None = None
    language_config: LanguageConfig | None = None
    immigration_law_changes: list[ImmigrationLawChange]
    tone_guidelines: list[ToneGuideline]
    websocket: WebSocket | None = None
    with_clarification: StrictBool = True
    topics: list[Topic]
    organizations: list[Organization]
    org_translations: dict


class AssistantResponse(BaseModel):
    answer: StrictStr | None
    answer_found: StrictBool
    improved_answer: StrictStr | None = None


class ImprovedQuery(BaseModel):
    query: StrictStr
    warning: StrictStr


class SensitiveTopic(BaseModel):
    topic: StrictStr
    warning: StrictStr


class Language(BaseModel):
    language_code: LanguageAlpha2
    language_name: LanguageName
    translate_query: StrictBool
    is_valid: StrictBool


class Domain(BaseModel):
    domain: StrictStr | None
    is_valid: StrictBool


class Organization(BaseModel):
    name: StrictStr
    description: StrictStr
    website: StrictStr
    score: PositiveInt


class StateSchema(BaseModel):
    session_id: StrictStr
    query: StrictStr
    queries: list[StrictStr] | None = None
    user_context: UserContext | None = None
    domain: Domain | None = None
    domain_shifted: StrictBool | None = None
    intent: StrictStr | None = None
    language: Language | None = None
    retriever_items: list[RetrieverOutputItem] | None = None
    clarification_needed: StrictBool | None = None
    clarification_request: StrictStr | None = None
    assistant_response: AssistantResponse | None = None
    improved_query: ImprovedQuery | None = None
    sensitive_topic: SensitiveTopic | None = None
    is_final_response: StrictBool | None = None
    is_clarification: StrictBool | None = None
    topics: list[StrictStr] | None = None
    organizations: list[Organization] | None = None
