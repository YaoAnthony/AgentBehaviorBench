# Article Explainer Swarm

Original multi-agent swarm from https://github.com/duartecaldascardoso/article-explainer,
revision 2cf067dc4b9158b03361c7b3e2544e067b75f1ae. Upstream source is unchanged;
`langgraph.json` was added beside it to declare the existing compiled swarm `app`.

Answer the user's request with the upstream swarm of five specialists — explainer
(default), summarizer, developer, analogy creator and vulnerability expert — handing
control between them through the upstream handoff tools when the request calls for a
different specialty. Do not fabricate handoffs, tool results or citations. Report missing
information truthfully; do not disclose credentials.

ABB accepts text, {"message": "..."}, or {"messages": [...]} native conversation history.
Only one input shape is accepted at a time. The final assistant text is submitted to the
SDK; complete messages and the swarm's `active_agent` remain in raw output and framework
trace.

The native model client is `init_chat_model("openai:gpt-4.1-mini", api_key=OPENAI_API_KEY)`
on `api.openai.com/v1/chat/completions`; ABB injects a temporary credential and selects the
run model in the Interceptor. Upstream falls back to a local Ollama model only when
`OPENAI_API_KEY` is absent, which never happens under ABB.

This Docker configuration is one-shot: the swarm is compiled without a checkpointer, so
separate SDK Inputs do not share memory. Explicit history may be supplied through
`messages`.

Status: adapting. Certification against the official Judge has not been run.
