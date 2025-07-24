from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema
from lupai.llm_experts import NewLawAlignment, NewLawAlignmentInput


from .utils import socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    answer = state.assistant_response.answer
    # NOTE: Conditional execution
    if state.domain.domain != "Immigration":
        logger.info("new_immigration_law_fixer skipped.")
        return {
            "assistant_response": {
                "answer": answer,
                "answer_found": state.assistant_response.answer_found,
                "improved_answer": answer,
            }
        }

    logger.info("running new_immigration_law_fixer...")
    conf = config["configurable"]

    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="new_immigration_law_fixer",
        ),
        websocket=conf["websocket"],
    )

    new_law_alignment = NewLawAlignment()
    new_law_alignment_output = await new_law_alignment.async_generate(
        expert_input=NewLawAlignmentInput(
            query_text=state.query,
            law_changes=conf["immigration_law_changes"],
            output_language=state.language.language_name,
            assistant_answer=state.assistant_response.answer,
        )
    )

    corrected_answer = new_law_alignment_output.corrected_answer
    if corrected_answer is None:
        return {
            "assistant_response": {
                "answer": answer,
                "answer_found": state.assistant_response.answer_found,
                "improved_answer": answer,
            }
        }

    return {
        "assistant_response": {
            "answer": answer,
            "answer_found": state.assistant_response.answer_found,
            "improved_answer": corrected_answer,
        }
    }


new_immigration_law_fixer = Node(
    name="new_immigration_law_fixer",
    run=run,
)
