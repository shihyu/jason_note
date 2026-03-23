#!/usr/bin/env python3
"""Advanced Skill Initializer

Creates a new skill folder with a more complete SKILL.md skeleton that covers the
full skill lifecycle: scope → design → validation → testing → packaging →
distribution → iteration.

Usage:
  ./init_skill_advanced.py <skill-name> --path <output-directory>

Examples:
  ./init_skill_advanced.py notion-project-setup --path ./skills/public
  ./init_skill_advanced.py linear-sprint-planner --path /tmp/skills
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.versioning import today_version


SKILL_TEMPLATE_ADV = """---
name: {skill_name}
description: [TODO: Write this as a decision boundary: what it does, when to use it, when not to use it, and what successful output looks like. Include real trigger phrases/file types. Keep under 1024 chars. Avoid < or >]
version: {skill_version}
metadata:
  author: [TODO]
---

# {skill_title}

## Single responsibility

- Primary job: [TODO: the one main thing this skill owns]
- Not this skill's job: [TODO]
- Split / handoff rule: [TODO: if the request also needs X/Y, hand off or compose with another skill]

<role>
[TODO: Who this skill acts as, for whom, and from what professional perspective.]
</role>

<decision_boundary>
Use when:
- [TODO]

Do not use when:
- [TODO]

Inputs:
- [TODO]

Successful output:
- [TODO]
</decision_boundary>

## Primary use cases (2-3)

1) **[Use case name]**
- Trigger examples: "[user phrasing]", "[paraphrase]"
- Required inputs: [TODO]
- Expected result: [what done looks like]

2) **[Use case name]**
- Trigger examples: ...
- Required inputs: ...
- Expected result: ...

3) **[Use case name]** (optional)

## Communication notes

- User vocabulary: [TODO: terms the user already uses]
- Avoid jargon: [TODO: terms to translate or avoid]
- Least-surprise rule: [TODO: what users will reasonably expect this skill to do]

## Routing boundaries

- Neighboring skills / workflows: [TODO]
- Negative triggers: [TODO: what this skill should NOT own]
- Handoff rule: [TODO: when another skill should take over]

## Language coverage

- Primary language(s): [TODO]
- Mixed-language trigger phrases: [TODO]
- Locale-specific wording risks: [TODO]

<success_criteria>
Quantitative:
- Trigger accuracy: [e.g., 90% of relevant queries]
- Tool calls: [target range]
- Failures: [e.g., 0 failed API calls per workflow]

Qualitative:
- Minimal user steering
- Repeatable output structure
- Works for a new user on first try
</success_criteria>

<workflow>
Step 0: Confirm inputs
- Action: Read the existing conversation/files first; ask follow-up questions only when a wrong assumption would materially change the outcome.
- Input: [TODO: what must be provided by the user before starting]
- Output: [TODO: confirmed scope / missing-info list / stop condition]
- Validation: [TODO]

Step 1: [First major step]
- Action: [TODO: imperative instruction]
- Input: [TODO]
- Output: [TODO]
- Validation: [TODO]

Step 2: [Next major step]
- Action: [TODO: imperative instruction]
- Input: [TODO]
- Output: [TODO]
- Validation: [TODO]

Step N: Finalization and QA
- Action: Run `python scripts/format_check.py .` (or from the skill-creator toolchain)
- Action: Validate outputs against the checklist in `references/quality_checklist.md`
- Output: [TODO: final artifact + QA summary]
</workflow>

<output_contract>
Return exactly these sections or fields in this order:
1. [TODO]
2. [TODO]
3. [TODO]

Formatting rules:
- [TODO: Markdown / JSON / SQL / table / etc.]
- [TODO: length limits]
- [TODO: whether extra sections are allowed]
- [TODO: what to do when information is missing]
</output_contract>

<tool_rules>
- [TODO: when to call which tool]
- [TODO: if a tool has side effects, state the approval rule]
- [TODO: if tool/function schema exists, make names, parameter descriptions, enum values, and required fields explicit]
- [TODO: keep the active tool set as small as practical]
</tool_rules>

