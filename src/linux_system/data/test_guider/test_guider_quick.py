#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guider 快速測試腳本 - 只測試 --help 參數
"""

import subprocess
import json
import time
from datetime import datetime

def run_command(cmd, timeout=2):
    """執行指令並返回結果"""
    try:
        process = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def test_commands():
    """測試所有指令的 --help"""

    # 定義所有指令類別和指令
    commands = {
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

    results = []
    total = 0
    success = 0

    print("=" * 60)
    print("開始測試 Guider 指令 --help 參數")
    print("=" * 60)

    for category, cmd_list in commands.items():
        print(f"\n[{category}] ({len(cmd_list)} 個指令)")

        for cmd in cmd_list:
            total += 1
            test_cmd = f"guider {cmd} --help"

            # 執行測試
            return_code, stdout, stderr = run_command(test_cmd, timeout=1)

            # 檢查是否成功
            if return_code == 0 or "ver." in stdout or "Usage:" in stdout:
                success += 1
                status = "✓"
                print(f"  [{total:3d}] {status} {cmd:20s}")

                # 記錄結果
                results.append({
                    "category": category,
                    "command": cmd,
                    "status": "success",
                    "has_help": True
                })
            else:
                status = "✗"
                print(f"  [{total:3d}] {status} {cmd:20s} - Failed")

                results.append({
                    "category": category,
                    "command": cmd,
                    "status": "failed",
                    "has_help": False,
                    "error": stderr[:100] if stderr else "Unknown error"
                })

    # 顯示摘要
    print("\n" + "=" * 60)
    print("測試摘要")
    print("=" * 60)
    print(f"總指令數: {total}")
    print(f"成功: {success}")
    print(f"失敗: {total - success}")
    print(f"成功率: {(success/total*100):.1f}%")

    # 儲存結果
    report = {
        "test_date": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "success": success,
            "failed": total - success,
            "success_rate": f"{(success/total*100):.1f}%"
        },
        "commands": results
    }

    with open("guider_help_test_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n測試結果已儲存至: guider_help_test_results.json")

    return report

if __name__ == "__main__":
    test_commands()