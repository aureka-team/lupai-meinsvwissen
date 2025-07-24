from agents.graph import Node
from common.logger import get_logger

# from lupai.meta.data_models.api import SocketOutput
# from lupai.multi_agent.schema import StateSchema, ConfigSchema, Organization
from lupai.multi_agent.schema import StateSchema, ConfigSchema

# from .utils import socket_send


logger = get_logger(__name__)


def set_organization_score(
    organization: dict,
    topics: set[str],
    language: str,
) -> dict:
    org_language = organization["language"]
    if org_language is not None and org_language != language:
        return organization | {"score": 0}

    obligatory_topics = organization["obligatory_topics"]
    optional_topics = organization["optional_topics"]

    n_obligatory_topics = len(obligatory_topics)
    n_optional_topics = len(optional_topics)

    if n_obligatory_topics and not obligatory_topics.issubset(topics):
        return organization | {"score": 0}

    language_score = 1 if org_language is not None else 0
    if not n_optional_topics:
        return organization | {"score": n_obligatory_topics + language_score}

    n_optional_matches = len(optional_topics.intersection(topics))
    return organization | {
        "score": n_obligatory_topics + n_optional_matches + language_score
    }


async def run(
    state: StateSchema,
    config: ConfigSchema,
) -> StateSchema:
    return {
        "organizations": None,
    }

    # logger.info("running organization_recommender...")

    # conf = config["configurable"]
    # await socket_send(
    #     socket_output=SocketOutput(
    #         session_id=state.session_id,
    #         status="organization_recommender",
    #     ),
    #     websocket=conf["websocket"],
    # )

    # topics = set(state.topics)
    # organizations = (
    #     set_organization_score(
    #         organization=org,
    #         topics=topics,
    #         language=state.language.language_name,
    #     )
    #     for org in conf["organizations"]
    # )

    # org_translations = conf["org_translations"]
    # organizations = (
    #     Organization(
    #         **(
    #             org
    #             | {
    #                 "description": org_translations[org["name"]][
    #                     state.language.language_name
    #                 ]
    #             }
    #         )
    #     )
    #     for org in organizations
    #     if org["score"] > 0
    # )

    # organizations = sorted(
    #     organizations,
    #     key=lambda x: x.score,
    #     reverse=True,
    # )

    # return {"organizations": organizations}


organization_recommender = Node(
    name="organization_recommender",
    run=run,
)
