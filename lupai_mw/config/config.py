from pydantic import StrictStr
from pydantic_settings import BaseSettings

from common.logger import get_logger


logger = get_logger(__name__)


class Config(BaseSettings):
    search_collections: tuple[StrictStr, ...] = (
        "mw_general",
        "mw_glossary",
        "mw_legal",
    )


config = Config()
logger.info(f"config: {config.model_dump()}")
