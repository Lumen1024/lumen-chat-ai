from ctypes import ArgumentError
from enum import Enum
import json
import os
from typing import Callable, List, Dict, Any, Literal, Optional, Self, Union
from pydantic import BaseModel
import requests


class AiToolParam(BaseModel):
    name: str
    type: Literal["string", "number", "integer", "boolean", "array", "object"]
    description: str
    required: bool = True


class AiTool(BaseModel):
    name: str
    description: str
    parameters: List[AiToolParam]
    action: Callable[[dict[str, Any]], str]

    def parse(self) -> Dict[str, Any]:
        properties = {
            param.name: {"type": param.type, "description": param.description}
            for param in self.parameters
        }

        required_params = [param.name for param in self.parameters if param.required]

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required_params if required_params else [],
                },
            },
        }


# parent class of all messages
class AiMessage(BaseModel):
    def parce(self) -> dict[str, Any]:
        raise NotImplementedError()


class SystemMessage(AiMessage):
    content: str

    def parce(self) -> dict[str, Any]:
        return {"role": "system", "content": self.content}


class UserMessage(AiMessage):
    content: str
    name: str | None = None

    def parce(self) -> dict[str, Any]:
        result = {"role": "user", "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any]

    def parce(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "function",
            "function": {"name": self.name, "arguments": json.dumps(self.arguments)},
        }

    @staticmethod
    def from_dict(tool_call: dict[str, Any]) -> "ToolCall":
        id = tool_call["id"]
        name = tool_call["function"]["name"]
        args = tool_call["function"]["arguments"]

        return ToolCall(id=id, name=name, arguments=json.loads(args))


class AssistantMesage(AiMessage):
    content: str
    tools_calls: list[ToolCall]

    def parce(self) -> dict[str, Any]:
        result: dict[str, Any] = {"role": "assistant", "content": self.content}
        if len(self.tools_calls) > 0:
            result["tool_calls"] = [x.parce() for x in self.tools_calls]
        return result

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "AssistantMesage":
        message = data["choices"][0]["message"]
        content = message["content"]

        tool_calls = (
            [ToolCall.from_dict(x) for x in message["tool_calls"]]
            if (message.get("tool_calls"))
            else []
        )
        return AssistantMesage(content=content, tools_calls=tool_calls)


# Сообщение от инструмента (результат выполнения функции)
class ToolMessage(AiMessage):

    tool_call_id: str
    content: str

    def parce(self) -> dict[str, Any]:
        return {
            "role": "tool",
            "content": self.content,
            "tool_call_id": self.tool_call_id,
        }


AiResponse = Union[str, ToolCall]


def parce_ai_response(response: dict[str, Any]) -> AiResponse:
    if response["choices"][0]["message"]["tool_calls"]:
        return ToolCall.from_dict(response)
    else:
        return response["choices"][0]["message"]["content"]


def run_tool(tools: list[AiTool], tool_call: ToolCall) -> ToolMessage:
    tool = next(filter(lambda x: tool_call.name == x.name, tools), None)
    if not tool:
        return ToolMessage(
            tool_call_id=tool_call.id, content="Dont find Function with this name"
        )

    return ToolMessage(
        tool_call_id=tool_call.id, content=tool.action(tool_call.arguments)
    )


def chat_deepseek(
    messages: list[AiMessage],
    tools: list[AiTool] | None = None,
    response_format: Literal["text", "json"] = "text",
    max_tokens: int | None = None,
) -> AssistantMesage:

    token = os.getenv("DEEPSEEK_KEY")
    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    data = {
        "messages": [x.parce() for x in messages],
        "model": "deepseek-chat",
        "max_tokens": max_tokens,
        "response_format": {"type": response_format},
    }
    if tools:
        data["tools"] = [x.parse() for x in tools]

    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    result = AssistantMesage.from_dict(response.json())
    messages.append(result)

    while len(result.tools_calls) != 0:
        for tool_call in result.tools_calls:
            if not tools:
                raise ArgumentError
            messages.append(run_tool(tools, tool_call))
        result = chat_deepseek(messages, tools)
        messages.append(result)

    return result
