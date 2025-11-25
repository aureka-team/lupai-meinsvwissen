import asyncio

from collections import Counter

from rich.table import Table
from rich.console import Console

from common.cache import RedisCache
from common.logger import get_logger

from lupai_mw.db import MongoConnector
from lupai_mw.llm_agents import (
    QueryClassifier,
    QueryClassifierDeps,
    QueryCategory,
)

from .query_categories import query_categories


console = Console()
logger = get_logger(__name__)


async def main() -> None:
    mongo_connector = MongoConnector()
    assistant_states = [
        state
        async for state in mongo_connector.find_multiple(collection="states")
    ]

    data_items = [
        {
            "session_id": state["session_id"],
            "query": state["query"],
            "answer_status": state["answer_status"],
            "sensitive_topic": state["sensitive_topic"],
        }
        for state in assistant_states
    ]

    logger.info(f"data_items: {len(data_items)}")
    session_ids = [di["session_id"] for di in data_items]
    num_sessions = len(session_ids)

    num_interactions = Counter(session_ids)
    avg_interactions = sum(num_interactions.values()) / len(num_interactions)

    out_of_domain_interactions = len(
        [di for di in data_items if di["answer_status"] == "out_of_domain"]
    )

    no_sources_interactions = len(
        [
            di
            for di in data_items
            if di["answer_status"] == "no_relevant_sources"
        ]
    )

    sensitive_topic_interactions = len(
        [di for di in data_items if di["sensitive_topic"] is not None]
    )

    table1 = Table(
        title="General Stats",
        show_header=True,
        header_style="bold magenta",
    )

    table1.add_column("")
    table1.add_column("Count")
    table1.add_column("%")

    table1.add_row(
        "number_of_sessions",
        f"[cyan]{num_sessions}[/cyan]",
        f"[cyan]{'-'}[/cyan]",
    )

    table1.add_row(
        "interactions_per_session",
        f"[cyan]{avg_interactions}[/cyan]",
        f"[cyan]{round((avg_interactions / len(data_items)), 3)}[/cyan]",
    )

    table1.add_row(
        "out_of_domain_interactions",
        f"[cyan]{out_of_domain_interactions}[/cyan]",
        f"[cyan]{round((out_of_domain_interactions / len(data_items)), 3)}[/cyan]",
    )

    table1.add_row(
        "no_sources_interactions",
        f"[cyan]{no_sources_interactions}[/cyan]",
        f"[cyan]{round((no_sources_interactions / len(data_items)), 3)}[/cyan]",
    )

    table1.add_row(
        "sensitive_topic_interactions",
        f"[cyan]{sensitive_topic_interactions}[/cyan]",
        f"[cyan]{round((sensitive_topic_interactions / len(data_items)), 3)}[/cyan]",
    )

    console.print("\n")
    console.print(table1)
    console.print("\n")

    query_categories_ = [QueryCategory(**qc) for qc in query_categories]
    qc_deps = [
        QueryClassifierDeps(
            user_query=di["query"],
            categories=query_categories_,
        )
        for di in data_items
    ]

    user_prompts = [
        "Identify the single Category that best fits the query" for _ in qc_deps
    ]

    qc = QueryClassifier(cache=RedisCache())
    qc_outputs = await qc.batch_generate(
        user_prompts=user_prompts,
        agent_deps_list=qc_deps,
    )

    cnt = Counter(qc_output.category for qc_output in qc_outputs)
    cnt_map = {cat: count for cat, count in cnt.items()}

    table2 = Table(
        title="Query Types",
        show_header=True,
        header_style="bold magenta",
    )

    console.print("\n")
    table2.add_column("")
    table2.add_column("Count")
    table2.add_column("%")

    for qc in query_categories:
        category = qc["name"]
        count = cnt_map.get(category)
        count = count if count is not None else 0
        table2.add_row(
            f"{category}",
            f"[cyan]{count}[/cyan]",
            f"[cyan]{round((count / len(data_items)), 3)}[/cyan]",
        )

    console.print(table2)


if __name__ == "__main__":
    asyncio.run(main())
