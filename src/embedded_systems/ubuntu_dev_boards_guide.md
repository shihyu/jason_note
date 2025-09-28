# Sipeed Tang Primer 25K & Milk-V Duo S Ubuntu 開發環境指南

## 目錄
- [一、Sipeed Tang Primer 25K (FPGA開發板)](#一sipeed-tang-primer-25k-fpga開發板)
  - [開發環境架設](#開發環境架設)
  - [範例程式碼測試](#範例程式碼測試)
- [二、Milk-V Duo S (RISC-V SBC)](#二milk-v-duo-s-risc-v-sbc)
  - [開發環境架設](#開發環境架設-1)
  - [範例程式碼測試](#範例程式碼測試-1)
  - [燒錄與執行](#燒錄與執行)
- [三、快速測試腳本](#三快速測試腳本)

---

## 一、Sipeed Tang Primer 25K (FPGA開發板)

### 開發環境架設

#### 1. 安裝 Gowin IDE (適用於 Tang Primer 25K)

```bash
# 重要提示：Tang Primer 25K 需要使用 Gowin IDE 1.9.9 或更新版本
# 請從高雲半導體官網下載最新版本：
# https://www.gowinsemi.com/en/support/download_eda/

# 方法一：手動下載（推薦）
# 1. 訪問 Gowin 官網下載頁面
# 2. 選擇 Linux 版本的 Gowin IDE (Version >= 1.9.9)
# 3. 下載後解壓縮

# 假設下載的檔案為 Gowin_V1.9.9_linux.tar.gz
tar -xzvf Gowin_V1.9.9_linux.tar.gz
cd IDE/

# 安裝依賴
sudo apt-get update
sudo apt-get install -y libglib2.0-0 libpng16-16 libfreetype6 libfontconfig1 \
                        libxrender1 libsm6 libxext6 libxft2 libncurses5

# 執行 IDE
./gw_ide

# 設定環境變數（根據實際安裝路徑調整）
echo 'export PATH=$PATH:/opt/Gowin/IDE/bin' >> ~/.bashrc
source ~/.bashrc

# 註：教育版 IDE 無需額外申請授權
```

#### 2. 安裝 openFPGALoader (燒錄工具)

```bash
# 安裝依賴
sudo apt-get install -y git cmake libftdi1-dev libhidapi-dev libudev-dev

# 編譯安裝
git clone https://github.com/trabucayre/openFPGALoader.git
cd openFPGALoader
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
```

#### 3. USB 權限設定

```bash
# 新增 udev 規則
sudo tee /etc/udev/rules.d/99-openfpgaloader.rules > /dev/null <<EOF
# Tang Primer 25K
ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010", MODE="0666", GROUP="plugdev"
EOF

# 重新載入規則
sudo udevadm control --reload-rules
sudo udevadm trigger

# 將使用者加入 plugdev 群組
sudo usermod -a -G plugdev $USER
```

### 範例程式碼測試

#### LED 閃爍範例 (Verilog)

建立 `led_blink.v` 檔案：

```verilog
// led_blink.v
module led_blink (
    input wire clk,      // 50MHz 時鐘
    input wire rst_n,    // 重置信號（低電平有效）
    output reg [5:0] led // 6個LED輸出
);

reg [24:0] counter;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        counter <= 25'd0;
        led <= 6'b000001;
    end else begin
        counter <= counter + 1;
        if (counter == 25'd25_000_000) begin  // 0.5秒
            counter <= 25'd0;
            led <= {led[4:0], led[5]};  // 循環點亮
        end
    end
end

endmodule
```

#### 約束檔案 (.cst)

建立 `tang_primer_25k.cst` 檔案：

```tcl
// tang_primer_25k.cst
IO_LOC "clk" 52;
IO_PORT "clk" IO_TYPE=LVCMOS33;

IO_LOC "rst_n" 88;
IO_PORT "rst_n" IO_TYPE=LVCMOS33 PULL_MODE=UP;

IO_LOC "led[0]" 86;
IO_LOC "led[1]" 87;
IO_LOC "led[2]" 89;
IO_LOC "led[3]" 90;
IO_LOC "led[4]" 91;
IO_LOC "led[5]" 92;
IO_PORT "led[0]" IO_TYPE=LVCMOS33 DRIVE=8;
IO_PORT "led[1]" IO_TYPE=LVCMOS33 DRIVE=8;
IO_PORT "led[2]" IO_TYPE=LVCMOS33 DRIVE=8;
IO_PORT "led[3]" IO_TYPE=LVCMOS33 DRIVE=8;
IO_PORT "led[4]" IO_TYPE=LVCMOS33 DRIVE=8;
IO_PORT "led[5]" IO_TYPE=LVCMOS33 DRIVE=8;
```

#### 編譯與燒錄

```bash
# 使用 Gowin IDE GUI 編譯（推薦）
# 1. 開啟 Gowin IDE
# 2. 創建新專案，選擇 GW5A-LV25MG121 晶片
# 3. 加入 led_blink.v 和約束檔案
# 4. 執行 Synthesize → Place & Route → Program Device

# 或使用 openFPGALoader 命令列燒錄
# 編譯後會生成 .fs 檔案
openFPGALoader -b tangprimer25k impl/pnr/led_blink.fs

# 也可以直接燒錄到 Flash
openFPGALoader -b tangprimer25k -f impl/pnr/led_blink.fs
```

---

## 二、Milk-V Duo S (RISC-V SBC)

### 開發環境架設

#### 1. 安裝交叉編譯工具鏈

```bash
# 下載 RISC-V 工具鏈
wget https://github.com/milkv-duo/duo-buildroot-sdk/releases/download/v1.0.0/riscv64-linux-musl-x86_64.tar.xz

# 解壓縮到 /opt
sudo tar -xJf riscv64-linux-musl-x86_64.tar.xz -C /opt/

# 設定環境變數
echo 'export PATH=$PATH:/opt/riscv64-linux-musl-x86_64/bin' >> ~/.bashrc
echo 'export CROSS_COMPILE=riscv64-linux-musl-' >> ~/.bashrc
source ~/.bashrc
```

#### 2. 安裝開發工具

```bash
# 基本開發工具
sudo apt-get install -y build-essential git wget python3 python3-pip
sudo apt-get install -y bc kmod cpio flex bison libssl-dev
sudo apt-get install -y libncurses5-dev libncursesw5-dev

# 串口工具
sudo apt-get install -y minicom picocom screen

# 網路工具
sudo apt-get install -y tftp-hpa tftpd-hpa nfs-kernel-server
```

#### 3. 下載 Duo S SDK

```bash
# Clone SDK
git clone https://github.com/milkv-duo/duo-buildroot-sdk.git
cd duo-buildroot-sdk

# 切換到 Duo S 分支
git checkout develop

# 設定環境
source build/envsetup.sh
# 選擇 milkv-duo-s
```

### 範例程式碼測試

#### 1. Hello World (C程式)

建立 `hello.c` 檔案：

```c
// hello.c
#include <stdio.h>
#include <unistd.h>

int main(void) {
    int i = 0;
    printf("Hello from Milk-V Duo S!\n");
    printf("RISC-V Architecture Test\n");
    
    while(i < 5) {
        printf("Count: %d\n", i);
        sleep(1);
        i++;
    }
    
    return 0;
}
```

編譯指令：

```bash
# 交叉編譯
riscv64-linux-musl-gcc -o hello hello.c

# 或使用 SDK 內的工具鏈
${CROSS_COMPILE}gcc -o hello hello.c
```

#### 2. GPIO LED 控制範例

建立 `gpio_led.c` 檔案：

```c
// gpio_led.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

#define GPIO_PIN "440"  // Duo S 的 LED GPIO
#define GPIO_PATH "/sys/class/gpio"

void gpio_export(const char* pin) {
    int fd = open(GPIO_PATH "/export", O_WRONLY);
    if (fd < 0) return;
    write(fd, pin, strlen(pin));
    close(fd);
}

void gpio_set_direction(const char* pin, const char* direction) {
    char path[64];
    snprintf(path, sizeof(path), GPIO_PATH "/gpio%s/direction", pin);
    int fd = open(path, O_WRONLY);
    if (fd < 0) return;
    write(fd, direction, strlen(direction));
    close(fd);
}

void gpio_write(const char* pin, int value) {
    char path[64];
    char val[2];
    snprintf(path, sizeof(path), GPIO_PATH "/gpio%s/value", pin);
    int fd = open(path, O_WRONLY);
    if (fd < 0) return;
    snprintf(val, sizeof(val), "%d", value);
    write(fd, val, 1);
    close(fd);
}

int main(void) {
    gpio_export(GPIO_PIN);
    gpio_set_direction(GPIO_PIN, "out");
    
    printf("LED Blinking on Milk-V Duo S\n");
    
    for (int i = 0; i < 10; i++) {
        gpio_write(GPIO_PIN, 1);
        printf("LED ON\n");
        sleep(1);
        
        gpio_write(GPIO_PIN, 0);
        printf("LED OFF\n");
        sleep(1);
    }
    
    return 0;
}
```

#### 3. Makefile 範例

建立 `Makefile` 檔案：

```makefile
# Makefile
CROSS_COMPILE ?= riscv64-linux-musl-
CC = $(CROSS_COMPILE)gcc
CFLAGS = -Wall -O2
TARGET = hello gpio_led

all: $(TARGET)

hello: hello.c
	$(CC) $(CFLAGS) -o $@ $<

gpio_led: gpio_led.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(TARGET)

.PHONY: all clean
```

### 燒錄與執行

#### 1. 準備 SD 卡映像

```bash
# 下載官方映像
wget https://github.com/milkv-duo/duo-buildroot-sdk/releases/download/v1.0.0/milkv-duo-s.img.xz

# 解壓縮
xz -d milkv-duo-s.img.xz

# 燒錄到 SD 卡（假設 SD 卡是 /dev/sdX）
# 注意：請確認 SD 卡裝置名稱，避免誤寫其他磁碟
sudo dd if=milkv-duo-s.img of=/dev/sdX bs=4M status=progress
sudo sync
```

#### 2. 串口連接

```bash
# 設定串口參數
# 波特率：115200, 8N1
sudo minicom -D /dev/ttyUSB0 -b 115200

# 或使用 picocom
sudo picocom -b 115200 /dev/ttyUSB0

# 退出 minicom: Ctrl+A, X
# 退出 picocom: Ctrl+A, Ctrl+X
```

#### 3. 透過網路傳輸檔案

在 Ubuntu 主機上：

```bash
# 設定 TFTP 伺服器
sudo systemctl start tftpd-hpa
sudo systemctl enable tftpd-hpa

# 將編譯好的檔案複製到 TFTP 目錄
sudo cp hello gpio_led /srv/tftp/
sudo chmod 755 /srv/tftp/*
```

在 Duo S 上（透過串口終端）：

```bash
# 設定網路
ifconfig eth0 192.168.1.100

# 從 TFTP 伺服器下載檔案
tftp -g -r hello 192.168.1.1
tftp -g -r gpio_led 192.168.1.1

# 執行程式
chmod +x hello gpio_led
./hello
./gpio_led
```

---

## 三、快速測試腳本

建立 `test_boards.sh` 檔案：

```bash
#!/bin/bash
# test_boards.sh
# 開發板環境測試腳本

echo "======================================"
echo "   Board Development Test Script      "
echo "======================================"
echo ""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 檢查函數
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2 found"
        $1 --version 2>&1 | head -n1
        return 0
    else
        echo -e "${RED}✗${NC} $2 not found"
        return 1
    fi
}

# 檢查 RISC-V 工具鏈
echo "=== Checking Development Tools ==="
echo ""
echo "1. RISC-V Toolchain:"
check_command "riscv64-linux-musl-gcc" "RISC-V GCC"

echo ""
echo "2. FPGA Tools:"
check_command "openFPGALoader" "openFPGALoader"

# 檢查 Gowin IDE
echo ""
if [ -d "/opt/Gowin/IDE" ] || [ -f "$(which gw_ide 2>/dev/null)" ]; then
    echo -e "${GREEN}✓${NC} Gowin IDE installed"
else
    echo -e "${RED}✗${NC} Gowin IDE not found"
fi

# 檢查連接的裝置
echo ""
echo "=== Detecting Connected Devices ==="
echo ""

# 偵測 Tang Primer 25K
echo "1. FPGA Boards:"
if lsusb | grep -q "0403:6010"; then
    echo -e "${GREEN}✓${NC} Tang Primer 25K detected"
    lsusb | grep "0403:6010"
else
    echo -e "${RED}✗${NC} Tang Primer 25K not detected"
fi

# 偵測串口設備
echo ""
echo "2. Serial Devices (Duo S):"
if ls /dev/ttyUSB* 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Serial devices found:"
    ls -la /dev/ttyUSB*
else
    echo -e "${RED}✗${NC} No serial devices found"
fi

# 檢查必要的服務
echo ""
echo "=== Checking Services ==="
echo ""

# TFTP 服務
if systemctl is-active --quiet tftpd-hpa; then
    echo -e "${GREEN}✓${NC} TFTP server is running"
else
    echo -e "${RED}✗${NC} TFTP server is not running"
    echo "   Run: sudo systemctl start tftpd-hpa"
fi

# 使用者群組
echo ""
echo "=== User Permissions ==="
if groups | grep -q "plugdev"; then
    echo -e "${GREEN}✓${NC} User is in plugdev group"
else
    echo -e "${RED}✗${NC} User is not in plugdev group"
    echo "   Run: sudo usermod -a -G plugdev $USER"
fi

if groups | grep -q "dialout"; then
    echo -e "${GREEN}✓${NC} User is in dialout group"
else
    echo -e "${RED}✗${NC} User is not in dialout group"
    echo "   Run: sudo usermod -a -G dialout $USER"
fi

echo ""
echo "======================================"
echo "          Test Complete               "
echo "======================================"
```

## 四、常見問題排除

### Tang Primer 25K 問題

1. **USB 裝置無法識別**
   - 檢查 USB 線材是否支援資料傳輸
   - 確認 udev 規則已正確設定
   - 重新插拔 USB 或重啟電腦

2. **Gowin IDE 相關問題**
   - Tang Primer 25K 使用 Gowin IDE (非 TD IDE)
   - 需要版本 >= 1.9.9
   - 教育版無需額外授權
   - 晶片型號：GW5A-LV25MG121

### Milk-V Duo S 問題

1. **串口無法連接**
   ```bash
   # 檢查串口權限
   sudo chmod 666 /dev/ttyUSB0
   # 或將使用者加入 dialout 群組
   sudo usermod -a -G dialout $USER
   ```

2. **SD 卡無法開機**
   - 確認使用至少 8GB 的 SD 卡
   - 使用 Class 10 或以上速度等級
   - 重新燒錄映像檔

3. **網路連接問題**
   ```bash
   # 在 Duo S 上設定靜態 IP
   ifconfig eth0 192.168.1.100 netmask 255.255.255.0
   route add default gw 192.168.1.1
   ```

## 五、實用連結

### Sipeed Tang Primer 25K
- [官方 Wiki](https://wiki.sipeed.com/hardware/en/tang/tang-primer-25k/primer-25k.html)
- [範例程式庫](https://github.com/sipeed/TangPrimer-25K-example)
- [Gowin IDE 下載](https://www.gowinsemi.com/en/support/download_eda/)
- [Gowin 官方文件](http://www.gowinsemi.com.cn/en/support/database/)

### Milk-V Duo S
- [官方文件](https://milkv.io/docs/duo/getting-started/duo-s)
- [GitHub SDK](https://github.com/milkv-duo/duo-buildroot-sdk)
- [社群論壇](https://community.milkv.io/)

## 六、測試驗證結果

### 已驗證項目 (2025-09-28)

✅ **C 程式碼編譯**
- hello.c 和 gpio_led.c 已成功編譯
- Makefile 測試通過
- 程式可正常執行（使用系統 GCC）

✅ **Verilog 程式碼**
- led_blink.v 語法正確
- tang_primer_25k.cst 約束檔案格式正確

✅ **測試腳本**
- test_boards.sh 可正常執行
- 環境檢測功能正常

### 注意事項

- 若無 RISC-V 工具鏈，可先用系統 GCC 測試程式邏輯
- FPGA 工具需要另外下載安裝
- 記得將使用者加入必要的群組（plugdev, dialout）

## 七、進階開發建議

### FPGA 開發建議
1. 使用版本控制管理 Verilog/VHDL 程式碼
2. 建立模擬測試環境 (使用 Verilator 或 iverilog)
3. 學習時序約束的設定
4. 使用 Chipscope/SignalTap 進行除錯

### RISC-V 開發建議
1. 熟悉 Device Tree 配置
2. 學習建立自訂的 Buildroot 套件
3. 開發核心模組驅動程式
4. 使用 GDB 進行遠端除錯

