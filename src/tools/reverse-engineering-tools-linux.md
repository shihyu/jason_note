# Reverse Engineering CLI Tools for Linux

> 整理 Linux 平台上可使用命令列（CLI）操作的逆向工程工具。
>
> **工具分類標記：**
> - ✅ = 純 CLI，無 GUI
> - ⚙️ = GUI + CLI 雙模式
> - 🔴 = 僅 GUI（不列入本文）
>
> 供 AI Agent 自動化使用。

---

## 目錄

- [核心工具鏈](#核心工具鏈)
- [靜態分析](#靜態分析)
- [動態調試追蹤](#動態調試追蹤)
- [符號執行與模擬](#符號執行與模擬)
- [框架 API](#框架-api)
- [加殼/脫殼](#加殼脫殼)
- [網絡分析](#網絡分析)
- [記憶體分析](#記憶體分析)
- [輔助工具](#輔助工具)
- [AI Agent 使用範例](#ai-agent-使用範例)

---

## 核心工具鏈

### IDA Pro (GUI + CLI)
```
說明: 最專業的商業逆向工程工具
支援: Windows/Linux/macOS
官網: https://hex-rays.com/ida-pro/

CLI 使用 (idal/idat):
  idal -B ./binary           # 反彙編並輸出 .asm
  idal -c -A ./binary       # 自動分析
  idal -o project.idb ./binary  # 指定資料庫輸出
  idal -P+ -o output.txt ./binary  # 輸出分析結果

重要腳本環境:
  IDAPython: IDA 內建 Python 環境
  idc: IDA C 類腳本語言
  idaapi: Python API 框架
```

### Radare2 (必裝)
```
安裝: apt install radare2
核心命令:
  r2 ./binary              # 進入互動模式
  r2 -A ./binary           # 分析所有
  r2 -c "aaa" ./binary     # 自動化分析
  rabin2 -l ./binary       # 列 Libraries
  rabin2 -s ./binary       # 列出 Symbols
  rabin2 -i ./binary       # 列出 Imports
  rabin2 -E ./binary       # 列出 Exports
  rafind2 -z ./binary      # 搜尋字串
  rafind2 -x 414243 ./binary # hex 搜尋
  ragg2 -b ./binary        # 編譯 Shellcode
```

### Ghidra (Headless Mode)
```
安裝: 手動下載 (https://ghidra-sre.org/)
CLI 使用:
  ./ghidraRun -analysis HEADLESS ./project -process ./binary -scriptPath /path/to/scripts -postScript AnalysisScript.java
```

### objdump (binutils 內建)
```
objdump -d ./binary                    # 反彙編
objdump -t ./binary                   # 符號表
objdump -h ./binary                   # Section 標頭
objdump -M intel -d ./binary          # Intel 語法
objdump -D ./binary                   # 反彙編所有
objdump --reloc ./binary              # 重定位資訊
readelf -a ./binary                   # ELF 完整資訊
readelf -s ./binary                   # 符號
readelf -l ./binary                   # Program headers
readelf -h ./binary                   # ELF Header
```

---

## 靜態分析

### nm (符號分析)
```bash
nm ./binary                 # 列出符號
nm -D ./binary              # 動態符號
nm -g ./binary              # 外部符號
nm -u ./binary              # 未定義符號
nm -C ./binary              # demangle C++
```

### strings (搜尋字串)
```bash
strings ./binary                            # 所有可列印字串
strings -n 8 ./binary                       # 長度 >= 8
strings -t x ./binary                       # hex 偏移量
strings -e s ./binary                       # UTF-8
strings -e l ./binary                       # UTF-16LE
strings ./binary | grep -i "password"       # 關鍵字搜尋
```

### file (檔案類型)
```bash
file ./binary
file -z ./binary                           # 偵測嵌入檔案
```

### size (Section 大小)
```bash
size ./binary
size -A -d ./binary                        # System V format
```

### strings + grep 組合技
```bash
# 常見關鍵字搜尋
strings ./binary | grep -E "(http|https|ftp)"
strings ./binary | grep -i "key\|pass\|token\|secret"
```

---

## 動態調試追蹤

### gdb + gef/pwndbg (必裝)
```bash
# 基本使用
gdb ./program
gdb -batch -ex "run" -ex "bt" ./program          # 批次模式
gdb -batch -ex "disassemble main" ./program

# 帶插件
gdb -ex "source /path/to/gef.py" ./program
gdb -ex "source /path/to/pwndbg/gdbinit.py" ./program

# 附加到行程
gdb -p <pid>

# 核心轉儲
gdb ./program -c core.dump
```

### strace (系統呼叫追蹤)
```bash
strace ./program                           # 追蹤所有
strace -f ./program                        # 包含 fork/vfork
strace -e trace=network ./program          # 僅網絡
strace -e trace=file ./program            # 僅檔案
strace -e trace=read,write ./program     # 僅讀寫
strace -p <pid>                           # 附加到行程
strace -c ./program                       # 計數統計
strace -tt -T ./program                    # 時間戳
strace -o output.txt ./program           # 輸出到檔案
str校試 -f -e trace=none -c ./program    # 計時統計
```

### ltrace (動態庫函數追蹤)
```bash
ltrace ./program                           # 追蹤函數
ltrace -f ./program                        # 包含 fork
ltrace -e "malloc,free,realloc" ./program # 僅指定函數
ltrace -i ./program                        # 顯示指令指標
ltrace -p <pid>                           # 附加到行程
ltrace -c ./program                       # 計數統計
```

### lldb (LLVM 調試器)
```bash
lldb ./program
lldb -b -o "run" -o "bt" ./program       # 批次模式
lldb -f ./program -s commands.txt         # 從檔案讀取命令
```

### rr (可重放調試)
```bash
rr record ./program              # 錄製
rr replay                       # 重放
rr replay -g                    # 互動模式
rr show                         # 顯示錄製
```

---

## 符號執行與模擬

### angr (二進制符號執行)
```python
import angr
import claripy

# 基本分析
p = angr.Project('./binary')
cfg = p.analyses.CFGFast()
print(cfg.functions)

# 找漏洞
find = 0x400abc
avoid = [0x400100]
s = p.factory.simulation_manager()
s.explore(find=find, avoid=avoid)
print(s.found[0].state.posix.dumps(0))
```

### Unicorn (CPU 模擬)
```python
from unicorn import *
from unicorn.x86_const import *

mu = Uc(UC_ARCH_X86, UC_MODE_64)
mu.mem_map(0x1000, 2 * 1024 * 1024)
mu.mem_write(0x1000, shellcode)
mu.reg_write(UC_X86_REG_RIP, 0x1000)
mu.emu_start(0x1000, 0x1010)
print(hex(mu.reg_read(UC_X86_REG_RAX)))
```

### capstone (反彙編引擎)
```python
from capstone import *

md = Cs(CS_ARCH_X86, CS_MODE_64)
for i in md.disasm(b'\x90\x90\x90', 0x1000):
    print(f"0x{i.address:x}:\t{i.mnemonic}\t{i.op_str}")
```

### keystone (彙編引擎)
```python
from keystone import *

ks = Ks(KS_ARCH_X86, KS_MODE_64)
encoding, count = ks.asm(b"mov rax, rbx")
print(bytes(encoding).hex())
```

---

## 框架 API

### pwntools (漏洞利用框架)
```python
from pwn import *

# 快速建立 Exploit
io = process('./vulnerable')
io.sendline(b'A' * 64 + p64(0xdeadbeef))
io.interactive()

# 遠程連接
io = remote('target.com', 8080)

# GDB 調試
gdb.attach(io, '''
set disassembly-flavor intel
break *0x400abc
''')

# 打包/解包
payload = flat(b'A' * 64, p64(0x12345678), p32(0xdeadbeef))
payload += b'\x00' * (128 - len(payload))
```

### IDAPython (需 IDA Pro)
```python
import idaapi
import idautils
import idc

# 枚舉函數
for func in idautils.Functions():
    print(hex(func), idc.get_func_name(func))

# 枚舉指令
for func in idautils.Functions():
    for instr in idautils.FuncItems(func):
        print(hex(instr), idc.GetDisasm(instr))

# 搜尋
for seg in idautils.Segments():
    for ref in idautils.DataRefsFrom(seg):
        print(hex(ref))
```

### ROP Gadget 搜尋
```bash
# 安裝
pip install ropper

# 搜尋
ropper --file ./binary --search "pop|ret"
ropper --file ./binary --search "pop rdi|ret"
ropper --file ./binary --ppr                           # pop pop ret
ropper --file ./binary -- GadgetsUntil陇 = 30              # 只顯示 gadget 數

# 搜尋 libc
ropper --file /lib/x86_64-linux-gnu/libc.so.6 --search "pop|ret"
```

### one_gadget (找 libc one_gadget)
```bash
# 安裝
gem install one_gadget

# 使用
one_gadget /lib/x86_64-linux-gnu/libc.so.6
one_gadget /lib/x86_64-linux-gnu/libc.so.6 -f         # 顯示詳細
```

---

## 加殼/脫殼

### UPX
```bash
# 安裝
apt install upx-ucl

# 加殼
upx -1 ./program -o ./program_packed          # 最快壓縮
upx -9 ./program -o ./program_packed         # 最大壓縮

# 脫殼
upx -d ./program_packed -o ./program_unpacked
upx -d -vv ./program_packed                   # 詳細輸出
```

### 自訂脫殼腳本 (Python)
```python
import struct

def unpack_pe(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    # 尋找 MZ header
    e_lfanew = struct.unpack_from('<I', data, 0x3C)[0]
    # 解析並脫殼
    return data

def unpack_elf(shellcode_base, dump_size):
    import subprocess
    result = subprocess.run(['cat', '/proc/self/maps'], capture_output=True, text=True)
    # 解析記憶體映射
    return memory_dump
```

---

## 網絡分析

### tshark (Wireshark CLI)
```bash
# 擷取
tshark -i eth0 -f "port 80" -w capture.pcap
tshark -i any -p                         # 不可見模式

# 分析
tshark -r capture.pcap                  # 讀取
tshark -r capture.pcap -Y "http"        # HTTP 過濾
tshark -r capture.pcap -T fields -e http.request.uri  # 取出欄位
tshark -r capture.pcap -z http,stat      # HTTP 統計
tshark -r capture.pcap -z io,phs        # 協議分組統計
```

### mitmproxy
```bash
# 安裝
pip install mitmproxy

# HTTP/HTTPS 代理（需要設定系統代理）
mitmdump -w output.csv                   # 存為 CSV
mitmdump -r input.csv                   # 重放流量
mitmdump --set addons=true              # 啟用插件

# 腳本模式
mitmdump -s add_header.py               # 自訂腳本
```

### curl (HTTP 測試)
```bash
curl -v http://target.com/api           # 詳細輸出
curl -X POST http://target.com/api -d '{"key":"value"}'
curl -H "Authorization: Bearer TOKEN" http://target.com/api
curl --proxy http://localhost:8080 http://target.com
curl -k                                 # 忽略 SSL 錯誤
```

### nc / ncat (網絡工具)
```bash
nc -lvnp 4444                           # 監聽
nc target.com 8080                      # 連接
ncat --ssl target.com 443                # SSL 連接
ncat -lvnp 4444 --sh-exec "echo hello"  # 執行命令
```

---

## 記憶體分析

### Volatility (記憶體取證)
```bash
# 安裝
pip install volatility3

# 基本使用
vol -f mem.dump linux.pslist                    # 列行程
vol -f mem.dump linux.psaux                     # 行程詳細
vol -f mem.dump linux.netstat                   # 網絡連接
vol -f mem.dump linux.proc_maps                 # 記憶體映射
vol -f mem.dump linux.dump_map -p <pid> -D ./output  # 傾印記憶體

# 搜尋記憶體
vol -f mem.dump linux.yarascan -y "password"    # YARA 掃描
vol -f mem.dump linux.strings -s                # 記憶體字串
```

### LiME (記憶體擷取)
```bash
# 載入模組
insmod ./lime.ko "path=mem.lime format=lime"

# 擷取
dd if=/dev/mem of=mem.lime bs=1M count=4096
```

### Rekall (記憶體分析)
```bash
# 安裝
pip install rekall

# 分析
rekall -f mem.dump pslist
rekall -f mem.dump memstats
rekall -f mem.dump linux_find_dll
```

---

## 輔助工具

### Binwalk (嵌入式分析)
```bash
binwalk firmware.bin                      # 掃描
binwalk -e firmware.bin                   # 提取
binwalk -e --run-as=root firmware.bin   # 自動提取
binwalk -B firmware.bin                   # 僅 entropy
binwalk -A firmware.bin                   # OPCode 分析
binwalk -Y firmware.bin                   # ARM 掃描
```

### YARA (惡意軟體分類)
```bash
# 安裝
pip install yara

# 使用
yara -r rules.yar ./target_directory     # 掃描目錄
yara -s rules.yar ./target_file          # 顯示匹配的規則
yara -g rules.yar ./target_file          # 顯示匹配規則和內容

# 配合使用
yara -r ./malware_rules /path/to/scan
```

### pefile (PE 檔案分析)
```python
import pefile

pe = pefile.PE('./target.exe')
print(f"Entry Point: {hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint)}")
print(f"Sections: {[s.Name.decode().strip() for s in pe.sections]}")
print(f"Imports: {[f'{imp.dll}:{[f.name for f in imp.imports]}' for imp in pe.DIRECTORY_ENTRY_IMPORT]}")

# 枚舉導出函數
if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
    for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        print(f"Export: {exp.name}")
```

### frida CLI (動態 instrumentation)
```bash
# 安裝
pip install frida-tools

# CLI 使用
frida -f ./target_program                 # 附加到新行程
frida -p <pid>                           # 附加到現有行程
frida -U -f ./target_program             # USB 設備

# 腳本
frida -f ./target -l script.js           # 載入腳本
frida -f ./target --no-pause -l script.js

# 列舉函數
frida-trace -i "malloc" -f ./target     # 追蹤 malloc
frida-trace -i "*send*" -f ./target     # 所有 send 函數
```

### hexdump / xxd (十六進制檢視)
```bash
hexdump -C ./binary | head -50            # 標準 hexdump
hexdump -C ./binary | grep -A2 "string"   # 搜尋特定內容
xxd ./binary > dump.hex                  # 轉換為文字
xxd -r dump.hex > binary                # 逆向轉換
```

### dd (資料操作)
```bash
dd if=./binary of=./section.bin bs=1 skip=0x1000 count=0x200  # 擷取片段
dd if=/dev/zero of=output.bin bs=1M count=10  # 建立大檔案
```

---

## AI Agent 使用範例

### 自動化逆向分析腳本
```python
#!/usr/bin/env python3
"""
AI Agent 逆向分析助手
"""
import subprocess
import sys
import os
import json

def run_cmd(cmd):
    """執行命令並返回輸出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout + result.stderr

def analyze_binary(path):
    """完整分析流程"""
    results = {}

    # 1. 檔案類型
    results['file_type'] = run_cmd(f"file {path}")

    # 2. 符號表
    results['symbols'] = run_cmd(f"nm -C {path}")

    # 3. 字串
    results['strings'] = run_cmd(f"strings -n 8 {path}")

    # 4. Section 資訊
    results['sections'] = run_cmd(f"readelf -l {path}")

    # 5. 動態連結
    results['libs'] = run_cmd(f"ldd {path}")

    # 6. 反彙編 (main 函數附近)
    results['disasm'] = run_cmd(f"objdump -M intel -d {path} | grep -A 50 '<main>'")

    return results

def find_vulnerabilities(path):
    """快速漏洞掃描"""
    findings = []

    # 不安全的函數
    unsafe_funcs = ['strcpy', 'strcat', 'gets', 'sprintf', 'scanf']
    for func in unsafe_funcs:
        result = run_cmd(f"objdump -M intel -d {path} | grep '{func}'")
        if result:
            findings.append(f"潜在不安全函数: {func}")

    # 危險權限
    result = run_cmd(f"readelf -d {path} | grep -i 'EXEC'")
    if 'EXEC' in result:
        findings.append("警告: 二进制文件具有EXEC权限")

    return findings

if __name__ == "__main__":
    binary_path = sys.argv[1]
    print(json.dumps(analyze_binary(binary_path), indent=2))
```

### 使用 angr 找漏洞
```python
#!/usr/bin/env python3
"""
使用 angr 自動找漏洞
"""
import angr
import sys

def find_vuln(binary_path):
    p = angr.Project(binary_path, auto_load_libs=False)

    # 找危險函數路徑
    find_addr = p.loader.find_symbol('vulnerable_function').rebased_addr
    avoid_addrs = [p.loader.find_symbol('safe_function').rebased_addr]

    simgr = p.factory.simulation_manager()
    simgr.explore(find=find_addr, avoid=avoid_addrs)

    if simgr.found:
        print(f"找到漏洞路徑: {simgr.found[0].state}")
        return simgr.found[0].state
    return None

if __name__ == "__main__":
    find_vuln(sys.argv[1])
```

---

## 快速參考表

| 用途 | CLI 工具 | 主要命令 |
|------|----------|----------|
| 靜態分析 | radare2 | `r2 -A binary` |
| 靜態分析 | binutils | `objdump -d`, `nm -C`, `readelf -a` |
| 字串搜尋 | strings | `strings -n 8 binary` |
| 動態追蹤 | strace | `strace -f -o out.txt program` |
| 函數追蹤 | ltrace | `ltrace -f -o out.txt program` |
| 調試 | gdb/rr | `gdb binary`, `rr record program` |
| 反彙編 | capstone | Python API |
| 符號執行 | angr | Python API |
| 模擬執行 | unicorn | Python API |
| 漏洞利用 | pwntools | Python API |
| 加脫殼 | upx | `upx -9 -o packed binary` |
| 流量分析 | tshark | `tshark -i eth0 -w cap.pcap` |
| 記憶體分析 | volatility | `vol -f mem.dump linux.pslist` |
| 規則掃描 | yara | `yara -r rules.yar ./` |
| 嵌入式分析 | binwalk | `binwalk -e firmware.bin` |

---

## 安裝脚本
```bash
#!/bin/bash
set -e

sudo apt update
sudo apt install -y \
  radare2 \
  gdb \
  strace \
  ltrace \
  binwalk \
  yara \
  upx-ucl \
  nasm \
  elfutils \
  python3-pip

pip3 install \
  pwntools \
  angr \
  capstone \
  unicorn \
  keystone-engine \
  volatility3 \
  pyelftools \
  pefile \
  lief \
  frida-tools \
  ropper \
  yara

echo "安裝完成!"
```
