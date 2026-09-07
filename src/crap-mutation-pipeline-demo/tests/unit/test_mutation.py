from pipeline.mutation import generate_mutants, run_mutation_testing

SOURCE = """
def is_adult(age):
    return age >= 18
"""


def make_runner(source_path, assertions_code):
    def run():
        ns = {}
        exec(source_path.read_text(), ns)
        try:
            exec(assertions_code, ns)
            return True  # 沒有 assertion 失敗 -> 突變體存活
        except AssertionError:
            return False  # assertion 失敗 -> 突變體被殺死

    return run


def test_generate_mutants_finds_operator_and_boundary():
    mutants = generate_mutants("if a >= b and c:\n    return a + b\n")
    tokens = {m.original_token for m in mutants}
    assert ">=" in tokens
    assert "and" in tokens
    assert "+" in tokens


def test_generate_mutants_does_not_double_match_ge():
    # ">=" 不應該被切成 ">" 額外多產生一個突變體
    mutants = generate_mutants("a >= b")
    assert [m.original_token for m in mutants] == [">="]


def test_generate_mutants_bare_lt_gt():
    mutants = generate_mutants("if price < 0 and score > 1:\n    pass\n")
    tokens = [m.original_token for m in mutants]
    assert tokens == ["<", "and", ">"]


def test_mutation_weak_test_leaves_survivors(tmp_path):
    f = tmp_path / "mod.py"
    f.write_text(SOURCE)
    runner = make_runner(f, "assert isinstance(is_adult(30), bool)\n")

    result = run_mutation_testing(f, runner)

    assert result.total == 1  # 只有一個 >= 運算子
    assert result.score < 100.0
    assert len(result.survived) == 1
    assert f.read_text() == SOURCE  # 跑完要還原原始檔案


def test_mutation_strong_test_kills_all(tmp_path):
    f = tmp_path / "mod.py"
    f.write_text(SOURCE)
    runner = make_runner(
        f,
        "assert is_adult(30) is True\n"
        "assert is_adult(10) is False\n"
        "assert is_adult(18) is True\n",
    )

    result = run_mutation_testing(f, runner)

    assert result.total == 1
    assert result.score == 100.0
    assert result.survived == []
    assert f.read_text() == SOURCE
