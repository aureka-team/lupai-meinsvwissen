import io
import asyncio

from tqdm import tqdm
from markitdown import MarkItDown

from common.logger import get_logger
from common.utils.async_utils import make_async

from rage.meta.interfaces import Document

from .base_loader import BaseLoader, DocumentMetadata


logger = get_logger(__name__)


class SvtippsLoader(BaseLoader):
    def __init__(
        self,
        max_concurrency: int = 5,
    ) -> None:
        super().__init__()

        self.semaphore = asyncio.Semaphore(max_concurrency)

    @make_async
    def get_document_(self, svtipps_item: dict) -> Document:
        binary_io = io.BytesIO(svtipps_item["html_content"].encode())

        md = MarkItDown()
        result = md.convert(binary_io)

        return Document(
            text=result.text_content,
            metadata=DocumentMetadata(
                source_type="svtipps",
                title=svtipps_item["title"],
                url=svtipps_item["url"],
                category=svtipps_item["category"],
            ).model_dump(),
        )

    async def get_document(
        self,
        svtipps_item: dict,
        pbar: tqdm,
    ) -> Document:
        async with self.semaphore:
            document = await self.get_document_(
                svtipps_item=svtipps_item,
            )

            pbar.update(1)
            return document

    async def get_documents(
        self,
        source_path: str | None = None,
    ) -> list[Document]:
        df_svtipps = self.get_parquet_data(file_name="svtipps.parquet")

        svtipps_items = df_svtipps.to_dicts()
        logger.info(f"svtipps_items: {len(svtipps_items)}")

        with tqdm(  # type: ignore
            total=len(svtipps_items),
            ascii=" ##",
            colour="#808080",
        ) as pbar:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(
                        self.get_document(
                            svtipps_item=svtipps_item,
                            pbar=pbar,
                        )
                    )
                    for svtipps_item in svtipps_items
                ]

            return [t.result() for t in tasks]
