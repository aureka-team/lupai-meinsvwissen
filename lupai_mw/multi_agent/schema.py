from pydantic import (
    BaseModel,
    StrictStr,
)

from common.logger import get_logger


logger = get_logger(__name__)


class ContextSchema(BaseModel):
    sensitive_topics: list[StrictStr]


class RelevantChunk(BaseModel):
    collection: StrictStr
    chunk_id: StrictStr
    text: StrictStr
    url: StrictStr


class StateSchema(BaseModel):
    session_id: StrictStr
    query: StrictStr
    sensitive_topic: StrictStr | None = None
    assistant_response: StrictStr | None = None
    relevant_chunks: list[RelevantChunk] = []
