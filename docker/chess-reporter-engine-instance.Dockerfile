# Stockfish build stage
FROM debian:bookworm-slim AS stockfish-builder

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

ARG STOCKFISH_VERSION=sf_18
RUN curl -L https://github.com/official-stockfish/Stockfish/archive/refs/tags/${STOCKFISH_VERSION}.tar.gz \
    | tar xz && \
    cd Stockfish-${STOCKFISH_VERSION}/src && \
    make -j$(nproc) build ARCH=x86-64-modern

# Python build stage
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY services/chess-reporter-engine-instance/pyproject.toml services/chess-reporter-engine-instance/pyproject.toml
COPY services/chess-reporter-engine-instance/src/ services/chess-reporter-engine-instance/src/
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --package chess-reporter-engine-instance

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Copy Stockfish
ARG STOCKFISH_VERSION=sf_18
COPY --from=stockfish-builder /Stockfish-${STOCKFISH_VERSION}/src/stockfish /usr/local/bin/stockfish

# Copy virtualenv and source
COPY --from=builder /app/.venv .venv
COPY services/chess-reporter-engine-instance/src/ services/chess-reporter-engine-instance/src/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/services/chess-reporter-engine-instance/src"

ENV ENGINE_INSTANCE_PORT=1999

EXPOSE ${ENGINE_INSTANCE_PORT}

CMD ["sh", "-c", "uvicorn chess_reporter_engine_instance.setup:app --host 0.0.0.0 --port ${ENGINE_INSTANCE_PORT}"]
