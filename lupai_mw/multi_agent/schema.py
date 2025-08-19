from operator import add
from typing import Annotated

from typing import Literal
from pydantic_extra_types.language_code import LanguageName
from pydantic import (
    BaseModel,
    StrictStr,
)

from common.logger import get_logger


logger = get_logger(__name__)


class Context(BaseModel):
    provider: Literal["openai", "ionos"]
    mcp_dsn: StrictStr
    sensitive_topics: list[StrictStr]


class RelevantChunk(BaseModel):
    text: StrictStr
    title: StrictStr
    category_title: StrictStr | None = None
    topics: list[StrictStr] = []
    url: StrictStr
    chunk_id: StrictStr


class State(BaseModel):
    session_id: StrictStr
    query: StrictStr
    language: LanguageName | None = None
    sensitive_topic: StrictStr | None = None
    assistant_response: StrictStr | None = None
    relevant_chunks: Annotated[list[RelevantChunk], add] = []
