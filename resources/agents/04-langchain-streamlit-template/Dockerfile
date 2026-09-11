# Outer ABB image; the upstream checkout under agent/ is installed unchanged.
# requirements.txt pins nothing, and upstream main.py calls create_react_agent with
# state_modifier=..., which LangGraph removed in 0.3. The image therefore reconstructs
# the 0.2 line the checkout was written against instead of editing Agent source.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime:/opt/agent/agent \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
WORKDIR /opt/agent
COPY agent/ ./agent/
RUN python -m pip install --no-cache-dir \
        'langgraph>=0.2.60,<0.3' 'langchain>=0.3,<0.4' 'langchain-openai>=0.2,<0.4' \
        streamlit streamlit-chat 'opentelemetry-sdk>=1.30,<2' \
    && useradd --create-home --uid 10001 agent
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
