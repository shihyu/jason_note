import pytest
import sys
import free_threaded_example

@pytest.fixture(scope="session", autouse=True)
def print_env_info():
    """在所有測試開始前，印出環境資訊，並在結束後印出提示。"""
    print("\n" + "=" * 59)
    print(f"Python version: {sys.version.split()[0]}")
    print(f"GIL enabled: {sys._is_gil_enabled()}")
    print(f"Rayon thread count: {free_threaded_example.get_thread_count()}")
    print("=" * 59)

    yield

    print("\n" + "-" * 59)
    if sys._is_gil_enabled():
        print("💡 提示：目前 GIL 已啟用。")
        print("執行 'uv run python -X gil=0 -m pytest -s ...' 來測試 freethreaded 版本")
    else:
        print("💡 提示：目前執行的是 free-threaded 版本（無 GIL）。")
        print("執行 'uv run python -X gil=1 -m pytest -s ...' 來比較有 GIL 的版本")
    print("-" * 59)

def test_parallel_processing(benchmark):
    """使用 pytest-benchmark 測試 process_red_envelopes_parallel 函式。"""
    result = benchmark(free_threaded_example.process_red_envelopes_parallel)
    assert isinstance(result, list)
    assert len(result) == 100