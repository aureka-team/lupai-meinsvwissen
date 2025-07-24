import os

from pydantic import BaseModel, StrictStr
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .utils import get_mongo_connector


MONGO_AUTH_COLLECTION = os.getenv("MONGO_AUTH_COLLECTION")


app = FastAPI()
security = HTTPBearer()


class User(BaseModel):
    username: StrictStr
    token: StrictStr


def auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    token = credentials.credentials
    mongo_connector = get_mongo_connector()
    user = mongo_connector.find(
        collection=MONGO_AUTH_COLLECTION,
        filter={"token": token},
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token.",
        )

    return User(**user)
