from common.logger import get_logger
from .schema import ContextSchema


logger = get_logger(__name__)


sensitive_topics = [
    "Psychological Violence",
    "Physical Violence",
    "Discrimination",
]


def get_multi_agent_context() -> ContextSchema:
    return ContextSchema(sensitive_topics=sensitive_topics)
