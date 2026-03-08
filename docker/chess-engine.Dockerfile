FROM debian:bookworm-slim AS chess-engine-builder

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

ARG STOCKFISH_VERSION=sf_18
RUN curl -L https://github.com/official-stockfish/Stockfish/archive/refs/tags/${STOCKFISH_VERSION}.tar.gz \
    | tar xz && \
    cd Stockfish-${STOCKFISH_VERSION}/src && \
    make -j$(nproc) build ARCH=x86-64-modern

FROM debian:bookworm-slim

ARG STOCKFISH_VERSION=sf_18
COPY --from=chess-engine-builder /Stockfish-${STOCKFISH_VERSION}/src/stockfish /usr/local/bin/stockfish

RUN apt-get update && apt-get install -y ncat && rm -rf /var/lib/apt/lists/*

EXPOSE 8080
CMD ["sh", "-c", "ncat -lk -p 8080 -e /usr/local/bin/stockfish"]
