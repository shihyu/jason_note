#!/usr/bin/env python3
"""Audit README, topics, and repo discovery surfaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RECOMMENDED_TOPICS = [
    "skills",
    "agent-skills",
    "openclaw-skills",
    "codex-skills",
    "claude-code-skills",
    "cursor-skills",
    "agents-md",
    "skill-md",
    "prompt-engineering",
    "ai-agents",
]


def audit_repo(root: Path) -> int:
    readme = root / "README.md"
    package_json = root / "package.json"
    settings_yml = root / ".github" / "settings.yml"
    failures = 0

    if not readme.exists():
        print("error:missing_readme")
        return 1

    readme_text = readme.read_text(encoding="utf-8").lower()
    for label, keywords in {
        "what": ("這是什麼", "repo 提供什麼"),
        "platforms": ("支援平台", "支援哪些 agent"),
        "featured": ("代表 skills", "最值得先裝"),
        "install": ("quick start", "安裝"),
        "search": ("搜尋 skill", "分類索引"),
        "contribute": ("contributing", "貢獻"),
    }.items():
        if not any(keyword.lower() in readme_text for keyword in keywords):
            failures += 1
            print(f"error:missing_readme_section:{label}")

    if package_json.exists():
        keywords = set(json.loads(package_json.read_text(encoding="utf-8")).get("keywords", []))
        missing = [topic for topic in RECOMMENDED_TOPICS if topic not in keywords]
        if missing:
            print("warn:package_keywords_missing:" + ",".join(missing))
    else:
        failures += 1
        print("error:missing_package_json")

    if settings_yml.exists():
        settings_text = settings_yml.read_text(encoding="utf-8").lower()
        missing_topics = [topic for topic in RECOMMENDED_TOPICS if f"- {topic.lower()}" not in settings_text]
        if missing_topics:
            print("warn:settings_topics_missing:" + ",".join(missing_topics))
    else:
        print("warn:missing_.github/settings.yml_for_repo_topics")

    if failures == 0:
        print("Repo discovery audit passed: 0 blocking issues")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit repo discovery surfaces")
    parser.add_argument("root", nargs="?", default=".", help="Repo root")
    args = parser.parse_args()
    return audit_repo(Path(args.root).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
