import argparse
import asyncio
import html
import os
import shutil
import subprocess
import tempfile

from collections.abc import Iterable
from pathlib import Path
from urllib.parse import quote_plus

from motor.motor_asyncio import AsyncIOMotorClient
from rich.console import Console

from common.utils.yaml_data import load_yaml
from lupai_mw.conf import assistant
from lupai_mw.config.config import config


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 27017
DEFAULT_USERNAME = "lupai-mw-prod-api-user"
DEFAULT_DATABASE = "lupai-mw-prod-api-db"
DEFAULT_AUTH_DATABASE = "lupai-mw-prod-api-db"
DEFAULT_HTML_OUTPUT = "/resources/reports/usage_report.html"
PDF_CONVERTER_CANDIDATES = (
    "google-chrome",
    "chromium",
    "chromium-browser",
)
SENSITIVE_EXAMPLES_SESSION_ID = "9f621d4d7ac445eca1d6011d68e9d4a1"

MESSAGE_HISTORY_COLLECTION = "message_history"
STATES_COLLECTION = "states"

console = Console(force_terminal=True, width=240)

COLUMN_LABELS = {
    "answer_status": "Status",
    "cache_read_tokens": "Cache R",
    "cache_write_tokens": "Cache W",
    "count": "Count",
    "day": "Day",
    "domain": "Domain",
    "input_tokens": "Input",
    "interactions": "Interactions",
    "interactions_per_session": "Average Interactions / Session",
    "intent": "Intent",
    "llm_calls": "LLM Calls",
    "month": "Month",
    "output_tokens": "Output",
    "pct": "Percent",
    "query": "Query",
    "sensitive_topic": "Topic",
    "sessions": "Sessions",
    "sensitive_topics": "Sensitive",
    "session_id": "Session",
    "total_tokens": "Total",
    "user": "User",
}

ACTIVITY_COLUMNS = (
    "month",
    "sessions",
    "interactions_per_session",
    "sensitive_topics",
)

DAILY_ACTIVITY_COLUMNS = (
    "day",
    "sessions",
    "interactions",
    "sensitive_topics",
)

MONTHLY_STATS_SOURCE_COLUMNS = (
    "month",
    "sessions",
    "interactions_per_session",
)

DAILY_STATS_SOURCE_COLUMNS = (
    "day",
    "sessions",
    "interactions",
)

CATEGORY_STATS_COLUMNS = (
    "domain",
    "count",
    "pct",
)

INTENT_STATS_COLUMNS = (
    "intent",
    "count",
    "pct",
)

STATS_COLUMN_LABELS = {
    "avg": "Average",
    "column": "Column",
    "max": "Max",
    "min": "Min",
    "total": "Total",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a MongoDB usage report from message_history and sessions.",
    )

    parser.add_argument("--host", default=os.getenv("MONGO_HOST", DEFAULT_HOST))
    parser.add_argument("--port", default=int(os.getenv("MONGO_PORT", DEFAULT_PORT)), type=int)
    parser.add_argument("--username", default=os.getenv("MONGO_USERNAME", DEFAULT_USERNAME))
    parser.add_argument("--database", default=DEFAULT_DATABASE)
    parser.add_argument("--auth-database", default=DEFAULT_AUTH_DATABASE)
    parser.add_argument("--html-output", default=DEFAULT_HTML_OUTPUT)
    parser.add_argument("--pdf-output")

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


def usage_projection() -> dict:
    return {
        "input_tokens": {"$ifNull": ["$usage.input_tokens", 0]},
        "cache_write_tokens": {"$ifNull": ["$usage.cache_write_tokens", 0]},
        "cache_read_tokens": {"$ifNull": ["$usage.cache_read_tokens", 0]},
        "output_tokens": {"$ifNull": ["$usage.output_tokens", 0]},
    }


def usage_group_fields() -> dict:
    return {
        "llm_calls": {"$sum": 1},
        "input_tokens": {"$sum": "$input_tokens"},
        "cache_write_tokens": {"$sum": "$cache_write_tokens"},
        "cache_read_tokens": {"$sum": "$cache_read_tokens"},
        "output_tokens": {"$sum": "$output_tokens"},
        "total_tokens": {
            "$sum": {
                "$add": [
                    "$input_tokens",
                    "$cache_write_tokens",
                    "$cache_read_tokens",
                    "$output_tokens",
                ],
            },
        },
    }


