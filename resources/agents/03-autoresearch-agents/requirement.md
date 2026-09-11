# Autoresearch Agent

Original autoresearch template from https://github.com/hwchase17/autoresearch-agents,
revision 552fd6a1bd607f6645cd4baba0a98858d62e8815. Upstream `agent.py` is unchanged;
`langgraph.json` was added beside it to declare the existing `build_agent()` entrypoint.

Accept a natural-language user request and answer it directly. Two native tools are
available — a calculator and a unit converter — and the upstream system prompt requires
using them for arithmetic or unit conversion rather than computing mentally. Do not
fabricate tool results or successful calls. Report missing information and tool errors
truthfully; do not disclose credentials.

ABB accepts text, {"message": "..."}, or {"messages": [...]} native conversation history.
Only one input shape is accepted at a time. The final assistant text is submitted to the
SDK; complete messages and the upstream `tools_used` accounting remain in raw output and
framework trace.

The native model client is `ChatOpenAI` on `api.openai.com/v1/chat/completions` with the
upstream model constant; ABB injects a temporary credential and selects the run model in
the Interceptor. No provider rewrite exists in Agent source.

This Docker configuration is one-shot: separate SDK Inputs do not share memory
automatically, and the upstream graph carries no checkpointer. Explicit history may be
supplied through `messages`.

Status: adapting. Certification against the official Judge has not been run.
