from multi_agents.graph import SimpleEdge


init_language_detector = SimpleEdge(
    source="init",
    target="language_detector",
)

init_sensitive_detector = SimpleEdge(
    source="init",
    target="sensitive_detector",
)

sensitive_detector_edges = SimpleEdge(
    source=[
        "language_detector",
        "sensitive_detector",
    ],
    target="assistant",
)

assistant_aggregator = SimpleEdge(
    source="assistant",
    target="aggregator",
)
