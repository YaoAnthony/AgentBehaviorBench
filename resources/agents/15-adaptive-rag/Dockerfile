# Outer ABB image; the upstream checkout under agent/ is used unchanged.
# Upstream has no package metadata, so its pinned requirements are installed and the
# checkout is imported from PYTHONPATH as the `src` package it expects.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime:/opt/agent/agent \
    TIKTOKEN_CACHE_DIR=/opt/agent/tiktoken
WORKDIR /opt/agent
COPY agent/ ./agent/
RUN python -m pip install --no-cache-dir -r agent/requirements.txt 'opentelemetry-sdk>=1.30,<2' \
    && useradd --create-home --uid 10001 agent
# Upstream counts tokens with tiktoken, which downloads its encoding on first use and is
# blocked at run time; warm the cache during the build instead.
RUN python -c "import tiktoken; [tiktoken.get_encoding(n) for n in ('cl100k_base', 'o200k_base')]" \
    && chmod -R a+rX /opt/agent/tiktoken
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
