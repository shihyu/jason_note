# SlickEdit 破解 — 暴力找出 License Check 位置

## 目標

透過逆向工程定位 `vs` binary 中的 license 驗證邏輯，找到並修改阻止軟體運行的關鍵位址。

---

## 方法一：二進制比對（Static Diff）

### 原理

比對「原始 trial 版」與「已破解版」的 hex 差異，快速找出被修改的 bytes。

### 步驟

```bash
# 1. 備份原始 binary
cp /opt/slickedit/bin/vs /opt/slickedit/bin/vs.original

# 2. 取得已破解版本（或自己修改後）
#    假設你從網路下載到 vs.cracked

# 3. 導出 hex 格式
hexdump -C vs.original > original.hex
hexdump -C vs.cracked > cracked.hex

# 4. 比對差異
diff original.hex cracked.hex

# 輸出範例：
# < 000190f0  0f b6 45 d7 83 c4 4c 5b 5e 5f 5d c3 8b 75 c4 c6  |....L[^_]..u..|
# > 000190f0  b0 01 90 90 83 c4 4c 5b 5e 5f 5d c3 8b 75 c4 c6  |......L[^_]..u..|
```

### 工具

| 工具 | 用途 |
|------|------|
| `hexdump -C` | 導出可讀的 hex dump |
| `diff` | 比對兩檔案差異 |
| `bindiff` | Binja/IDA 的 binary diff 插件 |
| `diaphora` | IDA Pro 的差異比對工具 |

---

## 方法二：動態調試（gdb Debugging）

### 原理

在程式運行時，逐步追蹤 license check 的執行流程，觀察程式在哪裡拒絕運行。

### 常用除錯指令

```bash
gdb /opt/slickedit/bin/vs

# 起始軟體
run

# 中斷在感興趣的 function
break fopen          # 開啟 .lic 檔
break strcmp         # 比對 license 字串
break open           # 開啟檔案
break access         # 檢查檔案是否存在

# 假設找到懷疑的 address
break *0x08049123

# 單步執行
ni    # 下一條指令（不進 function call）
si    # 下一條指令（進入 function call）

# 印出暫存器 / 記憶體
info registers
x/16x $esp          # 看 stack 上的資料
x/s 0x08049000      # 以字串格式顯示記憶體內容

# 繼續執行
continue
```

### 範例：追蹤 license 檔讀取

```bash
# 找出讀取 license 檔的 code
gdb /opt/slickedit/bin/vs
# 在 fopen 下斷點
break fopen
run

# 當斷點觸發時，查看 call stack
backtrace
# 這會顯示 license 驗證的 call chain

# 查看參數（fopen 的 filename）
print (char*) $eax   # 回傳值
print (char*) $esp+4 # 第一個參數 (filename)
```

### 參考：常見 License Check Pattern

```
fopen("./slickedit.lic")  或  fopen("/opt/slickedit/slickedit.lic")
  ↓
讀取檔案內容
  ↓
strstr(內容, "EXP_DATE")    → 找日期欄位
  ↓
atoi(日期字串)              → 轉成數字
  ↓
和今日日期比較
  ↓
過期 → 彈出提示視窗 / 拒絕啟動
```

---

## 方法三：字串搜尋（String Search）

### 原理

License 驗證一定會用到某些關鍵字元串（檔名、錯誤訊息等），搜尋這些字串再反追 trace 到參考位置。

### 步驟

```bash
# 1. 抽出所有可讀字串
strings /opt/slickedit/bin/vs > vs.strings

# 2. 找 license 相關字串
grep -i license vs.strings
grep -i expired vs.strings
grep -i trial vs.strings
grep -i "slickedit.lic" vs.strings
grep -i "not found" vs.strings
grep -i "evaluation" vs.strings

# 3. 取得該字串的 offset
strings -t x /opt/slickedit/bin/vs | grep -i license
# 輸出：  1a3f20 License file not found

# 4. 在 binary 中找到這個字串的 reference
#    （需要 objdump 反組譯）
objdump -d /opt/slickedit/bin/vs | grep -C3 1a3f20

# 5. 用 addr2line 轉成 function 名稱
addr2line -e /opt/slickedit/bin/vs 0x1a3f20
```

### 常用 string 關鍵字參考

| 類別 | 關鍵字 |
|------|--------|
| 檔案 | `slickedit.lic`, `.lic`, `license.dat` |
| 錯誤訊息 | `License not found`, `Evaluation expired`, `Trial period ended` |
| 日期 | `EXP_DATE`, `EXPDATE`, `expiration` |
| 比較 | `greater`, `less`, `today`, `current date` |

---

## 方法四：暴力 Patch Script

### 原理

直接暴力搜尋特定 hex pattern（文中的 machine code 序列），自動找出所有出現位置並替換。

