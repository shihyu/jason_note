import argparse
import subprocess
from pathlib import Path
from typing import Any, Dict

from pipeline.claude_agent import build_stage1_prompt, build_stage2_prompt, call_claude, parse_files
from pipeline.crap import crap_score, cyclomatic_complexity
from pipeline.languages.python_lang import parse_coverage as parse_coverage_python
from pipeline.mutation import run_mutation_testing
from pipeline.state import STATE_DIR, TaskState

WORKSPACE_ROOT = STATE_DIR / "workspace"
CRAP_THRESHOLD = 6
MAX_RETRIES = 3

DEFAULT_REQUIREMENT = (
    "計算購物車折扣：VIP 會員打 8 折，一般會員原價；價格不可為負數，價格為 0 時應正常回傳 0（不算負數錯誤）。"
)


def _run_python_stage3_4_5(
    workspace: Path, impl_filename: str, test_filename: str
) -> Dict[str, Any]:
    """對 workspace 內剛產生的 python 檔案跑 Cleanup(CRAP) + Strengthening(Mutation) + QA。"""
    test_run = subprocess.run(
        ["coverage", "run", "-m", "pytest", test_filename],
        cwd=workspace,
        capture_output=True,
    )
    if test_run.returncode != 0:
        return {
            "stage": "writing",
            "passed": False,
            "reason": f"單元測試沒有全部通過（exit code {test_run.returncode}），請確認測試真的呼叫了實作且斷言正確",
        }
    cov_report = subprocess.run(
        ["coverage", "report", impl_filename],
        cwd=workspace,
        check=True,
        capture_output=True,
        text=True,
    )
    cov = parse_coverage_python(cov_report.stdout)
    comp = cyclomatic_complexity((workspace / impl_filename).read_text(), "python")
    score = crap_score(comp, cov)

    if score > CRAP_THRESHOLD:
        return {"stage": "cleanup", "passed": False, "comp": comp, "cov": cov, "crap": score}

    def run_tests() -> bool:
        r = subprocess.run(
            ["python3", "-m", "pytest", test_filename, "-q"], cwd=workspace, capture_output=True
        )
        return r.returncode == 0

    mutation_result = run_mutation_testing(workspace / impl_filename, run_tests)
    if mutation_result.score < 100.0:
        return {
            "stage": "strengthening",
            "passed": False,
            "comp": comp,
            "cov": cov,
            "crap": score,
            "mutation_score": mutation_result.score,
            "survived": mutation_result.survived,
        }

    qa = subprocess.run(
        ["python3", "-m", "pytest", test_filename, "-q"], cwd=workspace, capture_output=True
    )
    return {
        "stage": "qa",
        "passed": qa.returncode == 0,
        "comp": comp,
        "cov": cov,
        "crap": score,
        "mutation_score": mutation_result.score,
    }


def run_pipeline(
    language: str,
    task_id: str,
    requirement: str,
    workspace_root: Path = WORKSPACE_ROOT,
    state_dir: Path = STATE_DIR,
    max_retries: int = MAX_RETRIES,
) -> Dict[str, Any]:
    if language != "python":
        raise NotImplementedError("完整五階段自動化目前只串好 python；其他語言的 Cleanup/Strengthening 已個別驗證，orchestration 尚未接上")

    workspace = workspace_root / task_id
    workspace.mkdir(parents=True, exist_ok=True)
    state = TaskState(task_id=task_id, language=language, requirement=requirement)

    spec = call_claude(build_stage1_prompt(requirement, language))
    state.spec = spec
    state.history.append({"stage": "specification", "output": spec})
    state.save(state_dir)

    impl_filename = f"{task_id}.py"
    test_filename = f"test_{task_id}.py"
    feedback = None

    for attempt in range(1, max_retries + 1):
        code_response = call_claude(
            build_stage2_prompt(
                spec, language, feedback=feedback, filenames={"impl": impl_filename, "test": test_filename}
            )
        )
        files = parse_files(code_response)
        if impl_filename not in files or test_filename not in files:
            raise RuntimeError(f"claude 回覆缺少必要檔案，收到: {list(files.keys())}")
        (workspace / impl_filename).write_text(files[impl_filename])
        (workspace / test_filename).write_text(files[test_filename])
        state.history.append({"stage": "writing", "attempt": attempt})
        state.save(state_dir)

        result = _run_python_stage3_4_5(workspace, impl_filename, test_filename)
        result["attempt"] = attempt
        state.history.append(result)
        state.save(state_dir)

        if result["stage"] == "writing" and not result["passed"]:
            feedback = result["reason"]
            continue

        if result["stage"] == "cleanup" and not result["passed"]:
            feedback = (
                f"CRAP Score = {result['crap']:.1f} 超過門檻 {CRAP_THRESHOLD}"
                f"（複雜度={result['comp']}, 覆蓋率={result['cov']*100:.0f}%），請簡化實作或補測試"
            )
            continue

        if result["stage"] == "strengthening" and not result["passed"]:
            survived_desc = "; ".join(
                f"{m.original_token}->{m.replacement_token} at pos {m.position}" for m in result["survived"]
            )
            feedback = (
                f"Mutation Score = {result['mutation_score']:.1f}% 未達 100%，"
                f"存活的突變: {survived_desc}，請補強測試涵蓋這些邊界"
            )
            continue

        if result["stage"] == "qa" and not result["passed"]:
            feedback = "QA 階段驗收測試失敗，請修正實作"
            continue

        state.stage = "done"
        state.save(state_dir)
        return {
            "status": "success",
            "attempts": attempt,
            "crap": result["crap"],
            "mutation_score": result["mutation_score"],
            "workspace": str(workspace),
        }

    state.stage = "failed"
    state.save(state_dir)
    return {"status": "failed", "reason": "超過 max_retries 仍未通過", "history": state.history}


def main() -> None:
    parser = argparse.ArgumentParser(prog="pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="跑完整五階段流水線")
    run_p.add_argument("--lang", required=True)
    run_p.add_argument("--task", required=True)
    run_p.add_argument("--requirement", default=DEFAULT_REQUIREMENT)

    args = parser.parse_args()
    if args.command == "run":
        result = run_pipeline(args.lang, args.task, args.requirement)
        print(result)


if __name__ == "__main__":
    main()
