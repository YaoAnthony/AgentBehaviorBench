# Outer ABB image; the upstream checkout under agent/ is used unchanged.
# Upstream ships requirements.txt without package metadata, so the checkout is imported
# from PYTHONPATH. LLM_PROVIDER and SEARCH_API select upstream's own OpenAI and Tavily
# paths; both are first-class options in its configuration.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/abb-runtime:/opt/agent/agent \
    LLM_PROVIDER=openai \
    LLM_MODEL=gpt-4o-mini \
    ACTIVITY_LLM_PROVIDER=openai \
    SEARCH_API=tavily
WORKDIR /opt/agent
COPY agent/ ./agent/
COPY constraints.txt ./constraints.txt
RUN python -m pip install --no-cache-dir -c constraints.txt -r agent/requirements.txt 'opentelemetry-sdk>=1.30,<2' \
    && useradd --create-home --uid 10001 agent
COPY .abb-runtime/ /opt/abb-runtime/
COPY bindings/ ./bindings/
COPY agent.toml ./agent.toml
USER agent
