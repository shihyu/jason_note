#!/bin/bash

set -e

verlte() {
    [ "$1" = "$(echo -e "$1\n$2" | sort -V | head -n 1)" ]
}

verlt() {
    [ "$1" = "$2" ] && return 1 || verlte $1 $2
}

qemu=$1
shift
qemu_options="$*"

# 修正版本解析 - 只取數字部分
qemu_version_raw=$($qemu --version | head -n 1)
qemu_version=$(echo "$qemu_version_raw" | grep -oP '\d+\.\d+\.\d+' | head -n 1)

# Debug output
echo "DEBUG: QEMU: $qemu" >&2
echo "DEBUG: Raw version: $qemu_version_raw" >&2
echo "DEBUG: Parsed version: $qemu_version" >&2
echo "DEBUG: Original options: $qemu_options" >&2

if [[ "$qemu" == *"qemu-system-aarch64"* ]]; then
    # 根據實際支援的機器類型調整邏輯
    # 你的 QEMU 8.2.2 支援 raspi3b 但不支援 raspi3
    if verlt "$qemu_version" "6.2.0"; then
        echo "DEBUG: Version < 6.2.0, but your QEMU supports raspi3b, keeping raspi3b" >&2
        # 不做任何轉換，保持 raspi3b
    else
        echo "DEBUG: Version >= 6.2.0, using raspi3b" >&2
    fi
fi

echo "DEBUG: Final options: $qemu_options" >&2
echo "DEBUG: Executing: $qemu $qemu_options" >&2

exec $qemu $qemu_options
