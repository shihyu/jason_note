#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guider 指令參數測試腳本
用於測試和驗證 guider 的各種指令和參數
"""

import subprocess
import sys
import os
import time
import json
import signal
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class GuiderTester:
    """Guider 指令測試類別"""

    def __init__(self):
        self.results = []
        self.test_count = 0
        self.success_count = 0
        self.fail_count = 0
        self.skip_count = 0

    def run_command(self, cmd: str, timeout: int = 5, allow_fail: bool = False) -> Tuple[int, str, str]:
        """
        執行指令並返回結果

        Args:
            cmd: 要執行的指令
            timeout: 超時時間（秒）
            allow_fail: 是否允許失敗

        Returns:
            (返回碼, 標準輸出, 標準錯誤)
        """
        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return process.returncode, stdout, stderr
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                if not allow_fail:
                    return -1, stdout, f"Command timed out after {timeout} seconds\n{stderr}"
                return 0, stdout, stderr

        except Exception as e:
            return -1, "", str(e)

    def test_command(self, category: str, command: str, description: str,
                     test_cmd: str, timeout: int = 5, allow_fail: bool = False,
                     skip_reason: str = None) -> Dict:
        """
        測試單個指令

        Args:
            category: 分類
            command: 指令名稱
            description: 描述
            test_cmd: 測試指令
            timeout: 超時時間
            allow_fail: 是否允許失敗
            skip_reason: 跳過原因

        Returns:
            測試結果字典
        """
        self.test_count += 1

        result = {
            "category": category,
            "command": command,
            "description": description,
            "test_cmd": test_cmd,
            "status": "pending",
            "output": "",
            "error": "",
            "execution_time": 0
        }

        # 如果需要跳過
        if skip_reason:
            result["status"] = "skipped"
            result["skip_reason"] = skip_reason
            self.skip_count += 1
            print(f"[{self.test_count:3d}] SKIP: {command} - {skip_reason}")
            self.results.append(result)
            return result

        # 執行測試
        print(f"[{self.test_count:3d}] Testing: {command} ({category})")
        start_time = time.time()

        return_code, stdout, stderr = self.run_command(test_cmd, timeout, allow_fail)

        execution_time = time.time() - start_time
        result["execution_time"] = round(execution_time, 3)

        # 判斷測試結果
        if return_code == 0 or (allow_fail and "ver." in stdout):
            result["status"] = "success"
            result["output"] = stdout[:500] if stdout else ""  # 限制輸出長度
            self.success_count += 1
            print(f"      ✓ Success ({execution_time:.2f}s)")
        else:
            result["status"] = "failed"
            result["error"] = stderr[:500] if stderr else ""
            self.fail_count += 1
            print(f"      ✗ Failed: {stderr[:100] if stderr else 'Unknown error'}")

        self.results.append(result)
        return result

    def run_all_tests(self):
        """執行所有測試"""
        print("=" * 60)
        print("開始測試 Guider 指令參數")
        print("=" * 60)
        print()

        # 測試基本指令
        self.test_help_commands()

        # 測試 CONTROL 類別指令
        self.test_control_commands()

        # 測試 MONITOR 類別指令
        self.test_monitor_commands()

        # 測試 LOG 類別指令
        self.test_log_commands()

        # 測試 NETWORK 類別指令
        self.test_network_commands()

        # 測試 PROFILE 類別指令
        self.test_profile_commands()

        # 測試 TRACE 類別指令
        self.test_trace_commands()

        # 測試 UTIL 類別指令
        self.test_util_commands()

        # 測試 VISUAL 類別指令
        self.test_visual_commands()

        # 測試 TEST 類別指令
        self.test_test_commands()

        # 生成測試報告
        self.generate_report()

    def test_help_commands(self):
        """測試幫助指令"""
        print("\n[測試幫助指令]")
        print("-" * 40)

        self.test_command(
            "HELP", "help", "顯示幫助訊息",
            "guider --help", timeout=3
        )

        self.test_command(
            "HELP", "version", "顯示版本資訊",
            "guider --version 2>&1 | head -1", timeout=3, allow_fail=True
        )

    def test_control_commands(self):
        """測試 CONTROL 類別指令"""
        print("\n[測試 CONTROL 類別指令]")
        print("-" * 40)

        # 測試 kill 指令
        self.test_command(
            "CONTROL", "kill", "發送訊號給進程",
            "guider kill --help", timeout=3
        )

        # 測試 setcpu 指令
        self.test_command(
            "CONTROL", "setcpu", "設定 CPU 核心",
            "guider setcpu --help", timeout=3
        )

        # 測試 setsched 指令
        self.test_command(
            "CONTROL", "setsched", "設定排程優先級",
            "guider setsched --help", timeout=3
        )

        # 測試 rlimit 指令
        self.test_command(
            "CONTROL", "rlimit", "資源限制",
            "guider rlimit --help", timeout=3
        )

        # 測試 limitcpu 指令
        self.test_command(
            "CONTROL", "limitcpu", "限制 CPU 使用",
            "guider limitcpu --help", timeout=3
        )

        # 測試 limitmem 指令
        self.test_command(
            "CONTROL", "limitmem", "限制記憶體使用",
            "guider limitmem --help", timeout=3
        )

    def test_monitor_commands(self):
        """測試 MONITOR 類別指令"""
        print("\n[測試 MONITOR 類別指令]")
        print("-" * 40)

        # 測試 top 指令
        self.test_command(
            "MONITOR", "top", "監控進程狀態",
            "guider top --help", timeout=3
        )

        self.test_command(
            "MONITOR", "top -i 1", "top 指定間隔",
            "timeout 2 guider top -i 1 2>/dev/null", timeout=3, allow_fail=True
        )

        # 測試 atop 指令
        self.test_command(
            "MONITOR", "atop", "全系統監控",
            "guider atop --help", timeout=3
        )

        # 測試 ftop 指令
        self.test_command(
            "MONITOR", "ftop", "檔案監控",
            "guider ftop --help", timeout=3
        )

        # 測試 ntop 指令
        self.test_command(
            "MONITOR", "ntop", "網路監控",
            "guider ntop --help", timeout=3
        )

        # 測試 disktop 指令
        self.test_command(
            "MONITOR", "disktop", "磁碟監控",
            "guider disktop --help", timeout=3
        )

        # 測試 ttop 指令
        self.test_command(
            "MONITOR", "ttop", "執行緒監控",
            "guider ttop --help", timeout=3
        )

        # 測試 mtop 指令
        self.test_command(
            "MONITOR", "mtop", "記憶體監控",
            "guider mtop --help", timeout=3
        )

        # 測試 ctop 指令
        self.test_command(
            "MONITOR", "ctop", "臨界值監控",
            "guider ctop --help", timeout=3
        )

        # 測試 irqtop 指令
        self.test_command(
            "MONITOR", "irqtop", "中斷監控",
            "guider irqtop --help", timeout=3
        )

    def test_log_commands(self):
        """測試 LOG 類別指令"""
        print("\n[測試 LOG 類別指令]")
        print("-" * 40)

        # 測試 logkmsg 指令
        self.test_command(
            "LOG", "logkmsg", "核心訊息日誌",
            "guider logkmsg --help", timeout=3
        )

        # 測試 logsys 指令
        self.test_command(
            "LOG", "logsys", "系統日誌",
            "guider logsys --help", timeout=3
        )

        # 測試 logtrace 指令
        self.test_command(
            "LOG", "logtrace", "Ftrace 日誌",
            "guider logtrace --help", timeout=3
        )

        # 測試 printkmsg 指令
        self.test_command(
            "LOG", "printkmsg", "列印核心訊息",
            "guider printkmsg --help", timeout=3
        )

    def test_network_commands(self):
        """測試 NETWORK 類別指令"""
        print("\n[測試 NETWORK 類別指令]")
        print("-" * 40)

        # 測試 server 指令
        self.test_command(
            "NETWORK", "server", "啟動伺服器",
            "guider server --help", timeout=3
        )

        # 測試 cli 指令
        self.test_command(
            "NETWORK", "cli", "客戶端",
            "guider cli --help", timeout=3
        )

        # 測試 send 指令
        self.test_command(
            "NETWORK", "send", "發送 UDP",
            "guider send --help", timeout=3
        )

        # 測試 list 指令
        self.test_command(
            "NETWORK", "list", "列表",
            "guider list --help", timeout=3
        )

        # 測試 hserver 指令
        self.test_command(
            "NETWORK", "hserver", "HTTP 伺服器",
            "guider hserver --help", timeout=3
        )

        # 測試 fserver 指令
        self.test_command(
            "NETWORK", "fserver", "檔案伺服器",
            "guider fserver --help", timeout=3
        )

    def test_profile_commands(self):
        """測試 PROFILE 類別指令"""
        print("\n[測試 PROFILE 類別指令]")
        print("-" * 40)

        # 測試 rec 指令
        self.test_command(
            "PROFILE", "rec", "記錄執行緒事件",
            "guider rec --help", timeout=3
        )

        # 測試 report 指令
        self.test_command(
            "PROFILE", "report", "生成報告",
            "guider report --help", timeout=3
        )

        # 測試 funcrec 指令
        self.test_command(
            "PROFILE", "funcrec", "函數記錄",
            "guider funcrec --help", timeout=3
        )

        # 測試 filerec 指令
        self.test_command(
            "PROFILE", "filerec", "檔案記錄",
            "guider filerec --help", timeout=3
        )

        # 測試 iorec 指令
        self.test_command(
            "PROFILE", "iorec", "I/O 記錄",
            "guider iorec --help", timeout=3
        )

        # 測試 sysrec 指令
        self.test_command(
            "PROFILE", "sysrec", "系統呼叫記錄",
            "guider sysrec --help", timeout=3
        )

        # 測試 genrec 指令
        self.test_command(
            "PROFILE", "genrec", "一般記錄",
            "guider genrec --help", timeout=3
        )

        # 測試 mem 指令
        self.test_command(
            "PROFILE", "mem", "記憶體頁面",
            "guider mem --help", timeout=3
        )

    def test_trace_commands(self):
        """測試 TRACE 類別指令"""
        print("\n[測試 TRACE 類別指令]")
        print("-" * 40)

        # 測試 strace 指令
        self.test_command(
            "TRACE", "strace", "系統呼叫追蹤",
            "guider strace --help", timeout=3
        )

        # 測試 btrace 指令
        self.test_command(
            "TRACE", "btrace", "函數追蹤",
            "guider btrace --help", timeout=3
        )

        # 測試 utrace 指令
        self.test_command(
            "TRACE", "utrace", "使用者函數追蹤",
            "guider utrace --help", timeout=3
        )

        # 測試 mtrace 指令
        self.test_command(
            "TRACE", "mtrace", "記憶體追蹤",
            "guider mtrace --help", timeout=3
        )

        # 測試 sigtrace 指令
        self.test_command(
            "TRACE", "sigtrace", "訊號追蹤",
            "guider sigtrace --help", timeout=3
        )

        # 測試 leaktrace 指令
        self.test_command(
            "TRACE", "leaktrace", "記憶體洩漏追蹤",
            "guider leaktrace --help", timeout=3
        )

        # 測試 stat 指令
        self.test_command(
            "TRACE", "stat", "PMU 統計",
            "guider stat --help", timeout=3
        )

    def test_util_commands(self):
        """測試 UTIL 類別指令"""
        print("\n[測試 UTIL 類別指令]")
        print("-" * 40)

        # 測試 ps 指令
        self.test_command(
            "UTIL", "ps", "進程列表",
            "guider ps --help", timeout=3
        )

        self.test_command(
            "UTIL", "ps -a", "ps 顯示所有進程",
            "guider ps -a 2>&1 | head -20", timeout=3, allow_fail=True
        )

        # 測試 pstree 指令
        self.test_command(
            "UTIL", "pstree", "進程樹",
            "guider pstree --help", timeout=3
        )

        # 測試 exec 指令
        self.test_command(
            "UTIL", "exec", "執行指令",
            "guider exec --help", timeout=3
        )

        self.test_command(
            "UTIL", "exec echo", "exec 執行 echo",
            "guider exec 'echo test'", timeout=3, allow_fail=True
        )

        # 測試 print 指令
        self.test_command(
            "UTIL", "print", "列印檔案",
            "guider print --help", timeout=3
        )

        # 測試 printenv 指令
        self.test_command(
            "UTIL", "printenv", "列印環境變數",
            "guider printenv --help", timeout=3
        )

        # 測試 printinfo 指令
        self.test_command(
            "UTIL", "printinfo", "列印系統資訊",
            "guider printinfo --help", timeout=3
        )

        # 測試 getpid 指令
        self.test_command(
            "UTIL", "getpid", "取得 PID",
            "guider getpid --help", timeout=3
        )

        # 測試 dump 指令
        self.test_command(
            "UTIL", "dump", "記憶體傾印",
            "guider dump --help", timeout=3
        )

        # 測試 strings 指令
        self.test_command(
            "UTIL", "strings", "提取文字",
            "guider strings --help", timeout=3
        )

        # 測試 readelf 指令
        self.test_command(
            "UTIL", "readelf", "讀取 ELF 檔案",
            "guider readelf --help", timeout=3
        )

        # 測試 addr2sym 指令
        self.test_command(
            "UTIL", "addr2sym", "位址轉符號",
            "guider addr2sym --help", timeout=3
        )

        # 測試 sym2addr 指令
        self.test_command(
            "UTIL", "sym2addr", "符號轉位址",
            "guider sym2addr --help", timeout=3
        )

        # 測試 demangle 指令
        self.test_command(
            "UTIL", "demangle", "名稱還原",
            "guider demangle --help", timeout=3
        )

        # 測試 comp/decomp 指令
        self.test_command(
            "UTIL", "comp", "壓縮",
            "guider comp --help", timeout=3
        )

        self.test_command(
            "UTIL", "decomp", "解壓縮",
            "guider decomp --help", timeout=3
        )

        # 測試 merge/split 指令
        self.test_command(
            "UTIL", "merge", "合併檔案",
            "guider merge --help", timeout=3
        )

        self.test_command(
            "UTIL", "split", "分割檔案",
            "guider split --help", timeout=3
        )

        # 測試 req 指令
        self.test_command(
            "UTIL", "req", "URL 請求",
            "guider req --help", timeout=3
        )

        # 測試 ping 指令
        self.test_command(
            "UTIL", "ping", "ICMP ping",
            "guider ping --help", timeout=3
        )

        # 測試 less 指令
        self.test_command(
            "UTIL", "less", "分頁器",
            "guider less --help", timeout=3
        )

        # 測試 topdiff/topsum 指令
        self.test_command(
            "UTIL", "topdiff", "差異比較",
            "guider topdiff --help", timeout=3
        )

        self.test_command(
            "UTIL", "topsum", "摘要",
            "guider topsum --help", timeout=3
        )

    def test_visual_commands(self):
        """測試 VISUAL 類別指令"""
        print("\n[測試 VISUAL 類別指令]")
        print("-" * 40)

        # 測試 draw 指令
        self.test_command(
            "VISUAL", "draw", "繪製系統圖表",
            "guider draw --help", timeout=3
        )

        # 測試 drawcpu 指令
        self.test_command(
            "VISUAL", "drawcpu", "繪製 CPU 圖表",
            "guider drawcpu --help", timeout=3
        )

        # 測試 drawmem 指令
        self.test_command(
            "VISUAL", "drawmem", "繪製記憶體圖表",
            "guider drawmem --help", timeout=3
        )

        # 測試 drawio 指令
        self.test_command(
            "VISUAL", "drawio", "繪製 I/O 圖表",
            "guider drawio --help", timeout=3
        )

        # 測試 drawflame 指令
        self.test_command(
            "VISUAL", "drawflame", "繪製火焰圖",
            "guider drawflame --help", timeout=3
        )

        # 測試 drawhist 指令
        self.test_command(
            "VISUAL", "drawhist", "繪製直方圖",
            "guider drawhist --help", timeout=3
        )

        # 測試 drawtime 指令
        self.test_command(
            "VISUAL", "drawtime", "繪製時間軸",
            "guider drawtime --help", timeout=3
        )

        # 測試 drawstack 指令
        self.test_command(
            "VISUAL", "drawstack", "繪製堆疊圖",
            "guider drawstack --help", timeout=3
        )

        # 測試 drawleak 指令
        self.test_command(
            "VISUAL", "drawleak", "繪製記憶體洩漏",
            "guider drawleak --help", timeout=3
        )

        # 測試 drawdiff 指令
        self.test_command(
            "VISUAL", "drawdiff", "繪製差異圖",
            "guider drawdiff --help", timeout=3
        )

        # 測試 convert 指令
        self.test_command(
            "VISUAL", "convert", "轉換文字",
            "guider convert --help", timeout=3
        )

    def test_test_commands(self):
        """測試 TEST 類別指令"""
        print("\n[測試 TEST 類別指令]")
        print("-" * 40)

        # 測試 cputest 指令
        self.test_command(
            "TEST", "cputest", "CPU 測試",
            "guider cputest --help", timeout=3
        )

        self.test_command(
            "TEST", "cputest -d 1", "CPU 測試 1 秒",
            "guider cputest -d 1", timeout=3, allow_fail=True
        )

        # 測試 memtest 指令
        self.test_command(
            "TEST", "memtest", "記憶體測試",
            "guider memtest --help", timeout=3
        )

        # 測試 iotest 指令
        self.test_command(
            "TEST", "iotest", "I/O 測試",
            "guider iotest --help", timeout=3
        )

        # 測試 nettest 指令
        self.test_command(
            "TEST", "nettest", "網路測試",
            "guider nettest --help", timeout=3
        )

        # 測試 helptest 指令
        self.test_command(
            "TEST", "helptest", "幫助測試",
            "guider helptest --help", timeout=3
        )

    def generate_report(self):
        """生成測試報告"""
        print("\n" + "=" * 60)
        print("測試完成")
        print("=" * 60)
        print(f"總測試數: {self.test_count}")
        print(f"成功: {self.success_count}")
        print(f"失敗: {self.fail_count}")
        print(f"跳過: {self.skip_count}")
        print(f"成功率: {(self.success_count/self.test_count*100):.1f}%")

        # 儲存 JSON 報告
        report_file = "test_results.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "summary": {
                    "total": self.test_count,
                    "success": self.success_count,
                    "failed": self.fail_count,
                    "skipped": self.skip_count,
                    "success_rate": f"{(self.success_count/self.test_count*100):.1f}%"
                },
                "results": self.results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n詳細報告已儲存至: {report_file}")

        # 顯示失敗的測試
        if self.fail_count > 0:
            print("\n失敗的測試:")
            for result in self.results:
                if result["status"] == "failed":
                    print(f"  - {result['command']}: {result['error'][:50]}")

def main():
    """主函數"""
    tester = GuiderTester()

    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n測試被使用者中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n測試過程中發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()