import asyncio
import tempfile
import filetype

from tqdm import tqdm
from more_itertools import flatten

from common.logger import get_logger
from common.utils.redis_cache import RedisCache, cache

from rage.meta.interfaces import Document
from rage.loaders import PDFMarkdownLoader, DocxLoader

from .base_loader import BaseLoader, DocumentMetadata


logger = get_logger(__name__)


# TODO: Validate this with Jonas.
file_loaders = {
    "pdf": PDFMarkdownLoader,
    "docx": DocxLoader,
    # "doc": DocxLoader,
}


class FileLoader(BaseLoader):
    def __init__(
        self,
        max_concurrency: int = 5,
    ) -> None:
        super().__init__()

        self.semaphore = asyncio.Semaphore(max_concurrency)

    @staticmethod
    # @cache(redis_cache=RedisCache())
    async def _get_file_documents(download_item: dict) -> list[Document]:
        # file_type = download_item["file_type"]

        with tempfile.NamedTemporaryFile(
            delete=False,
            mode="wb",
        ) as tmp_file:
            tmp_file.write(download_item["file_binary"])
            kind = filetype.guess(tmp_file.name)
            assert kind is not None

            extension = kind.extension
            _loader = file_loaders.get(extension)
            if _loader is None:
                logger.warning(f"ignoring extension: {extension}")
                return []

            loader = _loader()
            documents = await loader.load(source_path=tmp_file.name)

        return [
            Document(
                text=doc.text,
                metadata=DocumentMetadata(
                    download_id=download_item["data_id"],
                    title=download_item["title"],
                    url=download_item["download_link"],
                ).model_dump(),
            )
            for doc in documents
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
        logger.info("downloading meinsvwissen files.")
        df_downloads = self.get_parquet_data(file_name="downloads.parquet")

        download_items = df_downloads.to_dicts()  # type: ignore
        download_items = download_items[:20]

        with tqdm(  # type: ignore
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
