"""ABB person/timeline boundary; the supervisor graph and its sub-graphs stay upstream."""
import asyncio
import json
from collections.abc import Mapping


class EventTimelineGraph:
    """Drive the compiled supervisor graph exported by src/graph.py."""

    def invoke(self, value, config=None):
        return asyncio.run(self.ainvoke(value, config))

    async def ainvoke(self, value, config=None):
        from src.graph import graph

        person = _person(value)
        state = await graph.ainvoke({"person_to_research": person}, config=config)
        answer = _render(state)
        if not answer.strip():
            raise RuntimeError("Research finished without any events")
        return {"answer": answer,
                "structured_events": _plain(state.get("structured_events")),
                "used_domains": state.get("used_domains")}

    def close(self):
        pass


def _person(value):
    """Accept plain text, {"message": ...} or the native {"person_to_research": ...}."""
    if isinstance(value, str):
        value = {"message": value}
    if not isinstance(value, Mapping) or set(value) not in ({"message"}, {"person_to_research"}):
        raise ValueError("Supply either message text or a native person_to_research")
    person = value.get("message") or value.get("person_to_research")
    if not isinstance(person, str) or not person.strip():
        raise ValueError("The person to research must be a non-empty string")
    return person


def _render(state):
    """Render the chronology the graph produced as text."""
    events = _plain(state.get("structured_events"))
    if isinstance(events, (dict, list)) and events:
        return json.dumps(events, ensure_ascii=False, indent=2)
    summary = state.get("events_summary")
    return summary if isinstance(summary, str) else ""


def _plain(value):
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        return dump(mode="json")
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


def create_graph():
    return EventTimelineGraph()
