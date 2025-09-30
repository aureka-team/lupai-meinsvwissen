import asyncio

from common.logger import get_logger
from rage.meta.interfaces import Document

from .base_loader import BaseLoader


logger = get_logger(__name__)


class GlossaryLoader(BaseLoader):
    def __init__(
        self,
        max_concurrency: int = 5,
    ) -> None:
        super().__init__()

        self.semaphore = asyncio.Semaphore(max_concurrency)

    @staticmethod
    def row2md(row: dict) -> str:
        return "\n".join(
            f"## {k.upper()}\n{v}" for k, v in row.items() if v is not None
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
        return [Document(text=md_item) for md_item in md_items]
