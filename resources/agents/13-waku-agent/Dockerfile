# Outer ABB image; the upstream package under agent/ is installed unchanged.
# WAKU_PROVIDER selects upstream's own OpenAI path (its default is anthropic), and
# WAKU_HOME moves the local-first state onto the container's writable tmpfs, because
# the ABB container root filesystem is read-only.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime \
    WAKU_PROVIDER=openai \
    WAKU_MODEL=gpt-4o-mini \
    WAKU_SMALL_MODEL=gpt-4o-mini \
    WAKU_HOME=/tmp/.waku
WORKDIR /opt/agent
COPY agent/ ./agent/
# langchain-core is not an Agent dependency. ABB's worker attaches a LangChain
# callback to every Agent registered with framework = "langgraph", which is the only
# framework its adapter factory knows, so the import has to resolve inside the image.
RUN python -m pip install --no-cache-dir ./agent 'opentelemetry-sdk>=1.30,<2' \
        'langchain-core<1.0' \
    && useradd --create-home --uid 10001 agent
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
