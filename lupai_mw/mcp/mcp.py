from typing import Annotated
from qdrant_client import models

from functools import lru_cache
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, StrictStr, NonNegativeFloat, Field, PositiveInt

from rage.retriever import Retriever
from common.logger import get_logger


logger = get_logger(__name__)


retriever = Retriever()
mcp = FastMCP(
    name="LupAI MCP server",
    host="0.0.0.0",
)


COLLECTION_NAME = "HandbookGermany"
LAW_COLLECTION_NAME = "Gesetze"


class TextChunk(BaseModel):
    text: StrictStr = Field(
        description="The actual textual content of the chunk."
    )

    source_name: StrictStr = Field(
        description="The name of the source document from which the chunk originates."
    )

    source_author: StrictStr = Field(
        description="The name of the source author of the document from which the chunk originates."
    )

    source_tags: list[StrictStr] = Field(
        description="Tags or keywords associated with the source document."
    )

    document_index: PositiveInt = Field(
        description="The index of the document in the collection."
    )

    document_id: StrictStr = Field(
        description="The unique identifier of the document."
    )

    chunk_index: PositiveInt = Field(
        description="The index of this chunk within the document."
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


# class Document(BaseModel):
#     text: StrictStr = Field(
#         description="The actual textual content of the document."
#     )

#     document_index: PositiveInt = Field(
#         description="The index of the document in the collection."
#     )

#     document_id: StrictStr = Field(
#         description="The unique identifier of the document."
#     )


class SemanticSearchResult(TextChunk):
    """Extends TextChunk with a semantic similarity score."""

    score: NonNegativeFloat = Field(
        description="The similarity score for this chunk."
    )


@lru_cache(maxsize=1)
def get_collections() -> list[str]:
    collections = retriever.qadrant_client.get_collections()
    return [c.name for c in collections.collections]


@mcp.tool(
    name="semantic_search",
    description="Perform a dense vector semantic search across all text chunks.",
)
async def semantic_search(
    query: Annotated[
        str,
        Field(
            description="The natural language query to search for relevant text chunks."
        ),
    ],
) -> list[SemanticSearchResult]:
    """Perform semantic search across all text chunks."""

    results = await retriever.dense_search(
        collection_name=COLLECTION_NAME,
        query=query,
        k=10,
    )

    if not results:
        logger.warning(f"No results found for query: '{query}'")
        return []

    search_results = (
        SemanticSearchResult(
            text=r.text,
            source_name=r.metadata["source_name"],
            source_author=r.metadata["source_author"],
            source_tags=r.metadata["source_tags"],
            document_index=r.metadata["document_index"],
            document_id=r.metadata["document_id"],
            chunk_index=r.metadata["chunk_index"],
            chunk_id=r.metadata["chunk_id"],
            previous_chunk_id=r.metadata["previous_chunk_id"],
            next_chunk_id=r.metadata["next_chunk_id"],
            score=r.score,
        )
        for r in results
    )

    return sorted(
        search_results,
        key=lambda x: (
            x.document_index,
            x.chunk_index,
        ),
    )


@mcp.tool(
    name="german_law_semantic_search",
    description="Perform a dense vector semantic search across all German law text chunks.",
)
async def german_law_semantic_search(
    query: Annotated[
        str,
        Field(
            description="The natural language query in German to search for relevant text chunks."
        ),
    ],
) -> list[SemanticSearchResult]:
    """Perform a dense vector semantic search across all German law text chunks."""

    results = await retriever.dense_search(
        collection_name=LAW_COLLECTION_NAME,
        query=query,
        k=10,
    )

    if not results:
        logger.warning(f"No results found for query: '{query}'")
        return []

    search_results = (
        SemanticSearchResult(
            text=r.text,
            source_name=r.metadata["source_name"],
            source_author=r.metadata["source_author"],
            source_tags=r.metadata["source_tags"],
            document_index=r.metadata["document_index"],
            document_id=r.metadata["document_id"],
            chunk_index=r.metadata["chunk_index"],
            chunk_id=r.metadata["chunk_id"],
            previous_chunk_id=r.metadata["previous_chunk_id"],
            next_chunk_id=r.metadata["next_chunk_id"],
            score=r.score,
        )
        for r in results
    )

    return sorted(
        search_results,
        key=lambda x: (
            x.document_index,
            x.chunk_index,
        ),
    )


@mcp.tool(
    name="get_text_chunk",
    description="Retrieve a specific text chunk by its chunk_id.",
)
def get_text_chunk(
    chunk_id: Annotated[
        str, Field(description="The ID of the chunk to retrieve.")
    ],
) -> TextChunk | None:
    """Retrieve a specific text chunk from the collection using its chunk ID."""

    scroll_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.chunk_id", match=models.MatchValue(value=chunk_id)
            )
        ]
    )

    # FIXME: This is temporal!
    collections = get_collections()
    for collection in collections:
        results, _ = retriever.scroll(
            collection_name=collection,
            limit=1,
            scroll_filter=scroll_filter,
        )

        if results:
            break

    if not results:
        logger.error(f"no results found for chunk_id: {chunk_id}")
        return None

    result = results[0]
    return TextChunk(
        text=result.payload["page_content"],
        source_name=result.payload["metadata"]["source_name"],
        source_author=result.payload["metadata"]["source_author"],
        source_tags=result.payload["metadata"]["source_tags"],
        document_index=result.payload["metadata"]["document_index"],
        document_id=result.payload["metadata"]["document_id"],
        chunk_index=result.payload["metadata"]["chunk_index"],
        chunk_id=result.payload["metadata"]["chunk_id"],
        previous_chunk_id=result.payload["metadata"]["previous_chunk_id"],
        next_chunk_id=result.payload["metadata"]["next_chunk_id"],
    )


# @mcp.tool(
#     name="get_document",
#     description="Retrieve a specific document by its document ID.",
# )
# def get_document(
#     document_id: Annotated[
#         str, Field(description="The ID of the document to retrieve.")
#     ],
# ) -> Document | None:
#     """Retrieve a specific document by its document ID."""

#     scroll_filter = models.Filter(
#         must=[
#             models.FieldCondition(
#                 key="metadata.document_id",
#                 match=models.MatchValue(value=document_id),
#             )
#         ]
#     )

#     results, _ = retriever.scroll(
#         collection_name=COLLECTION_NAME,
#         limit=1,
#         scroll_filter=scroll_filter,
#     )

#     if not results:
#         logger.error(f"no results found for document_id: {document_id}")
#         return None

#     return Document(
#         text=" ".join(tc.payload["page_content"] for tc in results),
#         document_index=results[0].payload["metadata"]["document_index"],
#         document_id=results[0].payload["metadata"]["document_id"],
#     )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
