from typing import Hashable

from ..schema import State


def retriever_assistant_router(state: State) -> list[Hashable]:
    if not len(state.relevant_chunks):
        return ["aggregator"]

    return ["assistant"]
