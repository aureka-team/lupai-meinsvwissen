from typing import Literal

from pydantic import StrictStr
from pydantic_settings import BaseSettings
from pydantic_extra_types.language_code import LanguageName

from common.utils.yaml_data import load_yaml

from lupai_mw.conf import assistant
from lupai_mw.meta.schema import Domain, SensitiveTopic


domains = load_yaml(file_path=f"{assistant.__path__[0]}/domains.yaml")
domains_ = [Domain(**d) for d in domains["domains"]]
domain_translations = domains["domain-translations"]

messages = load_yaml(file_path=f"{assistant.__path__[0]}/messages.yaml")
invalid_language_warning = messages["invalid-language-warning"]
no_answer_messages = messages["no-answer-messages"]
invalid_domain_messages = messages["invalid-domain-messages"]
psr_domain_messages = messages["psr-domain-messages"]
sensitive_topic_messages = messages["sensitive-topic-messages"]

intents = load_yaml(file_path=f"{assistant.__path__[0]}/intents.yaml")
intents_ = intents["intents"]
intent_instructions = intents["intent-instructions"]

sensitive_topics = load_yaml(
    file_path=f"{assistant.__path__[0]}/sensitive-topics.yaml"
)

sensitive_topics = sensitive_topics["sensitive-topics"]


class MultiAgentConfig(BaseSettings):
    mcp_dsn: StrictStr = "http://lupai-mw-mcp:8000/mcp"
    provider: Literal["openai", "azure"] = "openai"

    valid_languages: list[LanguageName] = [
        LanguageName("German"),
        LanguageName("English"),
    ]

    retriever_metadata_fields: list[StrictStr] = [
        "title",
        "topics",
        "legal_type",
        "germany_region",
        "category",
    ]

    domains: list[Domain] = domains_
    domain_translations: dict = domain_translations
    invalid_language_warning: StrictStr = invalid_language_warning
    no_answer_messages: dict[str, str] = no_answer_messages
    invalid_domain_messages: dict[str, str] = invalid_domain_messages
    psr_domain_messages: dict[str, str] = psr_domain_messages
    intents: dict[str, dict[str, str]] = intents_
    intent_instructions: dict[str, str] = intent_instructions
    sensitive_topics: list[SensitiveTopic] = sensitive_topics
    sensitive_topic_messages: dict[str, dict[str, str]] = (
        sensitive_topic_messages
    )
