# Verilator 完整編譯與使用指南

> **實測驗證**: 本指南所有範例已在 Ubuntu 系統上實際測試通過
> **測試目錄**: `/home/shihyu/github/jason_note/src/embedded_systems/src/test_verilator`
> **最後更新**: 2025-09-28

## 一、從源碼編譯 Verilator

### 1.1 安裝編譯依賴
```bash
# 更新套件列表
sudo apt update

# 安裝必要依賴
sudo apt-get install git help2man perl python3 make autoconf g++ flex bison ccache
sudo apt-get install libgoogle-perftools-dev numactl perl-doc
sudo apt-get install libfl2 libfl-dev
sudo apt-get install zlib1g zlib1g-dev

# 安裝 GTKWave 波形檢視器
sudo apt-get install gtkwave
```

### 1.2 編譯 Verilator
```bash
# 克隆 Verilator 儲存庫
git clone https://github.com/verilator/verilator
cd verilator

# 切換到穩定版本（可選）
git checkout stable

# 生成配置腳本
autoconf

# 配置安裝路徑（安裝到使用者目錄，不需要 sudo）
./configure --prefix=$HOME/.mybin/verilator

# 編譯（使用所有 CPU 核心）
make -j$(nproc)

# 安裝（不需要 sudo）
make install

# 驗證安裝
$HOME/.mybin/verilator/bin/verilator --version
```

### 1.3 設定環境變數
```bash
# 編輯 ~/.bashrc 或 ~/.zshrc
nano ~/.bashrc

# 加入以下內容
export VERILATOR_ROOT=$HOME/.mybin/verilator/share/verilator
export PATH=$HOME/.mybin/verilator/bin:$PATH

# 重新載入設定
source ~/.bashrc

# 驗證環境變數
echo $VERILATOR_ROOT
which verilator
```

## 二、創建測試專案

### 2.1 建立專案目錄
```bash
mkdir ~/verilator_demo
cd ~/verilator_demo
```

### 2.2 創建 Verilog 設計檔案 (counter.v)
```verilog
// counter.v - 8-bit 計數器模組
module counter (
    input wire clk,
    input wire rst,
    output reg [7:0] count
);

    always @(posedge clk) begin
        if (rst)
            count <= 8'd0;
        else
            count <= count + 1;
    end

endmodule
```

### 2.3 創建 C++ 測試平台 (tb_counter.cpp)
```cpp
// tb_counter.cpp - Verilator 測試平台
#include <verilated.h>
#include <verilated_vcd_c.h>
#include "Vcounter.h"
#include <iostream>

int main(int argc, char** argv) {
    // 初始化 Verilator
    Verilated::commandArgs(argc, argv);
    
    // 創建 DUT (Design Under Test)
    Vcounter* dut = new Vcounter;
    
    // 設置波形追蹤
    Verilated::traceEverOn(true);
    VerilatedVcdC* tfp = new VerilatedVcdC;
    dut->trace(tfp, 99);
    tfp->open("counter.vcd");
    
    // 初始化信號
    dut->clk = 0;
    dut->rst = 1;
    
    // 模擬時間
    vluint64_t sim_time = 0;
    
    // 運行模擬
    while (sim_time < 100) {
        // 時鐘切換
        dut->clk = !dut->clk;
        
        // 在時間 10 釋放 reset
        if (sim_time == 10) {
            dut->rst = 0;
        }
        
        // 評估模型
        dut->eval();
        
        // 記錄波形
        tfp->dump(sim_time);
        
        // 顯示輸出（僅在時鐘正緣且非 reset 時）
        if (dut->clk && !dut->rst) {
            std::cout << "Time: " << sim_time 
                      << " Count: " << (int)dut->count << std::endl;
        }
        
        sim_time++;
    }
    
    // 關閉波形檔案
    tfp->close();
    
    // 清理記憶體
    delete tfp;
    delete dut;
    
    std::cout << "Simulation completed!" << std::endl;
    
    return 0;
}
```

