import asyncio

from functools import lru_cache
from more_itertools import flatten

from fastapi import WebSocket
from rage.meta.interfaces import RetrieverOutputItem

from lupai.db import MongoConnector
from lupai.meta.data_models.api import SocketOutput

from llm_experts.experts import LanguageTranslatorExpert

from text_encoders.encoders import OpenAIEncoder
from text_encoders.weaviate_cache import WeaviateCache

from rage.vector_store import WeaviateVectorStore
from rage.retrievers import HierarchicalRetriever


MAX_CONNECTIONS = 128


@lru_cache(maxsize=1)
def get_retriever() -> HierarchicalRetriever:
    encoder = OpenAIEncoder(
        weaviate_cache=WeaviateCache(max_connections=MAX_CONNECTIONS)
    )

    vector_store = WeaviateVectorStore(
        encoder=encoder,
        max_connections=MAX_CONNECTIONS,
    )

    return HierarchicalRetriever(
        weaviate_vector_store=vector_store,
        language_translator=LanguageTranslatorExpert(),
        # NOTE: The following parameters are crucial
        # for the proper operation of the assistant.
        wv_alpha=0.7,
        wv_min_vector_similarity=0.4,
        retriever_limit=10,
    )


def _get_location_collection_map() -> dict:
    mongo_connector = MongoConnector()
    location_collection_map = mongo_connector.get_location_collection_map()

    del mongo_connector
    return location_collection_map


# TODO: This logic is temporary.
@lru_cache(maxsize=1)
def get_wv_collections(location: str) -> list[str]:
    location_collection_map = _get_location_collection_map()
    if location == "Berlin":
        return list(flatten(location_collection_map.values()))

    return location_collection_map["Germany"]


def _filter_dict_items(dictionary: dict, keys: set[str]) -> dict:
    return {k: v for k, v in dictionary.items() if k in keys}


def get_chunk_metadata(
    retriever_item: RetrieverOutputItem,
    chunk_props: list[str],
) -> dict:
    return _filter_dict_items(
        dictionary=retriever_item.collection_metadata,
        keys=chunk_props,
    ) | _filter_dict_items(
        dictionary=retriever_item.model_dump(),
        keys=chunk_props,
    )


async def socket_send(
    socket_output: SocketOutput,
    websocket: WebSocket | None = None,
) -> None:
    if websocket is None:
        return

    await websocket.send_json(data=socket_output.model_dump())
    await asyncio.sleep(1e-6)
