from unittest.mock import patch, MagicMock

from pipeline.claude_agent import call_claude, parse_files, build_stage1_prompt, build_stage2_prompt


def test_call_claude_invokes_expected_command():
    fake = MagicMock(returncode=0, stdout="hello", stderr="")
    with patch("subprocess.run", return_value=fake) as mock_run:
        out = call_claude("say hi")
    args = mock_run.call_args[0][0]
    assert args[0] == "claude"
    assert "-p" in args
    assert "say hi" in args
    assert out == "hello"


def test_call_claude_raises_on_nonzero_exit():
    fake = MagicMock(returncode=1, stdout="", stderr="boom")
    with patch("subprocess.run", return_value=fake):
        try:
            call_claude("x")
            assert False, "should have raised"
        except RuntimeError as e:
            assert "boom" in str(e)


def test_parse_files_extracts_named_code_blocks():
    response = """
一些說明文字

### FILE: impl.py
```python
def f(x):
    return x
```

### FILE: test_impl.py
```python
def test_f():
    assert f(1) == 1
```
"""
    files = parse_files(response)
    assert set(files.keys()) == {"impl.py", "test_impl.py"}
    assert "def f(x):" in files["impl.py"]
    assert "def test_f():" in files["test_impl.py"]


def test_build_stage1_prompt_includes_requirement():
    prompt = build_stage1_prompt("計算運費", "python")
    assert "計算運費" in prompt
    assert "python" in prompt


def test_build_stage2_prompt_includes_spec_and_feedback():
    prompt = build_stage2_prompt("驗收測試內容", "python", feedback="CRAP 太高，請簡化")
    assert "驗收測試內容" in prompt
    assert "CRAP 太高，請簡化" in prompt
