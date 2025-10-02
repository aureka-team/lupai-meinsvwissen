from typing import Hashable
from langgraph.graph import END
from langgraph.runtime import get_runtime

from common.logger import get_logger

from ..schema import StateSchema, Context


logger = get_logger(__name__)


# FIXME: Duplicated logic in validation_checkpoint
def validation_checkpoint_router(state: StateSchema) -> list[Hashable]:
    runtime = get_runtime(Context)
    runtime_context = runtime.context

    if state.language not in runtime_context.valid_languages:
        return [END]

    if state.domain is None:
        return [END]

    if state.domain == "Primary School Representation":
        return [END]

    if state.user_context_request is None:
        return ["user_context_requester"]

    return ["retriever_assistant"]


def retriever_assistant_router(state: StateSchema) -> list[Hashable]:
    if not len(state.relevant_chunks):
        return [END]

    return ["assistant"]
