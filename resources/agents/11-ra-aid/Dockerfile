# Outer ABB image; the upstream package under agent/ is installed unchanged.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime \
    TIKTOKEN_CACHE_DIR=/opt/agent/tiktoken \
    RA_AID_MODEL=gpt-4o-mini
WORKDIR /opt/agent
RUN apt-get update && apt-get install --no-install-recommends -y git ripgrep \
    && rm -rf /var/lib/apt/lists/*
COPY agent/ ./agent/
COPY constraints.txt ./constraints.txt
RUN python -m pip install --no-cache-dir -c constraints.txt ./agent 'opentelemetry-sdk>=1.30,<2' \
    && useradd --create-home --uid 10001 agent
# Warm the tiktoken cache during the build; run-time egress stays on the declared route.
RUN python -c "import tiktoken; [tiktoken.get_encoding(n) for n in ('o200k_base', 'cl100k_base')]" \
    && chmod -R a+rX /opt/agent/tiktoken
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
