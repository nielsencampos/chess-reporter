# Python build stage
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY services/chess-reporter-engine-master/pyproject.toml services/chess-reporter-engine-master/pyproject.toml
COPY services/chess-reporter-engine-master/src/ services/chess-reporter-engine-master/src/
COPY services/chess-reporter-schemas/pyproject.toml services/chess-reporter-schemas/pyproject.toml
COPY services/chess-reporter-schemas/src/ services/chess-reporter-schemas/src/
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --package chess-reporter-engine-master

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Copy virtualenv and source
COPY --from=builder /app/.venv .venv
COPY services/chess-reporter-engine-master/src/ services/chess-reporter-engine-master/src/
COPY services/chess-reporter-schemas/src/ services/chess-reporter-schemas/src/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/services/chess-reporter-engine-master/src:/app/services/chess-reporter-schemas/src"

ENV ENGINE_MASTER_PORT=1000

EXPOSE ${ENGINE_MASTER_PORT}

CMD ["sh", "-c", "uvicorn chess_reporter_engine_master.setup:app --host 0.0.0.0 --port ${ENGINE_MASTER_PORT}"]
