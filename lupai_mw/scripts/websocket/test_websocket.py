import json
import uuid
import httpx
import asyncio
import websockets

from rich.panel import Panel
from rich.prompt import Prompt
from rich.console import Console

from pydantic import StrictStr, Field
from pydantic_settings import BaseSettings

from lupai_mw.meta.schema import UserContext
from lupai_mw.api.routers.chat import SocketInput


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
    "Saarlandes",
]


class Config(BaseSettings):
    test_user: StrictStr = Field(min_length=1)
    test_password: StrictStr = Field(min_length=1)
    test_http_protocol: StrictStr = Field(min_length=1)
    test_websocket_protocol: StrictStr = Field(min_length=1)
    test_socket_dsn: StrictStr = Field(min_length=1)
    exit_keywords: set[StrictStr] = exit_keywords


config = Config()  # type: ignore


async def get_token() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{config.test_http_protocol}://{config.test_socket_dsn}/auth/jwt/login",
            data={
                "username": config.test_user,
                "password": config.test_password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        response.raise_for_status()
        return response.json()["access_token"]


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
    session_id = uuid.uuid4().hex
    token = await get_token()

    SOCKET_URL = f"{config.test_websocket_protocol}://{config.test_socket_dsn}/lupai/chat?token={token}"
    console.print(SOCKET_URL)
    async with websockets.connect(SOCKET_URL) as websocket:
        assert websocket is not None

        console.print(
            Panel.fit(
                f"[bold cyan]Welcome to LupAI Meinsvwissen!\nsession_id: {session_id}[/bold cyan]",
                style="bold white",
            )
        )

        germany_region = option_selection(
            options=germany_regions,
            header_message="Select a germany region:",
            footer_message="Enter the number of the region",
        )

        if germany_region is None:
            return

        while True:
            query = Prompt.ask("[bold magenta]user[/bold magenta]")
            if query in config.exit_keywords:
                break

            message = SocketInput(
                user_query=query,
                session_id=session_id,
                user_context=UserContext(germany_region=germany_region),
            )

            message = message.model_dump_json()
            await websocket.send(message)

            async for response in websocket:
                response = json.loads(response)
                assistant_response = response.get("assistant_response")

                if assistant_response is None:
                    console.print(
                        f"[bold cyan]status: {response['status']} | {response['status_display']}[bold cyan]",
                        style="bold white",
                    )

                    continue

                console.print(response)
                console.print(
                    Panel.fit(
                        f"[bold cyan]{assistant_response}[/bold cyan]",
                        style="bold white",
                    )
                )

                break


if __name__ == "__main__":
    asyncio.run(main())
