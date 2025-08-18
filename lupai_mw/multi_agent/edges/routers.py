from typing import Hashable

from ..schema import StateSchema


def retriever_assistant_router(state: StateSchema) -> list[Hashable]:
    if not len(state.relevant_chunks):
        return ["aggregator"]

    return ["assistant"]
