#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整測試所有 Guider 指令的 --help 參數
"""

import subprocess
import json
import sys
from datetime import datetime

def test_command(cmd):
    """測試單個指令"""
    test_cmd = f"guider {cmd} --help"
    try:
        result = subprocess.run(
            test_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=2
        )
        # 檢查是否有正常輸出
        if result.returncode == 0 or "ver." in result.stdout or "Usage:" in result.stdout:
            return True, "Success"
        else:
            return False, result.stderr[:100] if result.stderr else "No output"
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def main():
    # 所有 182 個指令
    all_commands = {
        "CONTROL": [
            "cgroup", "freeze", "hook", "kill", "tkill", "limitcpu",
            "limitcpuset", "limitcpuw", "limitmem", "limitmemsoft",
            "limitpid", "limitread", "limitwrite", "pause", "remote",
            "rlimit", "setafnt", "setcpu", "setsched"
        ],
        "LOG": [
            "logand", "logdlt", "logjrl", "logkmsg", "logsys", "logtrace",
            "printand", "printdlt", "printjrl", "printkmsg", "printsyslog", "printtrace"
        ],
        "MONITOR": [
            "andtop", "atop", "attop", "bdtop", "bgtop", "btop", "cgtop",
            "contop", "ctop", "dbustop", "disktop", "dlttop", "fetop",
            "ftop", "gfxtop", "irqtop", "kstop", "ktop", "mdtop", "mtop",
            "ntop", "ptop", "pytop", "rtop", "slabtop", "stacktop",
            "systop", "top", "tptop", "trtop", "ttop", "utop", "vtop", "wtop"
        ],
        "NETWORK": [
            "cli", "event", "fserver", "hserver", "list", "send", "server", "start"
        ],
        "PROFILE": [
            "filerec", "funcrec", "genrec", "hprof", "iorec", "mem",
            "rec", "report", "sperf", "sysrec"
        ],
        "TEST": [
            "cputest", "helptest", "iotest", "memtest", "nettest"
        ],
        "TRACE": [
            "btrace", "leaktrace", "mtrace", "pytrace", "sigtrace",
            "stat", "strace", "utrace"
        ],
        "UTIL": [
            "addr2sym", "andcmd", "bugrec", "bugrep", "checkdup", "comp",
            "convlog", "decomp", "demangle", "dirdiff", "dump", "elftree",
            "exec", "fadvise", "flush", "getafnt", "getpid", "getprop",
            "less", "merge", "mkcache", "mnttree", "mount", "ping",
            "print", "printbind", "printboot", "printcg", "printdbus",
            "printdbusintro", "printdbusstat", "printdbussub", "printdir",
            "printenv", "printext", "printinfo", "printkconf", "printns",
            "printsdfile", "printsdinfo", "printsdunit", "printsig",
            "printslab", "printvma", "ps", "pstree", "readahead",
            "readelf", "req", "scrcap", "scrrec", "setprop", "split",
            "strings", "sym2addr", "sync", "sysrq", "systat", "topdiff",
            "topsum", "umount", "watch", "watchprop"
        ],
        "VISUAL": [
            "convert", "draw", "drawavg", "drawbitmap", "drawcpu",
            "drawcpuavg", "drawdelay", "drawdiff", "drawflame",
            "drawflamediff", "drawhist", "drawio", "drawleak",
            "drawmem", "drawmemavg", "drawpri", "drawreq", "drawrss",
            "drawrssavg", "drawstack", "drawtime", "drawviolin",
            "drawvss", "drawvssavg"
        ]
    }

    print("=" * 70)
    print("Guider 指令完整測試")
    print("=" * 70)

    total = 0
    success = 0
    failed = 0
    failed_commands = []

    # 測試每個類別
    for category, commands in all_commands.items():
        print(f"\n[{category}] 測試 {len(commands)} 個指令...")
        cat_success = 0
        cat_failed = 0

        for cmd in commands:
            total += 1
            is_success, msg = test_command(cmd)

            if is_success:
                success += 1
                cat_success += 1
                print(f"  ✓ {cmd}")
            else:
                failed += 1
                cat_failed += 1
                failed_commands.append({
                    "category": category,
                    "command": cmd,
                    "error": msg
                })
                print(f"  ✗ {cmd} - {msg}")

        print(f"  小計: 成功 {cat_success}, 失敗 {cat_failed}")

    # 顯示總結
    print("\n" + "=" * 70)
    print("測試總結")
    print("=" * 70)
    print(f"總計測試: {total} 個指令")
    print(f"成功: {success} 個")
    print(f"失敗: {failed} 個")
    print(f"成功率: {(success/total*100):.1f}%")

    # 顯示失敗的指令
    if failed_commands:
        print("\n" + "=" * 70)
        print("失敗的指令詳情")
        print("=" * 70)
        for item in failed_commands:
            print(f"[{item['category']}] {item['command']}: {item['error']}")

    # 儲存測試結果
    result = {
        "test_date": datetime.now().isoformat(),
        "total": total,
        "success": success,
        "failed": failed,
        "success_rate": f"{(success/total*100):.1f}%",
        "failed_commands": failed_commands
    }

    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n詳細測試結果已儲存至: test_results.json")

    # 返回狀態碼
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())