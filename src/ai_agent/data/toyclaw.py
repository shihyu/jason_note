#!/usr/bin/env python3
"""
toyclaw: a tiny XML-tag protocol runtime for LLM tool execution.

Now supports an Ollama-driven loop:
  - model emits XML blocks (e.g. <shell>...</shell>)
  - toyclaw executes and returns <json>/<markdown> observations
  - loop continues until model emits <final>...</final>
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List
import shlex


BLOCK_RE = re.compile(r"<(?P<tag>[a-zA-Z0-9_\-]+)>(?P<body>[\s\S]*?)</(?P=tag)>")
# 用最短匹配抓出成對 XML-like 區塊，避免一個大區塊把後面的多個 tag 吃掉。
# 這樣模型一次回多個 <shell>/<json>/<final> 時，runtime 可以逐段處理。


SYSTEM_PROMPT = """You are ToyClaw agent. You support TWO modes:

A) Chat mode (no tools needed)
- If the user asks for explanation, code sample, writing, translation, or general Q&A,
  respond directly with:
  <markdown>...</markdown>
- Keep answer complete and user-friendly.

B) Tool mode (commands/files needed)
- If the task requires filesystem/command execution, use XML tool blocks, e.g.:
  <shell>echo hello</shell>
- You can emit multiple blocks in one response.
- After receiving runtime output, decide next step.
- When complete, output:
  <final>...</final>

