#!/usr/bin/env python3
"""Check SKILL.md local references that break after standalone packaging."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PATH_REFERENCE_PATTERN = re.compile(r"(?<![\w/.-])((?:scripts|references|assets)/[A-Za-z0-9_./-]+)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that SKILL.md local path references exist inside the skill folder"
    )
    parser.add_argument("skill_path", nargs="?", default=".", help="Path to the skill folder")
    args = parser.parse_args()

    skill_dir = Path(args.skill_path).resolve()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"Missing SKILL.md: {skill_md}")
        return 1

    content = skill_md.read_text(encoding="utf-8")
    missing: list[str] = []
    for match in PATH_REFERENCE_PATTERN.finditer(content):
        prefix = content[max(0, match.start() - 24) : match.start()]
        if prefix.endswith("--out ") or prefix.endswith("--output "):
            continue
        token = match.group(1).rstrip(".,:;`)\"'")
        if any(marker in token for marker in ("<", ">", "*", "{", "}")):
            continue
        if not (skill_dir / token).exists():
            missing.append(token)

    missing = sorted(set(missing))
    if missing:
        for path in missing:
            print(f"missing_referenced_path:{path}")
        return 1

    print("Skill reference audit passed: 0 issues")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
