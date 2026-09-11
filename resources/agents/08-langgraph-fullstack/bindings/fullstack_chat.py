"""ABB message/result boundary; the upstream compiled graph answers unchanged."""
import asyncio
from collections.abc import Mapping


class FullstackChatGraph:
    """Drive the module-level graph in src/react_agent/graph.py."""

    def invoke(self, value, config=None):
        return asyncio.run(self.ainvoke(value, config))

    async def ainvoke(self, value, config=None):
        from langchain_core.messages import AIMessage
        from react_agent.graph import graph

        messages = _messages(value)
        result = await graph.ainvoke({"messages": messages}, config=config)
        history = result.get("messages", [])
        last = history[-1] if history else None
        if not isinstance(last, AIMessage) or last.tool_calls:
            raise RuntimeError("Agent stopped without a final assistant response")
        answer = last.content if isinstance(last.content, str) else str(last.content)
        if not answer.strip():
            raise RuntimeError("Agent returned an empty final response")
        return {"answer": answer, "messages": history}

    def close(self):
        pass


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


def create_graph():
    return FullstackChatGraph()
