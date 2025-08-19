import uuid
import asyncio
import logfire

import polars as pl

from pydantic import BaseModel, StrictStr

from common.logger import get_logger
from common.utils.path import create_path

from lupai_mw.multi_agent.schema import State, RelevantChunk
from lupai_mw.multi_agent import (
    get_multi_agent,
    get_multi_agent_context,
    MultiAgentConfig,
)

from .test_queries import test_queries, remove_extra_spaces, TestQuery


logger = get_logger(__name__)

logfire.configure(service_name="lupai-meinsvwissen")
logfire.instrument_pydantic_ai()
logfire.instrument_mcp()


OUT_PATH = "/resources/tests"
create_path(
    path=OUT_PATH,
    overwrite=True,
)


class MultiAgentOutput(BaseModel):
    sensitive_topic: StrictStr | None = None
    assistant_response: StrictStr | None = None
    relevant_chunks: list[RelevantChunk] = []


class Result(TestQuery):
    multi_agent_output: MultiAgentOutput


def get_row(result: Result) -> dict:
    return {
        "query": result.query,
        "expected_answer": result.expected_answer,
        "expected_sources": " | ".join(result.expected_sources),
        "sensitive_topic": result.multi_agent_output.sensitive_topic,
        "assistant_response": result.multi_agent_output.assistant_response,
        "relevant_chunks": "\n\n##########\n\n".join(
            f"{remove_extra_spaces(text=rc.text)} | {rc.url}"
            for rc in result.multi_agent_output.relevant_chunks
        ),
    }


async def main() -> None:
    multi_agent = get_multi_agent(with_memory=False)
    multi_agent.compile()
    multi_agent_context = get_multi_agent_context(config=MultiAgentConfig())

    final_states = []
    for test_query in test_queries:
        session_id = uuid.uuid4().hex
        logger.info(f"session_id: {session_id}")
        logger.info(f"test_query: {test_query.translations.query}")

        session_id = uuid.uuid4().hex
        state = await multi_agent.run(
            input_state=State(
                session_id=session_id,
                query=test_query.query,
            ),
            context=multi_agent_context,
            thread_id=session_id,
        )

        assert state is not None
        final_states.append(state.model_dump())

    reults = [
        Result(**(tq.model_dump() | {"multi_agent_output": fs}))
        for tq, fs in zip(test_queries, final_states)
    ]

    rows = map(get_row, reults)

    df = pl.from_dicts(data=rows)
    df.write_csv(file=f"{OUT_PATH}/test-queries.csv")


if __name__ == "__main__":
    asyncio.run(main())
