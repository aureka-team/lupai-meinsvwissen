import asyncio

from rage.meta.interfaces import Document

from .base_loader import BaseLoader


class PostLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()

    def _load_sections(self) -> list[dict]:
        sections = self.get_parquet_data(bucket_key="sections.parquet")
        return [
            s
            for s in sections
            if s["text"] is not None and not self.is_html(text=s["text"])
        ]

    def _load_posts(self) -> dict:
        posts = self.get_parquet_data(bucket_key="posts.parquet")
        return {p["id"]: p for p in posts}

    def _get_document(self, section: dict, post: dict) -> Document:
        return Document(
            text=section["text"],
            metadata={
                "post_id": section["post_id"],
                "title": post["title"],
                "date": post["date"],
                "topics": post["topics"],
                "related_posts": post["related_posts"],
            },
        )

    def _get_documents(self, source_path: str | None = None) -> list[Document]:
        sections = self._load_sections()
        posts = self._load_posts()

        return [
            self._get_document(
                section=section,
                post=posts[section["post_id"]],
            )
            for section in sections
        ]

    async def get_documents(
        self,
        source_path: str | None = None,
    ) -> list[Document]:
        return await asyncio.to_thread(
            self._get_documents,
            source_path=source_path,
        )
