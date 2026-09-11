# Adaptive RAG

Original agent from https://github.com/dhruvsinghal09/Adaptive-Rag, revision
6f6401e80687437064b669815d13242bf5703d37. Upstream source is unchanged;
`langgraph.json` was added beside it to declare the existing compiled graph `builder`.

Answer the user's question through upstream's adaptive route: classify the query, then
either retrieve from the vector store, search the web, or answer directly; grade retrieved
documents and rewrite the query when they do not support an answer. Do not present
retrieved or searched material that was not actually returned, and do not fabricate
citations. Report empty retrieval truthfully; do not disclose credentials.

ABB accepts text, {"message": "..."}, or {"messages": [...]} native conversation history.
Only one input shape is accepted at a time. The final assistant text is submitted to the
SDK; complete messages and the chosen route remain in raw output and framework trace.

The native model client is `langchain-openai` on `api.openai.com/v1/chat/completions`;
ABB injects a temporary credential and selects the run model in the Interceptor. The
web-search branch calls `api.tavily.com/search` and the Tavily key is passed through as a
runtime secret.

Upstream's Qdrant code is commented out in favour of an in-process FAISS store, so no
vector database service is needed; that store is built by an ingestion call this
configuration never makes, so the vector store starts empty and the adaptive route is
expected to fall to web search or a direct answer. The MongoDB chat history is likewise
unused here — this Docker configuration is one-shot, so separate SDK Inputs do not share
memory.

Upstream counts tokens with tiktoken, which fetches its encoding from
`openaipublic.blob.core.windows.net` on first use; that egress is not declared and the
Interceptor blocks it, so the image warms the cache at build time.

## Known onboarding blocker

The Agent builds its retriever with `OpenAIEmbeddings` before answering, so it calls
`api.openai.com/v1/embeddings`. That call cannot be declared:

- `protocol_plugin` must name a protocol the Interceptor registers — `json-http`,
  `openai-chat`, `openai-responses`, `anthropic-messages`, `gemini-content`. There is an
  `openai-embeddings` *wire* strategy, but no matching protocol, so an embeddings route
  fails validation.
- Even if it were routable, `OpenRouterTarget.prepare_request` sets `payload["model"]` to
  the single run model for every route, so a chat model name would be sent to an embeddings
  endpoint.

Left undeclared, the call is blocked with 403 and upstream reports
`Error initializing retriever`, which ends the run. The registry entry is therefore
`enabled = false`; everything else in this unit is complete and was exercised up to that
call.

Status: adapting, disabled. Certification against the official Judge has not been run.
