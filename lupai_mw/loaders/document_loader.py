import httpx
import asyncio
import tempfile

from tqdm import tqdm
from more_itertools import flatten

from rage.meta.interfaces import Document
from rage.loaders import PDFMarkdownLoaeder

from .base_loader import BaseLoader


VALID_FILE_TYPES = {
    "pdf",
}


class DocumentLoader(BaseLoader):
    def __init__(
        self,
        max_concurrency: int = 10,
    ) -> None:
        super().__init__()

        self.pdf_markdown_loader = PDFMarkdownLoaeder()
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def get_file_documents(
        self,
        download_link: str,
        pbar: tqdm,
    ) -> list[Document]:
        async with self.semaphore:
            async with httpx.AsyncClient() as client:
                response = await client.get(download_link)
                status_code = response.status_code
                assert status_code == 200, status_code

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    mode="wb",
                ) as tmp_file:
                    tmp_file.write(response.content)

                    documents = await self.pdf_markdown_loader.load(
                        source_path=tmp_file.name
                    )

                    pbar.update(1)
                    return documents

    async def get_documents(
        self, source_path: str | None = None
    ) -> list[Document]:
        download_links = [
            di["download_link"]
            for di in self.get_parquet_data(bucket_key="downloads.parquet")
            if di["file_type"] in VALID_FILE_TYPES
        ]

        with tqdm(
            total=len(download_links),
            ascii=" ##",
            colour="#808080",
        ) as pbar:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(
                        self.get_file_documents(
                            download_link=download_link,
                            pbar=pbar,
                        )
                    )
                    for download_link in download_links
                ]

            return list(flatten((t.result() for t in tasks)))
