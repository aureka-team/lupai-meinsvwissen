import asyncio

from pydantic import BaseModel, StrictStr

from common.logger import get_logger

from rage.retriever import Retriever
from rage.utils.embeddings import get_openai_embeddings
from rage.meta.interfaces import TextLoader, TextSplitter
from rage.splitters import MarkdownSplitter

from lupai_mw.loaders import PostLoader


logger = get_logger(__name__)


class CollectionItem(BaseModel):
    loader: type[TextLoader]
    splitter: type[TextSplitter]
    collection_name: StrictStr


async def main() -> None:
    collection_name = "general_sources"
    retriever = Retriever(dense_embeddings=get_openai_embeddings())
    retriever.create_payload_index(
        collection_name=collection_name,
        field_name="metadata.chunk_id",
    )

    retriever.create_payload_index(
        collection_name=collection_name,
        field_name="metadata.post_id",
    )

    collection_items = [
        CollectionItem(
            loader=PostLoader,
            splitter=MarkdownSplitter,
            collection_name=collection_name,
        ),
        # CollectionItem(
        #     loader=FileLoader,
        #     splitter=MarkdownSplitter,
        #     collection_name=collection_name,
        # ),
    ]

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
