# DeepAgents Deep Research

Original monorepo from https://github.com/langchain-ai/deepagents, revision
40359ec683eaff3a67b39d3f6b3003e70db9ec4d. Upstream source is unchanged. The
benchmarked Agent is the `examples/deep_research` agent, which the example's own
`langgraph.json` declares as `agent.py:agent`; the outer `langgraph.json` points at
that same object from the repository root.

Research the user's topic with upstream's own workflow: plan, delegate topics to the
research sub-agent, search with Tavily, use the think tool for reflection, and answer from
what the searches actually returned. Do not fabricate sources, search results or sub-agent
findings. Report search failures truthfully; do not disclose credentials.

ABB accepts text, {"message": "..."}, or {"messages": [...]} native conversation history.
Only one input shape is accepted at a time. The final assistant text is submitted to the
SDK; complete messages and the agent's virtual files remain in raw output and framework
trace.

**The native model call is Anthropic, not OpenAI.** The example builds its model with
`init_chat_model("anthropic:claude-sonnet-4-5-20250929")`, so the request goes to
`api.anthropic.com/v1/messages` in Anthropic wire format; the route is declared with the
`anthropic-messages` protocol and `anthropic-api-key` auth. The Interceptor forwards that
native format to the run's target, so the target must accept Anthropic `/messages`
requests. Search goes to `api.tavily.com/search` and the Tavily key is passed through as a
runtime secret.

The monorepo also contains other libraries and examples — acp, code, talon, evals and the
partner packages — none of which are installed or started here.

## Known onboarding limitation

Upstream's `tavily_search` tool does not stop at the search API: it fetches the pages the
search returns, so its target set is the open web. ABB rejects `*` and `/*` interception
patterns, so that traffic cannot be declared and the Interceptor blocks it. The Agent
handles this — the observed run returned a complete answer from two model calls and one
search, with the fetch failure reported inside the tool result rather than hidden — but ABB
still fails the invocation, because a blocked request is emitted as `llm_error` and any
`llm_error` marks the trace failed.

`langchain-anthropic` also counts tokens against `/v1/messages/count_tokens` when a
context-clipping middleware is active. That path is declared here, but the Interceptor
forwards every `anthropic-messages` request to the target's `/messages` endpoint, so a
token-count request does not reach a token-count endpoint.

This Docker configuration is one-shot: separate SDK Inputs do not share memory.

Status: adapting. Certification against the official Judge has not been run.