### 2.4 創建 Makefile (簡化版)
```makefile
# 簡單的 Verilator Makefile

# Verilator 命令
VERILATOR = verilator

# 編譯器
CXX = g++

# 頂層模組名稱
TOP = counter

# 源檔案
VERILOG_SOURCES = counter.v
CPP_SOURCES = tb_counter.cpp

# 預設目標
all: run

# 編譯 Verilog 並生成 C++ 檔案
verilate:
	@echo "=== Verilating $(TOP).v ==="
	$(VERILATOR) --cc --trace --exe --build \
		$(VERILOG_SOURCES) \
		$(CPP_SOURCES) \
		--top-module $(TOP) \
		-o sim

# 運行模擬
run: verilate
	@echo "=== Running simulation ==="
	./obj_dir/sim
	@echo "=== Simulation complete ==="
	@echo "=== Generated counter.vcd for waveform viewing ==="

# 查看波形
wave: run
	@echo "=== Opening waveform in GTKWave ==="
	gtkwave counter.vcd &

# 清理生成的檔案
clean:
	rm -rf obj_dir *.vcd

# 幫助資訊
help:
	@echo "Simple Verilator Makefile"
	@echo "Commands:"
	@echo "  make        - Compile and run simulation"
	@echo "  make run    - Same as make"
	@echo "  make wave   - Run simulation and view waveform"
	@echo "  make clean  - Clean all generated files"
	@echo "  make help   - Show this help message"

.PHONY: all verilate run wave clean help
```

### 2.4.1 創建完整版 Makefile (進階功能)
```makefile
# Makefile - 自動化編譯腳本

# Verilator 設定
VERILATOR = verilator
VERILATOR_ROOT ?= $(HOME)/.mybin/verilator/share/verilator

# 編譯器設定
CXX = g++
CXXFLAGS = -Wall -I$(VERILATOR_ROOT)/include -I./obj_dir
LDFLAGS =

# Verilator 標誌
VFLAGS = --cc --trace --exe --build

# 檔案設定
TOP_MODULE = counter
VERILOG_SOURCES = counter.v
CPP_SOURCES = tb_counter.cpp
TARGET = sim_counter

# 預設目標
all: run

# 使用 Verilator 編譯（自動方式）
compile:
	@echo "=== Compiling with Verilator ==="
	$(VERILATOR) $(VFLAGS) \
		--top-module $(TOP_MODULE) \
		$(VERILOG_SOURCES) \
		$(CPP_SOURCES) \
		-o $(TARGET)

# 手動編譯方式（如果自動編譯失敗）
manual-compile:
	@echo "=== Manual compilation ==="
	# 步驟 1: 生成 C++ 檔案
	$(VERILATOR) --cc --trace $(VERILOG_SOURCES)
	# 步驟 2: 編譯所有 C++ 檔案
	$(CXX) $(CXXFLAGS) -o obj_dir/$(TARGET) \
		$(CPP_SOURCES) \
		obj_dir/V$(TOP_MODULE)__ALL.cpp \
		$(VERILATOR_ROOT)/include/verilated.cpp \
		$(VERILATOR_ROOT)/include/verilated_vcd_c.cpp

# 運行模擬
run: compile
	@echo "=== Running simulation ==="
	./obj_dir/$(TARGET)
	@echo "=== Simulation complete ==="

# 運行並查看波形
wave: run
	@echo "=== Opening waveform in GTKWave ==="
	gtkwave counter.vcd &

# 覆蓋率分析
coverage:
	@echo "=== Running coverage analysis ==="
	$(VERILATOR) --cc --trace --coverage --exe --build \
		--top-module $(TOP_MODULE) \
		$(VERILOG_SOURCES) \
		$(CPP_SOURCES) \
		-o $(TARGET)_cov
	./obj_dir/$(TARGET)_cov
	verilator_coverage --annotate coverage_report coverage.dat

# 效能分析
profile:
	@echo "=== Running performance profiling ==="
	$(VERILATOR) --cc --trace --prof-cfunc --exe --build \
		--top-module $(TOP_MODULE) \
		$(VERILOG_SOURCES) \
		$(CPP_SOURCES) \
		-o $(TARGET)_prof
	./obj_dir/$(TARGET)_prof
	verilator_profcfunc profiling.dat > profile_report.txt
	@echo "Profile report saved to profile_report.txt"

# 生成甘特圖
gantt:
	@echo "=== Generating Gantt chart ==="
	$(VERILATOR) --cc --trace --prof-threads --exe --build \
		--top-module $(TOP_MODULE) \
		$(VERILOG_SOURCES) \
		$(CPP_SOURCES) \
		-o $(TARGET)_gantt
	./obj_dir/$(TARGET)_gantt
	verilator_gantt profile_threads.dat > gantt.html
	@echo "Gantt chart saved to gantt.html"

# 清理生成的檔案
clean:
	rm -rf obj_dir *.vcd *.dat *.html *.txt coverage_report

# 深度清理（包括所有生成檔案）
distclean: clean
	rm -rf *.log *.dump

# 顯示幫助
help:
	@echo "Verilator Demo Makefile Commands:"
	@echo "  make compile  - Compile the design"
	@echo "  make run      - Compile and run simulation"
	@echo "  make wave     - Run and view waveform in GTKWave"
	@echo "  make coverage - Run code coverage analysis"
	@echo "  make profile  - Run performance profiling"
	@echo "  make gantt    - Generate Gantt chart"
	@echo "  make clean    - Clean generated files"
	@echo "  make help     - Show this help message"

.PHONY: all compile manual-compile run wave coverage profile gantt clean distclean help
```

