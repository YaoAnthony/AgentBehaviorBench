# Multi-turn Agent Onboarding Batch

This page tracks a batch of Agents being onboarded from an external multi-turn
screening run. Each candidate was first verified outside AgentBench: 175 downloaded
Agent projects were each driven through a four-step conversation, and 35 of them
produced live, on-topic output at every step. Those 35 are the batch; the two Agents
already registered here (`company-research-agent`, `react-agent`) are two of them.

Every entry follows [How To Add Agent](../How%20To%20Add%20Agent.md) and the
[Agent unit layout](./Layout.md): upstream checkout under `agent/`, ABB configuration
outside it, native model traffic declared under `[llm_interception]`, and no provider
rewrite inside Agent source.

## Acceptance used per Agent

An entry is only committed after `python -m agentbench observe <agent-id>` runs the
real container against the real model and returns `Status: succeeded` with a non-empty
answer and at least one intercepted `llm_request`/`llm_response` pair. The observe
artifacts for each accepted Agent are recorded in the table below. `certify` against the
official Judge is a separate step and has not been run for this batch, so every entry
stays `status = "adapting"`.

## Environment used for the smoke runs

`OPENROUTER_BASE_URL` pointed at an OpenAI-compatible upstream and `OPENROUTER_MODEL`
at a tool-calling model; the Interceptor rewrote each Agent's native request to it. No
Agent source was changed to reach that upstream.

## Status

| # | Agent id | Upstream | Observe | Notes |
| --- | --- | --- | --- | --- |
| 01 | company-research-agent | guy-hartstein/company-research-agent | pre-existing | Registered before this batch |
| 02 | react-agent | langchain-ai/react-agent | pre-existing | Registered before this batch |
| 03 | autoresearch-agents | hwchase17/autoresearch-agents | succeeded | 3 chat completions, 103 OTel spans, calculator tool used |
| 04 | langchain-streamlit-template | hwchase17/langchain-streamlit-template | succeeded | 2 chat completions, 43 OTel spans; LangGraph pinned to the 0.2 line the checkout was written against |
| 05 | article-explainer | duartecaldascardoso/article-explainer | succeeded | 5-agent swarm, 47 OTel spans, 2.5k-char answer from the default explainer |
