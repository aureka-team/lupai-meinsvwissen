from pydantic import BaseModel, StrictStr, Field

from common.cache import RedisCache

from lupai.conf import llm_agents
from llm_agents.meta.interfaces import LLMAgent


class HGTagExtractorDeps(BaseModel):
    available_tags: tuple[StrictStr, ...] = Field(
        default=(
            "Living with Disability",
            "Learn German",
            "Skilled Workers",
            "Vocational Training",
            "Housing & Moving",
            "Household",
            "Forms of Employment",
            "Recognition of Foreign Certificates",
            "Citizenship",
            "Support for Families",
            "Preventive Care",
            "Family Reunification",
            "Everyday life",
            "Kids & Custody",
            "Healthcare System",
            "Marriage & Divorce",
            "Mobility",
            "Taxes",
            "Labour Laws",
            "Your Rights",
            "Visa & Residence",
            "Daycare & School",
            "Social Benefits",
            "Study",
            "Racism & Discrimination",
            "Job Search & Recognition",
            "State Aid",
        ),
        frozen=True,
    )


class HGTagExtractorOutput(BaseModel):
    extracted_tags: list[StrictStr] = Field(
        description="List of relevant tags that apply to the provided text.",
        default=[],
    )


class HGTagExtractor(LLMAgent[HGTagExtractorDeps, HGTagExtractorOutput]):
    def __init__(
        self,
        conf_path=f"{llm_agents.__path__[0]}/hg-tag-extractor.yaml",
        max_concurrency: int = 10,
        cache: RedisCache = None,
    ):
        super().__init__(
            conf_path=conf_path,
            deps_type=HGTagExtractorDeps,
            output_type=HGTagExtractorOutput,
            max_concurrency=max_concurrency,
            cache=cache,
        )
