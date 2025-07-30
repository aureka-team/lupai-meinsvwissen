from qdrant_client import models
from typing import Annotated, Literal

from functools import lru_cache
from mcp.server.fastmcp import FastMCP
from pydantic import (
    BaseModel,
    StrictStr,
    NonNegativeFloat,
    Field,
)

from rage.retriever import Retriever
from common.logger import get_logger


logger = get_logger(__name__)


retriever = Retriever()
mcp = FastMCP(
    name="Meinsvwissen MCP server",
    host="0.0.0.0",
)


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    return Retriever()


# TODO: Add post_id and related_posts?
class TextChunk(BaseModel):
    text: StrictStr = Field(
        description="The actual textual content of the chunk."
    )

    collection: StrictStr = Field(
        description="The name of the collection to which this text chunk belongs."
    )

    chunk_id: StrictStr = Field(
        description="The unique identifier of this chunk."
    )

    previous_chunk_id: StrictStr | None = Field(
        description="The unique chunk_id of the previous chunk in the same document.",
        default=None,
    )

    next_chunk_id: StrictStr | None = Field(
        description="The unique chunk_id of the next chunk in the same document.",
        default=None,
    )

    title: StrictStr = Field(
        description="The title of the post this chunk belongs to."
    )

    category_title: StrictStr = Field(
        description="The title of the section the document belongs to."
    )

    topics: list[StrictStr] = Field(
        description="A list of topics that describe the post this chunk belongs to."
    )


class SemanticSearchResult(TextChunk):
    """Extends TextChunk with a semantic similarity score."""

    score: NonNegativeFloat = Field(
        description="The similarity score for this chunk."
    )


@mcp.tool(
    name="semantic_search",
    description="Perform a semantic search across all text chunks in the specified collection.",
)
async def semantic_search(
    collection: Annotated[
        # TODO: Add meinsvwissen-glossary?
        Literal[
            "meinsvwissen-posts",
            "meinsvwissen-post-documents",
        ],
        Field(description="The collection of documents to search within."),
    ],
    query: Annotated[
        str,
        Field(
            description="The natural language query to search for relevant text chunks."
        ),
    ],
) -> list[SemanticSearchResult]:
    """Perform a semantic search across all text chunks in the specified collection."""

    retriever = get_retriever()
    results = await retriever.dense_search(
        collection_name=collection,
        query=query,
        k=5,
    )

    results = sorted(
        results,
        key=lambda r: (
            r.metadata["document_index"],
            r.metadata["chunk_index"],
        ),
    )

    return [
        SemanticSearchResult(
            text=r.text,
            collection=collection,
            chunk_id=r.metadata["chunk_id"],
            previous_chunk_id=r.metadata["previous_chunk_id"],
            next_chunk_id=r.metadata["next_chunk_id"],
            title=r.metadata["title"],
            category_title=r.metadata["category_title"],
            topics=r.metadata["topics"],
            score=r.score,
        )
        for r in results
    ]


@mcp.tool(
    name="get_text_chunk",
    description="Retrieve a specific text chunk from a collection using its unique chunk_id.",
)
def get_text_chunk(
    collection: Annotated[
        # TODO: Add meinsvwissen-glossary?
        Literal[
            "meinsvwissen-posts",
            "meinsvwissen-post-documents",
        ],
        Field(
            description="The collection from which to retrieve the text chunk."
        ),
    ],
    chunk_id: Annotated[
        str,
        Field(description="The unique chunk_id of the text chunk to retrieve."),
    ],
) -> TextChunk | None:
    """Retrieve a specific text chunk from a collection using its unique chunk_id."""

    scroll_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.chunk_id",
                match=models.MatchValue(value=chunk_id),
            )
        ]
    )

    retriever = get_retriever()
    results, _ = retriever.scroll(
        collection_name=collection,
        limit=1,
        scroll_filter=scroll_filter,
    )

    if not results:
        logger.error(f"no results found for chunk_id: {chunk_id}")
        return None

    result = results[0]
    return TextChunk(
        text=result.payload["page_content"],
        collection=collection,
        chunk_id=result.payload["metadata"]["chunk_id"],
        previous_chunk_id=result.payload["metadata"]["previous_chunk_id"],
        next_chunk_id=result.payload["metadata"]["next_chunk_id"],
        title=result.payload["metadata"]["title"],
        category_title=result.payload["metadata"]["category_title"],
        topics=result.payload["metadata"]["topics"],
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
