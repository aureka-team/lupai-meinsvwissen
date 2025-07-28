from typing import Any
from common.logger import get_logger
from pydantic import BaseModel, NonNegativeInt, PositiveInt

from pydantic_ai.mcp import CallToolFunc
from pydantic_ai.tools import RunContext


logger = get_logger(__name__)


TOOL_CALL_LIMIT = 5


class CallResult(BaseModel):
    call_result: Any | None = None
    used_calls: PositiveInt
    max_calls: PositiveInt
    remaining_calls: NonNegativeInt


async def process_tool_call(
    ctx: RunContext[Any],
    call_tool: CallToolFunc,
    tool_name: str,
    args: dict[str, Any],
) -> CallResult:
    if ctx.run_step > TOOL_CALL_LIMIT:
        return CallResult(
            used_calls=TOOL_CALL_LIMIT,
            max_calls=TOOL_CALL_LIMIT,
            remaining_calls=0,
        )

    call_result = await call_tool(
        tool_name,
        args,
        {
            "deps": ctx.deps,
        },
    )

    logger.info(
        {
            "tool": tool_name,
            "args": args,
        }
    )

    return CallResult(
        call_result=call_result,
        used_calls=ctx.run_step,
        max_calls=TOOL_CALL_LIMIT,
        remaining_calls=TOOL_CALL_LIMIT - ctx.run_step,
    )
