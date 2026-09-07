from unittest.mock import patch

from pipeline.cli import run_pipeline

SPEC_RESPONSE = "- [ ] 驗收測試 1：VIP 會員打 8 折\n- [ ] 驗收測試 2：價格為負數要報錯\n"

# 第一次嘗試：故意寫一個複雜度高、幾乎沒被測試覆蓋到的爛實作，用來驗證 Cleanup 階段會擋下並要求重寫
BAD_ATTEMPT_RESPONSE = """
### FILE: demo_task.py
```python
def demo_task(x):
    if x > 1:
        if x > 2:
            if x > 3:
                if x > 4:
                    return 0
    return 1
```

### FILE: test_demo_task.py
```python
from demo_task import demo_task


def test_returns_default_for_small_input():
    assert demo_task(0) == 1
```
"""

# 第二次嘗試：良好實作 + 涵蓋邊界的測試，CRAP 應該 <= 6、Mutation Score 應該 = 100%
GOOD_ATTEMPT_RESPONSE = """
### FILE: demo_task.py
```python
def demo_task(price, is_member):
    if price < 0:
        raise ValueError("price must not be negative")
    if is_member:
        return price * 0.8
    return price
```

### FILE: test_demo_task.py
```python
import pytest
from demo_task import demo_task


def test_member_discount():
    assert demo_task(100, True) == 80


def test_non_member_full_price():
    assert demo_task(100, False) == 100


def test_negative_price_raises():
    with pytest.raises(ValueError):
        demo_task(-1, True)


def test_zero_price_boundary():
    assert demo_task(0, False) == 0
```
"""


def test_run_pipeline_retries_on_high_crap_then_succeeds(tmp_path):
    with patch(
        "pipeline.cli.call_claude",
        side_effect=[SPEC_RESPONSE, BAD_ATTEMPT_RESPONSE, GOOD_ATTEMPT_RESPONSE],
    ):
        result = run_pipeline(
            "python",
            "demo_task",
            "計算折扣",
            workspace_root=tmp_path / "workspace",
            state_dir=tmp_path / "state",
        )

    assert result["status"] == "success"
    assert result["attempts"] == 2  # 第一次被 Cleanup 擋下，第二次才過
    assert result["crap"] <= 6
    assert result["mutation_score"] == 100.0
