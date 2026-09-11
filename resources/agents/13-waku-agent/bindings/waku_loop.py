"""ABB message/result boundary; the harness, loop and memory stay upstream.

Waku is not a LangGraph application: it runs its own harness/loop/memory cycle over
the provider SDKs. The binding calls the same entry point its CLI uses,
`Waku(Settings()).respond(message)`, and returns the reply. Model calls still leave
the container as native provider traffic, so the Interceptor captures them.
"""
import asyncio
import os
from collections.abc import Mapping


class WakuAgent:
    def __init__(self):
        self._agent = None

    def _build(self):
        if self._agent is None:
            os.makedirs(os.environ.get("WAKU_HOME", "/tmp/.waku"), exist_ok=True)
            from waku.app import Waku
            from waku.config import Settings
            self._agent = Waku(Settings())
        return self._agent

    def invoke(self, value, config=None):
        return asyncio.run(self.ainvoke(value, config))

    async def ainvoke(self, value, config=None):
        message = _message(value)
        # Build and run in the same worker thread: upstream opens its SQLite state with
        # check_same_thread=True, so the connection cannot cross threads.
        return await asyncio.to_thread(self._run, message)

    def _run(self, message):
        result = self._build().respond(message)
        answer = getattr(result, "reply", "") or ""
        if not answer.strip():
            raise RuntimeError("Waku returned an empty reply")
        return {"answer": answer, "iterations": getattr(result, "iterations", None)}

    def close(self):
        self._agent = None


def _message(value):
    """Accept plain text or {"message": ...}."""
    if isinstance(value, str):
        value = {"message": value}
    if not isinstance(value, Mapping) or set(value) != {"message"}:
        raise ValueError("Supply message text")
    message = value["message"]
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must be a non-empty string")
    return message


def create_graph():
    return WakuAgent()
