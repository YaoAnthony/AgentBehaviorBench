# E-Commerce Recommendation Pipeline

Original multi-agent recommendation system from
https://github.com/bcefghj/multi-agent-ecommerce-system, revision
faf0fd8309c550426f3b2cce057dd4566e209e09. Upstream source is unchanged; `langgraph.json`
was added beside it to declare the existing `build_recommendation_graph()` entrypoint.

Run the upstream pipeline for one shopper: build a user profile, recall and rerank
products, filter them against inventory, then write marketing copy for the products that
survive. Recommend only products the pipeline actually produced, and do not invent
products, prices or stock levels. Report empty results truthfully.

**This Agent is domain-locked.** It is a recommendation pipeline, not a conversational
assistant: it always answers with product recommendations regardless of the topic it is
given. ABB maps the incoming message to the pipeline's own request shape — a generated
`user_id`, the `search` scene and the message as the scene query — and renders the
pipeline's picked products and their marketing copy as the final text. Native pipeline
state may also be supplied directly, in which case it must carry `user_id`.

The native model client is `langchain-openai` pointed at **MiniMax**: upstream settings
default to `https://api.minimax.chat/v1` with model `MiniMax-M1`, and the credential comes
from `ECOM_LLM_API_KEY`. That route is declared as the model route, so ABB injects a
temporary credential into the variable upstream already reads and selects the run model in
the Interceptor. The MiniMax API is OpenAI-compatible, so the `openai-chat` protocol plugin
decodes it. No provider rewrite exists in Agent source.

The checkout also carries Java and Go services and a docker-compose file. They are not
started here and the Python pipeline does not call them; product, profile and inventory
data come from upstream's in-process fixtures. Upstream imports redis and pymilvus clients
but reaches neither during a run, and no other egress is declared.

This Docker configuration is one-shot: the pipeline is compiled without a checkpointer, so
separate SDK Inputs do not share memory.

Status: adapting. Certification against the official Judge has not been run.
