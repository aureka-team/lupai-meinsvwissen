import math

from typing import Any
from common.logger import get_logger

from cachetools import TTLCache
from pydantic_ai.tools import RunContext
from pydantic_ai.mcp import CallToolFunc, ToolResult

from fastmcp.tools import Tool
from fastmcp.server.middleware import Middleware, MiddlewareContext, CallNext


logger = get_logger(__name__)


TOOL_CALL_LIMIT = 5


# NOTE: Middleware on the client side.
async def process_tool_call(
    ctx: RunContext[Any],
    call_tool: CallToolFunc,
    tool_name: str,
    args: dict[str, Any],
) -> ToolResult:
    call_result = await call_tool(
        tool_name,
        args,
        {
            "deps": ctx.deps,
            "run_step": ctx.run_step,
        },
    )

    logger.info(
        {
            "tool": tool_name,
            "args": args,
        }
    )

    return call_result


# NOTE: Middleware on the server side.
# TODO: Can this approach be improved?
class ToolCallLimitMiddleware(Middleware):
    def __init__(self, limit: int = TOOL_CALL_LIMIT):
        self.limit = limit
        self.run_counts = TTLCache(
            maxsize=math.inf,
            ttl=300,
        )

    async def on_call_tool(
        self,
        context: MiddlewareContext,
        call_next: CallNext,
    ) -> Any:
        ctx = context.fastmcp_context
        assert ctx is not None

        meta = ctx.request_context.meta
        assert meta is not None

        session_id = ctx.session_id
        run_step = meta.model_dump()["run_step"]

        logger.info(
            {
                "session_id": session_id,
                "run_step": run_step,
            }
        )

        self.run_counts[session_id] = run_step
        return await call_next(context)

    async def on_list_tools(
        self,
        context: MiddlewareContext,
        call_next: CallNext,
    ) -> list[Tool]:
        ctx = context.fastmcp_context
        assert ctx is not None

        session_id = ctx.session_id
        run_step = self.run_counts.get(session_id)
        if run_step is None:
            return await call_next(context)

        if run_step > (self.limit - 1):
            logger.warning("Tool call limit reached. Hiding all tools.")
            return []

        return await call_next(context)
