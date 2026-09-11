# Outer ABB image; the upstream checkout under agent/ is used unchanged.
# Upstream's Configuration reads every field from the environment first, so LLM_MODEL
# selects its OpenAI path (its default is Gemini) without touching Agent source.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime:/opt/agent/agent \
    LLM_MODEL=openai:gpt-4o-mini \
    CHUNK_LLM_MODEL=openai:gpt-4o-mini
WORKDIR /opt/agent
COPY agent/ ./agent/
COPY constraints.txt ./constraints.txt
RUN python -m pip install --no-cache-dir -c constraints.txt ./agent 'opentelemetry-sdk>=1.30,<2' \
    && useradd --create-home --uid 10001 agent
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
