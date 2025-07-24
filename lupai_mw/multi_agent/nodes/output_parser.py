from agents.graph import Node
from common.logger import get_logger

from lupai.meta.data_models.api import SocketOutput
from lupai.multi_agent.schema import StateSchema, ConfigSchema

from .utils import socket_send


logger = get_logger(__name__)


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    logger.info("running output_parser...")

    conf = config["configurable"]
    await socket_send(
        socket_output=SocketOutput(
            session_id=state.session_id,
            status="output_parser",
        ),
        websocket=conf["websocket"],
    )

    language = state.language.language_name
    # NOTE: In case the detected languange is not valid.
    if not state.language.is_valid:
        logger.warning("invalid language.")
        answer = conf["language_config"]["invalid_language_warning"]
        valid_languages = sorted(conf["language_config"]["valid_languages"])
        valid_languages_text = f"{', '.join(valid_languages)}."

        answer = answer.format(
            detected_language=language,
            supported_languages=valid_languages_text,
        )

        return {
            "assistant_response": {
                "answer": answer,
                "answer_found": False,
                "improved_answer": answer,
            },
            "retriever_items": [],
            "is_final_response": True,
        }

    # NOTE: In case the detected domain is not valid.
    if not state.domain.is_valid:
        logger.warning("invalid domain.")

        valid_domains = [
            conf["domains"]["translations"][domain["domain"]][language]
            for domain in conf["domains"]["valid_domains"]
        ]

        valid_domains_text = f"{', '.join(valid_domains)}."
        answer = conf["messages"]["invalid_domain_answer"][language].format(
            valid_domains=valid_domains_text
        )

        return {
            "assistant_response": {
                "answer": answer,
                "answer_found": False,
                "improved_answer": answer,
            },
            "retriever_items": [],
            "is_final_response": True,
        }

    assistant_response = state.assistant_response
    # NOTE: In case the assistant was unable to answer the question.
    if assistant_response.answer is None:
        logger.warning("no answer found.")
        answer = conf["messages"]["no_retrieve_answer"][language]

        return {
            "assistant_response": {
                "answer": answer,
                "answer_found": False,
                "improved_answer": answer,
            },
            "is_final_response": True,
        }

    return {
        "assistant_response": assistant_response,
        "is_final_response": True,
    }


output_parser = Node(
    name="output_parser",
    run=run,
    is_finish_point=True,
)
