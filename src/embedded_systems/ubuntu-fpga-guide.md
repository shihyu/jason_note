# Ubuntu FPGA 開發環境完整指南

## 目錄
1. [FPGA 開發板選擇](#fpga-開發板選擇)
2. [開發工具安裝](#開發工具安裝)
3. [模擬與除錯工具](#模擬與除錯工具)
4. [RISC-V 開發環境](#risc-v-開發環境)
5. [開源工具鏈](#開源工具鏈)
6. [實用資源連結](#實用資源連結)

---

## FPGA 開發板選擇

### 預算與性能對比表

| 開發板 | 價格 (USD) | FPGA | 記憶體 | 特色 | 開源工具 | 推薦度 |
|--------|------------|------|--------|------|----------|--------|
| **Milk-V Duo S** | $20-25 | - | 512MB | RISC-V硬核+網口 | ✅ | ⭐⭐⭐⭐⭐ |
| **Tang Nano 9K** | $15 | Gowin 9K | 32MB | HDMI、便宜 | ❌ | ⭐⭐⭐⭐ |
| **ColorLight i5** | $30 | ECP5-25K | 32MB | 雙千兆網、改裝板 | ✅ | ⭐⭐⭐⭐⭐ |
| **Tang Primer 25K** | $45 | Gowin 23K | 128MB | PCIe、大記憶體 | ❌ | ⭐⭐⭐⭐ |
| **ColorLight i9** | $50 | ECP5-45K | 32MB | 資源多、雙網口 | ✅ | ⭐⭐⭐⭐⭐ |
| **VisionFive 2** | $55 | - | 4GB | 完整RISC-V電腦 | ✅ | ⭐⭐⭐⭐ |

### 選擇建議
- **初學者最佳**: Milk-V Duo S（便宜、實用、可跑 Linux）
- **FPGA 學習**: ColorLight i5（開源工具鏈）
- **高性能需求**: ColorLight i9 或 Tang Primer 25K

---

## 開發工具安裝

### 1. 基礎開發環境

```bash
# 更新系統
sudo apt update && sudo apt upgrade -y

# 安裝基礎工具
sudo apt install -y \
    build-essential \
    git \
    wget \
    curl \
    python3 \
    python3-pip \
    cmake \
    ninja-build \
    gtkwave \
    vim \
    tmux

# 安裝 Python 套件
pip3 install --user \
    pyserial \
    pillow \
    numpy
```

### 2. Verilator (Verilog 模擬器)

```bash
# 方法一：從套件管理器安裝（簡單但版本較舊）
sudo apt install verilator

# 方法二：從源碼編譯最新版（推薦）
sudo apt-get install git perl python3 make autoconf g++ flex bison ccache
sudo apt-get install libgoogle-perftools-dev numactl perl-doc
sudo apt-get install libfl2 libfl-dev zlibc zlib1g zlib1g-dev

git clone https://github.com/verilator/verilator
cd verilator
git checkout stable
autoconf
./configure --prefix=/usr/local
make -j$(nproc)
sudo make install
```

### 3. GTKWave (波形檢視器)

```bash
# 安裝 GTKWave
sudo apt install gtkwave

# 測試安裝
gtkwave --version
```

### 4. 開源 FPGA 工具鏈

#### Lattice ECP5 工具鏈 (適用於 ColorLight)

```bash
# 安裝 Yosys (綜合工具)
sudo apt install yosys

# 安裝 nextpnr-ecp5 (布局布線)
sudo apt install nextpnr-ecp5

# 安裝 prjtrellis (位流生成)
sudo apt install prjtrellis

# 安裝 openFPGALoader (燒錄工具)
# 方法一：從源碼編譯
git clone https://github.com/trabucayre/openFPGALoader.git
cd openFPGALoader
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
```

#### Gowin 工具鏈 (適用於 Tang Nano/Primer)

```bash
# 下載 Gowin EDA (需要註冊)
# https://www.gowinsemi.com/en/support/download_eda/

# 解壓縮
tar -xzf Gowin_V1.9.9_linux.tar.gz

# 安裝依賴
sudo apt-get install -y \
    libglib2.0-0 \
    libpng16-16 \
    libfreetype6 \
    libfontconfig1 \
    libxrender1 \
    libsm6 \
    libice6 \
    libxext6 \
    libx11-6 \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a

# 設定環境變數 (加入 ~/.bashrc)
export GOWIN_HOME=/path/to/gowin
export PATH=$GOWIN_HOME/IDE/bin:$PATH
export LD_LIBRARY_PATH=$GOWIN_HOME/IDE/lib:$LD_LIBRARY_PATH

# 設定 USB 權限
sudo cp $GOWIN_HOME/IDE/bin/99-gowin.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## 模擬與除錯工具

### Icarus Verilog (另一個模擬器選擇)

```bash
# 安裝 Icarus Verilog
sudo apt install iverilog

# 使用範例
iverilog -o test.vvp testbench.v design.v
vvp test.vvp
gtkwave dump.vcd
```

### 簡單的 Verilog 測試範例

```verilog
// counter.v
module counter(
    input clk,
    input reset,
    output reg [7:0] count
);
    always @(posedge clk) begin
        if (reset)
            count <= 0;
        else
            count <= count + 1;
    end
endmodule

// counter_tb.v
module counter_tb;
    reg clk = 0;
    reg reset = 1;
    wire [7:0] count;
    
    always #5 clk = ~clk;
    
    initial begin
        $dumpfile("counter.vcd");
        $dumpvars(0, counter_tb);
        #20 reset = 0;
        #200 $finish;
    end
    
    counter dut(
        .clk(clk),
        .reset(reset),
        .count(count)
    );
endmodule
```

```bash
# 執行模擬
iverilog -o counter.vvp counter_tb.v counter.v
vvp counter.vvp
gtkwave counter.vcd
```

---

## RISC-V 開發環境

### Milk-V Duo S 開發環境

```bash
# 安裝交叉編譯工具鏈
wget https://github.com/milkv-duo/duo-buildroot-sdk/releases/download/v1.0.0/host-tools.tar.gz
tar -xzf host-tools.tar.gz
export PATH=$PATH:$(pwd)/host-tools/gcc/riscv64-linux-musl-x86_64/bin

# 安裝串口工具
sudo apt install minicom picocom screen

# 設定串口權限
sudo usermod -a -G dialout $USER
# 需要重新登入

# 連接 Duo S
# USB 串口通常是 /dev/ttyUSB0 或 /dev/ttyACM0
minicom -D /dev/ttyUSB0 -b 115200
```

### SSH 連接設定 (Duo S)

```bash
# Duo S 透過網路連接
ssh root@192.168.42.1  # 預設 IP

# 或透過乙太網（Duo S 有 RJ45）
ssh root@[duo-s-ip]

# 設定 SSH 金鑰（免密碼登入）
ssh-keygen -t rsa
ssh-copy-id root@192.168.42.1
```

### 編譯範例程式

```c
// hello.c
#include <stdio.h>

int main() {
    printf("Hello from RISC-V!\n");
    return 0;
}
```

```bash
# 交叉編譯
riscv64-linux-musl-gcc hello.c -o hello

# 傳送到 Duo S
scp hello root@192.168.42.1:/root/

# 在 Duo S 上執行
ssh root@192.168.42.1 ./hello
```

---

## 開源工具鏈

### LiteX (SoC 生成框架)

```bash
# 安裝 LiteX
wget https://raw.githubusercontent.com/enjoy-digital/litex/master/litex_setup.py
python3 litex_setup.py --init --install

# 生成 RISC-V SoC 範例
cd litex-boards/litex_boards/targets
python3 colorlight_i5.py --build --cpu-type vexriscv
```

### RISC-V 軟核實現

```bash
# PicoRV32
git clone https://github.com/YosysHQ/picorv32.git

# VexRiscv
git clone https://github.com/SpinalHDL/VexRiscv.git

# 使用 FuseSoC 管理
pip3 install fusesoc
fusesoc library add fusesoc-cores https://github.com/fusesoc/fusesoc-cores
fusesoc run --target=colorlight_i5 servant
```

---

## 實用資源連結

### 官方資源
- [Milk-V 官方](https://milkv.io/)
- [Sipeed Wiki (Tang 系列)](https://wiki.sipeed.com/)
- [Gowin 半導體](https://www.gowinsemi.com/)
- [Lattice 半導體](https://www.latticesemi.com/)

### 開源專案
- [LiteX Framework](https://github.com/enjoy-digital/litex)
- [Yosys 綜合工具](https://github.com/YosysHQ/yosys)
- [nextpnr 布局布線](https://github.com/YosysHQ/nextpnr)
- [OpenFPGALoader](https://github.com/trabucayre/openFPGALoader)

### ColorLight 改裝資源
- [Chubby75 - ColorLight 5A-75B 逆向](https://github.com/q3k/chubby75)
- [ColorLight i5 資料](https://github.com/tomverbeure/colorlight_i5)
- [ColorLight i9 資料](https://github.com/wuxx/colorlight-i9)

### 學習資源
- [HDLBits - Verilog 練習](https://hdlbits.01xz.net/)
- [FPGA4Fun](https://www.fpga4fun.com/)
- [Nandland FPGA 教程](https://www.nandland.com/)
- [開源 FPGA 工具文檔](https://f4pga.readthedocs.io/)

### 社群
- [1BitSquared Discord](https://discord.gg/c4Dnr3b)
- [##fpga on libera.chat](https://web.libera.chat/##fpga)
- [Reddit r/FPGA](https://www.reddit.com/r/FPGA/)

---

## Vim 開發環境設定

### 安裝 Vim 和相關工具

```bash
# 安裝 Vim 8+ 或 Neovim
sudo apt install vim vim-gtk3  # Vim with clipboard support
# 或
sudo apt install neovim

# 安裝 ctags 和 cscope (程式碼導航)
sudo apt install universal-ctags cscope

# 安裝 ripgrep (快速搜尋)
sudo apt install ripgrep

# 安裝 fzf (模糊搜尋)
git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
~/.fzf/install
```

### Verilog/SystemVerilog Vim 設定

創建或編輯 `~/.vimrc`:

```vim
" === 基礎設定 ===
set nocompatible
filetype plugin indent on
syntax on
set number relativenumber
set expandtab
set tabstop=4
set shiftwidth=4
set autoindent
set smartindent
set hlsearch
set incsearch
set ignorecase
set smartcase
set mouse=a
set clipboard=unnamedplus
set cursorline
set colorcolumn=80
set encoding=utf-8

" === Verilog 特定設定 ===
autocmd FileType verilog,systemverilog setlocal tabstop=2 shiftwidth=2
autocmd FileType verilog,systemverilog setlocal commentstring=//\ %s

" === 快捷鍵設定 ===
" Leader 鍵設為空格
let mapleader=" "

" 快速編譯 Verilog
autocmd FileType verilog nnoremap <leader>c :!iverilog -o %:r.vvp %<CR>
autocmd FileType verilog nnoremap <leader>r :!vvp %:r.vvp<CR>
autocmd FileType verilog nnoremap <leader>w :!gtkwave %:r.vcd &<CR>

" 使用 Verilator
autocmd FileType verilog nnoremap <leader>v :!verilator --cc % --exe --trace<CR>

" === 自動補全括號 ===
inoremap ( ()<Left>
inoremap [ []<Left>
inoremap { {}<Left>
inoremap " ""<Left>

" === Verilog 程式碼片段 ===
" 輸入 ,mod 快速建立 module
autocmd FileType verilog inoreabbrev <buffer> ,mod module ()<CR>endmodule<Up><End><Left>
" 輸入 ,alw 快速建立 always block
autocmd FileType verilog inoreabbrev <buffer> ,alw always @(posedge clk) begin<CR>end<Up><End>
" 輸入 ,iff 快速建立 if-else
autocmd FileType verilog inoreabbrev <buffer> ,iff if () begin<CR>end else begin<CR>end<Up><Up><End><Left><Left><Left><Left><Left><Left><Left>

" === 狀態列 ===
set laststatus=2
set statusline=%F%m%r%h%w\ [%{&ff}]\ [%Y]\ [POS=%l,%v]\ [%p%%]\ [LEN=%L]
```

### 安裝 Vim 插件管理器 (vim-plug)

```bash
# 安裝 vim-plug
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```

### 配置 Vim 插件 (~/.vimrc 續)

```vim
" === vim-plug 插件管理 ===
call plug#begin('~/.vim/plugged')

" Verilog 語法高亮增強
Plug 'vhda/verilog_systemverilog.vim'

" 檔案瀏覽器
Plug 'preservim/nerdtree'

" 模糊搜尋
Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }
Plug 'junegunn/fzf.vim'

" 註釋工具
Plug 'preservim/nerdcommenter'

" Git 整合
Plug 'tpope/vim-fugitive'
Plug 'airblade/vim-gitgutter'

" 自動補全 (選擇性)
" Plug 'neoclide/coc.nvim', {'branch': 'release'}

" 顏色主題
Plug 'morhetz/gruvbox'
Plug 'joshdick/onedark.vim'

" 狀態列美化
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'

" 程式碼標籤
Plug 'preservim/tagbar'

" 多游標
Plug 'terryma/vim-multiple-cursors'

call plug#end()

" === 插件設定 ===
" NERDTree
nnoremap <leader>n :NERDTreeToggle<CR>
let NERDTreeShowHidden=1

" FZF
nnoremap <leader>f :Files<CR>
nnoremap <leader>b :Buffers<CR>
nnoremap <leader>g :Rg<CR>

" Tagbar
nnoremap <leader>t :TagbarToggle<CR>

" 顏色主題
colorscheme gruvbox
set background=dark

" Airline
let g:airline_powerline_fonts = 1
let g:airline#extensions#tabline#enabled = 1
```

### 安裝插件

```bash
# 在 Vim 中執行
:PlugInstall
```

### Verilog 專用工具整合

創建 `~/.vim/ftplugin/verilog.vim`:

```vim
" Verilog 檔案專用設定

" === Verilator 整合 ===
function! VerilatorCompile()
    let l:filename = expand('%')
    let l:output = system('verilator --lint-only ' . l:filename . ' 2>&1')
    if v:shell_error != 0
        echo l:output
    else
        echo "Verilator: No lint errors found!"
    endif
endfunction

nnoremap <buffer> <leader>l :call VerilatorCompile()<CR>

" === 自動格式化 ===
" 需要安裝 verible-verilog-format
if executable('verible-verilog-format')
    setlocal formatprg=verible-verilog-format\ -
endif

" === Ctags 設定 ===
" 產生 tags 檔案
nnoremap <buffer> <leader>ct :!ctags -R --languages=Verilog .<CR>

" === 快速跳轉 ===
" 跳到 module 定義
nnoremap <buffer> gd :tag <C-r><C-w><CR>
" 返回
nnoremap <buffer> gb <C-t>
```

### Tmux 整合 (多視窗開發)

創建 `~/.tmux.conf`:

```bash
# 基礎設定
set -g default-terminal "screen-256color"
set -g mouse on
set -g history-limit 10000

# 設定前綴鍵為 Ctrl+a
unbind C-b
set-option -g prefix C-a
bind-key C-a send-prefix

# 分割視窗
bind | split-window -h
bind - split-window -v

# Vim 風格切換視窗
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# 重新載入設定
bind r source-file ~/.tmux.conf \; display "Reloaded!"

# 狀態列
set -g status-bg black
set -g status-fg white
set -g status-left '#[fg=green]#S '
set -g status-right '#[fg=yellow]#(date +"%Y-%m-%d %H:%M")'
```

### FPGA 開發 Tmux 工作流程

```bash
#!/bin/bash
# fpga_dev.sh - FPGA 開發環境啟動腳本

tmux new-session -d -s fpga
tmux rename-window 'Editor'
tmux send-keys 'vim' C-m

tmux new-window -n 'Compile'
tmux new-window -n 'Simulate'
tmux new-window -n 'Terminal'

tmux select-window -t 1
tmux attach-session -t fpga
```

### 遠端開發設定 (SSH + Vim)

```bash
# ~/.ssh/config
Host duo-s
    HostName 192.168.42.1
    User root
    ForwardAgent yes
    Compression yes

# 同步 Vim 設定到遠端
scp ~/.vimrc duo-s:~/
scp -r ~/.vim duo-s:~/

# SSH + Tmux 持續會話
ssh duo-s -t tmux attach || tmux new
```

---

## 快速開始腳本

```bash
#!/bin/bash
# setup_fpga_env.sh

echo "=== Ubuntu FPGA 開發環境安裝腳本 ==="

# 基礎工具
echo "安裝基礎工具..."
sudo apt update
sudo apt install -y build-essential git wget curl python3 python3-pip \
    cmake ninja-build gtkwave vim vim-gtk3 neovim tmux iverilog verilator \
    minicom picocom screen universal-ctags cscope ripgrep

# Python 套件
echo "安裝 Python 套件..."
pip3 install --user pyserial pillow numpy fusesoc

# 開源 FPGA 工具
echo "安裝開源 FPGA 工具..."
sudo apt install -y yosys nextpnr-ecp5 prjtrellis

# 設定 USB 權限
echo "設定 USB 權限..."
sudo usermod -a -G dialout $USER

echo "=== 安裝完成 ==="
echo "請重新登入以套用群組變更"
echo "記得下載對應的商業工具（如 Gowin EDA）如果需要"
```

---

## 故障排除

### USB 權限問題
```bash
# 檢查群組
groups

# 加入 dialout 群組
sudo usermod -a -G dialout $USER

# 重新載入 udev 規則
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 找不到串口設備
```bash
# 列出所有串口
ls /dev/tty*

# 檢查 USB 設備
lsusb

# 查看核心訊息
dmesg | tail -20
```

### Verilator 編譯錯誤
```bash
# 檢查版本
verilator --version

# 清理並重新編譯
make clean
verilator --cc design.v --exe tb.cpp --trace
make -C obj_dir -f Vdesign.mk
```

---

## 總結

這份指南涵蓋了在 Ubuntu 上進行 FPGA 開發所需的所有基礎工具和設定。建議的學習路徑：

1. **開始**: 安裝基礎工具，選擇開發板
2. **學習**: 使用 Verilator + GTKWave 模擬簡單電路
3. **實作**: 購買 Milk-V Duo S 或 ColorLight i5 實際操作
4. **進階**: 實現 RISC-V 軟核，跑 Linux

記得經常更新工具並參與社群討論！

---

*最後更新：2024年*