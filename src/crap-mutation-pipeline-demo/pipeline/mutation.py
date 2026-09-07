import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List

# 語意層級的算子互換表。順序很重要：多字元 token（>=、<=、==、!=、&&、||）
# 必須排在對應的單字元 token（>、<）之前，regex 才不會把 ">=" 誤切成 ">" 多算一個突變體。
_TOKEN_ORDER = [">=", "<=", "==", "!=", "&&", "||", "and", "or", "true", "false", "+", "-", ">", "<"]
_REPLACEMENTS = {
    ">=": "<",
    "<=": ">",
    "==": "!=",
    "!=": "==",
    "&&": "||",
    "||": "&&",
    "and": "or",
    "or": "and",
    "true": "false",
    "false": "true",
    "+": "-",
    "-": "+",
    ">": ">=",
    "<": "<=",
}


def _build_pattern() -> re.Pattern:
    parts = []
    for tok in _TOKEN_ORDER:
        escaped = re.escape(tok)
        if tok.isalpha():
            escaped = rf"\b{escaped}\b"
        parts.append(escaped)
    return re.compile("|".join(parts))


_PATTERN = _build_pattern()


@dataclass
class Mutant:
    index: int
    original_token: str
    replacement_token: str
    position: int
    mutated_source: str


@dataclass
class MutationResult:
    total: int
    killed: int
    survived: List[Mutant] = field(default_factory=list)
    score: float = 100.0


def generate_mutants(source: str) -> List[Mutant]:
    mutants = []
    for i, m in enumerate(_PATTERN.finditer(source)):
        token = m.group(0)
        replacement = _REPLACEMENTS[token]
        mutated = source[: m.start()] + replacement + source[m.end() :]
        mutants.append(
            Mutant(
                index=i,
                original_token=token,
                replacement_token=replacement,
                position=m.start(),
                mutated_source=mutated,
            )
        )
    return mutants


def run_mutation_testing(source_path: Path, run_tests: Callable[[], bool]) -> MutationResult:
    """對 source_path 逐一套用單一突變、跑 run_tests()。

    run_tests() 回傳 True 代表測試仍然通過（突變體存活，測試有盲點）；
    回傳 False 代表測試失敗（突變體被殺死）。跑完一律還原原始檔案內容。
    """
    original = source_path.read_text()
    mutants = generate_mutants(original)
    killed = 0
    survived: List[Mutant] = []
    try:
        for mutant in mutants:
            source_path.write_text(mutant.mutated_source)
            if run_tests():
                survived.append(mutant)
            else:
                killed += 1
    finally:
        source_path.write_text(original)

    total = len(mutants)
    score = (killed / total * 100.0) if total else 100.0
    return MutationResult(total=total, killed=killed, survived=survived, score=score)
