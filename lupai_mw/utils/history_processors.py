from pydantic_ai.messages import ModelMessage, ToolCallPart, ToolReturnPart


def is_tool_message(message: ModelMessage) -> bool:
    if isinstance(message, ToolCallPart):
        return True

    if isinstance(message, ToolReturnPart):
        return True

    return False


def filter_tool_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
    return [
        message for message in messages if not is_tool_message(message=message)
    ]
