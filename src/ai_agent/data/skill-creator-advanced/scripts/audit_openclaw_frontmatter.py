#!/usr/bin/env python3
"""Check a skill folder for OpenClaw-compatible frontmatter."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n?", re.S)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that a skill uses single-line JSON metadata frontmatter"
    )
    parser.add_argument("skill_path", nargs="?", default=".", help="Path to the skill folder")
    args = parser.parse_args()

    skill_md = Path(args.skill_path).resolve() / "SKILL.md"
    if not skill_md.exists():
        print(f"Missing SKILL.md: {skill_md}")
        return 1

    content = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        print("Missing frontmatter")
        return 1

    metadata_line: str | None = None
    for line in match.group(1).splitlines():
        if line.startswith("metadata:"):
            metadata_line = line.split(":", 1)[1].strip()
            break

    if metadata_line is None:
        print("No metadata line found")
        return 1
    if not metadata_line:
        print("metadata must be single-line JSON")
        return 1

    try:
        parsed = json.loads(metadata_line)
    except json.JSONDecodeError as exc:
        print(f"Invalid metadata JSON: {exc}")
        return 1

    if not isinstance(parsed, dict):
        print("metadata must be a JSON object")
        return 1

    openclaw_metadata = parsed.get("openclaw")
    if openclaw_metadata is not None and not isinstance(openclaw_metadata, dict):
        print("metadata.openclaw must be an object")
        return 1
    if isinstance(openclaw_metadata, dict):
        requires = openclaw_metadata.get("requires")
        if requires is not None and not isinstance(requires, (list, dict, str)):
            print("metadata.openclaw.requires must be a string, list, or object")
            return 1
        primary_env = openclaw_metadata.get("primaryEnv")
        if primary_env is not None and not isinstance(primary_env, str):
            print("metadata.openclaw.primaryEnv must be a string")
            return 1

    frontmatter_lines = match.group(1).splitlines()
    values: dict[str, str] = {}
    for line in frontmatter_lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()

    if not values.get("homepage"):
        print("homepage is required")
        return 1
    if not values.get("license"):
        print("license is required")
        return 1

    for key in ("user-invocable", "disable-model-invocation", "command-dispatch"):
        if key in values and values[key].lower() not in {"true", "false"}:
            print(f"{key} must be true or false")
            return 1
    if values.get("command-dispatch", "").lower() == "true" and not values.get("command-tool"):
        print("command-dispatch requires command-tool")
        return 1

    print("OpenClaw frontmatter audit passed: 0 issues")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
