# Outer ABB image; the upstream monorepo under agent/ is used unchanged.
# The benchmarked Agent is the deep_research example, which imports the deepagents
# library from the same checkout.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime:/opt/agent/agent/examples/deep_research
WORKDIR /opt/agent
COPY agent/ ./agent/
RUN python -m pip install --no-cache-dir \
        ./agent/libs/deepagents ./agent/examples/deep_research \
        'opentelemetry-sdk>=1.30,<2' \
    && useradd --create-home --uid 10001 agent
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
