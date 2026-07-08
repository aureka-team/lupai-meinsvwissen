import argparse
import asyncio
import os

from urllib.parse import quote_plus

from motor.motor_asyncio import AsyncIOMotorClient
from rich import box
from rich.console import Console
from rich.table import Table

from lupai_mw.config.config import config


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 27017
DEFAULT_USERNAME = "lupai-mw-prod-api-user"
DEFAULT_DATABASE = "lupai-mw-prod-api-db"
DEFAULT_AUTH_DATABASE = "lupai-mw-prod-api-db"

STATES_COLLECTION = "states"

console = Console(force_terminal=True, width=240)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a full conversation report for a session_id.",
    )

    parser.add_argument("session_id")
    parser.add_argument("--host", default=os.getenv("MONGO_HOST", DEFAULT_HOST))
    parser.add_argument("--port", default=int(os.getenv("MONGO_PORT", DEFAULT_PORT)), type=int)
    parser.add_argument("--username", default=os.getenv("MONGO_USERNAME", DEFAULT_USERNAME))
    parser.add_argument("--database", default=DEFAULT_DATABASE)
    parser.add_argument("--auth-database", default=DEFAULT_AUTH_DATABASE)

    return parser.parse_args()


def build_mongo_uri(args: argparse.Namespace) -> str:
    if config.prod_mongodb_password is None:
        raise ValueError("PROD_MONGODB_PASSWORD must be set")

    username = quote_plus(args.username)
    escaped_password = quote_plus(config.prod_mongodb_password.get_secret_value())

    return (
        f"mongodb://{username}:{escaped_password}@{args.host}:{args.port}/"
        f"?authSource={quote_plus(args.auth_database)}&directConnection=true"
    )


async def get_session_states(db, session_id: str) -> list[dict]:
    cursor = db[STATES_COLLECTION].find({"session_id": session_id}).sort("_id", 1)
    return [doc async for doc in cursor]


def format_value(value: object) -> str:
    if value is None:
        return "-"

    return str(value)


def relevant_chunk_count(state: dict) -> str:
    relevant_chunks = state.get("relevant_chunks") or []
    return str(len(relevant_chunks))


def render_conversation(session_id: str, states: list[dict]) -> None:
    table = Table(
        title=f"Session {session_id}",
        show_header=True,
        header_style="bold bright_white",
        title_style="bold bright_cyan",
        box=box.SIMPLE_HEAVY,
        row_styles=("grey70",),
        expand=False,
        show_lines=True,
        padding=(0, 1),
    )

    table.add_column("#", justify="right", no_wrap=True, style="grey70")
    table.add_column("Role", no_wrap=True, style="grey70")
    table.add_column("Message", overflow="fold", style="grey70", min_width=48)
    table.add_column("Domain", overflow="fold", style="grey70", min_width=18)
    table.add_column("Intent", overflow="fold", style="grey70", min_width=18)
    table.add_column("Language", no_wrap=True, style="grey70")
    table.add_column("Sensitive", overflow="fold", style="grey70", min_width=12)
    table.add_column("Status", overflow="fold", style="grey70", min_width=14)
    table.add_column("Chunks", justify="right", no_wrap=True, style="grey70")

    for turn, state in enumerate(states, start=1):
        metadata = (
            format_value(state.get("domain")),
            format_value(state.get("intent")),
            format_value(state.get("language")),
            format_value(state.get("sensitive_topic")),
            format_value(state.get("answer_status")),
            relevant_chunk_count(state),
        )

        table.add_row(
            str(turn),
            "user",
            format_value(state.get("query")),
            *metadata,
        )
        table.add_row(
            str(turn),
            "assistant",
            format_value(state.get("assistant_response")),
            *metadata,
        )

    console.print("\n")
    console.print(table)


async def main() -> None:
    args = parse_args()

    mongo_uri = build_mongo_uri(args)
    client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5_000)
    db = client[args.database]

    states = await get_session_states(db, args.session_id)
    if not states:
        console.print(f"\n[grey70]No conversation found for session_id: {args.session_id}[/grey70]")
        client.close()
        return

    render_conversation(args.session_id, states)
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
