from typing import Literal
from pydantic_extra_types.language_code import LanguageName
from pydantic import (
    BaseModel,
    StrictStr,
)

from common.logger import get_logger


logger = get_logger(__name__)


class ContextSchema(BaseModel):
    provider: Literal["openai", "ionos"]
    mcp_dsn: StrictStr
    sensitive_topics: list[StrictStr]


class RelevantChunk(BaseModel):
    collection: StrictStr
    chunk_id: StrictStr
    text: StrictStr
    url: StrictStr


class StateSchema(BaseModel):
    session_id: StrictStr
    query: StrictStr
    language: LanguageName | None = None
    sensitive_topic: StrictStr | None = None
    assistant_response: StrictStr | None = None
    relevant_chunks: list[RelevantChunk] = []