def activity_pipeline(date_format: str, period_column: str) -> list[dict]:
    return [
        {
            "$project": {
                "session_id": 1,
                period_column: {
                    "$dateToString": {
                        "format": date_format,
                        "date": {"$toDate": "$_id"},
                        "timezone": "UTC",
                    },
                },
                "sensitive_topics": {"$cond": [{"$ne": ["$sensitive_topic", None]}, 1, 0]},
            },
        },
        {
            "$group": {
                "_id": f"${period_column}",
                "sessions": {"$addToSet": "$session_id"},
                "interactions": {"$sum": 1},
                "sensitive_topics": {"$sum": "$sensitive_topics"},
            },
        },
        {
            "$lookup": {
                "from": MESSAGE_HISTORY_COLLECTION,
                "let": {
                    "period": "$_id",
                    "session_ids": "$sessions",
                },
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$in": ["$session_id", "$$session_ids"]},
                                    {
                                        "$eq": [
                                            {
                                                "$dateToString": {
                                                    "format": date_format,
                                                    "date": "$date",
                                                    "timezone": "UTC",
                                                },
                                            },
                                            "$$period",
                                        ],
                                    },
                                ],
                            },
                        },
                    },
                    {
                        "$project": {
                            **usage_projection(),
                        },
                    },
                    {
                        "$group": {
                            "_id": None,
                            **usage_group_fields(),
                        },
                    },
                ],
                "as": "usage",
            },
        },
        {"$set": {"usage": {"$ifNull": [{"$first": "$usage"}, {}]}}},
        {
            "$project": {
                "_id": 0,
                period_column: "$_id",
                "sessions": {"$size": "$sessions"},
                "interactions": 1,
                "interactions_per_session": {
                    "$cond": [
                        {"$eq": [{"$size": "$sessions"}, 0]},
                        0,
                        {"$divide": ["$interactions", {"$size": "$sessions"}]},
                    ],
                },
                "sensitive_topics": 1,
                "llm_calls": {"$ifNull": ["$usage.llm_calls", 0]},
                "input_tokens": {"$ifNull": ["$usage.input_tokens", 0]},
                "cache_write_tokens": {"$ifNull": ["$usage.cache_write_tokens", 0]},
                "cache_read_tokens": {"$ifNull": ["$usage.cache_read_tokens", 0]},
                "output_tokens": {"$ifNull": ["$usage.output_tokens", 0]},
                "total_tokens": {"$ifNull": ["$usage.total_tokens", 0]},
            },
        },
        {"$sort": {period_column: 1}},
    ]


def session_examples_pipeline(session_id: str) -> list[dict]:
    return [
        {
            "$match": {
                "session_id": session_id,
            },
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "query": 1,
                "assistant_response": 1,
            },
        },
    ]


def category_stats_pipeline(field: str, missing_label: str = "unknown") -> list[dict]:
    return [
        {
            "$group": {
                "_id": {"$ifNull": [f"${field}", missing_label]},
                "count": {"$sum": 1},
            },
        },
        {
            "$setWindowFields": {
                "output": {
                    "total": {"$sum": "$count"},
                },
            },
        },
        {
            "$project": {
                "_id": 0,
                field: "$_id",
                "count": 1,
                "pct": {
                    "$cond": [
                        {"$eq": ["$total", 0]},
                        0,
                        {"$multiply": [{"$divide": ["$count", "$total"]}, 100]},
                    ],
                },
            },
        },
        {"$sort": {"count": -1, field: 1}},
    ]


async def aggregate(db, collection: str, pipeline: list[dict]) -> list[dict]:
    return [doc async for doc in db[collection].aggregate(pipeline)]


def format_int(value: int | None) -> str:
    return f"{value or 0:,}"


def format_value(value: object) -> str:
    if isinstance(value, int):
        return format_int(value)

    if isinstance(value, float):
        return f"{value:,.1f}"

    return str(value)


def html_column_label(column: str) -> str:
    label = STATS_COLUMN_LABELS.get(column, COLUMN_LABELS.get(column, column))

    if column == "interactions_per_session":
        return html.escape(label).replace(" ", "&nbsp;")

    return html.escape(label)


def html_bar_chart(rows: list[dict]) -> str:
    max_sessions = max((int(row.get("sessions") or 0) for row in rows), default=0)
    bar_rows = "".join(
        f"""
            <div class="bar-row">
                <span>{html.escape(format_value(row.get("month")))}</span>
                <div class="bar-track">
                    <div class="bar-fill" style="width: {(int(row.get("sessions") or 0) / max_sessions * 100) if max_sessions else 0:.2f}%"></div>
                </div>
                <span>{html.escape(format_value(row.get("sessions")))}</span>
            </div>
        """
        for row in rows
    )

    return f"""
        <div class="bar-chart" aria-label="Monthly sessions bar chart">
            {bar_rows}
        </div>
    """


