import boto3

import polars as pl

from bs4 import BeautifulSoup
from abc import abstractmethod

from botocore import UNSIGNED
from botocore.client import Config

from rage.meta.interfaces import TextLoader, Document


class BaseLoader(TextLoader):
    def __init__(
        self,
        s3_url: str = "https://fra1.digitaloceanspaces.com",
        bucket_name: str = "cdl-segg",
    ) -> None:
        super().__init__()

        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            "s3",
            region_name="fra1",
            endpoint_url=s3_url,
            config=Config(signature_version=UNSIGNED),
        )

    def is_html(self, text: str) -> bool:
        soup = BeautifulSoup(text, "html.parser")
        if soup.find() is None:
            return False

        return True

    def get_parquet_data(self, bucket_key: str) -> list[dict]:
        bucket_obj = self.s3.get_object(
            Bucket=self.bucket_name,
            Key=f"{self.bucket_name}/{bucket_key}",
        )

        bucket_data = bucket_obj["Body"].read()
        df = pl.read_parquet(source=bucket_data)
        return df.to_dicts()

    @abstractmethod
    async def get_documents(
        self,
        source_path: str | None = None,
    ) -> list[Document]:
        pass
