from fastapi import WebSocket
from common.logger import get_logger

from .schema import Context
from .config import MultiAgentConfig


logger = get_logger(__name__)


def get_multi_agent_context(
    config: MultiAgentConfig,
    websocket: WebSocket | None = None,
) -> Context:
    return Context(**(config.model_dump() | {"websocket": websocket}))
