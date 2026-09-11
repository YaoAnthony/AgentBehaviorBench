# Outer ABB image; the upstream checkout under agent/ is used unchanged.
# Upstream has no package metadata, so its pinned requirements are installed and the
# checkout is imported from PYTHONPATH as the `src` package it expects.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime:/opt/agent/agent \
    LLM_MODEL=gpt-4o-mini \
    TIKTOKEN_CACHE_DIR=/opt/agent/tiktoken \
    GRADIO_ANALYTICS_ENABLED=False \
    HF_HUB_DISABLE_TELEMETRY=1
WORKDIR /opt/agent
COPY agent/ ./agent/
RUN python -m pip install --no-cache-dir -r agent/requirements.txt 'opentelemetry-sdk>=1.30,<2' \
    && useradd --create-home --uid 10001 agent
# Upstream counts context with tiktoken, which downloads its encoding on first use.
# Warm that cache during the build so no run-time fetch is attempted; run-time egress is
# limited to the declared model route.
RUN python -c "import tiktoken; [tiktoken.get_encoding(n) for n in ('o200k_base', 'cl100k_base')]" \
    && chmod -R a+rX /opt/agent/tiktoken
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
