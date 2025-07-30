import requests

import polars as pl

from datetime import datetime
from pydantic import BaseModel, NonNegativeInt, StrictStr

from bs4 import BeautifulSoup
from abc import abstractmethod

from rage.meta.interfaces import TextLoader, Document


class DocumentMetadata(BaseModel):
    post_id: NonNegativeInt | None = None
    title: StrictStr
    category_title: StrictStr | None = None
    topics: list[StrictStr] = []
    date: datetime | None = None
    related_posts: list[NonNegativeInt] = []


class BaseLoader(TextLoader):
    def __init__(
        self,
        base_url: str = "https://cdl-segg.fra1.cdn.digitaloceanspaces.com/cdl-segg",
    ) -> None:
        super().__init__()

        self.base_url = base_url

    def is_html(self, text: str) -> bool:
        soup = BeautifulSoup(text, "html.parser")
        if soup.find() is None:
            return False

        return True

    def get_parquet_data(self, file_name: str) -> list[dict]:
        response = requests.get(f"{self.base_url}/{file_name}")
        assert response.status_code == 200

        df = pl.read_parquet(response.content)
        return df.to_dicts()

    @abstractmethod
    async def get_documents(
        self,
        source_path: str | None = None,
    ) -> list[Document]:
        pass
