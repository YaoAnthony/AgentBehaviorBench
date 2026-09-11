"""ABB message/result boundary; the graph, tools and prompt remain upstream."""
import asyncio
from collections.abc import Mapping


class AutoresearchGraph:
    """Drive the upstream ReAct graph built by agent.py:build_agent()."""

    def __init__(self):
        self._graph = None

    def _build(self):
        if self._graph is None:
            from agent import build_agent
            self._graph = build_agent()
        return self._graph

    def invoke(self, value, config=None):
        return asyncio.run(self.ainvoke(value, config))

    async def ainvoke(self, value, config=None):
        from langchain_core.messages import AIMessage

        messages = _messages(value)
        result = await self._build().ainvoke({"messages": messages}, config=config)
        history = result.get("messages", [])
        last = history[-1] if history else None
        if not isinstance(last, AIMessage) or last.tool_calls:
            raise RuntimeError("Agent stopped without a final assistant response")
        answer = last.content if isinstance(last.content, str) else str(last.content)
        if not answer.strip():
            raise RuntimeError("Agent returned an empty final response")
        return {"answer": answer, "messages": history, "tools_used": _tools_used(history)}

    def close(self):
        self._graph = None


def _messages(value):
    """Accept plain text, {"message": ...} or a native {"messages": [...]} history."""
    if isinstance(value, str):
        value = {"message": value}
    if not isinstance(value, Mapping) or set(value) not in ({"message"}, {"messages"}):
        raise ValueError("Supply either message text or a native messages list")
    if "message" in value:
        if not isinstance(value["message"], str) or not value["message"].strip():
            raise ValueError("message must be a non-empty string")
        return [{"role": "user", "content": value["message"]}]
    messages = value["messages"]
    if not isinstance(messages, (list, tuple)) or not messages:
        raise ValueError("messages must be a non-empty list")
    return list(messages)


def _tools_used(history):
    """Same tool accounting the upstream eval harness reports."""
    names = []
    for message in history:
        for call in getattr(message, "tool_calls", None) or ():
            names.append(call["name"])
    return names


def create_graph():
    return AutoresearchGraph()