def html_monthly_activity(rows: list[dict]) -> str:
    header_cells = "".join(
        f"<th>{html_column_label(column)}</th>"
        for column in ACTIVITY_COLUMNS
    )
    body_rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(format_value(row.get(column)))}</td>"
            for column in ACTIVITY_COLUMNS
        )
        + "</tr>"
        for row in rows
    )

    return f"""
        <section class="report-section">
            <h2>[ Monthly Activity ]</h2>
            {html_bar_chart(rows)}
            <div class="table-frame">
                <table class="monthly-activity-table">
                    <thead>
                        <tr>{header_cells}</tr>
                    </thead>
                    <tbody>
                        {body_rows}
                    </tbody>
                </table>
            </div>
        </section>
    """


def html_table(
    title: str,
    rows: Iterable[dict],
    columns: tuple[str, ...],
    table_class: str = "",
) -> str:
    header_cells = "".join(
        f"<th>{html_column_label(column)}</th>"
        for column in columns
    )
    body_rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(format_value(row.get(column)))}</td>"
            for column in columns
        )
        + "</tr>"
        for row in rows
    )

    return f"""
        <section class="report-section">
            <h2>[ {html.escape(title)} ]</h2>
            <div class="table-frame">
                <table class="{html.escape(table_class)}">
                    <thead>
                        <tr>{header_cells}</tr>
                    </thead>
                    <tbody>
                        {body_rows}
                    </tbody>
                </table>
            </div>
        </section>
    """


def html_dialogue_examples(title: str, rows: Iterable[dict]) -> str:
    turns = "".join(
        f"""
            <div class="dialogue-turn">
                <p><span class="speaker">User:</span><span>{html.escape(format_value(row.get("query")))}</span></p>
                <p><span class="speaker">Assistant:</span><span>{html.escape(format_value(row.get("assistant_response")))}</span></p>
            </div>
        """
        for row in rows
    )

    return f"""
        <section class="report-section">
            <h2>[ {html.escape(title)} ]</h2>
            <div class="dialogue">
                {turns}
            </div>
        </section>
    """


def intent_descriptions() -> tuple[dict, ...]:
    data = load_yaml(file_path=f"{assistant.__path__[0]}/intents.yaml")

    return tuple(
        {
            "intent": intent,
            "description": metadata["description"],
        }
        for intent, metadata in data["intents"].items()
    )


def html_intent_appendix(rows: Iterable[dict]) -> str:
    items = "".join(
        f"""
            <div class="appendix-item">
                <span>{html.escape(format_value(row.get("intent")))}</span>
                <p>{html.escape(format_value(row.get("description")))}</p>
            </div>
        """
        for row in rows
    )

    return f"""
        <section class="report-section">
            <h2>[ appendix :: intents ]</h2>
            <div class="appendix">
                {items}
            </div>
        </section>
    """


def html_sensitive_topic_appendix() -> str:
    data = load_yaml(file_path=f"{assistant.__path__[0]}/sensitive-topics.yaml")
    items = "".join(
        f"""
                <div class="appendix-item">
                    <span>{html.escape(format_value(topic.get("name")))}</span>
                    <p>{html.escape(format_value(topic.get("description")))}</p>
                </div>
        """
        for topic in data["sensitive-topics"]
    )

    return f"""
        <section class="report-section">
            <h2>[ appendix :: sensitive topics ]</h2>
            <div class="appendix">
                {items}
            </div>
        </section>
    """


