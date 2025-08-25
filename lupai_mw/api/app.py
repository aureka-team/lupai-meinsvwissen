from common.logger import get_logger
from fastapi import FastAPI, APIRouter

from .routers.chat import chat_router


logger = get_logger(__name__)


app = FastAPI()
router = APIRouter()


@app.get("/healthcheck", tags=["status"])
def healthcheck():
    return {
        "status": "ok",
    }


app.include_router(chat_router)
