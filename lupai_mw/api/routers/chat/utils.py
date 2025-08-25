from functools import lru_cache

from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from lupai_mw.multi_agent.schema import Context
from lupai_mw.multi_agent import (
    get_multi_agent_context,
    MultiAgentConfig,
)


def is_connected(websocket: WebSocket) -> bool:
    return websocket.application_state == WebSocketState.CONNECTED


@lru_cache()
def get_context() -> Context:
    return get_multi_agent_context(config=MultiAgentConfig())
