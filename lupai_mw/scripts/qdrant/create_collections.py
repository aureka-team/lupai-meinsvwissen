import asyncio

from functools import lru_cache
from pydantic import BaseModel, StrictStr

from common.cache import RedisCache
from common.logger import get_logger

from rage.retriever import Retriever
from rage.utils.embeddings import get_openai_embeddings
from rage.meta.interfaces import TextLoader, TextSplitter
from rage.splitters import MarkdownSplitter

from lupai_mw.loaders import (
    PostLoader,
    FileLoader,
    LegalLoader,
    SvtippsLoader,
    GlossaryLoader,
    PublicationLoader,
)


logger = get_logger(__name__)


class CollectionItem(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    loader: TextLoader
    splitter: type[TextSplitter]
    collection_name: StrictStr


@lru_cache()
def get_retriever() -> Retriever:
    return Retriever(dense_embeddings=get_openai_embeddings())


def create_indexes(collection_name: str) -> None:
    retriever = get_retriever()

    retriever.create_payload_index(
        collection_name=collection_name,
        field_name="metadata.chunk_id",
    )

    retriever.create_payload_index(
        collection_name=collection_name,
        field_name="metadata.germany_region",
    )


async def main() -> None:
    cache = RedisCache()
    collection_items = [
        CollectionItem(
            loader=PostLoader(),
            splitter=MarkdownSplitter,
            collection_name="general",
        ),
        CollectionItem(
            loader=FileLoader(cache=cache),
            splitter=MarkdownSplitter,
            collection_name="general",
        ),
        CollectionItem(
            loader=LegalLoader(),
            splitter=MarkdownSplitter,
            collection_name="legal",
        ),
        CollectionItem(
            loader=SvtippsLoader(),
            splitter=MarkdownSplitter,
            collection_name="general",
        ),
        CollectionItem(
            loader=GlossaryLoader(),
            splitter=MarkdownSplitter,
            collection_name="glossary",
        ),
        CollectionItem(
            loader=PublicationLoader(),
            splitter=MarkdownSplitter,
            collection_name="general",
        ),
    ]

    retriever = get_retriever()
    cache = RedisCache()

    for collection_item in collection_items:
        collection_name = collection_item.collection_name
        create_indexes(collection_name=collection_name)

        loader = collection_item.loader
        documents = await loader.load()
        logger.info(f"documents => {len(documents)}")

        splitter = collection_item.splitter()
        text_chunks = splitter.split_documents(documents=documents)
        logger.info(f"text_chunks => {len(text_chunks)}")

        retriever.create_collection(collection_name=collection_name)
        retriever.insert_text_chunks(
            collection_name=collection_name,
            text_chunks=text_chunks,
        )


if __name__ == "__main__":
    asyncio.run(main())
