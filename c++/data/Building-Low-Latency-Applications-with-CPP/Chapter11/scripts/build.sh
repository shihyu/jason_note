#!/bin/bash

# TODO - point these to the correct binary locations on your system.
CMAKE=$(which cmake)
NINJA=$(which ninja)

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p $ROOT_DIR/cmake-build-release
$CMAKE -DCMAKE_BUILD_TYPE=Release -DCMAKE_MAKE_PROGRAM=$NINJA -G Ninja -S "$ROOT_DIR" -B $ROOT_DIR/cmake-build-release

$CMAKE --build $ROOT_DIR/cmake-build-release --target clean -j 4
$CMAKE --build $ROOT_DIR/cmake-build-release --target all -j 4

mkdir -p $ROOT_DIR/cmake-build-debug
$CMAKE -DCMAKE_BUILD_TYPE=Debug -DCMAKE_MAKE_PROGRAM=$NINJA -G Ninja -S "$ROOT_DIR" -B $ROOT_DIR/cmake-build-debug

$CMAKE --build $ROOT_DIR/cmake-build-debug --target clean -j 4
$CMAKE --build $ROOT_DIR/cmake-build-debug --target all -j 4