def render_html_report(
    output_path: str,
    monthly_rows: list[dict],
    daily_rows: list[dict],
    domain_stats_rows: list[dict],
    intent_stats_rows: list[dict],
    sensitive_example_rows: list[dict],
) -> None:
    monthly_stats_rows = stats_rows(monthly_rows, MONTHLY_STATS_SOURCE_COLUMNS)
    daily_stats_rows = stats_rows(daily_rows, DAILY_STATS_SOURCE_COLUMNS)
    stats_columns = (
        "column",
        "total",
        "avg",
        "min",
        "max",
    )
    sections = "\n".join(
        (
            html_monthly_activity(monthly_rows),
            html_table("Monthly Stats", monthly_stats_rows, stats_columns, "monthly-stats-table"),
            html_table("Daily Stats", daily_stats_rows, stats_columns),
            html_table("Domain Stats", domain_stats_rows, CATEGORY_STATS_COLUMNS),
            html_table("Intent Stats", intent_stats_rows, INTENT_STATS_COLUMNS),
            html_dialogue_examples("Sensitive Interaction Example", sensitive_example_rows),
            html_intent_appendix(intent_descriptions()),
            html_sensitive_topic_appendix(),
        ),
    )

    document = f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LupAI Usage Report</title>
    <style>
        :root {{
            --bg: #050505;
            --text: #bdbdbd;
            --muted: #858585;
            --heading: #ffffff;
            --line: #2a2a2a;
        }}

        * {{
            box-sizing: border-box;
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
        }}

        body {{
            margin: 0;
            min-height: 100vh;
            color: var(--text);
            background: var(--bg);
            font-family: "JetBrains Mono", "Courier New", Courier, monospace;
            font-size: 14px;
            line-height: 1.5;
        }}

        main {{
            width: min(1040px, calc(100vw - 32px));
            margin: 0 auto;
            padding: 42px 0 72px;
        }}

        .masthead {{
            margin-bottom: 42px;
        }}

        h1 {{
            margin: 0 0 12px;
            color: var(--heading);
            font-size: clamp(2rem, 8vw, 6rem);
            font-weight: 400;
            letter-spacing: 0;
            text-transform: lowercase;
        }}

        .subtitle {{
            margin: 0;
            color: var(--muted);
            font-size: 0.95rem;
            white-space: pre-wrap;
        }}

        .report-section {{
            margin-top: 38px;
        }}

        h2 {{
            margin: 0 0 12px;
            color: var(--heading);
            font-size: 1rem;
            font-weight: 400;
            letter-spacing: 0;
            text-transform: lowercase;
        }}

        .table-frame {{
            overflow-x: auto;
            border-top: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
        }}

        .bar-chart {{
            border-top: 1px solid var(--line);
            padding: 10px 0 12px;
        }}

        .bar-row {{
            display: grid;
            grid-template-columns: 90px 1fr 52px;
            gap: 18px;
            align-items: center;
            padding: 5px 0;
            color: var(--text);
        }}

        .bar-row span:last-child {{
            color: var(--muted);
            text-align: right;
        }}

        .bar-track {{
            height: 10px;
            background: #171717;
        }}

        .bar-fill {{
            height: 100%;
            background: var(--text);
        }}

        table {{
            table-layout: fixed;
            width: 100%;
            min-width: 100%;
            border-collapse: collapse;
        }}

        .monthly-stats-table {{
            min-width: 980px;
        }}

        .monthly-stats-table th:first-child,
        .monthly-stats-table td:first-child {{
            width: 320px;
        }}

        th,
        td {{
            padding: 7px 14px;
            border-bottom: 1px solid var(--line);
            text-align: left;
            vertical-align: top;
            white-space: normal;
        }}

        th {{
            color: var(--muted);
            font-size: 0.88rem;
            font-weight: 400;
            text-transform: lowercase;
            white-space: nowrap;
        }}

        td {{
            color: var(--text);
            font-size: 0.88rem;
        }}

        .dialogue {{
            border-top: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
        }}

        .dialogue-turn {{
            padding: 14px 0;
            border-bottom: 1px solid var(--line);
        }}

        .dialogue-turn:last-child {{
            border-bottom: 0;
        }}

        .dialogue p {{
            display: grid;
            grid-template-columns: 100px 1fr;
            gap: 18px;
            color: var(--muted);
            margin: 0 0 14px;
            white-space: pre-wrap;
        }}

        .dialogue p:last-child {{
            margin-bottom: 0;
        }}

        .speaker {{
            color: var(--text);
            font-size: 0.88rem;
        }}

        .appendix {{
            border-top: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
        }}

        .appendix-item {{
            display: grid;
            grid-template-columns: minmax(180px, 0.35fr) 1fr;
            gap: 22px;
            padding: 9px 0;
            border-bottom: 1px solid var(--line);
        }}

        .appendix-item:last-child {{
            border-bottom: 0;
        }}

        .appendix-item span {{
            color: var(--text);
        }}

        .appendix-item p {{
            margin: 0;
            color: var(--muted);
        }}

        @media (max-width: 760px) {{
            main {{
                width: min(100vw - 24px, 1040px);
                padding-top: 28px;
            }}

            th,
            td {{
                padding-top: 6px;
                padding-bottom: 6px;
            }}

            .appendix-item {{
                grid-template-columns: 1fr;
                gap: 4px;
            }}
        }}

        @media print {{
            @page {{
                size: A4 landscape;
                margin: 0;
            }}

            body {{
                background: var(--bg);
            }}

            .table-frame {{
                overflow: visible;
            }}
        }}
    </style>
