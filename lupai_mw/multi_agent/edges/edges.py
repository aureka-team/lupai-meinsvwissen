from langgraph.graph import END

from multi_agents.graph import SimpleEdge, ConditionalEdge
from .routers import (
    retriever_assistant_router,
    validation_checkpoint_router,
)


validation_checkpoint_edges = SimpleEdge(
    source=[
        "domain_detector",
        "intent_detector",
        "language_detector",
        "user_context_extractor",
        "sensitive_topic_detector",
    ],
    target="validation_checkpoint",
)

validation_checkpoint_conditional = ConditionalEdge(
    source="validation_checkpoint",
    intermediates=[
        "user_context_requester",
        "retriever_assistant",
        END,
    ],
    router=validation_checkpoint_router,
)

user_context_requester_end = SimpleEdge(
    source="user_context_requester",
    target=END,
)

retriever_assistant_conditional = ConditionalEdge(
    source="retriever_assistant",
    intermediates=[
        "assistant",
        END,
    ],
    router=retriever_assistant_router,
)

assistant_end = SimpleEdge(
    source="assistant",
    target=END,
)
