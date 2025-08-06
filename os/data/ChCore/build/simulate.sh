#!/bin/bash

set -e

basedir=$(dirname "$0")
# basedir should be /build directory

$basedir/../scripts/qemu/qemu_wrapper.sh \
    qemu-system-aarch64 -gdb tcp::1234 -machine raspi3b -nographic -serial null -serial mon:stdio -m size=1G -kernel $basedir/kernel.img
