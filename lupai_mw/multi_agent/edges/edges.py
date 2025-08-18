from multi_agents.graph import SimpleEdge, ConditionalEdge

from .routers import retriever_assistant_router


init_language_detector = SimpleEdge(
    source="init",
    target="language_detector",
)

init_sensitive_topic_detector = SimpleEdge(
    source="init",
    target="sensitive_topic_detector",
)

sensitive_topic_detector_edges = SimpleEdge(
    source=[
        "language_detector",
        "sensitive_topic_detector",
    ],
    target="retriever_assistant",
)

retriever_assistant_conditional = ConditionalEdge(
    source="retriever_assistant",
    intermediates=[
        "assistant",
        "aggregator",
    ],
    router=retriever_assistant_router,
)

assistant_aggregator = SimpleEdge(
    source="assistant",
    target="aggregator",
)
