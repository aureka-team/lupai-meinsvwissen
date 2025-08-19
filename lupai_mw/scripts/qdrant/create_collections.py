import asyncio

from pydantic import BaseModel, StrictStr

from common.logger import get_logger

from rage.retriever import Retriever
from rage.utils.embeddings import get_openai_embeddings
from rage.meta.interfaces import TextLoader, TextSplitter
from rage.splitters import TokenSplitter, MarkdownSplitter

from lupai_mw.loaders import PostLoader, FileLoader


logger = get_logger(__name__)


class CollectionItem(BaseModel):
    loader: type[TextLoader]
    splitter: type[TextSplitter]
    collection_name: StrictStr


collection_items = [
    CollectionItem(
        loader=PostLoader,
        splitter=TokenSplitter,
        collection_name="general-sources",
    ),
    CollectionItem(
        loader=FileLoader,
        splitter=MarkdownSplitter,
        collection_name="general-sources",
    ),
]


async def main() -> None:
    retriever = Retriever(dense_embeddings=get_openai_embeddings())
    for collection_item in collection_items:
        loader = collection_item.loader()

        documents = await loader.load()
        logger.info(f"documents => {len(documents)}")

        splitter = collection_item.splitter()
        text_chunks = splitter.split_documents(documents=documents)
        logger.info(f"text_chunks => {len(text_chunks)}")

        collection_name = collection_item.collection_name
        retriever.create_collection(collection_name=collection_name)
        retriever.insert_text_chunks(
            collection_name=collection_name,
            text_chunks=text_chunks,
        )


if __name__ == "__main__":
    asyncio.run(main())
