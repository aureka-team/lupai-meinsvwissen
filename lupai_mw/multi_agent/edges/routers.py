from common.logger import get_logger
from lupai.multi_agent.schema import StateSchema


logger = get_logger(__name__)


def init_conditional_router(state: StateSchema) -> list[str]:
    if state.user_context is None:
        return ["user_context_initializer"]

    if state.clarification_request is None:
        return ["language_detector"]

    return ["clarification_checkpoint"]


def user_context_init_conditional_router(state: StateSchema) -> list[str]:
    if state.user_context is None:
        return ["user_context_extractor"]

    return ["language_detector"]


def domain_conditional_router(state: StateSchema) -> list[str]:
    if not state.domain.is_valid:
        return ["output_parser"]

    return ["retriever"]


def assistant_conditional_router(state: StateSchema) -> list[str]:
    if state.assistant_response.answer_found:
        return [
            "answer_improver",
            "topic_detector",
        ]

    return ["output_parser"]


def retriever_conditional_router(state: StateSchema) -> list[str]:
    if not len(state.retriever_items) and state.improved_query is None:
        return ["query_optimizer"]

    return ["sensitive_topic_detector"]


def clarification_decider_conditional_router(state: StateSchema) -> list[str]:
    if state.clarification_needed:
        return ["clarification_requester"]

    return ["assistant"]


def language_detector_conditional_router(state: StateSchema) -> list[str]:
    # FIXME
    if state.domain is not None and state.domain.domain is not None:
        return ["domain_shift_detector"]

    if state.language.is_valid:
        return ["domain_detector"]

    return ["output_parser"]


def domain_shift_conditional_router(state: StateSchema) -> list[str]:
    if state.domain_shifted:
        logger.info("the main domain was shifted.")
        return ["domain_detector"]

    return ["retriever"]


def intent_detector_conditional_router(state: StateSchema) -> list[str]:
    if state.intent in {"Translation"}:
        return ["generic_assistant"]

    return ["clarification_decider"]
