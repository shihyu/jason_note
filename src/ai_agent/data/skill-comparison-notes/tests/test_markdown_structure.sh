#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="$ROOT_DIR/docs"
TMP_DIR="$ROOT_DIR/tests/tmp"

mkdir -p "$TMP_DIR"

assert_file_exists() {
	local path="$1"
	if [[ ! -f "$path" ]]; then
		echo "缺少檔案: $path" >&2
		exit 1
	fi
}

assert_contains() {
	local path="$1"
	local pattern="$2"
	if ! rg -q --fixed-strings "$pattern" "$path"; then
		echo "檔案缺少必要內容: $path -> $pattern" >&2
		exit 1
	fi
}

assert_prompt_examples() {
	local path="$1"
	local count
	count="$(rg -c '^提示語句 [0-9]+：' "$path" || true)"
	if [[ "${count:-0}" -lt 3 ]]; then
		echo "提示語句分流示例不足 3 組: $path" >&2
		exit 1
	fi
}

README_FILE="$DOCS_DIR/README.md"

assert_file_exists "$README_FILE"

doc_count="$(find "$DOCS_DIR" -maxdepth 1 -name '*.md' | wc -l)"
if [[ "$doc_count" -ne 1 ]]; then
	echo "docs 目錄應只有 1 份 Markdown，實際為: $doc_count" >&2
	exit 1
fi

assert_contains "$README_FILE" "skill-creator"
assert_contains "$README_FILE" "skill-creator-advanced"
assert_contains "$README_FILE" "spec-organizer"
assert_contains "$README_FILE" "## 系統架構"
assert_contains "$README_FILE" "使用者需求"
assert_contains "$README_FILE" "互搶"
assert_contains "$README_FILE" "handoff"
assert_contains "$README_FILE" "| Skill | 核心工作 | 該接 | 不該接 | 主要交付物 |"
assert_contains "$README_FILE" '為什麼 `skill-creator-advanced` 是進階版'
assert_contains "$README_FILE" "避免互搶的方法"
assert_prompt_examples "$README_FILE"

echo "Markdown 結構檢查通過"