Global rules:
1) No markdown fences, no extra prose outside XML blocks.
2) Prefer concise, deterministic commands.
3) Do not invent command output.
"""


@dataclass
class Block:
    """保存解析後的單一 XML-like 區塊。"""

    tag: str
    body: str


def parse_blocks(text: str) -> List[Block]:
    """把輸入字串中所有合法區塊抓出來，並把 tag 統一轉小寫。"""

    return [Block(m.group("tag").lower(), m.group("body").strip()) for m in BLOCK_RE.finditer(text)]


def wrap_json(data: dict) -> str:
    """把 dict 包成 <json>，提供機器可讀的觀察結果。"""

    return f"<json>{json.dumps(data, ensure_ascii=False, indent=2)}</json>"


def wrap_markdown(text: str) -> str:
    """把人類可讀訊息包成 <markdown>。"""

    return f"<markdown>{text}</markdown>"


def wrap_response(meta: dict, human: str, machine: dict) -> str:
    """把摘要資訊、人類輸出、機器輸出包成統一 response 格式。"""

    return "\n".join(
        [
            "<response>",
            f"  <meta>{json.dumps(meta, ensure_ascii=False)}</meta>",
            f"  <human>{human}</human>",
            f"  <machine>{json.dumps(machine, ensure_ascii=False)}</machine>",
            "</response>",
        ]
    )


def render_output(raw: str, output_mode: str) -> str:
    """把內部 XML 輸出轉成 CLI 要顯示的格式。"""

    blocks = parse_blocks(raw)
    if not blocks:
        return raw

    # 收集所有 <markdown> 內容，最後串成使用者看的文字輸出。
    md_texts = [b.body for b in blocks if b.tag == "markdown"]
    json_objs = []
    for b in blocks:
        if b.tag == "json":
            try:
                json_objs.append(json.loads(b.body))
            except Exception:
                # 不讓壞掉的 JSON 直接炸掉顯示流程，保留原始內容方便除錯。
                json_objs.append({"raw": b.body})

    human = "\n\n".join(md_texts).strip() or "(no human output)"
    machine = {"json": json_objs}

    # 只要任何一個 JSON payload 明確回報 ok=false，整體 meta 就標成失敗。
    meta = {
        "ok": not any(isinstance(x, dict) and x.get("ok") is False for x in json_objs),
        "json_count": len(json_objs),
        "markdown_count": len(md_texts),
    }

    if output_mode == "human":
        return human
    if output_mode == "machine":
        return json.dumps(machine, ensure_ascii=False, indent=2)
    return wrap_response(meta=meta, human=human, machine=machine)


def is_probably_shell_command(text: str) -> bool:
    """判斷 `<final>` 內容看起來像指令還是一般文字。"""

    t = text.strip()
    if not t:
        return False
    # 出現 shell 常見運算子時，直接當成指令。
    if any(op in t for op in ["&&", "||", "|", ">", "<", ";"]):
        return True
    # 否則只檢查第一個 token 是否在白名單，避免把一般句子誤判成指令。
    try:
        first = shlex.split(t)[0]
    except Exception:
        first = t.split()[0]
    shell_heads = {
        "ls", "cat", "echo", "pwd", "cd", "mkdir", "rm", "cp", "mv", "grep", "find",
        "python", "python3", "pip", "git", "touch", "chmod", "chown", "sed", "awk", "curl", "wget",
        "node", "npm", "yarn", "pnpm", "bash", "sh", "zsh", "make", "pytest"
    }
    return first in shell_heads


def run_shell(cmd: str, cwd: Path, timeout: int = 30) -> str:
    """執行 shell 指令，並同時回傳機器可讀與人類可讀結果。"""

    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        payload = {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "cwd": str(cwd),
            "command": cmd,
        }
        md = "✅ 指令執行成功" if proc.returncode == 0 else "❌ 指令執行失敗"

        # 先放結構化 JSON，外部程式可直接解析 exit_code/stdout/stderr。
        parts = [wrap_json(payload), wrap_markdown(md)]

        # 再補上人類可直接閱讀的鏡像內容，CLI 顯示會比較友善。
        parts.append(wrap_markdown(f"$ {cmd}"))
        if proc.stdout:
            parts.append(wrap_markdown(f"stdout:\n{proc.stdout.rstrip()}"))
        if proc.stderr:
            parts.append(wrap_markdown(f"stderr:\n{proc.stderr.rstrip()}"))
        if not proc.stdout and not proc.stderr:
            parts.append(wrap_markdown("(no output)"))

        return "\n".join(parts)
    except subprocess.TimeoutExpired as e:
        payload = {
            "ok": False,
            "error": "timeout",
            "timeout_sec": timeout,
            "stdout": e.stdout or "",
            "stderr": e.stderr or "",
            "cwd": str(cwd),
            "command": cmd,
        }
        return "\n".join([wrap_json(payload), wrap_markdown("⏱️ 指令逾時")])
    except Exception as e:
        payload = {
            "ok": False,
            "error": str(e),
            "cwd": str(cwd),
            "command": cmd,
        }
        return "\n".join([wrap_json(payload), wrap_markdown("⚠️ 執行時發生例外")])


def handle_message(message: str, cwd: Path, timeout: int) -> str:
    """直接處理一段 XML 協議訊息，不經過 LLM 規劃迴圈。"""

    blocks = parse_blocks(message)
    if not blocks:
        return "\n".join(
            [
                wrap_json(
                    {
                        "ok": False,
                        "error": "no_xml_blocks",
                        "hint": "請用 <shell>...</shell>、<markdown>...</markdown>、<json>...</json> 或 <final>...</final>",
                    }
                ),
                wrap_markdown("我沒有讀到 XML 區塊。"),
            ]
        )

    # 每個 block 各自執行，最後把所有觀察結果依序串起來回傳。
    outputs: List[str] = []
    for b in blocks:
        if b.tag == "shell":
            outputs.append(run_shell(b.body, cwd=cwd, timeout=timeout))
        elif b.tag in {"markdown", "json", "final"}:
            # 這些 tag 在低階 runtime 不需要再解釋，只回報已收到。
            # 真正的語意處理由上層 llm loop 決定。
            outputs.append(
                "\n".join(
                    [
                        wrap_json({"ok": True, "received_tag": b.tag}),
                        wrap_markdown(f"已收到 <{b.tag}> 訊息。"),
                    ]
                )
            )
        else:
            outputs.append(
                "\n".join(
                    [
                        wrap_json({"ok": False, "error": "unsupported_tag", "tag": b.tag}),
                        wrap_markdown(f"不支援的標記：<{b.tag}>"),
                    ]
                )
            )

    return "\n".join(outputs)


def ollama_chat(model: str, messages: List[dict]) -> str:
    """把 messages 攤平成 prompt，交給 Ollama 跑一輪。"""

    transcript = []
    for m in messages:
        role = m.get("role", "user").upper()
        transcript.append(f"[{role}]\n{m.get('content', '')}\n")
    prompt = "\n".join(transcript) + "\n[ASSISTANT]\n"

    proc = subprocess.run(
        ["ollama", "run", model, prompt],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ollama failed: {proc.stderr.strip()}")

    return proc.stdout.strip()


def should_use_tool_mode(task: str) -> bool:
    """用關鍵字粗略判斷這個任務是否需要工具模式。"""

    t = task.lower()
    hints = [
        "建立", "新增", "產生", "放", "寫入", "存檔", "刪除", "列出", "執行", "檔案", "文件", "資料夾", "目錄",
        "shell", "command", "terminal", "file", "folder", "directory", "ls", "cat", "mkdir", "rm", "git", "python3",
    ]
    return any(h in t for h in hints)


def run_llm_loop(task: str, model: str, cwd: Path, timeout: int, max_steps: int, mode: str = "auto", trace: bool = False) -> str:
    """主代理迴圈：讓模型決定要不要呼叫工具，直到輸出 `<final>` 或超過步數。"""

    selected_mode = mode
    if selected_mode == "auto":
        # auto 模式下，先用關鍵字猜任務是純對話還是需要檔案/指令操作。
        selected_mode = "tool" if should_use_tool_mode(task) else "chat"

    mode_hint = (
        "Mode: TOOL. Use <shell> when needed, finish with <final>. Execute the exact user request (do not change target filename/path). Before <final>, verify result with commands like ls/cat."
        if selected_mode == "tool"
        else "Mode: CHAT. Reply directly in one <markdown>...</markdown>. Do NOT use <shell>."
    )

    messages: List[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Task: {task}\n{mode_hint}",
        },
    ]
    trace_logs: List[str] = []

    for step in range(1, max_steps + 1):
        # 每一輪都把完整對話歷史送給模型，讓它能根據前一輪的執行結果繼續決策。
        llm_out = ollama_chat(model=model, messages=messages)
        if trace:
            trace_logs.append(f"[step {step}] LLM output:\n{llm_out}")
        blocks = parse_blocks(llm_out)
        if len(blocks) == 1 and blocks[0].tag == "xml":
            # 有些模型會再包一層 <xml> 根節點，這裡拆開後繼續正常處理。
            inner = parse_blocks(blocks[0].body)
            if inner:
                blocks = inner

        if not blocks:
            # 模型沒照協議輸出時，不直接失敗；把錯誤觀察回灌給模型重試。
            obs = "\n".join(
                [
                    wrap_json({"ok": False, "error": "model_no_xml", "step": step}),
                    wrap_markdown("模型未回傳 XML，請改用 XML。"),
                ]
            )
            messages.append({"role": "assistant", "content": llm_out})
            messages.append({"role": "user", "content": obs})
            continue

        # tool 模式禁止純說明不做事，避免模型卡在一直解釋、不真正執行。
        if selected_mode == "tool" and not any(b.tag in {"shell", "final"} for b in blocks):
            obs = "\n".join(
                [
                    wrap_json({"ok": False, "error": "tool_mode_requires_shell", "step": step}),
                    wrap_markdown("你目前在 TOOL mode。請輸出 <shell>...</shell> 或 <final>...</final>，不要只回說明文字。"),
                ]
            )
            if trace:
                trace_logs.append(f"[step {step}] Runtime output:\n{obs}")
            messages.append({"role": "assistant", "content": llm_out})
            messages.append({"role": "user", "content": obs})
            continue

        # 先執行所有非 final 的 block，確保同一輪中的工具操作先落地。
        actionable = [b for b in blocks if b.tag != "final"]
        runtime_output = ""
        if actionable:
            runtime_output = handle_message("\n".join(f"<{b.tag}>{b.body}</{b.tag}>" for b in actionable), cwd=cwd, timeout=timeout)
            if trace:
                trace_logs.append(f"[step {step}] Runtime output:\n{runtime_output}")
            messages.append({"role": "assistant", "content": llm_out})
            messages.append({"role": "user", "content": runtime_output})

        # 同一輪可以一邊執行工具，一邊宣告任務完成。
        finals = [b for b in blocks if b.tag == "final"]
        if finals:
            final_body = finals[-1].body.strip()

            # 如果這一輪有實際執行工具，回傳內容要保留完整 runtime transcript，
            # 讓呼叫端既能看到最終結論，也能看到執行細節。
            if runtime_output:
                out = [
                    wrap_json({"ok": True, "done": True, "steps": step, "model": model}),
                    runtime_output,
                ]
                if final_body:
                    out.append(wrap_markdown(final_body))
                if trace and trace_logs:
                    out.append(wrap_markdown("\n\n".join(trace_logs)))
                return "\n".join(out)

            # 如果沒跑工具，但 final 本身像是裸指令，就幫它自動執行一次；
            # 否則把 final 內容當成最終文字答案直接回傳。
            if final_body and is_probably_shell_command(final_body) and not parse_blocks(final_body):
                out = [
                    wrap_json({"ok": True, "done": True, "steps": step, "model": model}),
                    wrap_markdown(f"[auto-exec final] `{final_body}`"),
                    run_shell(final_body, cwd=cwd, timeout=timeout),
                    f"<final>{final_body}</final>",
                ]
                if trace and trace_logs:
                    out.append(wrap_markdown("\n\n".join(trace_logs)))
                return "\n".join(out)

            if trace and trace_logs:
                return "\n".join([wrap_markdown(final_body or "完成"), wrap_markdown("\n\n".join(trace_logs))])
            return wrap_markdown(final_body or "完成")

    out = [
        wrap_json({"ok": False, "error": "max_steps_reached", "max_steps": max_steps, "model": model}),
        wrap_markdown("達到最大步數，任務未完成。"),
    ]
    if trace and trace_logs:
        out.append(wrap_markdown("\n\n".join(trace_logs)))
    return "\n".join(out)


def repl(cwd: Path, timeout: int, model: str, max_steps: int, mode: str, output_mode: str, trace: bool) -> int:
    """互動模式入口，可直接吃 XML 協議，也可吃自然語言任務。"""

    print(
        f"toyclaw ready. mode={mode}, output={output_mode}, trace={trace}. 可輸入 XML（<shell>...</shell>）或自然語言任務。輸入 exit 離開。",
        file=sys.stderr,
    )
    while True:
        try:
            line = input(f"[{mode}] > ")
        except EOFError:
            return 0

        text = line.strip()
        if text.lower() in {"exit", "quit"}:
            return 0
        if not text:
            continue

        # 使用者直接貼 XML 時，代表他要手動操作 runtime；
        # 否則就把輸入當作自然語言任務交給模型迴圈。
        if parse_blocks(text):
            raw = handle_message(text, cwd=cwd, timeout=timeout)
            print(render_output(raw, output_mode=output_mode))
        else:
            raw = run_llm_loop(task=text, model=model, cwd=cwd, timeout=timeout, max_steps=max_steps, mode=mode, trace=trace)
            print(render_output(raw, output_mode=output_mode))


def main() -> int:
    """CLI 入口：支援單次訊息、單次任務、或互動式 REPL。"""

    parser = argparse.ArgumentParser(description="Tiny XML protocol runtime for LLM<->tool calls")
    parser.add_argument("--cwd", default=".", help="working directory for shell commands")
    parser.add_argument("--timeout", type=int, default=30, help="shell timeout seconds")
    parser.add_argument("--message", help="single XML message to process")

    parser.add_argument("--llm-task", help="run task with Ollama loop")
    parser.add_argument("--ollama-model", default="qwen2.5:3b", help="Ollama model name")
    parser.add_argument("--max-steps", type=int, default=8, help="max llm loop steps")
    parser.add_argument("--mode", choices=["auto", "chat", "tool"], default="auto", help="llm mode: auto|chat|tool")
    parser.add_argument("--output", choices=["both", "human", "machine"], default="both", help="display format")
    parser.add_argument("--trace", action="store_true", help="show intermediate LLM/runtime steps")

    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()
    # 提前建立工作目錄，避免後續 shell 執行時因目錄不存在失敗。
    cwd.mkdir(parents=True, exist_ok=True)

    if args.llm_task:
        raw = run_llm_loop(task=args.llm_task, model=args.ollama_model, cwd=cwd, timeout=args.timeout, max_steps=args.max_steps, mode=args.mode, trace=args.trace)
        print(render_output(raw, output_mode=args.output))
        return 0

    if args.message is not None:
        raw = handle_message(args.message, cwd=cwd, timeout=args.timeout)
        print(render_output(raw, output_mode=args.output))
        return 0

    return repl(cwd=cwd, timeout=args.timeout, model=args.ollama_model, max_steps=args.max_steps, mode=args.mode, output_mode=args.output, trace=args.trace)


if __name__ == "__main__":
    raise SystemExit(main())