```python
#!/usr/bin/env python3
"""
slickedit_patch.py — 暴力搜尋並修補 license check
"""

import sys

def find_pattern(data, pattern):
    """找出所有符合 pattern 的位置"""
    pattern = bytes.fromhex(pattern.replace(' ', ''))
    results = []
    pos = 0
    while True:
        idx = data.find(pattern, pos)
        if idx == -1:
            break
        results.append(idx)
        pos = idx + 1
    return results

def patch_data(data, offset, new_bytes):
    """在特定 offset 將舊 bytes 換成新 bytes"""
    new_bytes = bytes.fromhex(new_bytes.replace(' ', ''))
    return data[:offset] + new_bytes + data[offset + len(new_bytes):]

def main():
    binary_path = '/opt/slickedit/bin/vs'

    with open(binary_path, 'rb') as f:
        data = f.read()

    print(f"Binary 大小: {len(data)} bytes")

    # 1. 搜尋原始 machine code pattern (文中的例子)
    original_pattern = '0F B6 45 D7 83 C4 4C 5B 5E 5F 5D C3 8B 75 C4 C6'
    print(f"\n搜尋原始 pattern:\n  {original_pattern}")

    found = find_pattern(data, original_pattern)
    if found:
        for offset in found:
            print(f"  ✓ 找到於 offset: 0x{offset:x}")
    else:
        print("  ✗ 找不到（可能已被別的方式修補）")

    # 2. 搜尋破解後的 pattern
    patched_pattern = 'B0 01 90 90 83 C4 4C 5B 5E 5F 5D C3 8B 75 C4 C6'
    print(f"\n搜尋破解後 pattern:\n  {patched_pattern}")

    found2 = find_pattern(data, patched_pattern)
    if found2:
        for offset in found2:
            print(f"  ✓ 找到於 offset: 0x{offset:x} (已修補)")
    else:
        print("  ✗ 找不到（尚未修補）")

    # 3. 若要實際修補
    #    把 offset 0x190f0 處的 0F B6 45 D7 換成 B0 01 90 90
    if found:
        offset = found[0]
        print(f"\n正在修補 offset 0x{offset:x}...")
        new_data = patch_data(data, offset, 'B0 01 90 90')

        with open(binary_path, 'wb') as f:
            f.write(new_data)
        print("  ✓ 修補完成")

if __name__ == '__main__':
    main()
```

### 使用方式

```bash
chmod +x slickedit_patch.py
./slickedit_patch.py
```

---

## 方法五：Hook 系統函式（LD_PRELOAD）

### 原理

不直接修改 binary，而是攔截標準 library call（`fopen`, `open`, `access` 等），在授權檢查前提前返回成功。

### 範例：Hook fopen

```c
/*
hook_license.c
編譯：gcc -shared -fPIC -o hook_license.so hook_license.c -ldl
*/

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>

// 攔截 fopen
FILE* fopen(const char* path, const char* mode) {
    static FILE* (*real_fopen)(const char*, const char*) = NULL;

    if (!real_fopen) {
        real_fopen = dlsym(RTLD_NEXT, "fopen");
    }

    // 當嘗試開啟 license 檔案時，直接回傳 NULL（視為不存在）
    if (strstr(path, ".lic") || strstr(path, "license")) {
        fprintf(stderr, "[hook] fopen 被攔截: %s\n", path);
        return NULL;  // 讓軟體走「找不到 license」的分支
    }

    return real_fopen(path, mode);
}
```

```bash
# 編譯
gcc -shared -fPIC -o hook_license.so hook_license.c -ldl

# 用 LD_PRELOAD 注入
LD_PRELOAD=$(pwd)/hook_license.so /opt/slickedit/bin/vs
```

---

## 實用工具清單

| 工具 | 安裝方式 | 用途 |
|------|----------|------|
| `gdb` | `apt install gdb` | 動態調試 |
| `objdump` | `apt install binutils` | 反組譯 |
| `strings` | `apt install binutils` | 抽出可讀字串 |
| `hexdump` | `apt install util-linux` | Hex 檢視 |
| `ghex` | `apt install ghex` | 圖形化 Hex 編輯 |
| `radare2` | `apt install radare2` | 整合逆向框架 |
| ` IDA Free` | 官網下載 | 專業反組譯工具 |

---

## 執行範例：完整流程

```bash
# Step 1: 字串搜尋，找 license 相關關鍵字
strings -t x /opt/slickedit/bin/vs | grep -i license

# Step 2: 對感興趣的 address 反組譯
objdump -d /opt/slickedit/bin/vs | grep -C5 "license"

# Step 3: 在 gdb 中對關鍵 function 下斷點
gdb /opt/slickedit/bin/vs
(gdb) break fopen
(gdb) run
# ... 逐步追蹤 ...

# Step 4: 確認要修補的位置後，用 Python script 自動修補
./slickedit_patch.py

# Step 5: 驗證修補結果
ghex /opt/slickedit/bin/vs &
# 搜尋 "B0 01 90 90"，確認出現在 0x190f0
```

---

## 破解原理速查表

| 原始 Machine Code | 修補後 | 效果 |
|-----------------|--------|------|
| `0F B6 45 D7` (movzx) | `B0 01 90 90` (mov al,1 + nop) | 強制返回 valid |
| `75` (jnz) | `EB` (jmp) | 無條件跳過檢查 |
| `74` (jz) | `EB` (jmp) | 無條件跳過失敗分支 |
| `0F 84 xx xx xx xx` (je) | `90 90 ...` (nop) | 移除條件跳轉 |

> **核心概念**：License check 通常是一連串 `cmp` + `je/jne` 指令。將「判斷過期就跳到拒絕」的 branch 淹沒（nop），或將「失敗時設 al=0」改成「al=1」，即可繞過檢查。
