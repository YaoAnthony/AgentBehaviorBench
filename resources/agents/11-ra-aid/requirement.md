# RA.Aid Research Agent

Original agent from https://github.com/ai-christianson/RA.Aid, revision
e71bb83dcfdf8796d41c746ad99bf4838d1d5914. Upstream source is unchanged.

Research the task the user gives and report what was actually found, using upstream's own
research loop and its file, search and shell tools. Do not claim to have read files,
executed commands or retrieved sources that were not really used; report tool failures and
missing information truthfully, and do not disclose credentials.

**The Agent's native interface is its CLI, not an importable graph.** RA.Aid builds its
agents internally and owns its own loop, tool approval and project state, so the outer
binding runs `python -m ra_aid --message <task> --research-only --provider openai
--model <model> --cowboy-mode --no-track-cost` and returns what that command prints.
`--research-only` keeps the run to a single research pass, and `--cowboy-mode` is what
makes it non-interactive. The declared `langgraph.json` entry documents that native entry
point; no LangGraph object is imported.

Because the Agent runs in its own process, LangChain callbacks do not reach the ABB worker,
so framework spans are not produced for this Agent. Model traffic is still captured: the
subprocess inherits the container's trust configuration and its requests go through the
Interceptor like any other.

ABB accepts text, {"message": "..."}, or the native {"task": "..."}. Only one input shape
is accepted at a time. The printed research report is submitted to the SDK; the exit code
and captured stderr remain in raw output.

The native model client is `langchain-openai` on `api.openai.com/v1/chat/completions`,
selected with upstream's own `--provider openai`; ABB injects a temporary credential and
selects the run model in the Interceptor. Upstream also supports Anthropic, Gemini, Bedrock,
Groq, Fireworks and Ollama providers, none of which are configured here.

Upstream checks `docs.ra-aid.ai/version.json` for a newer release when it starts. That is
declared as a tool route: left undeclared it is blocked, and one blocked request marks the
whole invocation's trace failed even when every model call pairs correctly.

RA.Aid writes project state next to its working directory and reads a home directory, and
the ABB container root filesystem is read-only, so the binding runs it under
`/tmp/ra-aid-workspace` with `HOME=/tmp/ra-aid-home` on the container's tmpfs. Upstream's
optional Tavily search is not configured, so that egress is undeclared and blocked.

## Known onboarding limitation

The Agent itself completes: observed runs produced 35k–76k character research reports from
9 to 15 model request/response pairs, with the version check served as a declared tool
call. ABB still fails the invocation, because one further request leaves the container to a
host that is not declared, and a single blocked request marks the whole trace failed.

Which host that is has not been pinned down. `ra_aid` makes exactly one outbound call of its
own — the version check, now declared — so the request comes from a dependency. ABB's
blocked-request event carries only a call id and the message "Undeclared network request
blocked", with no host or path, even though the Interceptor already has both in flow
metadata, so identifying it means re-running with container logs attached.

This Docker configuration is one-shot: each Input starts a new container with empty project
state, so separate SDK Inputs do not share memory.

Status: adapting. Certification against the official Judge has not been run.
