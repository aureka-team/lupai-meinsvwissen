from typing import Literal
from functools import lru_cache
from langchain_openai import OpenAIEmbeddings

from rage.embeddings import IonosEmbeddings


@lru_cache()
def get_openai_embeddings(
    model: str = "text-embedding-3-large",
    dimensions: int = 256,
) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=model,
        dimensions=dimensions,
    )


@lru_cache()
def get_ionos_embeddings(
    model: Literal[
        "BAAI/bge-large-en-v1.5",
        "BAAI/bge-m3",
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    ] = "BAAI/bge-m3",
) -> IonosEmbeddings:
    return IonosEmbeddings(model=model)
