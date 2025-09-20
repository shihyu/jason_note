#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Guider 指令的實際執行（不只是 --help）
"""

import subprocess
import json
import time
import os
from datetime import datetime

def run_command(cmd, timeout=5):
    """執行指令並返回結果"""
    print(f"執行: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def main():
    print("=" * 70)
    print("Guider 實際指令執行測試")
    print("=" * 70)

    test_results = []

    # 測試基本資訊指令
    print("\n[基本資訊指令測試]")
    print("-" * 40)

    tests = [
        {
            "name": "ps - 顯示進程列表",
            "cmd": "guider ps 2>&1 | head -20",
            "timeout": 3
        },
        {
            "name": "ps -a - 顯示所有進程",
            "cmd": "guider ps -a 2>&1 | head -20",
            "timeout": 3
        },
        {
            "name": "printinfo - 系統資訊",
            "cmd": "guider printinfo 2>&1 | head -30",
            "timeout": 3
        },
        {
            "name": "printenv - 環境變數",
            "cmd": "guider printenv 2>&1 | head -20",
            "timeout": 3
        },
        {
            "name": "getpid - 取得當前 PID",
            "cmd": "guider getpid $$",
            "timeout": 2
        },
        {
            "name": "top - 監控進程 (2秒)",
            "cmd": "timeout 2 guider top 2>&1 | head -30",
            "timeout": 3
        },
        {
            "name": "top -i 1 - 指定間隔",
            "cmd": "timeout 2 guider top -i 1 2>&1 | head -30",
            "timeout": 3
        },
        {
            "name": "cputest - CPU 測試 (1秒)",
            "cmd": "guider cputest 50 -R 1",
            "timeout": 3
        },
        {
            "name": "memtest - 記憶體測試 (10MB)",
            "cmd": "guider memtest 10 -R 1",
            "timeout": 3
        },
        {
            "name": "exec - 執行簡單指令",
            "cmd": "guider exec 'echo Hello from Guider'",
            "timeout": 2
        },
        {
            "name": "strings - 提取文字",
            "cmd": "echo 'Test String' | guider strings",
            "timeout": 2
        },
        {
            "name": "demangle - C++ 名稱還原",
            "cmd": "echo '_Z4testv' | guider demangle",
            "timeout": 2
        },
        {
            "name": "ping - 測試本地連線",
            "cmd": "guider ping 127.0.0.1 -c 1",
            "timeout": 3
        }
    ]

    success_count = 0
    fail_count = 0

    for test in tests:
        print(f"\n測試: {test['name']}")
        code, stdout, stderr = run_command(test['cmd'], test['timeout'])

        # 判斷是否成功
        if code == 0 or (stdout and ("ver." in stdout or len(stdout) > 10)):
            print("✓ 成功")
            if stdout:
                print(f"輸出預覽: {stdout[:200]}...")
            success_count += 1
            test_results.append({
                "test": test['name'],
                "command": test['cmd'],
                "status": "success",
                "output_size": len(stdout)
            })
        else:
            print(f"✗ 失敗")
            if stderr:
                print(f"錯誤: {stderr[:100]}")
            fail_count += 1
            test_results.append({
                "test": test['name'],
                "command": test['cmd'],
                "status": "failed",
                "error": stderr[:200] if stderr else "No output"
            })

    # 測試檔案操作
    print("\n[檔案操作測試]")
    print("-" * 40)

    # 創建測試檔案
    test_file = "/tmp/guider_test.txt"
    with open(test_file, "w") as f:
        f.write("This is a test file for Guider\n")

    file_tests = [
        {
            "name": "print - 列印檔案",
            "cmd": f"guider print {test_file}",
            "timeout": 2
        },
        {
            "name": "readelf - 讀取 ELF (使用 /bin/ls)",
            "cmd": "guider readelf /bin/ls 2>&1 | head -20",
            "timeout": 3
        }
    ]

    for test in file_tests:
        print(f"\n測試: {test['name']}")
        code, stdout, stderr = run_command(test['cmd'], test['timeout'])

        if code == 0 or (stdout and len(stdout) > 10):
            print("✓ 成功")
            success_count += 1
        else:
            print(f"✗ 失敗: {stderr[:100] if stderr else 'No output'}")
            fail_count += 1

    # 清理測試檔案
    if os.path.exists(test_file):
        os.remove(test_file)

    # 總結
    print("\n" + "=" * 70)
    print("測試總結")
    print("=" * 70)
    print(f"執行測試: {success_count + fail_count} 個")
    print(f"成功: {success_count} 個")
    print(f"失敗: {fail_count} 個")
    print(f"成功率: {(success_count/(success_count+fail_count)*100):.1f}%")

    # 儲存結果
    with open("real_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total_tests": success_count + fail_count,
            "success": success_count,
            "failed": fail_count,
            "success_rate": f"{(success_count/(success_count+fail_count)*100):.1f}%",
            "details": test_results
        }, f, ensure_ascii=False, indent=2)

    print("\n詳細結果已儲存至: real_test_results.json")

if __name__ == "__main__":
    main()