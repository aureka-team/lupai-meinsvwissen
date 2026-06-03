from pydantic import StrictStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    search_collections: tuple[StrictStr, ...] = (
        "mw_general",
        "mw_glossary",
        "mw_legal",
    )
