# LangGraph Fullstack Chatbot

Original fullstack template from https://github.com/langchain-ai/langgraph-fullstack-python,
revision 64c7af2aaddf3037e233f83b61fda621d5cd86cb. Upstream source and its own
`langgraph.json` are unchanged; ABB reaches the same `src/react_agent/graph.py:graph`
the template declares.

Answer the user's message directly. The upstream graph carries no tools and the upstream
system prompt ("You are a friendly, curious, geeky AI"). Do not fabricate tool results or
citations; report missing information truthfully and do not disclose credentials.

ABB accepts text, {"message": "..."}, or {"messages": [...]} native conversation history.
Only one input shape is accepted at a time. The final assistant text is submitted to the
SDK; complete messages remain in raw output and framework trace.

**The native model call is Anthropic, not OpenAI.** Upstream builds the graph with
`create_react_agent("anthropic:claude-3-5-haiku-latest")`, so the request goes to
`api.anthropic.com/v1/messages` in Anthropic wire format, and the route is declared with
the `anthropic-messages` protocol and `anthropic-api-key` auth. The Interceptor forwards
that native format to the run's target, so the configured target must accept Anthropic
`/messages` requests; an OpenAI-only upstream cannot serve this Agent. No provider rewrite
was added to Agent source to avoid that.

Upstream also ships a FastHTML app and an auth handler in the same package; neither is
started here.

This Docker configuration is one-shot: the template's graph has no checkpointer, so
separate SDK Inputs do not share memory. Explicit history may be supplied through
`messages`.

Status: adapting. Certification against the official Judge has not been run.
