import uuid

from json import JSONDecodeError
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, StrictStr, ValidationError, StrictBool

from common.logger import get_logger
from lupai_mw.multi_agent import get_multi_agent

from .utils import is_connected, get_context


logger = get_logger(__name__)


chat_router = APIRouter()


class ChatInput(BaseModel):
    query: StrictStr
    session_id: StrictStr | None = None


class ChatOutput(BaseModel):
    session_id: StrictStr | None = None
    assistant_response: StrictStr | None = None
    is_final: StrictBool = False
    error: StrictStr | None = None
    status: StrictStr | None = None


async def get_chat_input(
    session_id: str,
    websocket: WebSocket,
) -> ChatInput | None:
    try:
        data = await websocket.receive_json()
    except JSONDecodeError:
        logger.error("JSON decode error.")
        return

    # NOTE: In case of a ping message.
    if data.get("ping") is not None:
        return

    try:
        socket_input = ChatInput(**data)
    except ValidationError as err:
        logger.error(err)
        await websocket.send_json(
            ChatOutput(
                session_id=session_id,
                error=str(err),
            ).model_dump()
        )

        return

    return socket_input


@chat_router.websocket("/chat")
async def chat(websocket: WebSocket) -> None:
    query_params = websocket.query_params
    logger.info(f"query_params: {query_params}")

    await websocket.accept()

    session_id = query_params.get("session_id")
    session_id = uuid.uuid4().hex if session_id is None else session_id

    multi_agent = get_multi_agent()
    multi_agent.compile()

    try:
        while is_connected(websocket=websocket):
            chat_input = await get_chat_input(
                session_id=session_id,
                websocket=websocket,
            )

            if chat_input is None:
                continue

            context = get_context(websocket=websocket)
            try:
                state = await multi_agent.run(
                    input_state={
                        "session_id": session_id,
                        "query": chat_input.query,
                    },
                    context=context,
                    thread_id=session_id,
                )

                assert state is not None
                await websocket.send_json(
                    ChatOutput(**state.model_dump()).model_dump()
                )

            except Exception as err:
                logger.error(err)
                if is_connected(websocket=websocket):
                    await websocket.send_json(
                        ChatOutput(
                            session_id=session_id,
                            error=str(err),
                        ).model_dump()
                    )

                break

    except WebSocketDisconnect:
        pass
