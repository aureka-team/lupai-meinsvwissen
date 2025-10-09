import asyncio
import tempfile

from tqdm import tqdm
from more_itertools import flatten

from common.logger import get_logger

from rage.meta.interfaces import Document
from rage.loaders import PDFMarkdownLoader

from .base_loader import BaseLoader, DocumentMetadata


logger = get_logger(__name__)


class PublicationLoader(BaseLoader):
    def __init__(
        self,
        max_concurrency: int = 10,
    ) -> None:
        super().__init__()

        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.region_map = self.get_region_map()

    async def _get_publication_documents(
        self,
        publication_item: dict,
    ) -> list[Document]:
        with tempfile.NamedTemporaryFile(
            delete=False,
            mode="wb",
        ) as tmp_file:
            tmp_file.write(publication_item["pdf_binary"])
            file_path = tmp_file.name

            loader = PDFMarkdownLoader()
            documents = await loader.load(source_path=file_path)

        return [
            Document(
                text=doc.text,
                metadata=DocumentMetadata(
                    source_type="file",
                    title=publication_item["title"],
                    url=publication_item["url"],
                    germany_region=self.region_map.get(
                        publication_item["jurisdiction"]
                    ),
                ).model_dump(),
            )
            for doc in documents
        ]

    async def get_publication_documents(
        self,
        publication_item: dict,
        pbar: tqdm,
    ) -> list[Document]:
        async with self.semaphore:
            documents = await self._get_publication_documents(
                publication_item=publication_item
            )

            pbar.update(1)
            return documents

    async def get_documents(
        self,
        source_path: str | None = None,
    ) -> list[Document]:
        df_publications = self.get_parquet_data(
            file_name="publications.parquet"
        )

        publication_items = df_publications.to_dicts()
        logger.info(f"publication_items: {len(publication_items)}")

        with tqdm(  # type: ignore
            total=len(publication_items),
            ascii=" ##",
            colour="#808080",
        ) as pbar:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(
                        self.get_publication_documents(
                            publication_item=publication_item,
                            pbar=pbar,
                        )
                    )
                    for publication_item in publication_items
                ]

            results = (t.result() for t in tasks)
            return list(flatten(results))
