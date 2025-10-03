from typing import Annotated
from functools import lru_cache

from qdrant_client import models
from qdrant_client.models import Record

from fastmcp.server import FastMCP
from pydantic import (
    BaseModel,
    StrictStr,
    Field,
)

from common.logger import get_logger
from rage.retriever import Retriever
from rage.utils.embeddings import get_openai_embeddings

from .utils import ToolCallLimitMiddleware


logger = get_logger(__name__)


SEARCH_TOP_K = 5
SEARCH_SCORE_THRESHOLD = 0.3


retriever = Retriever(dense_embeddings=get_openai_embeddings())
mcp = FastMCP(
    name="Meinsvwissen MCP server",
    host="0.0.0.0",
)


# TODO: Add post_id and related_posts?
class TextChunk(BaseModel):
    text: StrictStr = Field(
        description="The actual textual content of the chunk."
    )

    title: StrictStr | None = Field(
        description="The title of the document this chunk belongs to.",
        default=None,
    )

    topics: list[StrictStr] = Field(
        description="A list of topics that describe the document this chunk belongs to.",
        default=[],
    )

    germany_region: StrictStr | None = Field(
        description="The Germany region associated with the document this chunk belongs to.",
        default=None,
    )

    url: StrictStr | None = Field(
        description="The url of the document.",
        default=None,
    )

    category: StrictStr | None = Field(
        description="The category of the document this chunk belongs to.",
        default=None,
    )

    legal_type: StrictStr | None = Field(
        description="The type of legal document this chunk belongs to.",
        default=None,
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


@lru_cache(maxsize=1)
def get_collections() -> list[str]:
    collections = retriever.qadrant_client.get_collections()
    return [c.name for c in collections.collections]


async def _search(
    query: str,
    collection_name: str,
    search_filter: models.Filter | None = None,
) -> list[TextChunk]:
    results = await retriever.dense_search(
        collection_name=collection_name,
        query=query,
        k=SEARCH_TOP_K,
        score_threshold=SEARCH_SCORE_THRESHOLD,
        search_filter=search_filter,
    )

    results = sorted(
        results,
        key=lambda x: (
            x.metadata["document_index"],
            x.metadata["chunk_index"],
        ),
    )

    return [
        TextChunk(
            text=r.text,
            chunk_id=r.metadata["chunk_id"],
            previous_chunk_id=r.metadata["previous_chunk_id"],
            next_chunk_id=r.metadata["next_chunk_id"],
            title=r.metadata["title"],
            topics=r.metadata["topics"],
            url=r.metadata["url"],
        )
        for r in results
    ]


def get_text_chunk_(chunk_id: str) -> Record | None:
    scroll_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.chunk_id",
                match=models.MatchValue(value=chunk_id),
            )
        ]
    )

    # FIXME: This is temporal!
    collections = get_collections()
    for collection in collections:
        results = retriever.scroll(
            collection_name=collection,
            limit=1,
            scroll_filter=scroll_filter,
        )

        if len(results):
            break

    if not len(results):
        logger.error(f"no results found for chunk_id: {chunk_id}")
        return None

    result = results[0]
    return result


@mcp.tool(
    name="general_search",
    description="Run a semantic search across general sources.",
)
async def general_search(
    query: Annotated[
        str,
        Field(
            description="The natural language query in German to search for relevant text chunks."
        ),
    ],
) -> list[TextChunk]:
    """Run a semantic search across general sources."""

    return await _search(
        query=query,
        collection_name="general",
    )


@mcp.tool(
    name="legal_search",
    description="Run a semantic search across legal sources.",
)
async def legal_search(
    query: Annotated[
        str,
        Field(
            description="The natural language query in German to search for relevant text chunks."
        ),
    ],
    germany_region: Annotated[
        str,
        Field(
            description="The specific federal state or jurisdiction within Germany to narrow the legal search scope."
        ),
    ],
) -> list[TextChunk]:
    """Run a semantic search across legal sources."""

    return await _search(
        query=query,
        collection_name="legal",
        search_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.germany_region",
                    match=models.MatchValue(value=germany_region),
                )
            ]
        ),
    )


@mcp.tool(
    name="glossary_search",
    description="Find glossary terms and region-specific definitions using a semantic search in German.",
)
async def glossary_search(
    query: Annotated[
        str,
        Field(
            description="The natural language query in German to search for relevant text chunks."
        ),
    ],
) -> list[TextChunk]:
    """Find glossary terms and region-specific definitions using a semantic search in German."""

    return await _search(
        query=query,
        collection_name="glossary",
    )


@mcp.tool(
    name="get_text_chunk",
    description="Retrieve a specific text chunk using its `chunk_id`.",
)
def get_text_chunk(
    chunk_id: Annotated[
        str, Field(description="The `chunk_id` of the chunk to retrieve.")
    ],
) -> TextChunk | None:
    """Retrieve a specific text chunk using its `chunk_id`."""

    result = get_text_chunk_(chunk_id=chunk_id)
    if result is None:
        return

    assert result.payload is not None
    return TextChunk(
        text=result.payload["page_content"],
        chunk_id=result.payload["metadata"]["chunk_id"],
        previous_chunk_id=result.payload["metadata"]["previous_chunk_id"],
        next_chunk_id=result.payload["metadata"]["next_chunk_id"],
        title=result.payload["metadata"]["title"],
        topics=result.payload["metadata"]["topics"],
        url=result.payload["metadata"]["url"],
    )


if __name__ == "__main__":
    mcp.add_middleware(ToolCallLimitMiddleware())
    mcp.run(transport="streamable-http")
