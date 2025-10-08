from common.logger import get_logger

from beanie import init_beanie
from starlette.types import ASGIApp
from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware


from .db import User, db
from .schemas import UserCreate, UserRead, UserUpdate
from .users import auth_backend, fastapi_users

from .routers import chat_router


logger = get_logger(__name__)


def cors_factory(app: ASGIApp) -> ASGIApp:
    return CORSMiddleware(
        app,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(
        database=db,
        document_models=[
            User,
        ],
    )
    yield


app = FastAPI(lifespan=lifespan)
router = APIRouter()

app.add_middleware(cors_factory)
app.get("/", include_in_schema=False)(lambda: RedirectResponse(url="/docs/"))


@app.get("/healthcheck", tags=["status"])
def healthcheck():
    return {"status": "ok"}


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),  # type: ignore
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),  # type: ignore
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),  # type: ignore
    prefix="/users",
    tags=["users"],
)

app.include_router(chat_router)