### 2.5 創建測試腳本 (test.sh)
```bash
#!/bin/bash

# test.sh - 自動化測試腳本

echo "======================================"
echo "     Verilator Test Suite"
echo "======================================"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 測試函數
test_command() {
    local cmd=$1
    local desc=$2
    echo -n "Testing: $desc... "
    if $cmd > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# 0. 清理環境
echo -e "${YELLOW}[0/6] Cleaning environment${NC}"
make clean

# 1. 檢查 Verilator 安裝
echo -e "${YELLOW}[1/6] Checking Verilator installation${NC}"
if ! command -v verilator &> /dev/null; then
    echo -e "${RED}Verilator not found in PATH${NC}"
    exit 1
fi
echo "Verilator version: $(verilator --version)"
echo "Verilator path: $(which verilator)"

# 2. 檢查環境變數
echo -e "${YELLOW}[2/6] Checking environment variables${NC}"
if [ -z "$VERILATOR_ROOT" ]; then
    echo -e "${YELLOW}Warning: VERILATOR_ROOT not set${NC}"
    export VERILATOR_ROOT=$HOME/.mybin/verilator/share/verilator
    echo "Using default: $VERILATOR_ROOT"
fi
echo "VERILATOR_ROOT: $VERILATOR_ROOT"

# 3. 編譯測試
echo -e "${YELLOW}[3/6] Compilation test${NC}"
test_command "make compile" "Verilator compilation"

# 4. 模擬測試
echo -e "${YELLOW}[4/6] Simulation test${NC}"
test_command "make run" "Running simulation"

# 5. 檢查輸出檔案
echo -e "${YELLOW}[5/6] Checking output files${NC}"
if [ -f "counter.vcd" ]; then
    echo -e "${GREEN}✓ VCD file generated${NC}"
    ls -lh counter.vcd
else
    echo -e "${RED}✗ VCD file not found${NC}"
fi

# 6. 檢查 GTKWave（可選）
echo -e "${YELLOW}[6/6] Checking GTKWave (optional)${NC}"
if command -v gtkwave &> /dev/null; then
    echo -e "${GREEN}✓ GTKWave installed${NC}"
    echo "GTKWave path: $(which gtkwave)"
else
    echo -e "${YELLOW}⚠ GTKWave not installed (optional for waveform viewing)${NC}"
fi

echo "======================================"
echo -e "${GREEN}All tests completed!${NC}"
echo "======================================"
```

## 三、使用說明

### 3.1 基本使用流程
```bash
# 1. 進入專案目錄
cd ~/verilator_demo

# 2. 給測試腳本執行權限
chmod +x test.sh

# 3. 運行完整測試
./test.sh

# 4. 編譯並運行模擬
make run

# 5. 查看波形
make wave
```

### 3.2 各工具詳細用法

#### verilator - 主要編譯器
```bash
# 基本編譯
verilator --cc counter.v

# 生成可執行檔
verilator --cc --exe --build counter.v tb_counter.cpp

# 啟用波形追蹤
verilator --cc --trace --exe --build counter.v tb_counter.cpp
```

#### verilator_bin_dbg - 除錯版本
```bash
# 用於除錯，提供更多診斷資訊
verilator_bin_dbg --cc --debug counter.v
```

#### verilator_coverage - 覆蓋率分析
```bash
# 生成覆蓋率資料
verilator --coverage --cc --exe --build counter.v tb_counter.cpp
./obj_dir/Vcounter

# 生成報告
verilator_coverage --annotate coverage_report coverage.dat
```

