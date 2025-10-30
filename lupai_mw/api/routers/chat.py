import os
import jwt
import uuid

from json import JSONDecodeError
from jwt import ExpiredSignatureError, InvalidTokenError

from common.logger import get_logger

from pydantic_extra_types.language_code import LanguageName
from pydantic import (
    BaseModel,
    StrictStr,
    ValidationError,
    Field,
)

from fastapi.websockets import WebSocketState
from fastapi.exceptions import WebSocketException
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from lupai_mw.meta.schema import UserContext
from lupai_mw.multi_agent.schema import RelevantChunk
from lupai_mw.multi_agent.config import MultiAgentConfig
from lupai_mw.multi_agent import get_multi_agent, get_multi_agent_context

from lupai_mw.api.users import User

from .utils import insert_user_session, insert_state


logger = get_logger(__name__)


JWT_SECRET = os.getenv("JWT_SECRET", "")
assert len(JWT_SECRET)


chat_router = APIRouter()
multi_agent = get_multi_agent()


class SocketInput(BaseModel):
    user_query: StrictStr = Field(description="The query provided by the user.")
    user_context: UserContext | None = Field(
        description="Additional context about the user.",
        default=None,
    )

    session_id: StrictStr | None = Field(
        description="Optional session identifier to maintain continuity across multiple interactions.",
        default=None,
    )


class SocketOutput(BaseModel):
    session_id: StrictStr | None = Field(
        description="Session identifier to track the conversation across multiple exchanges.",
        default=None,
    )

    domain: StrictStr | None = Field(
        description="The domain inferred from the user query.",
        default=None,
    )

    intent: StrictStr | None = Field(
        description="The recognized intent behind the user query.",
        default=None,
    )

    user_context: UserContext | None = Field(
        description="Additional context about the user.",
        default=None,
    )

    language: LanguageName | None = Field(
        description="The detected language of the query.",
        default=None,
    )

    assistant_response: StrictStr | None = Field(
        description="The assistant's generated response to the user's query.",
        default=None,
    )

    relevant_chunks: list[RelevantChunk] = Field(
        description="A list of retrieved chunks relevant to the query.",
        default_factory=list,
    )

    status: StrictStr | None = Field(
        description="The current step being executed in the multi-agent.",
        default=None,
    )

    status_display: StrictStr | None = Field(
        description="Human-friendly status message intended for UI display.",
        default=None,
    )

    error: StrictStr | None = Field(
        description="Error details if the request failed or could not be processed.",
        default=None,
    )


def is_connected(websocket: WebSocket) -> bool:
    return (
        websocket.application_state == WebSocketState.CONNECTED
        and websocket.client_state == WebSocketState.CONNECTED
    )


async def get_socket_input(websocket: WebSocket) -> SocketInput | None:
    try:
        data = await websocket.receive_json()
    except JSONDecodeError:
        logger.error("JSON decode error.")
        return

    try:
        socket_input = SocketInput(**data)
    except ValidationError as err:
        logger.error(err)
        await websocket.send_json(
            SocketOutput(error=str("Internal Server Error")).model_dump(),
        )

        return

    return socket_input


@chat_router.websocket("/lupai/chat")
async def multi_agent_chat(websocket: WebSocket) -> None:
    query_params = websocket.query_params
    token = query_params.get("token")
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
            audience="fastapi-users:auth",
        )

    except ExpiredSignatureError:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Token expired",
        )

        return

    except InvalidTokenError:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token",
        )

        return

    user_id = payload.get("sub")
    if user_id is None:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token",
        )

        return

    user = await User.get(user_id)
    if user is None or not user.is_active:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token",
        )

        return

    await websocket.accept()
    user_name = user.email
    logger.info(f"user {user_name} connected.")

    session_id = uuid.uuid4().hex
    logger.info(f"session_id: {session_id}")

    context = get_multi_agent_context(
        config=MultiAgentConfig(),
        websocket=websocket,
    )

    while is_connected(websocket=websocket):
        try:
            socket_input = await get_socket_input(websocket=websocket)
        except WebSocketDisconnect:
            break

        if socket_input is None:
            break

        await insert_user_session(
            user=user_name,
            session_id=session_id,
        )

        try:
            input_state = {
                "session_id": session_id,
                "query": socket_input.user_query,
                "user_context": socket_input.user_context,
            }

            logger.info(f"input_state: {input_state}")
            state = await multi_agent.run(
                input_state=input_state,
                context=context,
                thread_id=session_id,
            )

            assert state is not None
            await websocket.send_json(
                SocketOutput(**state.model_dump()).model_dump()
            )

            await insert_state(state=state.model_dump())

        except Exception as err:
            logger.error(err)
            if is_connected(websocket=websocket):
                await websocket.send_json(
                    SocketOutput(
                        session_id=session_id,
                        error=str("Internal Server Error"),
                    ).model_dump()
                )

            break

    logger.info("connection closed.")
