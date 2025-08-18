from multi_agents.graph import MultiAgentGraph
from lupai_mw.multi_agent.schema import StateSchema, ContextSchema
from .nodes import (
    init,
    language_detector,
    sensitive_topic_detector,
    retriever_assistant,
    assistant,
    aggregator,
)

from .edges import (
    init_language_detector,
    init_sensitive_topic_detector,
    sensitive_topic_detector_edges,
    retriever_assistant_conditional,
    assistant_aggregator,
)


def get_multi_agent() -> MultiAgentGraph:
    nodes = [
        init,
        language_detector,
        sensitive_topic_detector,
        retriever_assistant,
        assistant,
        aggregator,
    ]

    edges = [
        init_language_detector,
        init_sensitive_topic_detector,
        sensitive_topic_detector_edges,
        retriever_assistant_conditional,
        assistant_aggregator,
    ]

    multi_agent = MultiAgentGraph(
        state_schema=StateSchema,
        context_schema=ContextSchema,
        nodes=nodes,
        edges=edges,
        with_memory=True,
    )

    multi_agent.compile()
    return multi_agent
