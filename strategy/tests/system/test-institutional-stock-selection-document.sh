#!/usr/bin/env bash
set -euo pipefail

strategy_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
summary_file="${strategy_dir}/../SUMMARY.md"
article_file="${strategy_dir}/法人選股與資產配置策略指南.md"

test ! -e "${strategy_dir}/test.md"
test -f "${article_file}"

test "$(rg -c '^# ' "${article_file}")" -eq 1
rg -q '^# 法人選股與資產配置策略指南$' "${article_file}"
rg -q '^## 面對籌碼集中的盤勢：法人的核心思維$' "${article_file}"
rg -q '^## 法人選股的三大原則$' "${article_file}"

if rg -n 'Studio 面板|需要我|為您生成|為您做|Entry Barrier|well-known|Portfolio|YoY|Beat Guidance|台灣公司' "${article_file}"; then
    echo "文件仍含對話式殘文、未在地化用語或簡體慣用詞" >&2
    exit 1
fi

rg -Fq -- '- [法人選股與資產配置策略指南](strategy/法人選股與資產配置策略指南.md)' "${summary_file}"
! rg -q 'strategy/test\.md' "${summary_file}"

if rg -n '!\[[^]]*\]\(https?://' "${article_file}"; then
    echo "文件仍引用遠端圖片" >&2
    exit 1
fi

while IFS= read -r image_path; do
    test -f "${strategy_dir}/${image_path}"
done < <(rg -o '!\[[^]]*\]\((images/[^)]+)\)' -r '$1' "${article_file}" || true)

echo "法人選股與資產配置策略指南文件驗證通過"
