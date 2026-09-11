"""ABB topic/report boundary; the research loop and its tools stay upstream."""
import asyncio
import os
from collections.abc import Mapping


class EnterpriseResearchGraph:
    """Drive the compiled graph exported by src/graph.py."""

    def invoke(self, value, config=None):
        return asyncio.run(self.ainvoke(value, config))

    async def ainvoke(self, value, config=None):
        from src.graph import graph
        from src.state import SummaryStateInput

        topic = _topic(value)
        # Upstream's own harnesses run this graph at recursion_limit 100; LangGraph's
        # default of 25 stops the research loop before it can finish.
        config = dict(config or {})
        config.setdefault("recursion_limit", 100)
        # The graph reads the provider from state and falls back to Google/Vertex when it
        # is absent; name the OpenAI path ABB declares a route for.
        state = await graph.ainvoke(
            SummaryStateInput(research_topic=topic,
                              llm_provider=os.environ.get("LLM_PROVIDER", "openai"),
                              llm_model=os.environ.get("LLM_MODEL", "gpt-4o-mini")),
            config=config)
        summary = state.get("running_summary")
        if not isinstance(summary, str) or not summary.strip():
            raise RuntimeError("Research loop finished without a running summary")
        return {"answer": summary,
                "sources_gathered": state.get("sources_gathered"),
                "research_loop_count": state.get("research_loop_count")}

    def close(self):
        pass


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


def create_graph():
    return EnterpriseResearchGraph()
