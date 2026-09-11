"""ABB message/result boundary; the five-agent swarm stays upstream."""
import asyncio
from collections.abc import Mapping


class ArticleExplainerSwarm:
    """Drive the compiled swarm exported by explainer/graph.py."""

    def __init__(self):
        self._graph = None

    def _build(self):
        if self._graph is None:
            from explainer.graph import app
            self._graph = app
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
            raise RuntimeError("Swarm stopped without a final assistant response")
        answer = last.content if isinstance(last.content, str) else str(last.content)
        if not answer.strip():
            raise RuntimeError("Swarm returned an empty final response")
        return {"answer": answer, "messages": history,
                "active_agent": result.get("active_agent")}

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


def create_graph():
    return ArticleExplainerSwarm()
