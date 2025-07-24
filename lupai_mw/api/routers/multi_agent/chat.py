import os
import uuid

# import logfire
import datetime

from json import JSONDecodeError
from common.logger import get_logger

from pydantic import ValidationError
from fastapi.websockets import WebSocketState
from fastapi.exceptions import WebSocketException
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from lupai.api.utils import get_mongo_connector
from lupai.multi_agent.schema import StateSchema
from lupai.meta.data_models.api import SocketInput, SocketOutput
from lupai.multi_agent import get_multi_agent, get_multi_agent_config


MONGO_AUTH_COLLECTION = os.getenv("MONGO_AUTH_COLLECTION")
MONGO_SESSION_COLLECTION = os.getenv("MONGO_SESSION_COLLECTION")


logger = get_logger(__name__)
# logfire.configure(service_name="lupai")
# _ = logfire.instrument_openai()


chat_router = APIRouter()
multi_agent = get_multi_agent()


def authenticate(token: str) -> str | None:
    mongo_connector = get_mongo_connector()
    user = mongo_connector.find(
        collection=MONGO_AUTH_COLLECTION,
        filter={
            "token": token,
        },
    )

    if user is None:
        return

    return user["username"]


def is_connected(websocket: WebSocket) -> bool:
    return websocket.application_state == WebSocketState.CONNECTED


async def get_socket_input(
    session_id: str,
    websocket: WebSocket,
) -> SocketInput | None:
    try:
        data = await websocket.receive_json()
    except JSONDecodeError:
        logger.error("JSON decode error.")
        return

    # NOTE: In case of ping message.
    if data.get("ping") is not None:
        return

    try:
        socket_input = SocketInput(**data)
    except ValidationError as err:
        logger.error(err)
        await websocket.send_json(
            SocketOutput(
                session_id=session_id,
                error={"detail": str(err)},
            ).model_dump()
        )

        return

    return socket_input


@chat_router.websocket("/lupai/multi_agent/chat")
async def multi_agent_chat(websocket: WebSocket) -> None:
    query_params = websocket.query_params
    logger.info(f"query_params: {query_params}")

    token = query_params.get("token")
    if token is None:
        # NOTE: In case the token is not present.
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    user = authenticate(token=token)
    if user is None:
        # NOTE: In case the token is invalid.
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    await websocket.accept()
    logger.info(f"user {user} connected.")

    session_id = query_params.get("session_id")
    session_id = uuid.uuid4().hex if session_id is None else session_id
    logger.info(f"new connection: {session_id}")

    mongo_connector = get_mongo_connector()
    mongo_connector.insert_doc(
        doc={
            "user": user,
            "session_id": session_id,
            "date": datetime.datetime.now(),
        },
        collection=MONGO_SESSION_COLLECTION,
    )

    # FIXME: How can I avoid defining the config variable as global?
    config = None

    try:
        while is_connected(websocket=websocket):
            socket_input = await get_socket_input(
                session_id=session_id,
                websocket=websocket,
            )
            if socket_input is None:
                continue

            if config is None:
                config = get_multi_agent_config(
                    session_id=session_id,
                    location=socket_input.location,
                    user_context=socket_input.user_context,
                    websocket=websocket,
                )

            try:
                state = await multi_agent.run(
                    input_state={
                        "session_id": session_id,
                        "query": socket_input.user_query,
                    },
                    config=config,
                    thread_id=session_id,
                )

                state = StateSchema(**state).model_dump()
                await websocket.send_json(SocketOutput(**state).model_dump())

            except Exception as err:
                logger.error(err)
                if is_connected(websocket=websocket):
                    await websocket.send_json(
                        SocketOutput(
                            session_id=session_id,
                            error={"detail": str(err)},
                        ).model_dump()
                    )

                break

    except WebSocketDisconnect:
        pass

    logger.info(f"connection closed: {session_id}")
    # NOTE: Clean up.
    if config is not None:
        config.history.client.close()
        del config
