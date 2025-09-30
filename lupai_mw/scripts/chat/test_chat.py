import uuid
import asyncio

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
    console.print(
        Panel.fit(
            "[bold cyan]Choose a Germany Region[/bold cyan]",
            style="bold white",
        )
    )

    germany_region = Prompt.ask(
        "Germany Region",
        choices=germany_regions,
        default="Berlin",
    )

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
        console.print(Panel.fit("[bold cyan]Select a query:[/bold cyan]"))
        for idx, q in enumerate(test_queries):
            console.print(f"{idx}) {q}")

        while True:
            selection = Prompt.ask(
                "[bold cyan]Enter the number of the query[/bold cyan]"
            )

            try:
                idx = int(selection)
            except Exception:
                console.print(f"[red]Invalid selection: {selection}[/red]")
                continue

            if idx >= 0 and idx < len(test_queries):
                query = test_queries[idx]
                break

            console.print(f"[red]Invalid selection: {selection}[/red]")

    while True:
        query = (
            Prompt.ask("[bold magenta]user[/bold magenta]")
            if query is None
            else query
        )

        console.print(query)
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
