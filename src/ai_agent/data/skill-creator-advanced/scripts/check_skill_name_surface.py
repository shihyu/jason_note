#!/usr/bin/env python3
"""Check naming and description surfaces for a repo or skill collection."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

MAX_SLUG_LENGTH = 32
MAX_DESCRIPTION_LENGTH = 180
JARGON_TOKENS = {"metadata", "frontmatter", "benchmark", "evals", "registry", "telemetry"}


def _discover_skill_dirs(root: Path) -> list[Path]:
    skills_root = root / "skills" if (root / "skills").is_dir() else root
    return sorted(path for path in skills_root.iterdir() if path.is_dir() and (path / "SKILL.md").exists())


def _read_frontmatter(skill_dir: Path) -> dict:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    _, block, _ = text.split("---", 2)
    data = yaml.safe_load(block)
    return data if isinstance(data, dict) else {}


def _quoted_phrases(text: str) -> list[str]:
    return re.findall(r"[「『\"“”`](.{2,80}?)[」』\"“”`]", text)


def audit_repo(root: Path) -> int:
    failures = 0
    skill_dirs = _discover_skill_dirs(root)
    commands = {skill_dir.name.replace("-", "_"): skill_dir.name for skill_dir in skill_dirs}

    for skill_dir in skill_dirs:
        frontmatter = _read_frontmatter(skill_dir)
        description = str(frontmatter.get("description", "")).strip()
        command = skill_dir.name.replace("-", "_")
        warnings: list[str] = []
        errors: list[str] = []

        if len(skill_dir.name) > MAX_SLUG_LENGTH:
            errors.append(f"slug_too_long:{len(skill_dir.name)}")
        if len(command) > 32:
            errors.append(f"slash_command_too_long:{len(command)}")
        if len(description) > MAX_DESCRIPTION_LENGTH:
            warnings.append(f"description_may_be_too_long:{len(description)}")
        if not _quoted_phrases(description):
            warnings.append("description_missing_trigger_phrase")
        if not any(marker in description.lower() for marker in ("不", "不要", "not", "without")):
            warnings.append("description_missing_boundary")

        latin_tokens = re.findall(r"[a-z][a-z0-9-]{2,}", description.lower())
        if latin_tokens:
            jargon_ratio = sum(1 for token in latin_tokens if token in JARGON_TOKENS) / len(latin_tokens)
            if jargon_ratio > 0.34:
                warnings.append("description_may_use_too_much_internal_jargon")

        overlaps = [
            peer_name
            for peer_command, peer_name in commands.items()
            if peer_name != skill_dir.name and (peer_command.startswith(command) or command.startswith(peer_command))
        ]
        warnings.extend(f"command_prefix_overlap:{peer_name}" for peer_name in sorted(overlaps))

        if errors or warnings:
            print(f"[{skill_dir.name}] command={command}")
            for issue in errors:
                failures += 1
                print(f"  - error:{issue}")
            for issue in warnings:
                print(f"  - warn:{issue}")

    if failures == 0:
        print("Name surface audit passed: 0 blocking issues")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check skill naming surfaces")
    parser.add_argument("root", nargs="?", default=".", help="Repo root or skills directory")
    args = parser.parse_args()
    return audit_repo(Path(args.root).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
