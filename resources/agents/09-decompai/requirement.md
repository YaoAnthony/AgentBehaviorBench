# DecompAI Reverse Engineering Agent

Original agent from https://github.com/louisgthier/decompai, revision
0c2398c09e318be1bb6f6a52d13e572fac7c519b. Upstream source is unchanged;
`langgraph.json` was added beside it to declare the existing module-level `graph`.

Answer reverse-engineering questions and, when a binary is available, drive the upstream
tools — radare2, Ghidra scripts, a sandboxed shell and file management — to analyse it.
Report tool failures and missing binaries truthfully; never present an unexecuted
disassembly, decompilation or shell result as if it had run, and do not disclose
credentials.

ABB accepts text, {"message": "..."}, or {"messages": [...]} native conversation history.
Only one input shape is accepted at a time. The final assistant text is submitted to the
SDK; complete messages remain in raw output and framework trace.

The native model client is `ChatOpenAI` with no base URL override, so requests go to
`api.openai.com/v1/chat/completions` with the credential from `OPENAI_API_KEY`. ABB
injects a temporary credential and selects the run model in the Interceptor. Upstream also
supports a Gemini path, selected by putting "gemini" in `LLM_MODEL`; the image keeps the
OpenAI path, so only the OpenAI route is declared.

Upstream's analysis tools run inside a separate privileged runner container that this
configuration does not provide, and no Docker socket is mounted into the Agent container.
A tool call that needs the runner therefore fails, and the Agent is expected to say so
rather than invent results. Questions that need no binary are answered directly. Upstream
also applies an in-process rate limiter of one model request every five seconds, which
bounds how fast any run can go.

The checkout carried a `decompai_analysis_sessions` symlink pointing at a host
`/tmp` path left by an earlier local run. It is runtime state, not source, and ABB
refuses symlinks in a build context, so it is not vendored here. Upstream creates that
directory itself at `ANALYSIS_SESSIONS_ROOT`.

Two upstream dependencies reach the network on their own: tiktoken downloads its encoding
on first use, and Gradio posts usage analytics. Both are handled in the image rather than
declared as routes — the tiktoken cache is warmed during the build and Gradio analytics are
switched off — so run-time egress is limited to the declared model route.

This Docker configuration is one-shot: the checkpointer is created per container, so
separate SDK Inputs do not share memory.

Status: adapting. Certification against the official Judge has not been run.
