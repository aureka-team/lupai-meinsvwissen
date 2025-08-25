import httpx
import asyncio
import tempfile

from tqdm import tqdm
from more_itertools import flatten
from pydantic import BaseModel, StrictStr

from common.logger import get_logger
from common.utils.redis_cache import RedisCache, cache

from rage.meta.interfaces import Document
from rage.loaders import PDFMarkdownLoaeder

from .base_loader import BaseLoader, DocumentMetadata


logger = get_logger(__name__)


VALID_FILE_TYPES = {
    "pdf",
}


class DownloadItem(BaseModel):
    download_link: StrictStr
    binary_content: bytes | None = None
    title: StrictStr
    category_title: StrictStr | None = None


async def get_documents(
    binary_content: bytes,
    download_link: str,
    title: str,
    category_title: str | None,
) -> list[Document]:
    with tempfile.NamedTemporaryFile(
        delete=False,
        mode="wb",
    ) as tmp_file:
        tmp_file.write(binary_content)
        pdf_markdown_loader = PDFMarkdownLoaeder()

        # TODO: PDFs with images must be implemented.
        # try:
        documents = await pdf_markdown_loader.load(source_path=tmp_file.name)

        # except Exception:
        #     logger.error(f"error loading file from: {download_link}")
        #     return []

        return [
            Document(
                text=doc.text,
                metadata=DocumentMetadata(
                    title=title,
                    url=download_link,
                    category_title=category_title,
                ).model_dump(),
            )
            for doc in documents
            if doc.text
        ]


class FileLoader(BaseLoader):
    def __init__(
        self,
        max_concurrency: int = 5,
    ) -> None:
        super().__init__()

        self.semaphore = asyncio.Semaphore(max_concurrency)

    def get_download_items(self) -> list[DownloadItem]:
        download_items = [
            DownloadItem(
                download_link=di["download_link"],
                title=di["title"],
                category_title=di["category_title"],
            )
            for di in self.get_parquet_data(file_name="downloads.parquet")
            if di["file_type"] in VALID_FILE_TYPES
        ]

        pub_download_items = [
            DownloadItem(
                download_link=di["url"],
                title=di["title"],
                binary_content=di["pdf_binary"],
            )
            for di in self.get_parquet_data(file_name="publications.parquet")
        ]

        return download_items  # + pub_download_items

    @staticmethod
    @cache(redis_cache=RedisCache())
    async def _get_file_documents(
        download_item: DownloadItem,
    ) -> list[Document]:
        title = download_item.title
        category_title = download_item.category_title
        download_link = download_item.download_link
        binary_content = download_item.binary_content

        if binary_content is not None:
            return await get_documents(
                binary_content=binary_content,
                download_link=download_link,
                title=title,
                category_title=category_title,
            )

        async with httpx.AsyncClient(verify=False) as client:
            download_link = download_item.download_link
            try:
                response = await client.get(
                    download_link,
                    timeout=300,
                )

                status_code = response.status_code
                assert status_code == 200, status_code

                binary_content = response.content
                return await get_documents(
                    binary_content=binary_content,
                    download_link=download_link,
                    title=title,
                    category_title=category_title,
                )

            except Exception as error:
                logger.error(binary_content)
                logger.error(f"error downloading from: {download_link}")
                raise error
                # return []

    async def get_file_documents(
        self,
        download_item: DownloadItem,
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
        download_items = self.get_download_items()

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
