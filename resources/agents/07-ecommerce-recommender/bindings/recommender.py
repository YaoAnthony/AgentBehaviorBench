"""ABB request/answer boundary; the four-agent recommendation pipeline stays upstream."""
import asyncio
import uuid
from collections.abc import Mapping


class EcommerceRecommender:
    """Drive the compiled pipeline from python/orchestrator/graph.py."""

    def __init__(self):
        self._graph = None

    def _build(self):
        if self._graph is None:
            from orchestrator.graph import build_recommendation_graph
            self._graph = build_recommendation_graph()
        return self._graph

    def invoke(self, value, config=None):
        return asyncio.run(self.ainvoke(value, config))

    async def ainvoke(self, value, config=None):
        state = _state(value)
        result = await self._build().ainvoke(state, config=config)
        answer = _render(result)
        if not answer.strip():
            raise RuntimeError("Pipeline finished without any recommendation")
        return {"answer": answer,
                "products": [_plain(p) for p in result.get("final_products", [])],
                "marketing_copies": result.get("marketing_copies", []),
                "experiment_group": result.get("experiment_group")}

    def close(self):
        self._graph = None


def _state(value):
    """The pipeline takes a shopper, not a chat turn: the message becomes its scene query."""
    if isinstance(value, str):
        value = {"message": value}
    if not isinstance(value, Mapping):
        raise ValueError("Supply message text or a native pipeline state")
    if set(value) == {"message"}:
        message = value["message"]
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must be a non-empty string")
        return {"user_id": f"abb-{uuid.uuid4().hex[:8]}", "scene": "search",
                "num_items": 5, "context": {"query": message}}
    if "user_id" not in value:
        raise ValueError("A native pipeline state must carry user_id")
    return dict(value)


def _render(result):
    """Render the pipeline's own output — picked products and their copy — as text."""
    lines = []
    copies = {c.get("product_id"): c for c in result.get("marketing_copies", []) if isinstance(c, dict)}
    for product in result.get("final_products", []):
        plain = _plain(product)
        pid = plain.get("product_id") or plain.get("id")
        copy = copies.get(pid) or {}
        title = plain.get("title") or plain.get("name") or pid
        text = copy.get("copy") or copy.get("text") or ""
        lines.append(f"- {title}: {text}".rstrip(": "))
    return "\n".join(lines)


def _plain(item):
    dump = getattr(item, "model_dump", None)
    if callable(dump):
        return dump(mode="json")
    return item if isinstance(item, dict) else {"value": str(item)}


def create_graph():
    return EcommerceRecommender()
