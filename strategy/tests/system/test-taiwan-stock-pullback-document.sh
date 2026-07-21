#!/usr/bin/env bash
set -euo pipefail

strategy_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
summary_file="${strategy_dir}/../SUMMARY.md"
article_file="${strategy_dir}/台股回檔警訊與反彈選股策略.md"

test ! -e "${strategy_dir}/test.md"
test -f "${article_file}"

test "$(rg -c '^# ' "${article_file}")" -eq 1
rg -q '^# 台股回檔警訊與反彈選股策略$' "${article_file}"
rg -q '^## 避開大回檔的三個警訊$' "${article_file}"
rg -q '^## 大盤止跌回穩的三個訊號$' "${article_file}"
rg -q '^## 現階段的反彈選股策略$' "${article_file}"

if rg -n '簡體|台灣|台、日|級別|K線|鐿鈦/環宇|[^ ]ABF|ABF[^ ]' "${article_file}"; then
    echo "文件仍含待修正的用字或中英文間距" >&2
    exit 1
fi

rg -Fq -- '- [台股回檔警訊與反彈選股策略](strategy/台股回檔警訊與反彈選股策略.md)' "${summary_file}"
! rg -q 'strategy/test\.md' "${summary_file}"

if rg -n '!\[[^]]*\]\(https?://' "${article_file}"; then
    echo "文件仍引用遠端圖片" >&2
    exit 1
fi

echo "台股回檔警訊與反彈選股策略文件驗證通過"
