# Event Deep Research

Original agent from https://github.com/bernatsampera/event-deep-research, revision
b5b82fcbddb874d9beee1bca29aea362589efbf2. Upstream source and its own
`langgraph.json` are unchanged; ABB drives the same `supervisor` graph it declares.

Research one person and return a chronology of their life events, grouped into upstream's
own categories — early life, personal, career and legacy — built from what the searches
actually returned. Do not invent events, dates or sources; report gaps truthfully and do
not disclose credentials.

**This Agent is domain-locked.** Its input is a person to research, not a free-form
question, so ABB maps the incoming message to `person_to_research` and renders the
structured chronology as the final text.

Upstream's Configuration reads every field from the environment before the runnable
config, so `LLM_MODEL=openai:gpt-4o-mini` selects its OpenAI path; the default is Gemini.
The native model request therefore goes to `api.openai.com/v1/chat/completions` and ABB
injects a temporary credential and selects the run model in the Interceptor.

Two tool services are declared: `api.tavily.com/search` for search, with the Tavily key
passed through as a runtime secret, and `api.firecrawl.dev` for page scraping. No
Firecrawl credential is configured, so scrape calls are expected to be rejected by that
service; upstream treats crawled content as optional and continues from search results.
Declaring the route keeps that failure a normal tool response rather than blocked egress.

Upstream also wires a Langfuse callback; without Langfuse keys it stays inert, and its
egress is undeclared and blocked.

This Docker configuration is one-shot: separate SDK Inputs do not share memory.

## Known onboarding blocker

The Agent cannot start on its OpenAI path. `src/llm_service.py` builds every model through
`init_chat_model(configurable_fields=("model", "max_tokens", "api_key", "reasoning"))` and
then always sets `"reasoning": "False"` — the string. `ChatOpenAI` declares `reasoning` as
a dictionary, so construction fails before any request is made:

```
ValidationError 1 validation error for ChatOpenAI
reasoning
  Input should be a valid dictionary [type=dict_type, input_value='False', input_type=str]
```

That value is hardcoded, not read from configuration, so no ABB-side setting avoids it.
Upstream's default provider is Gemini, where this apparently goes unnoticed; running the
Agent as configured here would need either a target that serves Gemini requests or a change
in Agent source, and Agent source is not modified for onboarding.

The registry entry is therefore `enabled = false`. Everything else in this unit — binding,
routes, image — is complete and was exercised up to model construction.

Status: adapting, disabled. Certification against the official Judge has not been run.
