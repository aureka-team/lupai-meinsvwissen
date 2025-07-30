from pydantic import (
    BaseModel,
    StrictStr,
)

from common.logger import get_logger


logger = get_logger(__name__)


class ContextSchema(BaseModel):
    sensitive_topics: list[StrictStr]


class StateSchema(BaseModel):
    session_id: StrictStr
    query: StrictStr
    assistant_response: StrictStr
