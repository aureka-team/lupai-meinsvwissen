from multi_agents.graph import MultiAgentGraph
from lupai_mw.multi_agent.schema import StateSchema, ContextSchema
from .nodes import (
    init,
    language_detector,
    assistant,
    sensitive_detector,
    aggregator,
)

from .edges import (
    init_language_detector,
    init_sensitive_detector,
    sensitive_detector_edges,
    assistant_aggregator,
)


def get_multi_agent() -> MultiAgentGraph:
    nodes = [
        init,
        language_detector,
        assistant,
        sensitive_detector,
        aggregator,
    ]

    edges = [
        init_language_detector,
        init_sensitive_detector,
        sensitive_detector_edges,
        assistant_aggregator,
    ]

    multi_agent = MultiAgentGraph(
        state_schema=StateSchema,
        context_schema=ContextSchema,
        nodes=nodes,
        edges=edges,
    )

    multi_agent.compile()
    return multi_agent