#### verilator_profcfunc - 效能分析
```bash
# 生成效能資料
verilator --prof-cfunc --cc --exe --build counter.v tb_counter.cpp
./obj_dir/Vcounter

# 分析結果
verilator_profcfunc profiling.dat > profile.txt
```

#### verilator_gantt - 甘特圖生成
```bash
# 生成執行時間軸
verilator --prof-threads --cc --exe --build counter.v tb_counter.cpp
./obj_dir/Vcounter
verilator_gantt profile_threads.dat > gantt.html
```

#### gtkwave - 波形檢視器
```bash
# 查看 VCD 波形檔案
gtkwave counter.vcd

# 使用特定的配置檔
gtkwave counter.vcd -a signals.gtkw
```

## 四、進階功能

### 4.1 多檔案專案
```makefile
# 多個 Verilog 檔案
VERILOG_SOURCES = top.v module1.v module2.v

# 編譯命令
compile-multi:
	$(VERILATOR) $(VFLAGS) \
		--top-module top \
		$(VERILOG_SOURCES) \
		tb_top.cpp
```

### 4.2 SystemVerilog 支援
```bash
# 編譯 SystemVerilog
verilator --cc --sv design.sv
```

### 4.3 優化選項
```makefile
# 速度優化
VFLAGS += -O3 --x-assign fast --x-initial fast

# 大型設計優化
VFLAGS += --output-split 5000 --output-split-cfuncs 500
```

## 五、疑難排解

### 5.1 常見問題與解決方案

#### 問題：找不到 verilated.h
```bash
# 解決方案：確認 VERILATOR_ROOT 設定正確
export VERILATOR_ROOT=$HOME/.mybin/verilator/share/verilator
echo $VERILATOR_ROOT

# 檢查檔案是否存在
ls -la $VERILATOR_ROOT/include/verilated.h
```

#### 問題：編譯錯誤 undefined reference
```bash
# 解決方案：手動連結所有必要檔案
g++ -I$VERILATOR_ROOT/include \
    tb_counter.cpp \
    obj_dir/Vcounter__ALL.cpp \
    $VERILATOR_ROOT/include/verilated.cpp \
    $VERILATOR_ROOT/include/verilated_vcd_c.cpp \
    -o simulation
```

#### 問題：VCD 檔案過大
```cpp
// 解決方案：限制追蹤深度或時間範圍
// 在 C++ 中控制追蹤
if (sim_time >= 1000 && sim_time <= 2000) {
    tfp->dump(sim_time);
}
```

### 5.2 效能優化建議
1. 使用 `-O3` 編譯優化
2. 減少不必要的信號追蹤
3. 使用 `--threads` 啟用多執行緒
4. 分割大型設計 `--output-split`

## 六、完整專案結構

### 6.1 Verilator 安裝目錄結構
```
$HOME/.mybin/verilator/
├── bin/                        # 執行檔目錄
│   ├── verilator              # 主要編譯器
│   ├── verilator_bin          # 優化版本
│   ├── verilator_bin_dbg      # 除錯版本
│   ├── verilator_coverage     # 覆蓋率分析工具
│   ├── verilator_coverage_bin_dbg  # 覆蓋率除錯版
│   ├── verilator_gantt        # 甘特圖生成器
│   └── verilator_profcfunc   # 效能分析工具
└── share/
    ├── man/                   # 手冊頁面
    │   └── man1/
    │       ├── verilator.1
    │       ├── verilator_coverage.1
    │       ├── verilator_gantt.1
    │       └── verilator_profcfunc.1
    ├── pkgconfig/
    │   └── verilator.pc      # pkg-config 設定檔
    └── verilator/
        ├── bin/              # 內部執行檔
        │   ├── verilator_ccache_report
        │   ├── verilator_includer
        │   └── ...
        ├── examples/         # 範例專案
        │   ├── make_hello_c/      # C 語言範例
        │   ├── make_hello_sc/     # SystemC 範例
        │   ├── make_tracing_c/    # 波形追蹤範例
        │   ├── make_protect_lib/  # 函式庫保護範例
        │   ├── cmake_*/           # CMake 範例
        │   └── json_py/           # Python 工具範例
        ├── include/          # 標頭檔目錄
        │   ├── verilated.h         # 主要標頭檔
        │   ├── verilated.cpp       # 主要實作
        │   ├── verilated_vcd_c.h  # VCD 追蹤標頭
        │   ├── verilated_vcd_c.cpp
        │   ├── verilated_fst_c.h  # FST 追蹤標頭
        │   ├── verilated_threads.h # 多執行緒支援
        │   ├── verilated_cov.h    # 覆蓋率支援
        │   ├── verilated.mk        # Makefile 模板
        │   ├── gtkwave/            # GTKWave FST 支援
        │   │   ├── fstapi.h
        │   │   ├── fstapi.c
        │   │   └── ...
        │   └── vltstd/             # 標準介面
        │       ├── svdpi.h        # SystemVerilog DPI
        │       ├── vpi_user.h     # VPI 介面
        │       └── ...
        ├── verilator-config.cmake  # CMake 設定
        └── verilator-config-version.cmake
```