<default_follow_through_policy>
- Directly do: [TODO: low-risk, reversible, no external side effects]
- Ask first: [TODO: write operations, destructive actions, external side effects]
- Stop and report: [TODO: missing prerequisites, unsafe state, policy conflict]
</default_follow_through_policy>

<examples>
Example 1
Input:
- [TODO]

Output:
[TODO]

Example 2 (optional)
Input:
- [TODO]

Output:
[TODO]
</examples>

<model_notes>
- GPT-style models: [TODO: what should be explicit step-by-step]
- Reasoning models: [TODO: goals, constraints, reasoning effort, what NOT to overspecify]
- Multi-turn split: [TODO: when to break analysis / execution / drafting / QA into separate turns]
</model_notes>

## Testing plan

### Triggering tests
- Should trigger:
  - [TODO]
- Should NOT trigger:
  - [TODO]
- Near-miss / confusing cases:
  - [TODO]
- Should ask before acting:
  - [TODO]

### Functional tests
- Test case: [TODO]
  - Given:
  - When:
  - Then:

### Performance comparison (optional)
- Baseline (no skill):
- With skill:

### ROI guardrail
- Quality gain must justify extra:
  - Time:
  - Tokens:
  - Maintenance burden:

### Regression gates
- Minimum pass-rate delta:
- Maximum allowed time increase:
- Maximum allowed token increase:
- Maximum under-trigger failures:
- Maximum over-trigger failures:

### Feedback loop
- Common failure signals:
  - [TODO]
- Likely fix:
  - [TODO: description / workflow / resources]

### Model / routing checks
- GPT-style prompt pass:
  - [TODO]
- Reasoning-model pass:
  - [TODO]
- Neighbor-skill confusion:
  - [TODO]

## Eval workflow

- Save approved prompts to `assets/evals/evals.json`
- Define release thresholds in `assets/evals/regression_gates.json`
- Prepare paired runs with `python scripts/prepare_eval_workspace.py <path/to/skill>`
- If the environment supports subagents or parallel workers, launch with-skill and baseline runs in the same batch
- After runs complete, aggregate results and generate a review viewer
- Validate release thresholds with `python scripts/check_regression_gates.py <benchmark.json> --config assets/evals/regression_gates.json`

## Distribution notes

- Packaging: `python scripts/package_skill.py <path/to/skill-folder>`
- Repo-level README belongs *outside* this skill folder.

## Troubleshooting

- Symptom:
- Cause:
- Fix:

## Resources

This template includes optional resource directories:
- `scripts/` for deterministic helpers
- `references/` for long docs loaded on demand
- `assets/` for templates/fonts/icons used in output and reusable eval fixtures
"""

EXAMPLE_REFERENCE_QUALITY = """# Quality checklist

Use this checklist before packaging or shipping a new version.

## Structure
- [ ] Folder name is kebab-case
- [ ] SKILL.md exists (case-sensitive)
- [ ] YAML frontmatter starts/ends with ---
- [ ] Frontmatter has name + description
- [ ] No < or > in frontmatter
- [ ] No README.md inside skill folder

## Triggering
- [ ] Triggers on obvious queries
- [ ] Triggers on paraphrases
- [ ] Does NOT trigger on unrelated queries
- [ ] Does NOT steal queries from neighboring skills
- [ ] Works on expected language variants
- [ ] Description clearly says when to use and when NOT to use the skill

## Functionality
- [ ] Skill has one clear primary job
- [ ] Instructions use imperative steps with input/output/validation
- [ ] Core workflow works end-to-end
- [ ] Errors handled with actionable guidance
- [ ] Output matches required structure
- [ ] Output contract is explicit
- [ ] Default follow-through policy is explicit
- [ ] Examples exist when style/format quality matters
- [ ] Tool rules are explicit if the skill uses tools

