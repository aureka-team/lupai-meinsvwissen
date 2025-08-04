from common.logger import get_logger

from .schema import ContextSchema
from .config import MultiAgentConfig


logger = get_logger(__name__)


def get_multi_agent_context(config: MultiAgentConfig) -> ContextSchema:
    return ContextSchema(**config.model_dump())
