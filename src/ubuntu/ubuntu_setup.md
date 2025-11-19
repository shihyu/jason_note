# Ubuntu 系統設定與開發環境配置指南

## 目錄
- [系統套件管理](#系統套件管理)
- [系統基本設定](#系統基本設定)
- [開發工具安裝](#開發工具安裝)
- [開發環境配置](#開發環境配置)
- [中文輸入法設定](#中文輸入法設定)
- [系統效能優化](#系統效能優化)
- [工具軟體安裝](#工具軟體安裝)

## 系統套件管理

### 選擇套件來源
```sh
sudo /usr/bin/software-properties-gtk
```

### Ubuntu 22.04 套件安裝
```sh
sudo apt-get install autoconf automake linux-headers-`uname -r` \
 libclang-dev p7zip guake p7zip-full liblzma-dev \
 indicator-multiload filezilla pidgin pcmanx-gtk2 gparted meld \
 speedcrunch vim ssh id-utils cflow autogen \
 cutecom hexedit ccache clang pbzip2 smplayer plink putty-tools \
 ghex doxygen doxygen-doc libstdc++6 lib32stdc++6 build-essential \
 doxygen-gui graphviz git-core cconv alsa-oss wmctrl terminator \
 curl cgdb dos2unix libreadline-dev tmux \
 hexedit ccache ruby subversion htop astyle ubuntu-restricted-extras \
 libncurses5-dev xdot universal-ctags cscope \
 libsdl1.2-dev gitk libncurses5-dev binutils-dev gtkterm \
 libtool mpi-default-dev libbz2-dev libicu-dev scons csh \
 enca ttf-anonymous-pro libperl4-corelibs-perl cgvg catfish gawk \
 i2c-tools sshfs wavesurfer audacity fcitx fcitx-chewing libswitch-perl bin86 \
 inotify-tools u-boot-tools subversion crash tree mscgen krename umbrello \
 intel2gas kernelshark trace-cmd pppoe dcfldd flex bison help2man \
 texinfo texi2html ghp-import autossh samba sdcv xournal cloc geogebra \
 libluajit-5.1-dev libacl1-dev libgpmg1-dev libgtk-3-dev libgtk2.0-dev \
 liblua5.2-dev libperl-dev libselinux1-dev libtinfo-dev libxaw7-dev \
 libxpm-dev libxt-dev gnome-control-center gettext libtool libtool-bin cmake g++ pkg-config unzip xsel
```

### Ubuntu 24.04 套件安裝
```sh
sudo apt-get install autoconf automake linux-headers-`uname -r` \
clang xdot git meld gparted cmake g++ pkg-config unzip xsel librust-openssl-dev \
terminator universal-ctags cscope htop libfuse2 ghp-import libpcre3-dev libpcre2-dev curl fonts-firacode
```

### 常見問題修正

#### Balena Etcher 在 Ubuntu 24.04 的修正
```sh
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
```

## 系統基本設定

### 網路連線修復
解決有線連線不見或網路圖示消失的問題：
```sh
sudo apt-get install gnome-control-center
sudo service network-manager stop
sudo rm /var/lib/NetworkManager/NetworkManager.state
sudo service network-manager start
sudo gedit /etc/NetworkManager/NetworkManager.conf
# 把 managed=false 改成 managed=true
sudo service network-manager restart
```

### 檔案開啟工具設定
```sh
sudo ln -s /usr/bin/xdg-open ~/.mybin/o
```

### 時區設定
```sh
# 互動式時區設定
tzselect

# 設定臺北時區
sudo cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime

# 安裝時間同步工具
sudo apt-get install ntpdate

# 同步時間
sudo ntpdate time.stdtime.gov.tw
sudo hwclock -w

# 設定自動時間同步
echo "@daily /usr/sbin/ntpdate time.stdtime.gov.tw > /dev/null" | crontab -
```

## 開發工具安裝

### 常用開發工具 Git Repositories
```sh
git clone https://github.com/clvv/fasd
git clone https://github.com/junegunn/fzf
git clone https://github.com/sharkdp/fd
git clone https://github.com/cgdb/cgdb
git clone https://github.com/neovim/neovim.git
git clone https://github.com/BurntSushi/ripgrep
git clone https://github.com/ggreer/the_silver_searcher
git clone https://github.com/universal-ctags/ctags
```

### CMake 編譯工具安裝
```sh
wget https://cmake.org/files/v3.26/cmake-3.26.0.tar.gz
./bootstrap --prefix=$HOME/.mybin/cmake
make 
make install
export PATH="$HOME/.mybin/cmake/bin:$PATH"
```

## 開發環境配置

### Node.js 安裝
```sh
# 下載地址：https://nodejs.org/en/
export N_PREFIX=$HOME/.mybin/node-v17.8.0-linux-x64/
export PATH=$N_PREFIX/bin:$PATH
```

### GitBook 安裝
```sh
sudo apt-get update
sudo apt-get install nodejs npm
sudo npm install gitbook -g
```

### Rust 程式語言安裝
```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# 更新 Rust 版本
rustup update
```

### GitHub 多帳號 SSH 設定
```sh
cd ~/.ssh
ssh-keygen -t rsa -C "account1@email.com" -f id_rsa_account1
ssh-keygen -t rsa -C "account2@email.com" -f id_rsa_account2

# 建立 config 檔
touch config

# 編輯 config 檔內容
cat << EOF > config
#account1
Host github.com-account1
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa_account1

#account2
Host github.com-account2
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa_account2
EOF

# 修改相對應 repo 的 remote url 範例：
# ssh://git@github.com-account1/username/repo1.git
```

## 中文輸入法設定

### Ubuntu 22.04 以前版本 (fcitx)
```sh
sudo apt-get install fcitx-table-boshiamy     # 嘸蝦米
sudo apt-get install fcitx-table-cangjie-big  # 倉頡大字集
sudo apt-get install fcitx-table-zhengma-large # 鄭碼大字集
sudo apt-get install fcitx-table-wubi-large   # 五筆大字集
sudo apt-get install fcitx-chewing            # 新酷音
sudo apt-get install fcitx-sunpinyin          # 雙拼
sudo apt-get install fcitx-table-easy-big     # 輕鬆大詞庫
sudo apt-get install fcitx-m17n
sudo apt-get remove ibus

# 設定輸入法
im-config
# 選 fcitx 為預設，重開機或重新登入
# 切換快捷鍵：Ctrl+Space (切換輸入法), Ctrl+Shift (選擇輸入法), Ctrl+Shift+F (簡繁轉換)
```

### Ubuntu 24.04 版本 (fcitx5)
```sh
# 更新套件列表
sudo apt update

# 安裝 fcitx5 核心組件
sudo apt install fcitx5 fcitx5-chinese-addons fcitx5-frontend-gtk4 fcitx5-frontend-gtk3 fcitx5-frontend-qt5

# 安裝庫注音輸入法
sudo apt install fcitx5-chewing

# 安裝 fcitx5 設定工具
sudo apt install fcitx5-config-qt fcitx5-data
```

#### 設定環境變數
```sh
# 編輯 ~/.bashrc
cat << 'EOF' >> ~/.bashrc
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
export INPUT_METHOD=fcitx
export SDL_IM_MODULE=fcitx
export GLFW_IM_MODULE=ibus
EOF
```

#### 設定自動啟動
```sh
cp /usr/share/applications/org.fcitx.Fcitx5.desktop ~/.config/autostart/
```

#### 設定輸入法
1. 開啟 fcitx5 設定工具：在應用程式選單中找到「Fcitx 5 Configuration」
2. 點擊左下角的「+」號新增輸入法
3. 取消勾選「Only Show Current Language」
4. 搜尋「Chewing」並加入
5. 可以調整輸入法的順序

#### 故障排除
```sh
# 診斷設定
fcitx5-diagnose
```

## 系統效能優化

### 虛擬記憶體 (Swap) 設定
```sh
# 1. 建立 4GB swap 檔案
sudo fallocate -l 4G /swapfile

# 2. 設定權限並啟用
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 3. 設定開機自動掛載
echo '/swapfile   none swap    sw 0 0' | sudo tee -a /etc/fstab
```

### RamDisk 設定
將 /tmp 目錄設置到記憶體中以提升效能：

```sh
# 建立臨時目錄
mkdir /dev/shm/tmp
chmod 1777 /dev/shm/tmp
sudo mount --bind /dev/shm/tmp /tmp
```

#### 開機自動執行設定
```sh
# 建立啟動腳本
sudo tee /etc/init.d/ramtmp.sh << 'EOF'
#!/bin/sh
# RamDisk tmp
PATH=/sbin:/bin:/usr/bin:/usr/sbin

mkdir -p /dev/shm/tmp
mkdir -p /dev/shm/cache
mount --bind /dev/shm/tmp /tmp
mount --bind /dev/shm/cache /home/shihyu/.cache
chmod 1777 /dev/shm/tmp
chmod 1777 /dev/shm/cache
EOF

# 設定執行權限
sudo chmod 755 /etc/init.d/ramtmp.sh

# 建立開機啟動連結
cd /etc/rcS.d
sudo ln -s ../init.d/ramtmp.sh S50ramtmp.sh
```

## 工具軟體安裝

### 電子書閱讀器 Foliate
支援 .epub、.mobi、.azw 和 .azw3 格式（不支援 PDF）：
```sh
sudo add-apt-repository ppa:apandada1/foliate
sudo apt update
sudo apt install foliate
```

### AdGuard VPN CLI 安裝
```sh
# 安裝 AdGuard VPN CLI
curl -fsSL https://raw.githubusercontent.com/AdguardTeam/AdGuardVPNCLI/master/scripts/release/install.sh | sh -s -- -v

# 登入帳號
adguardvpn-cli login

# 連線 VPN
adguardvpn-cli connect

# 查看可用位置
adguardvpn-cli list-locations

# 連線到指定位置
adguardvpn-cli connect -l Tokyo

# 其他常用指令
adguardvpn-cli logout           # 登出
adguardvpn-cli check-update     # 檢查更新
adguardvpn-cli --help-all       # 查看所有指令
adguardvpn-cli uninstall        # 移除
```