# Outer ABB image; the upstream checkout under agent/ is used unchanged.
# The Python service lives in agent/python and is imported from PYTHONPATH; the Java and
# Go siblings in the same checkout are not started, and the Python pipeline does not call
# them.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime:/opt/agent/agent/python
WORKDIR /opt/agent
COPY agent/ ./agent/
RUN python -m pip install --no-cache-dir -r agent/python/requirements.txt \
        'opentelemetry-sdk>=1.30,<2' \
    && useradd --create-home --uid 10001 agent
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
