#!/bin/bash

set -euo pipefail

CXX="${CXX:-g++}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_RELEASE="$ROOT_DIR/build-release"
BUILD_DEBUG="$ROOT_DIR/build-debug"

mkdir -p "$BUILD_RELEASE" "$BUILD_DEBUG"

for src in "$ROOT_DIR"/*.cpp; do
    base="$(basename "$src" .cpp)"
    $CXX -std=gnu++20 -O3 -DNDEBUG -march=native -o "$BUILD_RELEASE/$base" "$src"
    $CXX -std=gnu++20 -g -O0 -o "$BUILD_DEBUG/$base" "$src"
done
