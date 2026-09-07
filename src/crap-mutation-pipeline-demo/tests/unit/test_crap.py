import math

import pytest

from pipeline.crap import crap_score, cyclomatic_complexity


@pytest.mark.parametrize(
    "comp,cov,expected",
    [
        (2, 1.0, 2.0),
        (2, 0.0, 6.0),
        (5, 0.0, 30.0),
        # 原文表格寫 10.1，套公式實算應為 10.8，判斷原文為筆誤，以公式結果為準
        (10, 0.8, 10.8),
        (10, 0.0, 110.0),
    ],
)
def test_crap_score_matches_formula(comp, cov, expected):
    assert math.isclose(crap_score(comp, cov), expected, rel_tol=1e-9)


def test_complexity_python_if_for_while():
    src = """
def f(x):
    if x > 0:
        for i in range(x):
            while i > 0:
                i -= 1
    return x
"""
    assert cyclomatic_complexity(src, "python") == 4  # if+for+while+1


def test_complexity_python_and_or_except():
    src = """
def f(a, b):
    try:
        if a and b or not a:
            return 1
    except ValueError:
        return 0
"""
    assert cyclomatic_complexity(src, "python") == 5  # if+and+or+except+1


def test_complexity_go():
    src = """
func f(x int) int {
    if x > 0 {
        for i := 0; i < x; i++ {
            if i%2 == 0 && x > 1 {
                continue
            }
        }
    }
    return x
}
"""
    assert cyclomatic_complexity(src, "go") == 5  # if+if+for+&&+1


def test_complexity_rust():
    src = """
fn f(x: i32) -> i32 {
    if x > 0 {
        match x {
            1 => 1,
            _ => 0,
        }
    } else {
        0
    }
}
"""
    assert cyclomatic_complexity(src, "rust") == 3  # if+match+1


def test_complexity_javascript():
    src = """
function f(x) {
  if (x > 0) {
    for (let i = 0; i < x; i++) {
      if (i % 2 === 0 || x < 0) { continue; }
    }
  }
  return x;
}
"""
    assert cyclomatic_complexity(src, "javascript") == 5  # if+if+for+||+1


def test_complexity_c():
    src = """
int f(int x) {
    if (x > 0) {
        while (x > 0) {
            x--;
        }
    }
    return x;
}
"""
    assert cyclomatic_complexity(src, "c") == 3  # if+while+1


def test_unsupported_language_raises():
    with pytest.raises(ValueError):
        cyclomatic_complexity("if true {}", "cobol")
