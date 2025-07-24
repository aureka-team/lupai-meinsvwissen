from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema
from lupai.llm_experts import SensitiveResponse, SensitiveResponseInput


from .utils import socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    answer = state.assistant_response.answer
    # NOTE: Conditional execution
    if state.sensitive_topic is None:
        logger.info("response_sensitizer skipped.")
        return {
            "assistant_response": {
                "answer": answer,
                "answer_found": state.assistant_response.answer_found,
                "improved_answer": answer,
            }
        }

    logger.info("running response_sensitizer...")
    conf = config["configurable"]

    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="response_sensitizer",
        ),
        websocket=conf["websocket"],
    )

    sensitive_response = SensitiveResponse()
    sensitive_response_output = await sensitive_response.async_generate(
        expert_input=SensitiveResponseInput(
            query_text=state.query,
            tone_guidelines=conf["tone_guidelines"],
            output_language=state.language.language_name,
            assistant_answer=state.assistant_response.answer,
        )
    )

    softened_answer = sensitive_response_output.softened_answer
    if softened_answer is None:
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
            "improved_answer": softened_answer,
        }
    }


response_sensitizer = Node(
    name="response_sensitizer",
    run=run,
)
