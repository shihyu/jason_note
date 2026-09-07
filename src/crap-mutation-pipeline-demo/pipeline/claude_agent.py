import re
import subprocess
from typing import Dict, Optional

FILE_MARKER = re.compile(r"^### FILE:\s*(\S+)\s*$", re.MULTILINE)


def call_claude(prompt: str, timeout: int = 600) -> str:
    """呼叫 `claude -p` headless CLI，回傳純文字回覆。會消耗使用者帳號的 token。"""
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "text"],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed (exit={result.returncode}): {result.stderr}")
    return result.stdout


def parse_files(response: str) -> Dict[str, str]:
    """解析回覆中以 `### FILE: <name>` 標記分隔的多檔案內容，並去除 markdown code fence。"""
    matches = list(FILE_MARKER.finditer(response))
    files: Dict[str, str] = {}
    for i, m in enumerate(matches):
        filename = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(response)
        block = response[start:end].strip()
        block = re.sub(r"^```[a-zA-Z]*\n", "", block)
        block = re.sub(r"\n```$", "", block)
        files[filename] = block.strip() + "\n"
    return files


def build_stage1_prompt(requirement: str, language: str) -> str:
    return f"""你是一個五階段 TDD 流水線的 Specification agent。
語言：{language}
需求：{requirement}

任務：只產生驗收測試（Acceptance Tests），用 checklist 條列描述可觀察的行為，不要預設實作細節、不要輸出程式碼。
輸出格式：
- [ ] 驗收測試 1：<描述>
- [ ] 驗收測試 2：<描述>
"""


def build_stage2_prompt(
    spec: str, language: str, feedback: Optional[str] = None, filenames: Optional[Dict[str, str]] = None
) -> str:
    filenames = filenames or {"impl": "impl", "test": "test_impl"}
    feedback_block = f"\n上一輪未通過的回饋（請針對這個修正）：{feedback}\n" if feedback else ""
    return f"""你是一個五階段 TDD 流水線的 Writing agent。
語言：{language}
驗收測試：
{spec}
{feedback_block}
任務：根據驗收測試，先寫單元測試、再寫最小實作（TDD 原則），每個函式環形複雜度盡量 <= 4。
輸出格式（務必照這個格式，每個檔案用 "### FILE: <檔名>" 開頭，內容包在 ```{language} code fence 裡）：

### FILE: {filenames['impl']}
```{language}
<實作程式碼>
```

### FILE: {filenames['test']}
```{language}
<單元測試程式碼>
```
"""
