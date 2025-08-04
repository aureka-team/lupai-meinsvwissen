from typing import Literal
from pydantic import StrictStr
from pydantic_settings import BaseSettings


class MultiAgentConfig(BaseSettings):
    provider: Literal["openai", "ionos"] = "openai"
    mcp_dsn: StrictStr = "http://lupai-mw-mcp:8000/mcp"
    sensitive_topics: list[StrictStr] = [
        "Psychological Violence",
        "Physical Violence",
        "Discrimination",
    ]
