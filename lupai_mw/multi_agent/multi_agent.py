from multi_agents.graph import MultiAgentGraph
from lupai_mw.multi_agent.schema import StateSchema, ContextSchema
from .nodes import assistant, sensitive_detector, aggregator

from .edges import sensitive_detector_assistant, assistant_aggregator


def get_multi_agent() -> MultiAgentGraph:
    nodes = [
        assistant,
        sensitive_detector,
        aggregator,
    ]

    edges = [
        sensitive_detector_assistant,
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
