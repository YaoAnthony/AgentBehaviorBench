"""ABB message/result boundary; the agent itself stays the upstream load_agent() graph."""
import asyncio
import os
from collections.abc import Mapping


class StreamlitTemplateGraph:
    """Drive the upstream graph built by main.py:load_agent().

    main.py is a Streamlit script: importing it runs the page code. The import is
    done with a bare-mode Streamlit (no script run context), which logs warnings and
    returns inert widgets, so only load_agent() has an effect here.
    """

    def __init__(self):
        self._graph = None

    def _build(self):
        if self._graph is None:
            os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
            os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
            from main import load_agent
            self._graph = load_agent()
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
        return {"answer": answer, "messages": history}

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
    return StreamlitTemplateGraph()
