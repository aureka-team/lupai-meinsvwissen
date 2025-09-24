from multi_agents.graph import MultiAgentGraph
from lupai_mw.multi_agent.schema import StateSchema, Context

from .nodes import (
    user_context_requester,
    user_context_extractor,
    language_detector,
    retriever_assistant,
    assistant,
    domain_detector,
    validation_checkpoint,
    intent_detector,
)

from .edges import (
    validation_checkpoint_conditional,
    validation_checkpoint_edges,
    retriever_assistant_conditional,
    user_context_requester_end,
    assistant_end,
)


def get_multi_agent() -> MultiAgentGraph:
    nodes = [
        user_context_requester,
        user_context_extractor,
        language_detector,
        retriever_assistant,
        assistant,
        domain_detector,
        validation_checkpoint,
        intent_detector,
    ]

    edges = [
        validation_checkpoint_conditional,
        validation_checkpoint_edges,
        retriever_assistant_conditional,
        user_context_requester_end,
        assistant_end,
    ]

    multi_agent = MultiAgentGraph(
        state_schema=StateSchema,
        context_schema=Context,
        nodes=nodes,
        edges=edges,
        with_memory=True,
    )

    multi_agent.compile()
    return multi_agent
