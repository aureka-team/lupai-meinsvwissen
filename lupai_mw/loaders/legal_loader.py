import io
import asyncio

from tqdm import tqdm
from markitdown import MarkItDown

from common.logger import get_logger
from common.utils.async_utils import make_async

from rage.meta.interfaces import Document

from .base_loader import BaseLoader, DocumentMetadata


logger = get_logger(__name__)


class LegalLoader(BaseLoader):
    def __init__(
        self,
        max_concurrency: int = 5,
    ) -> None:
        super().__init__()

        self.semaphore = asyncio.Semaphore(max_concurrency)

    @make_async
    def get_document_(self, legal_resource: dict) -> Document:
        binary_io = io.BytesIO(legal_resource["html"].encode())

        md = MarkItDown()
        result = md.convert(binary_io)

        return Document(
            text=result.text_content,
            metadata=DocumentMetadata(
                source_type="legal",
                title=legal_resource["title"],
                url=legal_resource["url"],
                legal_type=legal_resource["type"],
                jurisdiction=legal_resource["jurisdiction"],
            ).model_dump(),
        )

    async def get_document(
        self,
        legal_resource: dict,
        pbar: tqdm,
    ) -> Document:
        async with self.semaphore:
            document = await self.get_document_(
                legal_resource=legal_resource,
            )

            pbar.update(1)
            return document

    async def get_documents(
        self,
        source_path: str | None = None,
    ) -> list[Document]:
        df_legal_resources = self.get_parquet_data(
            file_name="legal_resources.parquet"
        )

        legal_resources = df_legal_resources.to_dicts()
        logger.info(f"legal_resources: {len(legal_resources)}")

        with tqdm(  # type: ignore
            total=len(legal_resources),
            ascii=" ##",
            colour="#808080",
        ) as pbar:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(
                        self.get_document(
                            legal_resource=legal_resource,
                            pbar=pbar,
                        )
                    )
                    for legal_resource in legal_resources
                ]

            return [t.result() for t in tasks]
