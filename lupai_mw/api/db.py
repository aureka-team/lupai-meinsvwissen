import os
import motor.motor_asyncio

from beanie import Document
from fastapi_users.db import BeanieBaseUser
from fastapi_users_db_beanie import BeanieUserDatabase


MONGO_DSN = os.getenv("MONGO_DSN")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "")
assert len(MONGO_DATABASE)


client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGO_DSN,
    uuidRepresentation="standard",
)

db = client[MONGO_DATABASE]


class User(BeanieBaseUser, Document):
    pass


async def get_user_db():
    yield BeanieUserDatabase(User)
