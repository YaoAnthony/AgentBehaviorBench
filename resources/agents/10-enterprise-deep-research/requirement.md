# Enterprise Deep Research

Original research agent from https://github.com/SalesforceAIResearch/enterprise-deep-research,
revision 59f8f2ad318e70b8615ddb036e3042036a924f2d. Upstream source and its own
`langgraph.json` are unchanged; ABB drives the same `frank_deep_researcher` graph the
project declares.

Take a research topic, run upstream's search-and-reflect loop over it, and return the
running summary it produces with the sources it actually gathered. Do not fabricate
sources, search results or citations; report search failures and gaps truthfully and do
not disclose credentials.

ABB accepts text, {"message": "..."}, or the native {"research_topic": "..."}. Only one
input shape is accepted at a time. The running summary is submitted to the SDK; the
gathered sources and research loop count remain in raw output and framework trace.

Upstream selects its provider from `LLM_PROVIDER` and its search backend from
`SEARCH_API`; the image picks the OpenAI and Tavily paths, both first-class upstream
options. The native model request therefore goes to `api.openai.com/v1/chat/completions`
and search to `api.tavily.com/search`, and both are declared. ABB injects a temporary
model credential and selects the run model in the Interceptor; the Tavily key is passed
through as a runtime secret. No provider rewrite exists in Agent source.

Upstream also ships optional visualization, code-interpreter and browser tools. They are
not configured here, so any egress they would need is undeclared and the Interceptor
blocks it.

Two upstream demo scripts, `math_client.py` and `math_client_new.py`, carry a hardcoded
OpenAI key as a default value. They are standalone MCP examples that nothing in `src/`
imports, and the onboarding rules forbid vendoring credentials, so they are not included in
this unit. The 4 MB upstream tech-report PDF is left out for size. Everything the graph
uses is unchanged.

The binding runs the graph at `recursion_limit` 100, the value upstream's own benchmark
harness uses; LangGraph's default of 25 ends the research loop before it reaches a stop
condition.

This Docker configuration is one-shot: separate SDK Inputs do not share memory.

## Verification status

`observe` completed: status `succeeded`, 31 model request/response pairs, 21 Tavily
searches, 511 OTel spans and a 36k-character report, with no blocked requests at all. An
earlier run stopped at LangGraph's default `recursion_limit` of 25; the binding now runs at
100, the value upstream's own benchmark harness uses.

Three configuration facts were needed, all outside Agent source: a
`constraints.txt` pinning the LangChain family below 1.0, `langchain-mcp-adapters` below
0.2 and `mcp` below 2 (upstream leaves those open and the new majors break its imports);
`LLM_PROVIDER`/`SEARCH_API` selecting upstream's OpenAI and Tavily paths; and the provider
named in the input state, because the graph falls back to Google Vertex when the state does
not carry one, which fails with `GOOGLE_CLOUD_PROJECT is not set`.

Status: adapting. Certification against the official Judge has not been run.
