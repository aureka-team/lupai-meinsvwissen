import asyncstdlib as a

from datetime import datetime, timezone

from lupai_mw.db import MongoConnector
from common.logger import get_logger


logger = get_logger(__name__)


SESSION_COLLECTION = "sessions"
STATE_COLLECTION = "states"


@a.lru_cache()
async def get_mongo_connector() -> MongoConnector:
    mongo_connector = MongoConnector()
    await mongo_connector.ensure_index(
        collection_name=SESSION_COLLECTION,
        field_name="user",
    )

    await mongo_connector.ensure_index(
        collection_name=SESSION_COLLECTION,
        field_name="session_id",
    )

    await mongo_connector.ensure_index(
        collection_name=SESSION_COLLECTION,
        field_name="date",
    )

    return mongo_connector


@a.lru_cache()
async def insert_user_session(user: str, session_id: str) -> None:
    mongo_connector = await get_mongo_connector()
    result = await mongo_connector.find(
        query_filter={
            "user": user,
            "session_id": session_id,
        },
        collection=SESSION_COLLECTION,
    )

    if result is not None:
        return

    await mongo_connector.insert_doc(
        doc={
            "user": user,
            "session_id": session_id,
            "date": datetime.now(timezone.utc),
        },
        collection=SESSION_COLLECTION,
    )


async def insert_state(state: dict) -> None:
    mongo_connector = await get_mongo_connector()
    await mongo_connector.insert_doc(
        doc=state,
        collection=STATE_COLLECTION,
    )
