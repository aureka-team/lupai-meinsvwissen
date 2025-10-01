import asyncio

from common.logger import get_logger
from rage.meta.interfaces import Document

from .base_loader import BaseLoader, DocumentMetadata


logger = get_logger(__name__)


class GlossaryLoader(BaseLoader):
    def __init__(
        self,
        max_concurrency: int = 5,
    ) -> None:
        super().__init__()

        self.region_map = self.get_region_map()
        self.semaphore = asyncio.Semaphore(max_concurrency)

    def row2md(self, row: dict) -> str:
        return "\n".join(
            f"## {self.region_map.get(k.upper(), k.upper())}\n{v}"
            for k, v in row.items()
            if v is not None
        )

    async def get_documents(
        self,
        source_path: str | None = None,
    ) -> list[Document]:
        df_glossary_terms = self.get_parquet_data(
            file_name="glossary_terms.parquet"
        )

        glossary_terms_items = df_glossary_terms.to_dicts()
        logger.info(f"glossary_terms_items: {len(glossary_terms_items)}")

        md_items = map(self.row2md, glossary_terms_items)
        return [
            Document(
                text=md_item,
                metadata=DocumentMetadata(source_type="glossary").model_dump(),
            )
            for md_item in md_items
        ]
