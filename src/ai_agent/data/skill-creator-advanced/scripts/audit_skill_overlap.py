#!/usr/bin/env python3
"""Build a lightweight overlap matrix across local skills."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


def _discover_skill_dirs(root: Path) -> list[Path]:
    skills_root = root / "skills" if (root / "skills").is_dir() else root
    return sorted(path for path in skills_root.iterdir() if path.is_dir() and (path / "SKILL.md").exists())


def _load_surface(skill_dir: Path) -> tuple[str, set[str], list[str]]:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    _, block, _ = text.split("---", 2)
    frontmatter = yaml.safe_load(block) or {}
    description = str(frontmatter.get("description", ""))
    triggers = re.findall(r"[「『\"“”`](.{2,80}?)[」』\"“”`]", description)
    latin = re.findall(r"[a-z][a-z0-9-]{2,}", f"{skill_dir.name} {description}".lower())
    cjk = re.findall(r"[\u4e00-\u9fff]{2}", description)
    tokens = set(latin + cjk + triggers)
    return skill_dir.name, tokens, triggers


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return 0.0 if not union else len(left & right) / len(union)


def audit_overlap(root: Path, top_k: int) -> int:
    records = [_load_surface(skill_dir) for skill_dir in _discover_skill_dirs(root)]
    failures = 0

    for name, tokens, triggers in records:
        neighbors = []
        for other_name, other_tokens, other_triggers in records:
            if other_name == name:
                continue
            score = _jaccard(tokens, other_tokens)
            neighbors.append((score, other_name, sorted(set(triggers) & set(other_triggers))))
        neighbors.sort(key=lambda item: (-item[0], item[1]))

        top_neighbors = neighbors[:top_k]
        hit_at_1 = top_neighbors[0][0] if top_neighbors else 0.0
        hit_at_3 = sum(item[0] for item in top_neighbors)
        print(f"[{name}] hit@1={hit_at_1:.4f} hit@3={hit_at_3:.4f}")
        for score, other_name, shared in top_neighbors:
            if score >= 0.25:
                failures += 1
            shared_text = ",".join(shared) if shared else "-"
            print(f"  - neighbor:{other_name} score={score:.4f} shared_triggers={shared_text}")

    print("Neighbor confusion matrix ready")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local skill overlap matrix")
    parser.add_argument("root", nargs="?", default=".", help="Repo root or skills directory")
    parser.add_argument("--top-k", type=int, default=3, help="How many nearest neighbors to print")
    args = parser.parse_args()
    return audit_overlap(Path(args.root).resolve(), args.top_k)


if __name__ == "__main__":
    raise SystemExit(main())
