import httpx

from tempfile import NamedTemporaryFile

from common.logger import get_logger
from rage.loaders import PDFMarkdownLoader


logger = get_logger(__name__)


async def get_pdf_text(pdf_url: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(pdf_url)

        except Exception:
            logger.error(f"pdf_url: {pdf_url}")
            raise

        status_code = response.status_code
        assert response.status_code == 200, status_code

        with NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as tmp_file:
            tmp_file.write(response.content)
            loader = PDFMarkdownLoader()
            documents = await loader.load(source_path=tmp_file.name)

            return documents[0].text
