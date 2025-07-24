from typing import Literal
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from common.logger import get_logger
from lupai.api.auth import auth, User
from lupai.pipelines.sunflower import webhook_pipeline


logger = get_logger(__name__)


sunflower_router = APIRouter()


class SunflawerWebhookInput(BaseModel):
    event: Literal["content_updated"] = Field(
        description="The type of event that occurred on the client side."
    )


class SunflawerWebhookOutput(BaseModel):
    status: Literal["ok", "error"] = Field(
        description="The result of processing the webhook."
    )


@sunflower_router.post("/lupai/sunflower/webhook", tags=["sunflower"])
async def sunflower_webhook(
    sunflower_webhook_input: SunflawerWebhookInput,
    user: User = Depends(auth),
) -> SunflawerWebhookOutput:
    logger.info(f"event => {sunflower_webhook_input.event}")
    logger.info(f"user => {user.username}")

    try:
        await webhook_pipeline()
        return SunflawerWebhookOutput(status="ok")

    except Exception as error:
        logger.error(error)
        return SunflawerWebhookOutput(status="error")
