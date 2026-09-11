# Outer ABB image; the upstream checkout under agent/ is used unchanged.
# Upstream has a flat layout with no package metadata, so its declared requirements
# are installed and the checkout is imported from PYTHONPATH.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime:/opt/agent/agent \
    MODEL_PROVIDER=openai \
    MODEL_NAME=gpt-4o-mini \
    SUMMARIZATION_MODEL=gpt-4o-mini \
    SEARCH_PROVIDER=duckduckgo
WORKDIR /opt/agent
COPY agent/ ./agent/
RUN python -m pip install --no-cache-dir -r agent/requirements.txt 'opentelemetry-sdk>=1.30,<2' \
    && useradd --create-home --uid 10001 agent
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
