#!/usr/bin/env python3
"""Generate catalog/skills.yaml for a repo of skills."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

import yaml


def _discover_skill_dirs(root: Path) -> list[Path]:
    skills_root = root / "skills" if (root / "skills").is_dir() else root
    return sorted(path for path in skills_root.iterdir() if path.is_dir() and (path / "SKILL.md").exists())


def _infer_archetype(name: str, description: str) -> str:
    lowered = f"{name} {description}".lower()
    if any(keyword in lowered for keyword in ("creator", "diagnostic", "audit", "publish", "install", "打包", "診斷", "稽核")):
        return "ops"
    if any(keyword in lowered for keyword in ("strategy", "planner", "organizer", "alignment", "decomposer", "規劃", "整理", "對齊", "拆解")):
        return "router"
    if any(keyword in lowered for keyword in ("diagram", "humanize", "estimation", "改寫", "估計", "轉換")):
        return "utility"
    return "executor"


def _dump_yaml(data, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{pad}{key}:")
                lines.append(_dump_yaml(value, indent + 2))
            else:
                lines.append(f"{pad}{key}: {_scalar(value)}")
        return "\n".join(lines)
    if isinstance(data, list):
        lines = []
        for value in data:
            if isinstance(value, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(_dump_yaml(value, indent + 2))
            else:
                lines.append(f"{pad}- {_scalar(value)}")
        return "\n".join(lines)
    return f"{pad}{_scalar(data)}"


def _scalar(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    if re.fullmatch(r"[A-Za-z0-9._/+:-]+", text):
        return text
    return json.dumps(text, ensure_ascii=False)


def generate_catalog(root: Path, out_path: Path) -> Path:
    skills = []
    for skill_dir in _discover_skill_dirs(root):
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        _, block, _ = text.split("---", 2)
        frontmatter = yaml.safe_load(block) or {}
        description = str(frontmatter.get("description", ""))
        metadata = frontmatter.get("metadata") if isinstance(frontmatter.get("metadata"), dict) else {}
        skills.append(
            {
                "name": skill_dir.name,
                "archetype": _infer_archetype(skill_dir.name, description),
                "category": metadata.get("category", "general"),
                "triggers": re.findall(r"[「『\"“”`](.{2,80}?)[」』\"“”`]", description),
                "negative-boundaries": [clause.strip() for clause in re.split(r"[；。]", description) if "不" in clause or "not" in clause.lower()],
                "platforms": ["openclaw", "clawhub", "skill-md"],
                "maturity": "active",
                "deprecated-by": None,
                "homepage": frontmatter.get("homepage", ""),
                "version": frontmatter.get("version", ""),
            }
        )

    document = {"generated_at": str(date.today()), "skills": skills}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_dump_yaml(document) + "\n", encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate catalog/skills.yaml")
    parser.add_argument("root", nargs="?", default=".", help="Repo root")
    parser.add_argument("--out", default="catalog/skills.yaml", help="Output path relative to repo root")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    out_path = (root / args.out).resolve()
    generate_catalog(root, out_path)
    print(f"Wrote catalog: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