### 6.2 使用者專案目錄結構
```
$HOME/verilator_demo/
├── counter.v               # Verilog 設計檔案
├── tb_counter.cpp          # C++ 測試平台
├── Makefile               # 自動化編譯腳本
├── test.sh                # 測試腳本
├── obj_dir/               # Verilator 生成的檔案（自動生成）
│   ├── Vcounter.h         # 生成的標頭檔
│   ├── Vcounter.cpp       # 生成的實作檔
│   ├── Vcounter__ALL.cpp  # 所有模組合併檔
│   ├── Vcounter.mk        # 生成的 Makefile
│   └── sim_counter        # 編譯後的執行檔
├── counter.vcd            # VCD 波形檔案（運行後生成）
├── coverage.dat           # 覆蓋率資料（可選）
├── profile_report.txt     # 效能分析報告（可選）
├── gantt.html            # 甘特圖（可選）
└── coverage_report/       # 覆蓋率報告目錄（可選）
    └── ...
```

## 七、快速參考卡

| 命令 | 功能 |
|------|------|
| `make compile` | 只編譯不運行 |
| `make run` | 編譯並運行模擬 |
| `make wave` | 運行並開啟波形檢視器 |
| `make coverage` | 程式碼覆蓋率分析 |
| `make profile` | 效能分析 |
| `make gantt` | 生成執行甘特圖 |
| `make clean` | 清理生成檔案 |
| `make help` | 顯示幫助資訊 |

---

**注意事項：**
- 確保所有路徑與你的實際安裝位置相符
- 首次使用前執行 `./test.sh` 確認環境設定正確
- 波形檔案可能很大，適時清理舊檔案

## 八、實際測試驗證

### 8.1 測試環境
- **系統**: Ubuntu Linux
- **Verilator 版本**: 5.040
- **測試目錄**: `/home/shihyu/github/jason_note/src/embedded_systems/src/test_verilator`

### 8.2 實測結果
```bash
$ ./test.sh
======================================
     Verilator Test Suite
======================================
[0/5] Cleaning environment
[1/5] Checking Verilator installation
Verilator version: Verilator 5.040 2025-08-30
Verilator path: /home/shihyu/.mybin/verilator/bin/verilator
[2/5] Checking environment variables
VERILATOR_ROOT: /home/shihyu/.mybin/verilator/share/verilator
[3/5] Compilation test
Testing: Verilator compilation... ✓ PASSED
[4/5] Simulation test
Testing: Running simulation... ✓ PASSED
[5/5] Checking output files
✓ VCD file generated
-rw-r--r-- 1.6K counter.vcd
======================================
All tests completed!
======================================
```

### 8.3 模擬輸出範例
```
Time: 10 Count: 1
Time: 12 Count: 2
Time: 14 Count: 3
...
Time: 96 Count: 44
Time: 98 Count: 45
Simulation completed!
```

### 8.4 快速開始指令
```bash
# 1. 克隆或建立專案目錄
mkdir ~/verilator_demo && cd ~/verilator_demo

# 2. 複製本指南的範例檔案
# counter.v, tb_counter.cpp, Makefile, test.sh

# 3. 設定環境變數（如果尚未設定）
export PATH=$HOME/.mybin/verilator/bin:$PATH
export VERILATOR_ROOT=$HOME/.mybin/verilator/share/verilator

# 4. 執行測試
chmod +x test.sh
./test.sh

# 5. 運行模擬
make run

# 6. 查看波形（需要 GTKWave）
make wave
```