## Maintenance
- [ ] Version bumped in top-level version
- [ ] Changes documented (outside the skill folder, e.g., repo release notes)
- [ ] Evals saved to assets/evals/evals.json (if benchmarking this skill)
- [ ] Regression gates defined (if benchmarking this skill)
- [ ] ROI review completed
- [ ] Long workflows are split into stages or multi-turn steps when appropriate
- [ ] Model-specific notes added if GPT-style and reasoning models need different guidance
"""

EXAMPLE_EVALS_JSON = """{{
  "skill_name": "{skill_name}",
  "evals": [
    {{
      "id": 1,
      "name": "happy-path",
      "prompt": "[TODO: realistic user request]",
      "expected_output": "[TODO: what success looks like]",
      "files": [],
      "expectations": [
        "[TODO: verifiable expectation]"
      ]
    }}
  ]
}}
"""

EXAMPLE_REGRESSION_GATES_JSON = """{{
  "min_pass_rate_delta": 0.0,
  "max_time_increase_seconds": 30.0,
  "max_token_increase": 5000,
  "require_non_negative_pass_rate": true
}}
"""

EXAMPLE_SCRIPT_PLACEHOLDER = """#!/usr/bin/env python3
\"\"\"Example helper script for {skill_name}\n\nReplace or delete this file.\n\"\"\"\n\nfrom __future__ import annotations\n\n\ndef main() -> None:\n    print(\"TODO: implement helper script\")\n\n\nif __name__ == \"__main__\":\n    main()\n"""


def title_case_skill_name(skill_name: str) -> str:
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def is_kebab_case(name: str) -> bool:
    return re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is not None


def init_skill(skill_name: str, path: str) -> Path:
    if not is_kebab_case(skill_name) or len(skill_name) > 64:
        raise ValueError("skill-name must be kebab-case, <= 64 chars")

    skill_dir = Path(path).resolve() / skill_name
    if skill_dir.exists():
        raise FileExistsError(f"Skill directory already exists: {skill_dir}")

    skill_dir.mkdir(parents=True, exist_ok=False)

    # SKILL.md
    skill_title = title_case_skill_name(skill_name)
    (skill_dir / "SKILL.md").write_text(
        SKILL_TEMPLATE_ADV.format(
            skill_name=skill_name,
            skill_title=skill_title,
            skill_version=today_version(),
        ),
        encoding="utf-8",
    )

    # scripts/
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    ex = scripts_dir / "example.py"
    ex.write_text(EXAMPLE_SCRIPT_PLACEHOLDER.format(skill_name=skill_name), encoding="utf-8")
    ex.chmod(0o755)

    # references/
    refs_dir = skill_dir / "references"
    refs_dir.mkdir(exist_ok=True)
    (refs_dir / "quality_checklist.md").write_text(EXAMPLE_REFERENCE_QUALITY, encoding="utf-8")

    # assets/
    assets_dir = skill_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    evals_dir = assets_dir / "evals"
    evals_dir.mkdir(exist_ok=True)
    (evals_dir / "evals.json").write_text(
        EXAMPLE_EVALS_JSON.format(skill_name=skill_name),
        encoding="utf-8",
    )
    (evals_dir / "regression_gates.json").write_text(
        EXAMPLE_REGRESSION_GATES_JSON,
        encoding="utf-8",
    )

    return skill_dir


def main() -> int:
    if len(sys.argv) < 4 or sys.argv[2] != "--path":
        print("Usage: init_skill_advanced.py <skill-name> --path <path>")
        return 1

    skill_name = sys.argv[1]
    path = sys.argv[3]

    try:
        skill_dir = init_skill(skill_name, path)
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    print(f"Created: {skill_dir}")
    print("Next steps:")
    print("1) Edit SKILL.md (decision boundary + workflow + output contract + follow-through policy)")
    print("2) Add scripts/references/assets as needed")
    print("3) Run format/structure checks (format_check.py + quick_validate.py)")
    print("4) Package with package_skill.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
