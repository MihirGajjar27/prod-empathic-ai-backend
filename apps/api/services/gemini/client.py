import os
from dataclasses import dataclass
from typing import Any, Sequence
from services.gemini.schemas import normalize_tool_calls
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage


def get_client(*, api_key: str) -> Any:
    project = os.getenv("VERTEXAI_PROJECT")
    location = os.getenv("VERTEXAI_LOCATION")
    default_model_name = os.getenv("GEMINI_MODEL_KG") or "gemini-2.5-flash-lite"
    model_kwargs: dict[str, Any] = {
        "model_name": default_model_name,
        "location": location,
        "temperature": 0, # idk we should probably mess a bit with the termperature to allow fo rmore 'creative resps'?
        "max_retries": 2, # to prevent the loops
    }
    if project:
        model_kwargs["project"] = project

    chat_model = ChatVertexAI(**model_kwargs)
    return VertexAiGeminiClient(
        chat_model=chat_model,
        project=project,
        location=location,
        model_name=default_model_name,
        api_key_supplied=bool(api_key),
    )


async def generate_kg_tool_calls(
    *,
    client: Any,
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    tool_declarations: Sequence[Any],
) -> dict[str, Any]:
    tools = list(tool_declarations)
    if not tools:
        raise ValueError("tool_declarations must contain at least one LangChain tool schema")

    if hasattr(client, "with_model_name"):
        client = client.with_model_name(model_name)

    runnable = client.bind_forced_tools(tools)
    response = await runnable.ainvoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )

    return {
        "tool_calls": normalize_tool_calls(response),
        "raw_response": _serialize_response(response),
        "usage": _extract_usage_metadata(response),
    }


@dataclass(frozen=True)
class VertexAiGeminiClient:
    chat_model: Any
    project: str | None
    location: str
    model_name: str
    api_key_supplied: bool = False

    def bind_forced_tools(self, tools: Sequence[Any]) -> Any:
        tool_list = list(tools)
        if not hasattr(self.chat_model, "bind_tools"):
            raise RuntimeError("model doesn't support forced tools :(")
        return self.chat_model.bind_tools(tool_list, tool_choice="any")

    def with_model_name(self, model_name: str) -> "VertexAiGeminiClient":
        if not model_name or model_name == self.model_name:
            return self

        chat_model = ChatVertexAI(
            model_name=model_name,
            location=self.location,
            project=self.project,
            temperature=0,
            max_retries=2,
        )
        return VertexAiGeminiClient(
            chat_model=chat_model,
            project=self.project,
            location=self.location,
            model_name=model_name,
            api_key_supplied=self.api_key_supplied,
        )


def _resolve_tool_name(tool: Any) -> str:
    name = getattr(tool, "name", None)
    if isinstance(name, str) and name:
        return name
    if hasattr(tool, "__name__"):
        return str(tool.__name__)
    raise ValueError(f"couldn't resolve toolname for declr: {tool!r}")


def _serialize_response(response: Any) -> dict[str, Any]:
    if hasattr(response, "model_dump"):
        dumped = response.model_dump()
        if isinstance(dumped, dict):
            return dumped

    return {
        "content": getattr(response, "content", None),
        "tool_calls": getattr(response, "tool_calls", []),
        "additional_kwargs": getattr(response, "additional_kwargs", {}),
        "response_metadata": getattr(response, "response_metadata", {}),
    }


def _extract_usage_metadata(response: Any) -> dict[str, Any] | None:
    response_metadata = getattr(response, "response_metadata", None)
    if isinstance(response_metadata, dict):
        usage = response_metadata.get("usage_metadata")
        if isinstance(usage, dict):
            return usage

    usage_metadata = getattr(response, "usage_metadata", None)
    if isinstance(usage_metadata, dict):
        return usage_metadata

    return None
