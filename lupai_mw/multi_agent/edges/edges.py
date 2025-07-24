from langgraph.graph import START
from agents.graph import SimpleEdge, ConditionalEdge

from .routers import (
    init_conditional_router,
    domain_conditional_router,
    assistant_conditional_router,
    retriever_conditional_router,
    clarification_decider_conditional_router,
    language_detector_conditional_router,
    domain_shift_conditional_router,
    user_context_init_conditional_router,
    intent_detector_conditional_router,
)


start_init = SimpleEdge(
    source=START,
    target="init",
)

init_conditional = ConditionalEdge(
    source="init",
    intermediates=[
        "user_context_initializer",
        "language_detector",
        "clarification_checkpoint",
    ],
    router=init_conditional_router,
)

domain_conditional = ConditionalEdge(
    source="domain_detector",
    intermediates=[
        "retriever",
        "output_parser",
    ],
    router=domain_conditional_router,
)

# user_context_initializer_language_detector = SimpleEdge(
#     source="user_context_initializer",
#     target="language_detector",
# )

user_context_init_conditional = ConditionalEdge(
    source="user_context_initializer",
    intermediates=[
        "user_context_extractor",
        "language_detector",
    ],
    router=user_context_init_conditional_router,
)

user_context_extractor_language_detector = SimpleEdge(
    source="user_context_extractor",
    target="language_detector",
)

clarification_checkpoint_assistant = SimpleEdge(
    source="clarification_checkpoint",
    target="assistant",
)

clarification_checkpoint_ = SimpleEdge(
    source="clarification_checkpoint",
    target="language_detector",
)

language_detector_conditional = ConditionalEdge(
    source="language_detector",
    intermediates=[
        "domain_detector",
        "domain_shift_detector",
        "output_parser",
    ],
    router=language_detector_conditional_router,
)

domain_shift_conditional = ConditionalEdge(
    source="domain_shift_detector",
    intermediates=[
        "domain_detector",
        "retriever",
    ],
    router=domain_shift_conditional_router,
)

sensitive_topic_detector_intent_detector = SimpleEdge(
    source="sensitive_topic_detector",
    target="intent_detector",
)

# clarification_decider_edges = SimpleEdge(
#     source=[
#         "sensitive_topic_detector",
#         "intent_detector",
#     ],
#     target="clarification_decider",
# )

intent_detector_conditional = ConditionalEdge(
    source="intent_detector",
    intermediates=[
        "clarification_decider",
        "generic_assistant",
    ],
    router=intent_detector_conditional_router,
)

generic_assistant_output_parser = SimpleEdge(
    source="generic_assistant",
    target="output_parser",
)

clarification_decider_conditional = ConditionalEdge(
    source="clarification_decider",
    intermediates=[
        "clarification_requester",
        "assistant",
    ],
    router=clarification_decider_conditional_router,
)

clarification_requester_output_parser = SimpleEdge(
    source="clarification_requester",
    target="output_parser",
)

topic_detector_organization_recommender = SimpleEdge(
    source="topic_detector",
    target="organization_recommender",
)

retriever_conditional = ConditionalEdge(
    source="retriever",
    intermediates=[
        "query_optimizer",
        "sensitive_topic_detector",
    ],
    router=retriever_conditional_router,
)

assistant_conditional = ConditionalEdge(
    source="assistant",
    intermediates=[
        "answer_improver",
        "output_parser",
        "topic_detector",
    ],
    router=assistant_conditional_router,
)

query_optimizer_retriever = SimpleEdge(
    source="query_optimizer",
    target="retriever",
)

answer_improver_new_immigration_law_fixer = SimpleEdge(
    source="answer_improver",
    target="new_immigration_law_fixer",
)

new_immigration_law_fixer_response_sensitizer = SimpleEdge(
    source="new_immigration_law_fixer",
    target="response_sensitizer",
)

output_parser_edges = SimpleEdge(
    source=[
        "response_sensitizer",
        "organization_recommender",
    ],
    target="output_parser",
)
