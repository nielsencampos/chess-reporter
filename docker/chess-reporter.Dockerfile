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

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Copy Stockfish
ARG STOCKFISH_VERSION=sf_18
COPY --from=stockfish-builder /Stockfish-${STOCKFISH_VERSION}/src/stockfish /usr/local/bin/stockfish

# Copy virtualenv and source
COPY --from=builder /app/.venv .venv
COPY src/ src/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/src"
ENV STOCKFISH_PATH="/usr/local/bin/stockfish"

CMD ["python", "-m", "chess_reporter"]
