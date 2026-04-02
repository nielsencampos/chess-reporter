# Python build stage
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY services/shared/pyproject.toml services/shared/pyproject.toml
COPY services/shared/src/ services/shared/src/
COPY services/chess-reporter/pyproject.toml services/chess-reporter/pyproject.toml
COPY services/chess-reporter/src/ services/chess-reporter/src/
COPY services/chess-reporter-jupyter-lab/pyproject.toml services/chess-reporter-jupyter-lab/pyproject.toml
COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-dev --package chess-reporter-jupyter-lab

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY services/chess-reporter/src/ services/chess-reporter/src/
COPY services/shared/src/ services/shared/src/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/services/chess-reporter/src:/app/services/shared/src"

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--notebook-dir=/app/notebooks", "--IdentityProvider.token="]
