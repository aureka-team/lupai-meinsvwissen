import asyncio

from rage.meta.interfaces import Document

from .base_loader import BaseLoader, DocumentMetadata


class PostLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()

    def _load_sections(self) -> list[dict]:
        sections = self.get_parquet_data(file_name="sections.parquet")
        return [
            s
            for s in sections
            if s["text"] is not None and not self.is_html(text=s["text"])
        ]

    def _load_posts(self) -> dict:
        posts = self.get_parquet_data(file_name="posts.parquet")
        return {p["id"]: p for p in posts}

    def _get_document(self, section: dict, post: dict) -> Document:
        post_id = section["post_id"]
        return Document(
            text=section["text"],
            metadata=DocumentMetadata(
                post_id=post_id,
                title=post["title"],
                url=f"https://meinsvwissen.de/?p={post_id}",
                topics=post["topics"],
                date=post["date"],
                related_posts=post["related_posts"],
            ).model_dump(),
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