</head>
<body>
    <main>
        <header class="masthead">
            <h1>usage report</h1>
            <p class="subtitle">project  :: lupai meinsvwissen
content  :: activity / stats</p>
        </header>
        {sections}
    </main>
</body>
</html>
"""

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(document, encoding="utf-8")


def pdf_output_path(html_output: str, pdf_output: str | None) -> Path:
    if pdf_output:
        return Path(pdf_output)

    return Path(html_output).with_suffix(".pdf")


def is_pdf_converter_usable(candidate: str) -> bool:
    result = subprocess.run(
        (candidate, "--version"),
        capture_output=True,
        text=True,
        check=False,
    )

    return result.returncode == 0


def pdf_converter() -> str:
    converter = next(
        (
            candidate
            for candidate in PDF_CONVERTER_CANDIDATES
            if shutil.which(candidate) and is_pdf_converter_usable(candidate)
        ),
        None,
    )
    if converter is None:
        raise RuntimeError("PDF generation requires a usable google-chrome or chromium binary")

    return converter


def print_html_file(html_file: Path, print_dir: Path) -> Path:
    print_helpers = """
    <style>
        @media print {
            @page {
                size: 1540px 1200px;
                margin: 0;
            }

            .table-frame {
                overflow: visible !important;
            }
        }
    </style>
    <script>
        window.addEventListener("load", () => {
            const height = Math.ceil(document.documentElement.scrollHeight + 20);
            const style = document.createElement("style");
            style.textContent = `
                @media print {
                    @page {
                        size: 1540px ${height}px;
                        margin: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        });
    </script>
    """
    print_file = print_dir / html_file.name
    print_file.write_text(
        html_file.read_text(encoding="utf-8").replace("</head>", f"{print_helpers}</head>"),
        encoding="utf-8",
    )

    return print_file


def convert_html_to_pdf(html_output: str, pdf_output: str | None = None) -> Path:
    html_file = Path(html_output)
    output_file = pdf_output_path(html_output, pdf_output)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as profile_dir:
        print_file = print_html_file(html_file, Path(profile_dir))
        subprocess.run(
            (
                pdf_converter(),
                "--headless",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-component-extensions-with-background-pages",
                "--disable-gpu",
                "--disable-crash-reporter",
                "--disable-breakpad",
                "--no-first-run",
                "--no-pdf-header-footer",
                "--window-size=1500,1200",
                f"--user-data-dir={profile_dir}",
                f"--print-to-pdf={output_file}",
                str(print_file),
            ),
            check=True,
            env={**os.environ, "XDG_RUNTIME_DIR": profile_dir},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    return output_file


def stats_rows(rows: list[dict], columns: tuple[str, ...]) -> tuple[dict, ...]:
    numeric_columns = tuple(column for column in columns if column not in {"day", "month"})

    return tuple(
        {
            "column": COLUMN_LABELS.get(column, column),
            "total": sum(values),
            "avg": sum(values) / len(values) if values else 0,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
        }
        for column in numeric_columns
        for values in ([int(row.get(column) or 0) for row in rows],)
    )


async def main() -> None:
    args = parse_args()

    mongo_uri = build_mongo_uri(args)
    client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5_000)
    db = client[args.database]

    monthly_rows = await aggregate(db, STATES_COLLECTION, activity_pipeline("%Y-%m", "month"))
    daily_rows = await aggregate(db, STATES_COLLECTION, activity_pipeline("%Y-%m-%d", "day"))
    sensitive_example_rows = await aggregate(
        db,
        STATES_COLLECTION,
        session_examples_pipeline(SENSITIVE_EXAMPLES_SESSION_ID),
    )
    domain_stats_rows = await aggregate(
        db,
        STATES_COLLECTION,
        category_stats_pipeline("domain", "Out of domain"),
    )
    intent_stats_rows = await aggregate(db, STATES_COLLECTION, category_stats_pipeline("intent"))

    render_html_report(
        args.html_output,
        monthly_rows,
        daily_rows,
        domain_stats_rows,
        intent_stats_rows,
        sensitive_example_rows,
    )
    console.print(f"\n[bold bright_cyan]HTML report:[/bold bright_cyan] [grey70]{args.html_output}[/grey70]")
    pdf_report = convert_html_to_pdf(args.html_output, args.pdf_output)
    console.print(f"[bold bright_cyan]PDF report:[/bold bright_cyan] [grey70]{pdf_report}[/grey70]")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
