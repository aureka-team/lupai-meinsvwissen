import httpx
import asyncio
import tempfile

from tqdm import tqdm
from more_itertools import flatten

from common.logger import get_logger
from common.utils.redis_cache import RedisCache, cache

from rage.meta.interfaces import Document
from rage.loaders import PDFMarkdownLoaeder

from .base_loader import BaseLoader, DocumentMetadata


logger = get_logger(__name__)


VALID_FILE_TYPES = {
    "pdf",
}


class FileLoader(BaseLoader):
    def __init__(
        self,
        max_concurrency: int = 10,
    ) -> None:
        super().__init__()

        self.semaphore = asyncio.Semaphore(max_concurrency)

    @staticmethod
    @cache(redis_cache=RedisCache())
    async def _get_file_documents(download_item: dict) -> list[Document]:
        async with httpx.AsyncClient() as client:
            download_link = download_item["download_link"]
            response = await client.get(download_link)

            status_code = response.status_code
            assert status_code == 200, status_code

            with tempfile.NamedTemporaryFile(
                delete=False,
                mode="wb",
            ) as tmp_file:
                tmp_file.write(response.content)
                pdf_markdown_loader = PDFMarkdownLoaeder()

                # FIXME: This try / except is a workaround!
                try:
                    documents = await pdf_markdown_loader.load(
                        source_path=tmp_file.name
                    )

                except Exception:
                    logger.error(f"error loading file from: {download_link}")
                    return []

                return [
                    Document(
                        text=doc.text,
                        metadata=DocumentMetadata(
                            title=download_item["title"],
                            url=download_link,
                            category_title=download_item["category_title"],
                        ).model_dump(),
                    )
                    for doc in documents
                    if doc.text
                ]

    async def get_file_documents(
        self,
        download_item: dict,
        pbar: tqdm,
    ) -> list[Document]:
        async with self.semaphore:
            documents = await self._get_file_documents(
                download_item=download_item
            )

            pbar.update(1)
            return documents

    async def get_documents(
        self, source_path: str | None = None
    ) -> list[Document]:
        download_items = [
            di
            for di in self.get_parquet_data(file_name="downloads.parquet")
            if di["file_type"] in VALID_FILE_TYPES
        ]

        with tqdm(
            total=len(download_items),
            ascii=" ##",
            colour="#808080",
        ) as pbar:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(
                        self.get_file_documents(
                            download_item=download_item,
                            pbar=pbar,
                        )
                    )
                    for download_item in download_items
                ]

            results = (t.result() for t in tasks)
            return list(flatten(results))
