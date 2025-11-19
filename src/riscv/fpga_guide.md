# FPGA 學習指南 - 從入門到實踐

## 目錄
1. [FPGA vs 韌體 C 語言開發差異](#fpga-vs-韌體-c-語言開發差異)
2. [FPGA 入門開發板推薦](#fpga-入門開發板推薦)
3. [Tang Nano 9K Ubuntu 開發環境](#tang-nano-9k-ubuntu-開發環境)
4. [Tang Nano 學習專案與路徑](#tang-nano-學習專案與路徑)
5. [FPGA vs CPU 平行運算比較](#fpga-vs-cpu-平行運算比較)

---

## FPGA vs 韌體 C 語言開發差異

### 執行模式的根本差異

#### FPGA（硬體描述）
- 使用 HDL（Hardware Description Language）如 Verilog 或 VHDL
- 描述的是實際的硬體電路結構
- 所有邏輯是**並行執行**的，同時發生
- 直接定義硬體的連接和行為

#### 韌體 C 語言（軟體程式）
- 在微控制器/處理器上執行
- 程式碼是**循序執行**的，一行接一行
- 透過 CPU 指令集來運作
- 需要既有的處理器硬體架構

### 開發思維的差異

#### FPGA 思維
- 電路如何連接
- 時脈域（clock domain）的管理
- 資源使用（LUT、觸發器、記憶體區塊）
- 時序約束（timing constraints）
- 平行處理架構設計

#### C 語言韌體思維
- 程式流程控制
- 記憶體管理
- 中斷處理
- RTOS 或任務排程
- 演算法效率

### 效能特性

#### FPGA 優勢
- 極低延遲（奈秒級）
- 真正的平行處理
- 可以同時處理多個資料流
- 適合高速即時訊號處理

#### C 語言韌體優勢
- 開發速度快
- 除錯相對容易
- 複雜演算法實現較簡單
- 成本較低（使用現成的 MCU）

### 實際應用範例

#### FPGA (Verilog)
```verilog
always @(posedge clk) begin
    if (counter == 50000000) begin
        led <= ~led;
        counter <= 0;
    end else
        counter <= counter + 1;
end
```

#### C 語言韌體
```c
while(1) {
    GPIO_Toggle(LED_PIN);
    delay_ms(1000);
}
```

### 選擇建議

**選 FPGA 當：**
- 需要極高速處理（如高速 ADC 資料處理）
- 需要精確的時序控制
- 需要大量平行運算
- 需要自訂硬體介面

**選 C 語言韌體當：**
- 控制邏輯較複雜
- 需要快速開發原型
- 成本考量重要
- 需要豐富的軟體生態系支援

---

## FPGA 入門開發板推薦

### 入門級開發板（價格親民）

#### 1. Tang Nano 系列（高雲半導體）
- **Tang Nano 9K**：約 $15-25 美元
  - GW1NR-9 FPGA，8640 個 LUT
  - 內建 HDMI 介面、USB-JTAG
  - 適合學習基礎數位邏輯、小型專案

#### 2. iCEBreaker（Lattice）
- 約 $70-80 美元
- Lattice iCE40UP5K FPGA
- 開源工具鏈支援（Yosys + nextpnr）
- 豐富的擴充板（PMOD）

#### 3. Sipeed Lichee Tang Primer
- 約 $30-40 美元
- Anlogic EG4S20 FPGA
- 有 LCD 螢幕接口
- 適合影像處理入門

### 主流學習板

#### 4. Digilent Basys 3（Xilinx）
- 約 $150 美元（學生價更低）
- **Artix-7 FPGA**（XC7A35T）
- 16 個開關、16 個 LED、七段顯示器
- 大學課程常用，教學資源豐富
- 支援 Vivado 免費版本

#### 5. Terasic DE0-Nano（Intel/Altera）
- 約 $80-90 美元
- Cyclone IV FPGA
- 內建加速度計、ADC
- 豐富的 GPIO
- Quartus Prime Lite 免費支援

#### 6. Digilent Arty A7
- 約 $130-250 美元（依規格）
- Artix-7 FPGA（有 35T 和 100T 版本）
- Arduino 相容接頭
- 乙太網路、DDR3 記憶體

### 進階學習板

#### 7. Terasic DE10-Lite
- 約 $85 美元（學術價）
- Intel MAX 10 FPGA
- 豐富的周邊（VGA、加速度計、Arduino 接頭）
- 適合教學和進階專案

#### 8. PYNQ-Z2
- 約 $120-150 美元
- Zynq-7000（ARM + FPGA）
- 支援 Python 程式設計
- 適合軟硬體協同設計

### 選擇建議

- **完全新手（預算有限）**：推薦 Tang Nano 9K
- **系統性學習**：推薦 Basys 3 或 DE0-Nano
- **想學 SoC/軟硬整合**：推薦 PYNQ-Z2

---

## Tang Nano 9K Ubuntu 開發環境

### 方法一：官方 IDE（推薦新手）

#### 高雲官方 IDE - Gowin EDA

```bash
# 1. 下載教育版（免費）
# 從高雲官網下載：https://www.gowinsemi.com/cn/support/download_eda/

# 2. 解壓縮後安裝
tar -xzf Gowin_V1.9.9_linux.tar.gz
cd Gowin_V1.9.9_linux

# 3. 執行 IDE
./IDE/bin/gw_ide

# 4. 安裝 license（教育版免費）
```

#### 燒錄工具 - openFPGALoader

```bash
# 安裝依賴
sudo apt-get install libftdi1-2 libftdi1-dev libhidapi-dev libudev-dev cmake pkg-config git

# 編譯安裝 openFPGALoader
git clone https://github.com/trabucayre/openFPGALoader.git
cd openFPGALoader
mkdir build
cd build
cmake ..
make -j$(nproc)
sudo make install

# 燒錄到 Tang Nano 9K
openFPGALoader -b tangnano9k -f your_design.fs
```

### 方法二：開源工具鏈（進階用戶）

#### Apicula + Yosys + nextpnr

```bash
# 1. 安裝 Python 環境
sudo apt-get install python3 python3-pip python3-venv

# 2. 建立虛擬環境
python3 -m venv fpga-env
source fpga-env/bin/activate

# 3. 安裝 Apicula（高雲 FPGA 支援）
pip install apycula

# 4. 安裝 Yosys（綜合工具）
sudo apt-get install yosys

# 5. 安裝 nextpnr-gowin
git clone https://github.com/YosysHQ/nextpnr.git
cd nextpnr
cmake -DARCH=gowin -DGOWIN_BBA_EXECUTABLE=`which gowin_bba` .
make -j$(nproc)
sudo make install
```

### 完整開發流程範例

#### 1. 寫 Verilog 程式碼

```verilog
// blink.v
module blink(
    input clk,
    output reg [5:0] led
);
    reg [25:0] counter;
    
    always @(posedge clk) begin
        counter <= counter + 1;
        if (counter == 26'd27_000_000) begin  // 約 0.5 秒
            counter <= 0;
            led <= ~led;
        end
    end
endmodule
```

#### 2. 約束檔案（.cst）

```tcl
// tangnano9k.cst
IO_LOC "clk" 52;  // 27MHz 時脈
IO_LOC "led[0]" 10;
IO_LOC "led[1]" 11;
IO_LOC "led[2]" 13;
IO_LOC "led[3]" 14;
IO_LOC "led[4]" 15;
IO_LOC "led[5]" 16;
```

#### 3. 使用開源工具鏈編譯

```bash
# 綜合
yosys -p "read_verilog blink.v; synth_gowin -top blink -json blink.json"

# 佈局佈線
nextpnr-gowin --json blink.json --write blink_pnr.json \
    --device GW1NR-LV9QN88PC6/I5 --family GW1N-9C \
    --cst tangnano9k.cst

# 生成位元流
gowin_pack -d GW1N-9C -o blink.fs blink_pnr.json

# 燒錄
openFPGALoader -b tangnano9k blink.fs
```

### USB 權限設定

```bash
# 建立 udev 規則
sudo nano /etc/udev/rules.d/99-openfpgaloader.rules

# 加入以下內容
ATTR{idVendor}=="0403", ATTR{idProduct}=="6010", MODE="0666", GROUP="plugdev"

# 重新載入規則
sudo udevadm control --reload-rules
sudo udevadm trigger

# 確保用戶在 plugdev 群組
sudo usermod -a -G plugdev $USER
```

---

## Tang Nano 學習專案與路徑

### 基礎數位邏輯學習

#### 入門專案
- **LED 控制**：學習時脈分頻、計數器
- **按鈕消除彈跳**：理解數位訊號處理
- **七段顯示器**：多工掃描、解碼器設計
- **PWM 呼吸燈**：脈波寬度調變原理
- **流水燈花樣**：狀態機設計

#### 核心概念
- 組合邏輯 vs 循序邏輯
- 同步設計、時脈域
- Finite State Machine（FSM）
- 時序約束基礎

### 通訊協定實作

```verilog
// UART 發送器實作範例
module uart_tx(
    input clk,
    input [7:0] data,
    input send,
    output reg tx
);
    // 學習串列通訊原理
    // 鮑率產生、起始/停止位元
endmodule
```

可以實作：
- **UART**：與電腦通訊、debug
- **SPI**：控制 OLED 螢幕、SD 卡
- **I2C**：讀取感測器
- **WS2812**：控制 RGB LED 燈條

### 視訊/顯示專案

Tang Nano 9K 的 HDMI 功能：
- **VGA/HDMI 輸出**：產生視訊時序
- **簡單遊戲**：乒乓球、貪食蛇、俄羅斯方塊
- **字元顯示**：ROM 字型表、framebuffer
- **圖形產生**：幾何圖形、碎形圖案

```verilog
// HDMI 640x480 顯示範例架構
module hdmi_display(
    input clk,
    output hdmi_clk_p,
    output [2:0] hdmi_data_p
);
    // 學習視訊時序
    // H-Sync, V-Sync, blanking
    // RGB 像素產生
endmodule
```

### 數位訊號處理（DSP）

#### 音訊處理
- **蜂鳴器音樂**：頻率產生、音符編碼
- **PDM 麥克風**：數位濾波器
- **音訊效果器**：延遲、混響基礎

#### 訊號產生與處理
- **DDS 訊號產生器**：正弦波、方波
- **FIR 濾波器**：基礎數位濾波
- **FFT 基礎**：頻譜分析入門

### 處理器與電腦架構

#### 軟核 CPU
Tang Nano 9K 可以跑小型 RISC-V！
- **PicoRV32**：精簡 RISC-V 核心
- **自製 CPU**：8 位元或 16 位元簡易處理器

學習內容：
- 指令集架構
- 流水線概念
- 記憶體介面

```verilog
// 簡易 8-bit CPU 架構
module simple_cpu(
    input clk,
    input reset,
    output [7:0] addr,
    inout [7:0] data
);
    // 學習 fetch-decode-execute
    // 暫存器、ALU、控制單元
endmodule
```

### 實用專案範例

1. **邏輯分析儀**
   - 多通道訊號擷取
   - 觸發條件設定
   - UART 傳送數據到 PC

2. **復古遊戲機**
   - NES 遊戲模擬器的 PPU
   - 簡單的 8-bit 遊戲
   - 搖桿控制介面

3. **LED 矩陣控制器**
   - WS2812 LED 動畫
   - 音樂視覺化
   - POV 顯示器

4. **頻率計/訊號產生器**
   - 測量外部訊號頻率
   - 產生各種波形
   - PWM 控制器

### 學習路徑建議

#### 階段一：基礎（1-2 個月）
1. LED、按鈕、基本 I/O
2. 計數器、分頻器
3. FSM 狀態機
4. UART 通訊

#### 階段二：中級（2-3 個月）
1. VGA/HDMI 顯示
2. SPI、I2C 協定
3. 簡單遊戲設計
4. 記憶體控制

#### 階段三：進階（3-6 個月）
1. 軟核 CPU 實作
2. DSP 應用
3. 高速介面
4. 複雜專案整合

### 學習資源

#### GitHub 專案
- [Sipeed 官方範例](https://github.com/sipeed/TangNano-9K-example)
- [社群專案集合](https://github.com/janschiefer/tang-nano-9k-hello-world)

#### 影片教學
- B站：「高雲 FPGA」、「Tang Nano 9K 入門」
- YouTube：搜尋 "Tang Nano 9K projects"

---

## FPGA vs CPU 平行運算比較

### 兩種平行運算的本質差異

#### C 語言多核心（軟體平行）
```c
// 4 核心 CPU 執行
#pragma omp parallel for
for(int i = 0; i < 1000; i++) {
    result[i] = data[i] * 2 + 3;
}
```
- 還是在**執行指令**，只是有 4 個 CPU 同時執行
- 每個核心仍然是**循序處理**它分配到的任務
- 受限於核心數量（4核、8核、16核）
- 需要作業系統排程、context switch

#### FPGA（硬體平行）
```verilog
// 1000 個乘加器同時運算
generate
    for(genvar i = 0; i < 1000; i++) begin
        assign result[i] = data[i] * 2 + 3;
    end
endgenerate
```
- 真的建立了 **1000 個實體乘加器電路**
- 這 1000 個運算在**同一個時脈週期**完成
- 沒有排程、沒有等待、沒有 context switch

### 具體比較範例：影像處理

#### C 語言多核心版本
```c
// 使用 8 核心 CPU
#pragma omp parallel for num_threads(8)
for(int y = 1; y < height-1; y++) {
    for(int x = 1; x < width-1; x++) {
        int sum = 0;
        // 9 個乘加運算，循序執行
        for(int ky = -1; ky <= 1; ky++) {
            for(int kx = -1; kx <= 1; kx++) {
                sum += image[y+ky][x+kx] * kernel[ky+1][kx+1];
            }
        }
        output[y][x] = sum;
    }
}
```

#### FPGA 版本
```verilog
// 9 個乘法器同時運算
always @(posedge clk) begin
    // 這 9 個乘法「同時」發生
    mult[0] <= pixel[0] * kernel[0];
    mult[1] <= pixel[1] * kernel[1];
    mult[2] <= pixel[2] * kernel[2];
    mult[3] <= pixel[3] * kernel[3];
    mult[4] <= pixel[4] * kernel[4];
    mult[5] <= pixel[5] * kernel[5];
    mult[6] <= pixel[6] * kernel[6];
    mult[7] <= pixel[7] * kernel[7];
    mult[8] <= pixel[8] * kernel[8];
    
    // 加法樹也是並行的
    sum <= mult[0] + mult[1] + mult[2] + 
           mult[3] + mult[4] + mult[5] + 
           mult[6] + mult[7] + mult[8];
end
```

### 平行程度的差異

#### CPU 多核心限制
```
處理 1920×1080 影像：
- 單核：2,073,600 個像素循序處理
- 8 核：每核處理 259,200 個像素（仍是循序）
- 最多幾十個核心（伺服器 CPU）
```

#### FPGA 可能的平行度
```
同樣處理 1920×1080 影像：
- 可以建立 100 個卷積運算單元
- 每個單元每週期處理 1 個像素
- 甚至可以 pipeline，每週期輸出多個像素
```

### 實際應用比較：比特幣挖礦

#### CPU（C語言）
```c
// 8 核心 CPU
for(int nonce = start; nonce < end; nonce++) {
    hash = SHA256(SHA256(block_header + nonce));
    if(hash < target) found = true;
}
// 8 核心 = 8 個 hash 平行運算
```

#### FPGA
```verilog
// 可以實例化 1000 個 SHA256 模組
generate
    for(genvar i = 0; i < 1000; i++) begin
        sha256_core hash_unit(
            .data(block_header + nonce + i),
            .hash(hash_result[i])
        );
    end
endgenerate
// 1000 個 SHA256 單元同時運算！
```

### 平行運算的層級

```
平行運算層級比較：

1. 單核心 CPU + SIMD
   └─ 有限的向量運算（如 AVX-512）

2. 多核心 CPU（2-128 核）
   └─ 多個循序執行單元

3. GPU（幾千個核心）
   └─ SIMT 架構，適合規則的平行運算

4. FPGA（只受晶片資源限制）
   └─ 真正的硬體平行，可自定義架構
   └─ 可以有數千個運算單元同時工作
```

### 各有適合的場景

#### CPU 多核心適合
- 複雜的控制邏輯
- 不規則的平行任務
- 需要大量記憶體的運算
- 通用運算

#### FPGA 大量平行適合
- 規則的平行運算（如訊號處理）
- 低延遲要求（金融交易）
- 串流處理（影像、網路封包）
- 自定義運算架構

### 結論

C 語言多核心確實是平行運算，但它是**任務級平行**（task-level parallelism），而 FPGA 提供的是**位元級平行**（bit-level parallelism）和**運算單元級平行**。

打個比方：
- **CPU 多核心**像是有 8 個工人，每個工人還是一次做一件事
- **FPGA**像是可以僱用 1000 個專門的機器人，每個只做特定工作，但全部同時進行

兩者都是平行運算，但平行的粒度和靈活度完全不同！

---

## FPGA vs RISC-V 的關係

### FPGA 和 RISC-V 的本質差異

#### FPGA 是什麼
- **硬體平臺**：可編程的晶片
- 像是「空白的積木盒」
- 你可以在上面建造任何數位電路
- 包括建造一個 CPU！

#### RISC-V 是什麼
- **指令集架構（ISA）**：CPU 的「語言規範」
- 定義 CPU 如何執行指令
- 是開源的 CPU 架構（像 ARM、x86 的替代品）
- 需要實際的硬體來實現

### Tang Nano 9K 的 RISC-V 實現

#### 軟核 RISC-V（最可能）
```verilog
// 在 FPGA 內部用邏輯閘實現一個 RISC-V CPU
module picorv32_core (
    input clk,
    input resetn,
    output [31:0] mem_addr,
    output [31:0] mem_wdata,
    input [31:0] mem_rdata
);
    // RISC-V CPU 的 Verilog 實現
endmodule
```

- **你可以選擇**：要不要在 FPGA 裡放一個 RISC-V CPU
- 可以用 FPGA 的邏輯資源「建造」一個 RISC-V 處理器
- 常見的軟核：PicoRV32、VexRiscv、NEORV32

### 實際運用場景

#### 純 FPGA 模式
```verilog
// 直接寫硬體邏輯，不需要 CPU
module led_controller(
    input clk,
    output [5:0] led
);
    // 純硬體邏輯控制
endmodule
```

#### FPGA + 軟核 RISC-V 模式
```c
// RISC-V 上跑的 C 程式
int main() {
    while(1) {
        GPIO_write(LED_PORT, pattern);
        delay_ms(100);
        complex_algorithm();  // 複雜演算法
    }
}
```

### 混合架構範例
```
┌─────────────────────────────────┐
│      Tang Nano 9K FPGA          │
│                                 │
│  ┌──────────────┐  ┌─────────┐ │
│  │  RISC-V      │  │  自訂   │ │
│  │  軟核 CPU    │←→│  硬體   │ │
│  │  (可選)      │  │  加速器 │ │
│  └──────────────┘  └─────────┘ │
│                                 │
│  ┌──────────────┐  ┌─────────┐ │
│  │   UART       │  │  HDMI   │ │
│  │   控制器     │  │  輸出   │ │
│  └──────────────┘  └─────────┘ │
└─────────────────────────────────┘
```

### 為什麼要在 FPGA 裡放 RISC-V？

**優點**：
1. **彈性控制**：用 C 寫複雜邏輯比 Verilog 簡單
2. **軟硬結合**：RISC-V 負責控制流程，FPGA 硬體加速處理
3. **熟悉的開發**：可以用 GCC、標準 C 庫

**缺點**：
1. **消耗資源**：RISC-V 軟核佔用 FPGA 邏輯
2. **效能限制**：軟核 CPU 通常只能跑 50-100 MHz
3. **複雜度增加**：需要處理軟硬體介面

### Tang Nano 9K 資源分配
```
GW1NR-9 FPGA 總資源：
- 8640 個 LUT
- 6480 個觸發器

如果實現 PicoRV32：
- 約使用 2000-3000 個 LUT
- 剩餘 5000+ LUT 可做其他硬體

你可以選擇：
1. 100% 純 FPGA 邏輯
2. 70% FPGA + 30% RISC-V
3. 根據專案需求調整
```

---

## FPGA vs CPU（ARM/x86）的根本差異

### 晶片類型的根本區別

#### CPU（ARM、x86）- 固定的處理器
```
┌──────────────────────────┐
│     CPU 晶片（固定）      │
│                          │
│  ▣ 算術邏輯單元 (ALU)     │
│  ▣ 控制單元              │
│  ▣ 暫存器組              │  
│  ▣ 快取記憶體            │
│  ▣ 指令解碼器            │
└──────────────────────────┘
```
- **製造時就決定**了所有電路
- 只能執行預定的指令集
- 你寫軟體在上面跑

#### FPGA - 可編程的邏輯晶片
```
┌──────────────────────────┐
│    FPGA 晶片（空白）      │
│                          │
│  □ □ □ □ □ □ □ □        │
│  □ □ □ □ □ □ □ □        │
│  □ □ □ □ □ □ □ □        │
│  □ □ □ □ □ □ □ □        │
│  (可編程邏輯區塊)         │
└──────────────────────────┘
```
- 像是「數位樂高積木」
- 你決定要建造什麼電路
- 可以建造 CPU、GPU 或任何數位電路

### 執行方式完全不同

#### ARM/x86 CPU
```c
// 軟體程式
int sum = a + b;  // CPU 執行 ADD 指令
```
過程：
1. 從記憶體取指令
2. 解碼指令 
3. 執行 ADD 運算
4. 存回結果
（需要多個時脈週期）

#### FPGA
```verilog
// 硬體電路
assign sum = a + b;  // 直接建造加法器
```
過程：
1. 直接用邏輯閘建造加法器電路
2. 訊號通過就得到結果
（一個時脈週期或更少）

### 具體例子：實現乘法

#### ARM CPU 做乘法
```assembly
; ARM 組合語言
MUL R0, R1, R2  ; 使用 CPU 內建的乘法器
```
- 使用 CPU **預先設計好**的乘法單元
- 無法改變乘法器的實作方式

#### x86 CPU 做乘法
```assembly
; x86 組合語言  
IMUL EAX, EBX   ; 使用 Intel 設計的乘法器
```
- 同樣是固定的硬體乘法器
- Intel 或 AMD 設計好的

#### FPGA 做乘法
```verilog
// 你可以選擇不同的實現方式！

// 方式1：直接乘法器
assign result = a * b;

// 方式2：自己設計的移位加法器
module multiplier(
    input [7:0] a, b,
    output [15:0] result
);
    // 自訂乘法邏輯
endmodule

// 方式3：查表法
// 方式4：Booth 演算法
// ... 任何你想要的方式
```

### 形象化比喻

**CPU（ARM/x86）像是：**
- **瑞士刀** 🔪
- 功能固定（刀、剪刀、開瓶器）
- 很方便，拿來就用
- 但你不能把剪刀變成鋸子
- 通用但每個功能不一定最優

**FPGA 像是：**
- **一箱樂高積木** 🧱
- 你決定要組什麼
- 可以組成任何東西
- 今天組汽車，明天可以拆掉組飛機
- 為特定用途最佳化

### 效能與應用場景差異

#### 任務：處理 1000 個數字相加

**ARM/x86 CPU 方式**：
```c
for(int i = 0; i < 1000; i++) {
    sum += array[i];  // 循序，1000 次迴圈
}
```
- 一個一個加
- 需要 1000+ 個時脈週期

**FPGA 方式**：
```verilog
// 建造 1000 個加法器同時運算！
always @(posedge clk) begin
    sum <= array[0] + array[1] + array[2] + ... + array[999];
end
```
- 平行處理
- 幾個時脈週期完成

### 為什麼會有這些不同的晶片？

#### CPU 的優勢與用途
```
優點：
✓ 容易編程（C/Python）
✓ 作業系統支援
✓ 豐富的軟體生態
✓ 適合複雜控制邏輯

應用：
• 個人電腦
• 手機
• 伺服器
• 通用運算
```

#### FPGA 的優勢與用途
```
優點：
✓ 超低延遲
✓ 大量平行處理
✓ 可自訂架構
✓ 硬體級效能

應用：
• 5G 基地臺
• 高頻交易
• AI 推論加速
• 原型設計
```

### 處理器家族定位
```
通用處理器（CPU）
├── x86（Intel, AMD）
│   └── 桌機、筆電、伺服器
├── ARM
│   └── 手機、平板、嵌入式
└── RISC-V
    └── 開源、IoT、嵌入式

可編程邏輯（不是CPU！）
└── FPGA（Xilinx, Intel, Lattice）
    └── 可以變成任何數位電路
```

### 混合型產品 - SoC FPGA
```
┌─────────────────────────┐
│   Xilinx Zynq           │
│  ┌─────┐    ┌────────┐ │
│  │ ARM │ ←→ │  FPGA  │ │
│  │ CPU │    │  邏輯  │ │
│  └─────┘    └────────┘ │
└─────────────────────────┘
```
- 固定的 ARM CPU + 可編程 FPGA
- 結合兩者優點

### 簡單總結比較表

| 特性 | CPU (ARM/x86) | FPGA |
|------|---------------|------|
| 是什麼 | 固定的處理器 | 可編程邏輯晶片 |
| 執行什麼 | 軟體指令 | 硬體電路 |
| 如何改變功能 | 寫新軟體 | 重新配置硬體 |
| 平行能力 | 有限（核心數） | 極高（受資源限制） |
| 開發難度 | 簡單（寫程式） | 困難（設計電路） |
| 延遲 | 微秒級 | 奈秒級 |
| 適合 | 通用運算、控制 | 平行處理、加速 |

**關鍵理解**：
- **CPU** = 買現成的計算機
- **FPGA** = 買電子零件自己組計算機

FPGA 不是 CPU，但 FPGA 可以用來**建造**一個 CPU！

---

## 總結

FPGA 提供了一種與傳統軟體開發完全不同的思維方式。透過 Tang Nano 9K 這樣的入門開發板，你可以用很低的成本開始學習硬體設計的精髓。從簡單的 LED 控制開始，逐步掌握平行處理、時序設計、通訊協定等核心概念，最終能夠設計出自己的數位系統。

關鍵是要動手實作，從簡單的專案開始，逐步挑戰更複雜的設計。FPGA 的學習曲線雖然陡峭，但一旦掌握，你將擁有一種強大的硬體設計能力，能夠解決許多傳統軟體難以處理的問題。

### 重要觀念釐清

1. **FPGA ≠ CPU**：FPGA 是可編程邏輯晶片，不是處理器
2. **FPGA 可以實現 CPU**：用 FPGA 的邏輯資源可以建造一個 CPU（如 RISC-V）
3. **選擇彈性**：可以純用 FPGA、純用軟核 CPU、或混合使用
4. **平行運算差異**：FPGA 是真正的硬體平行，CPU 多核心是任務級平行

### 下一步建議

1. 購買一塊 Tang Nano 9K 開發板
2. 在 Ubuntu 上搭建開發環境
3. 從 LED 閃爍開始第一個專案
4. 逐步學習更複雜的設計
5. 參與社群，分享你的專案

祝你的 FPGA 學習之旅順利！
