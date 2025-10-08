import os

from typing import AsyncIterator

from pymongo import AsyncMongoClient
from pymongo.results import DeleteResult

from common.logger import get_logger


logger = get_logger(__name__)


MONGO_DATABASE = os.getenv("MONGO_DATABASE", "lupai")
MONGO_DSN = os.getenv("MONGO_DSN", "mongodb://lupai-mw-mongo:27017")


class MongoConnector:
    def __init__(
        self,
        mongo_dsn: str = MONGO_DSN,
        mongo_database: str = MONGO_DATABASE,
    ):
        self.client = AsyncMongoClient(mongo_dsn)
        self.db = self.client[mongo_database]

    async def insert_doc(self, doc: dict, collection: str) -> None:
        await self.db[collection].insert_one(doc)

    async def insert_docs(self, docs: list[dict], collection: str) -> None:
        await self.db[collection].insert_many(docs)

    async def find(
        self,
        collection: str,
        query_filter: dict = {},
        projection: dict = {},
    ) -> dict | None:
        return await self.db[collection].find_one(query_filter, projection)

    async def find_multiple(
        self,
        collection: str,
        query_filter: dict = {},
        projection: dict = {},
        limit: int = 0,
    ) -> AsyncIterator[dict]:
        cursor = self.db[collection].find(query_filter, projection).limit(limit)
        async for doc in cursor:
            yield doc

    async def create_index(self, collection: str, key: str) -> None:
        await self.db[collection].create_index(key)

    async def delete_docs(
        self,
        collection: str,
        query: dict = {},
    ) -> DeleteResult:
        return await self.db[collection].delete_many(query)

    async def ensure_index(self, collection_name: str, field_name: str) -> None:
        collection = self.db[collection_name]
        indexes = await collection.index_information()

        index_name = f"{field_name}_index"
        if index_name in indexes:
            return

        await collection.create_index(
            [(field_name, 1)],
            name=index_name,
        )
