from multi_agents.graph import SimpleEdge


sensitive_detector_assistant = SimpleEdge(
    source="sensitive_detector",
    target="c",
)

assistant_aggregator = SimpleEdge(
    source="aggregator",
    target="aggregator",
)
