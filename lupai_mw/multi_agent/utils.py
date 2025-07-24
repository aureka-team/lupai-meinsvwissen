import os

from common.logger import get_logger
from common.utils.yaml_data import load_yaml
from common.utils.json_data import load_json

from fastapi import WebSocket

from lupai.conf import agent, experts
from lupai.loaders import load_organizations
from lupai.utils.chat_history import get_mongodb_chat_history

from .schema import ConfigSchema


logger = get_logger(__name__)


BASE_CONF_PATH = agent.__path__[0]
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")


def get_multi_agent_config(
    session_id: str,
    location: str,
    user_context: dict | None = None,
    with_clarification: bool = True,
    websocket: WebSocket | None = None,
) -> ConfigSchema:
    wv_base_conf = load_yaml(file_path=f"{BASE_CONF_PATH}/weaviate.yaml")
    sensitive_topics = load_yaml(
        file_path=f"{BASE_CONF_PATH}/sensitive-content.yaml"
    )

    intents = load_yaml(file_path=f"{BASE_CONF_PATH}/intents.yaml")
    assistant_expert_conf = load_yaml(
        file_path=f"{experts.__path__[0]}/assistant.yaml"
    )

    language = load_yaml(file_path=f"{BASE_CONF_PATH}/language.yaml")

    return ConfigSchema(
        **{
            "location": location,
            "user_context": user_context,
            "wv": {
                "chunk_props": set(wv_base_conf["chunk-properties"]),
                "query_props": wv_base_conf["query-properties"],
                "return_props": wv_base_conf["return-properties"],
            },
            "sensitive_topics": {
                "topics": [
                    st["topic"] for st in sensitive_topics["sensitive-topics"]
                ],
                "warnings": {
                    st["topic"]: st["warning"]
                    for st in sensitive_topics["sensitive-topics"]
                },
                "translations": sensitive_topics["translations"],
            },
            "domains": load_yaml(file_path=f"{BASE_CONF_PATH}/domains.yaml"),
            "intents": {
                "intents": intents,
                "instructions": {
                    item["intent"]: assistant_expert_conf[item["instructions"]]
                    for item in intents
                },
            },
            "topics": load_yaml(file_path=f"{BASE_CONF_PATH}/topics.yaml"),
            "organizations": load_organizations(
                file_path="/resources/notion/organizations.csv"
            ),
            "org_translations": load_json(
                json_file_path=f"{BASE_CONF_PATH}/org-translations.json"
            ),
            "messages": load_yaml(file_path=f"{BASE_CONF_PATH}/messages.yaml"),
            "history": get_mongodb_chat_history(
                session_id=session_id,
                collection_name="chat-history",
                database_name="lupai",
                connection_string=MONGO_URI,
                # history_size=100,
            ),
            "language_config": {
                "valid_languages": set(language["valid-languages"]),
                "invalid_language_warning": language[
                    "invalid-language-warning"
                ],
            },
            "immigration_law_changes": load_yaml(
                file_path=f"{BASE_CONF_PATH}/immigration-law-changes.yaml"
            ),
            "tone_guidelines": load_yaml(
                file_path=f"{BASE_CONF_PATH}/tone-guidelines.yaml"
            ),
            "with_clarification": with_clarification,
            "websocket": websocket,
        }
    )
