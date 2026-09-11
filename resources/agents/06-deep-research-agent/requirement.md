# Deep Research Agent

Original research workflow from https://github.com/tarun7r/deep-research-agent,
revision a974b4cd03436d37d459170f2a524dace13d8482. Upstream source is unchanged;
`langgraph.json` was added beside it to declare the existing `create_research_graph()`
entrypoint.

Take a research topic, plan searches for it, run those searches, synthesize the findings
and return a complete markdown report with citations drawn from the pages actually
retrieved. Do not fabricate sources, search results or citations, and do not present
unretrieved material as sourced. Report search failures and missing information truthfully;
do not disclose credentials.

ABB accepts text, {"message": "..."}, or the native {"research_topic": "..."}. Only one
input shape is accepted at a time. The final report is submitted to the SDK; the complete
accumulated workflow state — plan, search results, key findings, report sections — remains
in raw output and framework trace.

Upstream selects its model provider from `MODEL_PROVIDER`; the image sets the OpenAI path,
which is a first-class upstream option, so the native client is `langchain-openai` on
`api.openai.com/v1/chat/completions`. ABB injects a temporary credential and selects the
run model in the Interceptor. No provider rewrite exists in Agent source.

Search runs through the upstream Tavily provider, selected with `SEARCH_PROVIDER`, and
`api.tavily.com/search` is the one declared tool route. Upstream also tries to fetch the
pages its searches return; that traffic has no bounded host set, so it is not declared and
the Interceptor blocks it. Upstream treats page content as optional and falls back to
search snippets, which is the behavior benchmarked here.

This Docker configuration is one-shot: the in-memory checkpointer is created per container,
so separate SDK Inputs do not share memory.

## Known onboarding limitation

Upstream also exposes a page-content extraction tool, and the model calls it on whatever
URLs a search returns. That target set is the open web, and ABB rejects `*` / `/*`
interception patterns, so the traffic cannot be declared and the Interceptor blocks it
with 403. The Agent itself handles that: the observed run produced a complete 34k-character
report from 20 model calls and 13 Tavily searches.

ABB still fails the invocation. A blocked request is emitted as `llm_error`, and
`InterceptionTraceState.emit` treats any `llm_error` as a failed trace, so
`observe` ends with "Agent invocation completed without a matched LLM request/response
trace" even though all 20 model request/response pairs completed and were captured. Any
Agent that browses arbitrary URLs will hit this, so it is recorded here rather than worked
around by declaring `required = false`, which would misdescribe a model-backed Agent.

Status: adapting. Certification against the official Judge has not been run.
