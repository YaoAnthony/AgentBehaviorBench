# Waku Agent

Original agent from https://github.com/ShenSeanChen/waku-agent, revision
21486b39ca2b59cf3a616159139712f4bef0914c. Upstream source is unchanged.

Answer the user with upstream's own harness/loop/memory cycle, using its local-first tools
and memory. Do not claim to have used a tool, read a calendar entry or recalled a memory
that was not really retrieved; report tool failures truthfully and do not disclose
credentials.

**This Agent is not a LangGraph application.** It runs its own loop over the provider SDKs,
so the outer binding calls the same entry point its CLI uses —
`Waku(Settings()).respond(message)` — and returns the reply. The declared
`langgraph.json` entry documents that native object; no LangGraph graph exists. Because
the loop does not emit LangChain callbacks, framework spans are sparse for this Agent;
model traffic is still captured by the Interceptor.

The image also installs `langchain-core`, which the Agent itself does not use. ABB's
adapter factory registers one framework, `langgraph`, and its worker attaches a LangChain
callback to every Agent registered under it, so the import must resolve inside the image
even for an Agent that never calls LangChain.

ABB accepts text or {"message": "..."}. The reply is submitted to the SDK; the loop's
iteration count remains in raw output.

Upstream's default provider is Anthropic; the image selects its OpenAI path with
`WAKU_PROVIDER=openai`, which is a first-class upstream option, so the native request goes
to `api.openai.com/v1/chat/completions` with the credential from `OPENAI_API_KEY`. ABB
injects a temporary credential and selects the run model in the Interceptor. No provider
rewrite exists in Agent source.

Upstream keeps its state — memory database, calendar, outbox, traces — under `WAKU_HOME`,
which defaults to `.waku` beside the working directory. The ABB container root filesystem
is read-only, so the image points it at the container's tmpfs. Memory therefore starts
empty for every Input and does not persist across them; optional integrations (Telegram,
Notion, Google Calendar, Supabase) are unconfigured, so their egress is undeclared and
blocked.

This Docker configuration is one-shot: separate SDK Inputs do not share memory.

Status: adapting. Certification against the official Judge has not been run.
