"""ABB topic/report boundary; planning, search and writing stay upstream."""
import asyncio
from collections.abc import Mapping


class DeepResearchGraph:
    """Drive the upstream workflow built by src/graph.py:create_research_graph()."""

    def __init__(self):
        self._graph = None

    def _build(self):
        if self._graph is None:
            from src.graph import create_memory_checkpointer, create_research_graph
            # Same checkpointer run_research() uses; the thread id comes from ABB config.
            self._graph = create_research_graph(checkpointer=create_memory_checkpointer())
        return self._graph

    def invoke(self, value, config=None):
        return asyncio.run(self.ainvoke(value, config))

    async def ainvoke(self, value, config=None):
        from src.state import ResearchState

        topic = _topic(value)
        state = await self._build().ainvoke(ResearchState(research_topic=topic), config=config)
        if state.get("error"):
            raise RuntimeError(f"Research workflow reported an error: {state['error']}")
        report = state.get("final_report")
        if not isinstance(report, str) or not report.strip():
            raise RuntimeError("Research workflow finished without a final report")
        return {"answer": report, "state": _plain(state)}

    def close(self):
        self._graph = None


def _topic(value):
    """Accept plain text, {"message": ...} or the native {"research_topic": ...}."""
    if isinstance(value, str):
        value = {"message": value}
    if not isinstance(value, Mapping) or set(value) not in ({"message"}, {"research_topic"}):
        raise ValueError("Supply either message text or a native research_topic")
    topic = value.get("message") or value.get("research_topic")
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("The research topic must be a non-empty string")
    return topic


def _plain(state):
    """Keep the accumulated state JSON-serialisable for the result envelope."""
    plain = {}
    for key, item in state.items():
        dump = getattr(item, "model_dump", None)
        if callable(dump):
            plain[key] = dump(mode="json")
        elif isinstance(item, list):
            plain[key] = [x.model_dump(mode="json") if hasattr(x, "model_dump") else x for x in item]
        else:
            plain[key] = item
    return plain


def create_graph():
    return DeepResearchGraph()
