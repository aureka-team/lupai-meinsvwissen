import json
import uuid
import asyncio
import websockets

from rich.prompt import Prompt
from rich.console import Console
from rich.panel import Panel

from lupai_mw.api.routers.chat import ChatInput


console = Console()


SOCKET_URI = "ws://lupai-mw-api:8000/chat"


async def main():
    session_id = uuid.uuid4().hex
    async with websockets.connect(SOCKET_URI) as websocket:
        assert websocket is not None

        console.print(
            Panel.fit(
                "[bold cyan]Welcome to LupAI Meinsvwissen! Enter your query below:[/bold cyan]",
                style="bold white",
            )
        )

        while True:
            console.print(
                f"session_id: {session_id}",
                style="bold cyan",
            )

            query = Prompt.ask()
            message = ChatInput(
                query=query,
                session_id=session_id,
            )

            message = message.model_dump_json()
            await websocket.send(message)

            async for response in websocket:
                response = json.loads(response)
                if response["is_final"]:
                    assistant_response = response["assistant_response"]
                    assistant_response = (
                        assistant_response
                        if assistant_response is not None
                        else "No answer."
                    )

                    console.print(
                        assistant_response,
                        style="bold white",
                    )

                    break


if __name__ == "__main__":
    asyncio.run(main())
