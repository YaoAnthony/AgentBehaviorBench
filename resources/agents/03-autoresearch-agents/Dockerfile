# Outer ABB image; the upstream checkout under agent/ is installed unchanged.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime
WORKDIR /opt/agent
COPY agent/ ./agent/
# Upstream ships no dependency file; these are the imports agent.py declares.
RUN python -m pip install --no-cache-dir \
        'langchain-openai>=0.3,<1' 'langgraph>=0.3,<1' 'opentelemetry-sdk>=1.30,<2' \
    && useradd --create-home --uid 10001 agent
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
