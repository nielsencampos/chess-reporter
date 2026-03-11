#!/usr/bin/env bash
# Builds Stockfish from source and installs it to bin/stockfish.
# Works on Linux (x86_64, arm64) and macOS (Intel, Apple Silicon).

set -euo pipefail

VERSION="18"
BIN_DIR="bin"
STOCKFISH_PATH="$BIN_DIR/stockfish"

if [ -f "$STOCKFISH_PATH" ]; then
    echo "Stockfish already installed at $STOCKFISH_PATH"
    exit 0
fi

mkdir -p "$BIN_DIR"

# Detect CPU architecture for the right Makefile target
ARCH=$(uname -m)
case "$ARCH" in
    x86_64)  ARCH_TARGET="x86-64-avx2" ;;
    arm64|aarch64) ARCH_TARGET="apple-silicon" ;;
    *)       ARCH_TARGET="x86-64" ;;
esac

# macOS: clang is the default; Linux: prefer g++ if available
if command -v g++ &>/dev/null; then
    COMPILER="g++"
else
    COMPILER="clang++"
fi

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Downloading Stockfish $VERSION source..."
curl -fsSL "https://github.com/official-stockfish/Stockfish/archive/refs/tags/sf_${VERSION}.tar.gz" \
    | tar -xz -C "$TMP_DIR"

SRC_DIR=$(ls -d "$TMP_DIR"/Stockfish-*/src)

echo "Building Stockfish (arch=$ARCH_TARGET, compiler=$COMPILER)..."
make -C "$SRC_DIR" -j"$(nproc 2>/dev/null || sysctl -n hw.logicalcpu)" \
    profile-build \
    ARCH="$ARCH_TARGET" \
    CXX="$COMPILER"

mv "$SRC_DIR/stockfish" "$STOCKFISH_PATH"
chmod +x "$STOCKFISH_PATH"

echo "Stockfish installed at $STOCKFISH_PATH"
