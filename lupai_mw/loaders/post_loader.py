import asyncio

from tqdm import tqdm

from common.logger import get_logger
from common.utils.json_data import group_by_key

from rage.meta.interfaces import Document

from .utils import get_pdf_text
from .base_loader import BaseLoader, DocumentMetadata


logger = get_logger(__name__)


class PostLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()

    # TODO: Validate this with Jonas.
    async def get_section_text(self, post_section: dict) -> str | None:
        section_type = post_section["type"]
        section_text = post_section["text"]
        section_title = post_section["title_right"]
        external_link = post_section["external_link"]
        transcript_url = post_section["transcript_url"]

        section_text = section_text.strip() if section_text else None
        section_title = section_title.strip() if section_title else None

        if section_type == "plain_text":
            assert section_text is not None
            return section_text

        parts = []

        if section_title is not None:
            parts.append(f"## {section_title.strip()}")

        if section_text is not None:
            parts.append(section_text.strip())

        if external_link is not None:
            parts.append(f"[{external_link}]({external_link})")

        if transcript_url is not None:
            transcript_text = await get_pdf_text(pdf_url=transcript_url)
            if transcript_text is not None:
                parts.append(transcript_text)

        text = "\n".join(parts).strip()
        if not len(text):
            logger.warning(f"post_section with no text: {post_section}")
            return

        return text

    async def get_section_text_item(
        self,
        post_sections: list[dict],
        pbar: tqdm,
    ) -> dict | None:
        section_texts = [
            await self.get_section_text(post_section=ps) for ps in post_sections
        ]

        section_texts = [st for st in section_texts if st is not None]
        if not len(section_texts):
            pbar.update(1)
            return

        # FIXME
        text = "\n".join(section_texts).strip()
        text_lines: list[str] = []
        for text_line in text.split("\n"):
            if text_line == "\n":
                text_lines.append(text_line)
                continue

            if text_line not in text_lines:
                text_lines.append(text_line)

        text = "\n".join(text_lines)
        title = post_sections[0]["title"]
        text = f"# {title}\n{text}"

        section_text_item = {
            "text": text,
            "metadata": {
                "post_id": post_sections[0]["id"],
                "title": title,
                "url": f"https://meinsvwissen.de/?p={post_sections[0]['id']}",
                "topics": post_sections[0]["topics"],
                "date": post_sections[0]["date"],
                # "related_posts": post_sections[0]["related_posts"],
            },
        }

        pbar.update(1)
        return section_text_item

    async def get_documents(
        self,
        source_path: str | None = None,
    ) -> list[Document]:
        df_posts = self.get_parquet_data(file_name="posts.parquet")
        df_sections = self.get_df_sections()

        df_posts_merged = df_posts.join(
            df_sections,
            left_on="id",
            right_on="post_id",
            how="left",
        )

        section_items = df_posts_merged.to_dicts()
        post_section_groups = list(
            group_by_key(
                section_items,
                group_key="id",
                sort_key="id",
            )
        )

        with tqdm(  # type: ignore
            total=len(post_section_groups),
            desc="Creating section text items",
            ascii=" ##",
            colour="#808080",
        ) as pbar:
            async with asyncio.TaskGroup() as tg:
                tasks = [
                    tg.create_task(
                        self.get_section_text_item(
                            post_sections=post_sections,
                            pbar=pbar,
                        )
                    )
                    for post_sections in post_section_groups
                ]

            section_text_items = [t.result() for t in tasks]

        return [
            Document(
                text=sti["text"],
                metadata=DocumentMetadata(**sti["metadata"]).model_dump(),
            )
            for sti in section_text_items
            if sti is not None
        ]
