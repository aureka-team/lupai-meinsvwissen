from typing import Any

from multi_agents.graph import Node
from common.logger import get_logger

from langgraph.runtime import get_runtime
from lupai_mw.multi_agent.schema import StateSchema, Context


logger = get_logger(__name__)


async def run(state: StateSchema) -> dict[str, Any]:
    logger.info("running validation_checkpoint...")

    runtime = get_runtime(Context)
    runtime_context = runtime.context

    detected_language = state.language
    supported_languages = runtime_context.valid_languages

    if detected_language not in supported_languages:
        return {
            "assistant_response": runtime_context.invalid_language_warning.format(
                supported_languages=supported_languages,
            ),
            "user_context_request": None,
        }

    assert detected_language is not None
    if state.domain is None:
        valid_domains = runtime_context.domain_translations[detected_language]
        return {
            "assistant_response": runtime_context.invalid_domain_messages[
                detected_language
            ].format(valid_domains=valid_domains),
            "user_context_request": None,
        }

    if state.domain == "Primary School Representation":
        logger.info("psr_domain")
        return {
            "assistant_response": runtime_context.psr_domain_messages[
                detected_language
            ],
            "user_context_request": None,
        }

    return {}


validation_checkpoint = Node(
    name="validation_checkpoint",
    run=run,
    is_finish_point=True,
)
