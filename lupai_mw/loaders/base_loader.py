import requests

import polars as pl

from datetime import datetime
from functools import lru_cache
from pydantic import BaseModel, NonNegativeInt, StrictStr

from abc import abstractmethod

from common.logger import get_logger
from rage.meta.interfaces import TextLoader, Document


logger = get_logger(__name__)


class DocumentMetadata(BaseModel):
    source_type: StrictStr
    category: StrictStr | None = None
    post_id: NonNegativeInt | None = None
    download_id: NonNegativeInt | None = None
    title: StrictStr | None = None
    url: StrictStr | None = None
    post_urls: list[StrictStr] = []
    topics: list[StrictStr] = []
    date: datetime | None = None
    legal_type: StrictStr | None = None
    germany_region: StrictStr | None = None
    # related_posts: list[NonNegativeInt] = []


class BaseLoader(TextLoader):
    def __init__(
        self,
        base_url: str = "https://cdl-segg.fra1.cdn.digitaloceanspaces.com/cdl-segg",
    ) -> None:
        super().__init__()
        self.base_url = base_url

    def get_parquet_data(self, file_name: str) -> pl.DataFrame:
        response = requests.get(f"{self.base_url}/{file_name}")

        status_code = response.status_code
        assert response.status_code == status_code, (
            f"status_code: {status_code}"
        )

        return pl.read_parquet(response.content)

    @lru_cache()
    def get_region_map(self) -> dict:
        df_scc = self.get_parquet_data(
            file_name="student_council_committees.parquet"
        )

        return {row["jurisdiction"]: row["name"] for row in df_scc.to_dicts()}

    @lru_cache()
    def get_df_sections(self) -> pl.DataFrame:
        df_sections = self.get_parquet_data(file_name="sections.parquet")
        return df_sections

    @lru_cache()
    def get_posts_map(self) -> dict:
        df_posts = self.get_parquet_data(file_name="posts.parquet")
        return {p["id"]: p for p in df_posts.to_dicts()}

    @abstractmethod
    async def get_documents(
        self,
        source_path: str | None = None,
    ) -> list[Document]:
        pass
