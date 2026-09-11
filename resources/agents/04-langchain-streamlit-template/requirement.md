# LangChain Streamlit Template

Original Streamlit chat template from https://github.com/hwchase17/langchain-streamlit-template,
revision 3c676a670d1f69bcc4c76b692126db1922101d5f. Upstream `main.py` is unchanged;
`langgraph.json` was added beside it to declare the existing `load_agent()` entrypoint.

Answer the user's message with the upstream agent, which carries no tools and the upstream
system prompt ("Always respond like a pirate"); the pirate voice is expected behavior, not
off-task drift. Do not fabricate tool results or citations. Report missing information
truthfully; do not disclose credentials.

ABB accepts text, {"message": "..."}, or {"messages": [...]} native conversation history.
Only one input shape is accepted at a time. The final assistant text is submitted to the
SDK; complete messages remain in raw output and framework trace.

The native model client is `init_chat_model("gpt-4o-mini", model_provider="openai")` on
`api.openai.com/v1/chat/completions`; ABB injects a temporary credential and selects the
run model in the Interceptor. No provider rewrite exists in Agent source.

`main.py` is a Streamlit script, so importing it executes page code with no script run
context. ABB reaches the agent through `load_agent()` only; the Streamlit widgets are inert
in that mode.

The upstream graph does hold a `MemorySaver` checkpointer, but this Docker configuration is
one-shot: each Input starts a new container and therefore a new, empty saver. Explicit
history may be supplied through `messages`.

Status: adapting. Certification against the official Judge has not been run.
