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
| 07 | ecommerce-recommender | bcefghj/multi-agent-ecommerce-system | succeeded | Native provider is MiniMax, not OpenAI; 3 chat completions, 43 OTel spans. Domain-locked pipeline |
| 06 | deep-research-agent | tarun7r/deep-research-agent | agent ok / ABB rejects | 20 chat completions, 13 Tavily searches, 607 OTel spans, 34k-char report; observe fails because upstream's crawl tool hits undeclared hosts and a blocked request is emitted as `llm_error` |
| 09 | decompai | louisgthier/decompai | succeeded | 1 streamed chat completion (499 chunks), 31 OTel spans, 5.3k-char answer; tiktoken cache warmed at build and Gradio analytics disabled so no undeclared egress |
| 13 | waku-agent | ShenSeanChen/waku-agent | succeeded | Not a LangGraph Agent: its own loop over the provider SDKs, driven through Waku(Settings()).respond(). 2 chat completions; framework spans absent by construction |
| 14 | event-deep-research | bernatsampera/event-deep-research | blocked, disabled | Upstream hardcodes reasoning="False" into every model; ChatOpenAI requires a dict, so its OpenAI path cannot construct a model. Registered with enabled = false |

## Not onboarded in this batch

The remaining screened Agents are listed with the specific thing that blocks them. None of
them is blocked by "it does not work" — each ran in the external screening — but ABB
deliberately runs one container with declared egress only, and these need more than that.
Where the external screening stubbed an Agent's tools to keep a conversation alive, that is
called out, because a stub is not an onboarding.

| Agent | Blocked on |
| --- | --- |
| TauricResearch/TradingAgents | Live market data (yfinance, finnhub) and a ticker-shaped input; a single screening run took over 20 minutes |
| bytedance/deer-flow | Application-scale configuration (config schema v38), Postgres/Redis, and Firecrawl/Serper credentials |
| langchain-ai/open-swe | Node toolchain, an e2b sandbox and GitHub App credentials |
| xerrors/Yuxi | Backend requires Postgres, Redis, Qdrant/Milvus and a sandbox provisioner |
| PurpleAILAB/Decepticon | Neo4j plus privileged Docker tooling inside the Agent container |
| simonlin1212/TradingAgents-astock | Market data services (sina, eastmoney, yfinance) and long runtimes |
| beenuar/AiSOC | Monorepo services: Postgres, Neo4j, Qdrant, Redis |
| 1517005260/graph-rag-agent | Neo4j with a prebuilt knowledge graph; the external screening only kept it alive by replacing its retrieval tool with a stub |
| olaxbt/ai-market-maker | Postgres and market fixtures |
| ginlix-ai/LangAlpha | Postgres, Redis, Playwright and Polygon/Serper/Firecrawl credentials |
| hrithikkoduri/WebRover | Browses arbitrary sites through Playwright; that egress cannot be declared, since ABB rejects wildcard host patterns |
| vinay-gatech/stocks-insights-ai-agent | Postgres, MongoDB and market data |
| nuglifeleoji/Options-Analytics-Agent | Requires POLYGON_API_KEY at import time; also ChromaDB |
| john-adeojo/graph_websearch_agent | SERPER_API_KEY |
| dhruvsinghal09/Adaptive-Rag | Qdrant, MongoDB and a Rust service |
| quarqlabs/argus | Composio account and credential |
| KodyKendall/LlamaBot | Postgres and Playwright |
| ai-forever/giga_agent | Postgres (Aegra), GigaChat credentials, e2b |
| skygazer42/Weaver | Postgres/pgvector, ChromaDB, e2b, Playwright |
| YUHAO-corn/manufacturing-agents | ChromaDB, MongoDB, Redis and market data |
| CopilotKit/scene-creator-copilot | Gemini-native wire format; needs a target that serves Gemini requests |

Two paths would move most of these forward, in ABB rather than in Agent source:

1. A documented way to run an Agent's non-model dependencies beside it — the
   `benchmark_mocks/` idea from the AgentFactory flow, extended to services the Agent
   dials over the network rather than imports.
2. Credentials for the third-party services these Agents natively use, supplied the same
   way `TAVILY_API_KEY` already is.

## Notes for ABB

Three things surfaced while onboarding this batch, all recorded against the Agent they were
found on:

- A blocked request is reported as `llm_error`, and `InterceptionTraceState.emit` treats any
  `llm_error` as a failed trace. An Agent that touches one undeclared host — even for a
  non-model purpose it recovers from — therefore fails `observe` with "Agent invocation
  completed without a matched LLM request/response trace", after every model call paired
  correctly. Seen on candidates 06 and 09.
- The blocked-request event carries no host, so diagnosing which dependency reached out
  means re-running with container logs. Adding the host and path to that event would make
  it a one-step fix.
- The adapter factory registers one framework, `langgraph`, and the observer factory is
  keyed to the same name. An Agent that does not use LangChain must still be registered as
  `langgraph` and must still install `langchain-core`, or its worker fails at import. Seen
  on candidate 13, which runs its own loop over the provider SDKs.
