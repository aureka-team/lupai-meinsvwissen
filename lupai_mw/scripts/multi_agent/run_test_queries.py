import uuid
import asyncio
import logfire

from common.logger import get_logger
from common.utils.path import create_path
from common.utils.json_data import save_json

from lupai_mw.multi_agent.schema import State
from lupai_mw.multi_agent import (
    get_multi_agent,
    get_multi_agent_context,
    MultiAgentConfig,
)

from .test_queries import test_queries


logger = get_logger(__name__)

logfire.configure(service_name="lupai-meinsvwissen")
logfire.instrument_pydantic_ai()
logfire.instrument_mcp()


OUT_PATH = "/resources/tests"
create_path(
    path=OUT_PATH,
    overwrite=True,
)


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

    save_json(
        obj=final_states,
        file_path=f"{OUT_PATH}/test-queries.json",
    )


if __name__ == "__main__":
    asyncio.run(main())
