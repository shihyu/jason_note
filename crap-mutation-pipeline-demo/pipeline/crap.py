import re

# 各語言的「決策點」關鍵字/運算子，用來估算環形複雜度（McCabe）。
# 通用做法：複雜度 = 決策點出現次數 + 1（基礎路徑）。
LANGUAGE_KEYWORDS = {
    "python": [r"\bif\b", r"\belif\b", r"\bfor\b", r"\bwhile\b", r"\bexcept\b", r"\bcase\b", r"\band\b", r"\bor\b"],
    "go": [r"\bif\b", r"\bfor\b", r"\bcase\b", r"&&", r"\|\|"],
    "rust": [r"\bif\b", r"\bfor\b", r"\bwhile\b", r"\bmatch\b", r"&&", r"\|\|"],
    "javascript": [r"\bif\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"\bcatch\b", r"&&", r"\|\|"],
    "c": [r"\bif\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"&&", r"\|\|"],
}


def cyclomatic_complexity(source: str, language: str) -> int:
    if language not in LANGUAGE_KEYWORDS:
        raise ValueError(f"unsupported language: {language}")
    count = sum(len(re.findall(pattern, source)) for pattern in LANGUAGE_KEYWORDS[language])
    return count + 1


def crap_score(comp: int, cov: float) -> float:
    """CRAP(m) = comp(m)^2 * (1 - cov(m))^3 + comp(m)"""
    return comp**2 * (1 - cov) ** 3 + comp
