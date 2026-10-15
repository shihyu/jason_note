#!/usr/bin/env python3
"""Report display-column drift in fenced and indented Markdown diagrams under a tree."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SKILL_SCRIPTS = Path.home() / ".codex/skills/cjk-ascii-diagram/scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

from align import analyze  # noqa: E402
from wcwidth import wcswidth  # noqa: E402


OPEN_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
BOX_CORNERS = "┌┐└┘╔╗╚╝"
TABLE_BORDERS = "┌┬┐│┆╞╪╡└┴┘"


@dataclass(frozen=True)
class FenceBlock:
    first_line: int
    language: str
    lines: tuple[str, ...]
    closed: bool = True


@dataclass(frozen=True)
class Issue:
    line: int
    column: int
    message: str


def parse_fences(text: str) -> list[FenceBlock]:
    """Extract fenced blocks while retaining their original content line numbers."""
    lines = text.splitlines()
    blocks: list[FenceBlock] = []
    index = 0
    while index < len(lines):
        opening = OPEN_FENCE.match(lines[index])
        if opening is None or (opening.group(1)[0] == "`" and "`" in opening.group(2)):
            index += 1
            continue
        indent = len(lines[index]) - len(lines[index].lstrip(" "))
        marker = opening.group(1)
        language = opening.group(2).strip().split(" ")[0].lower()
        closing = re.compile(
            r"^ {0,3}" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}\s*$"
        )
        first_line = index + 2
        body: list[str] = []
        index += 1
        while index < len(lines) and closing.fullmatch(lines[index]) is None:
            line = lines[index]
            leading = len(line) - len(line.lstrip(" "))
            body.append(line[min(indent, leading) :])
            index += 1
        closed = index < len(lines)
        if closed:
            index += 1
        blocks.append(FenceBlock(first_line, language, tuple(body), closed))
    return blocks


def parse_indented_blocks(text: str) -> list[FenceBlock]:
    """Extract four-space or tab-indented code blocks outside fenced blocks."""
    lines = text.splitlines()
    fenced_lines: set[int] = set()
    for block in parse_fences(text):
        fenced_lines.update(
            range(block.first_line - 1, block.first_line - 1 + len(block.lines))
        )

    def unindent(line: str) -> str | None:
        if line.startswith("\t"):
            return line[1:]
        if line.startswith("    "):
            return line[4:]
        return None

    blocks: list[FenceBlock] = []
    index = 0
    while index < len(lines):
        if index in fenced_lines or unindent(lines[index]) is None:
            index += 1
            continue
        first_line = index + 1
        body: list[str] = []
        while index < len(lines) and index not in fenced_lines:
            content = unindent(lines[index])
            if content is None:
                break
            body.append(content)
            index += 1
        blocks.append(FenceBlock(first_line, "indented", tuple(body)))
    return blocks


def is_diagram(block: FenceBlock) -> bool:
    """Identify line-art blocks without interpreting ordinary prose or code."""
    content = "\n".join(block.lines)
    if any(char in content for char in BOX_CORNERS):
        return True
    if any(line.lstrip().startswith(("+---", "+===")) for line in block.lines):
        return True
    return any(char in content for char in "┬┴┼") and any(
        char in content for char in "├┤│"
    )


def _positions(line: str, borders: str) -> tuple[list[int], int]:
    columns = [
        wcswidth(line[:index])
        for index, char in enumerate(line)
        if char in borders
    ]
    return columns, wcswidth(line)


def _polars_issues(block: FenceBlock) -> list[Issue]:
    issues: list[Issue] = []
    lines = block.lines
    for top_index, top in enumerate(lines):
        if not (top.startswith("┌") and top.endswith("┐")):
            continue
        expected, width = _positions(top, TABLE_BORDERS)
        bottom_found = False
        for row_index in range(top_index + 1, len(lines)):
            row = lines[row_index]
            if not row.startswith(("│", "╞", "└")):
                break
            actual, row_width = _positions(row, TABLE_BORDERS)
            if actual != expected or row_width != width:
                issues.append(
                    Issue(
                        block.first_line + row_index,
                        actual[-1] if actual else 0,
                        f"table columns {actual}, width {row_width}; expected {expected}, width {width}",
                    )
                )
            if row.startswith("└"):
                bottom_found = True
                break
        if not bottom_found:
            issues.append(Issue(block.first_line + top_index, 0, "table has no closing border"))
    return issues


def analyze_block(block: FenceBlock) -> list[Issue]:
    """Return original-file locations of drift without modifying the diagram."""
    if not block.closed:
        return [Issue(block.first_line - 1, 0, "code block is not closed")]
    content = "\n".join(block.lines)
    if "╞" in content and "╪" in content and "┆" in content:
        return _polars_issues(block)
    _, found = analyze(content)
    return [Issue(block.first_line + line - 1, column, message) for line, column, message in found]


def scan_path(root: Path) -> tuple[int, int, list[tuple[Path, Issue]]]:
    """Scan all Markdown files beneath root and return file/block counts and issues."""
    files = [root] if root.is_file() else sorted(root.rglob("*.md"))
    file_count = 0
    diagram_count = 0
    issues: list[tuple[Path, Issue]] = []
    for path in files:
        if ".git" in path.parts:
            continue
        file_count += 1
        text = path.read_text(encoding="utf-8")
        blocks = sorted(
            (*parse_fences(text), *parse_indented_blocks(text)),
            key=lambda block: block.first_line,
        )
        for block in blocks:
            if not is_diagram(block):
                continue
            diagram_count += 1
            issues.extend((path, issue) for issue in analyze_block(block))
    return file_count, diagram_count, issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--check", action="store_true", help="exit 1 if any drift is reported")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not root.exists():
        parser.error(f"path does not exist: {root}")
    try:
        files, blocks, issues = scan_path(root)
    except (OSError, UnicodeDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    for path, issue in issues:
        relative = path.relative_to(root) if root.is_dir() else path.name
        print(f"{relative}:{issue.line}:{issue.column}: {issue.message}")
    print(f"Scanned {files} Markdown files, {blocks} diagram blocks, {len(issues)} findings")
    return int(args.check and bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
