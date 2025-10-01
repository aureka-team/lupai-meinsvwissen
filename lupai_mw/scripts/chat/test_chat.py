import os
import uuid
import time
import asyncio
import logfire

from rich.panel import Panel
from rich.prompt import Prompt
from rich.console import Console

from lupai_mw.meta.schema import UserContext
from lupai_mw.multi_agent.schema import StateSchema
from lupai_mw.multi_agent import (
    get_multi_agent,
    get_multi_agent_context,
    MultiAgentConfig,
)


logfire_token = os.getenv("LOGFIRE_TOKEN")
if logfire_token is not None:
    logfire.configure(service_name="lupai-meinsvwissen")
    logfire.instrument_pydantic_ai()
    logfire.instrument_mcp()
    logfire.instrument_openai()
    time.sleep(1)


console = Console()


exit_keywords = {
    "q",
    "quit",
    "exit",
}

test_queries = [
    "What is the difference between consent and compromise?",
    "How do I organize a student representation?",
    "Was ist der unterschied zwisschen konsensieren und kompromis?",
    "Who is Nikola Tesla?",
    "How can I buy a car?",
]

germany_regions = [
    "Baden-Württemberg",
    "Bayern",
    "Brandenburg",
    "Berlin",
    "Bremen",
    "Hamburg",
    "Hessen",
    "Mecklenburg-Vorpommern",
    "Niedersachsen",
    "Nordrhein-Westfalen",
    "Rheinland-Pfalz",
    "Sachsen",
    "Sachsen-Anhalt",
    "Schleswig-Holstein",
    "Thüringen",
    "Landesschülervertretung des Saarlandes",
]


def option_selection(
    options: list[str],
    header_message: str,
    footer_message: str,
) -> str | None:
    console.print(Panel.fit(f"[bold cyan]{header_message}[/bold cyan]"))
    for idx, q in enumerate(options, start=1):
        console.print(f"{idx}) {q}")

    while True:
        selection = Prompt.ask(f"[bold cyan]{footer_message}[/bold cyan]")
        if selection in exit_keywords:
            return

        try:
            idx = int(selection) - 1
        except Exception:
            console.print(f"[red]Invalid selection: {selection}[/red]")
            continue

        if idx >= 0 and idx < len(options):
            selection = options[idx]
            console.print(selection)
            return selection

        console.print(f"[red]Invalid selection: {selection}[/red]")


async def main():
    multi_agent = get_multi_agent()
    multi_agent.compile()

    config = MultiAgentConfig()
    multi_agent_context = get_multi_agent_context(config=config)

    multi_agent.display_graph()
    console.print(
        Panel.fit(
            "[bold cyan]Welcome to LupAI Meinsvwissen![/bold cyan]",
            style="bold white",
        )
    )

    session_id = uuid.uuid4().hex
    germany_region = option_selection(
        options=germany_regions,
        header_message="Select a germany region:",
        footer_message="Enter the number of the region",
    )

    if germany_region is None:
        return

    session_id = uuid.uuid4().hex
    console.print(
        Panel.fit(
            "[bold cyan]Choose an option:\n1) Select a test query\n2) Enter a new query[/bold cyan]",
            style="bold white",
        )
    )

    option = Prompt.ask(
        "Your choice",
        choices=["1", "2"],
        default="1",
    )

    query = None
    if option == "1":
        query = option_selection(
            options=test_queries,
            header_message="Select a query:",
            footer_message="Enter the number of the query",
        )

        if query is None:
            return

    while True:
        query = (
            Prompt.ask("[bold magenta]user[/bold magenta]")
            if query is None
            else query
        )

        if query in exit_keywords:
            break

        state = await multi_agent.run(
            input_state=StateSchema(
                session_id=session_id,
                query=query,
                user_context=UserContext(germany_region=germany_region),
            ),
            context=multi_agent_context,
            thread_id=session_id,
        )

        console.print(state)
        assert state is not None

        console.print(
            Panel.fit(
                f"[bold cyan]{state.assistant_response}[/bold cyan]",
                style="bold white",
            )
        )

        query = None


if __name__ == "__main__":
    asyncio.run(main())
