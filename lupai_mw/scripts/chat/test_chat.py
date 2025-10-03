import os
import uuid
import time
import asyncio
import logfire

from more_itertools import flatten

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


if os.getenv("LOGFIRE_TOKEN") is not None:
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
    "Landesschülervertretung des Saarlandes",  # TODO: Ask to Jonas.
]

test_queries = [
    {
        "german": "Meine Schüler sind unmotiviert. Was kann ich tun?",
        "english": "My students are unmotivated. What can I do?",
    },
    {
        "german": "Unsere Schulleitung verbietet uns einen instagram-Account für die SV zu gründen. Ist das legal?",
        "english": "Our school administration is forbidding us from creating an Instagram account for the student council. Is that legal?",
    },
    {
        "german": "Wie wird die Wahl von Schulsprecher:innen organisiert?",
        "english": "How is the election of student representatives organized?",
    },
    {
        "german": "Dürfen Klassensprecher:innen von Lehrer:innen abgesetzt werden?",
        "english": "Are class representatives allowed to be removed by teachers?",
    },
    {
        "german": "Wie bereite ich einen Projekttag für die SV sinnvoll vor? Methoden, Ablaufplan, Vorbereitung",
        "english": "How do I properly prepare a project day for the student council? Methods, schedule, preparation",
    },
    {
        "german": "Woher kriegen wir Geld für die SV-Arbeit?",
        "english": "Where can we get money for student council work?",
    },
    {
        "german": "Welche Rechte haben Schüler:innen?",
        "english": "What rights do students have?",
    },
    {
        "german": "Was gibt es für coole SV-Projekte?",
        "english": "What are some cool student council projects?",
    },
    {
        "german": "Wir hätten gern ein SV-Seminar an der Schule. Wen können wir dazu anfragen?",
        "english": "We would like to have a student council seminar at the school. Who can we contact about this?",
    },
    {
        "german": "Nazis sind ein Problem bei uns. Was können wir als SV dagegen tun?",
        "english": "Nazis are a problem at our school. What can we do as the student council to address this?",
    },
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
    _test_queries = (tq.values() for tq in test_queries)
    _test_queries = list(flatten(_test_queries))

    if option == "1":
        query = option_selection(
            options=_test_queries,
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
