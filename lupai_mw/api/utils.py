from functools import lru_cache
from lupai.db import MongoConnector


@lru_cache(maxsize=1)
def get_mongo_connector() -> MongoConnector:
    return MongoConnector()
