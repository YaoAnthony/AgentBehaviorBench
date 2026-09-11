# Outer ABB image; the upstream checkout under agent/ is used unchanged.
# Upstream declares its dependencies in pyproject.toml but has a flat layout with
# several top-level directories, so `pip install ./agent` cannot build it. The
# declared runtime dependencies are installed directly and the checkout is imported
# from PYTHONPATH instead; the dev-only linter is left out.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime:/opt/agent/agent
WORKDIR /opt/agent
COPY agent/ ./agent/
RUN python -m pip install --no-cache-dir \
        langgraph langgraph-swarm langchain langchain_openai langchain_community \
        langchain_text_splitters langchain_ollama streamlit pypdf \
        'streamlit-pdf-viewer>=0.0.26' 'opentelemetry-sdk>=1.30,<2' \
    && useradd --create-home --uid 10001 agent
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
