# Ubuntu 系統設定與開發環境

## 目錄
- [開發工具安裝](#開發工具安裝)
- [系統套件管理](#系統套件管理)
- [系統設定](#系統設定)
- [開發環境配置](#開發環境配置)
- [進階設定](#進階設定)

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
terminator universal-ctags cscope htop libfuse2 ghp-import libpcre3-dev libpcre2-dev curl fonts-firacode \

```

### Balena Etcher 在 Ubuntu 24.04 的修正
```sh
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
```



### 電子書閱讀器 Foliate
閱讀器支援 .epub、.mobi、.azw 和 .azw3 格式，不支援 PDF 檔案。

```sh
sudo add-apt-repository ppa:apandada1/foliate
sudo apt update
sudo apt install foliate
```

## 系統設定

### 網路連線修復
解決有線連線不見或網路圖示消失的問題：

```sh
sudo apt-get install gnome-control-center
sudo service network-manager stop
sudo rm /var/lib/NetworkManager/NetworkManager.state
sudo service network-manager start
sudo gedit /etc/NetworkManager/NetworkManager.conf
（把false改成true）
sudo service network-manager restart
```

### 檔案開啟工具設定

```sh
sudo ln -s /usr/bin/xdg-open ~/.mybin/o
```



### RamDisk 設定
將 /tmp 目錄設置到記憶體中以提升效能：

```sh
基本上只要打以下指令，就能將 /tmp 綁定到 /dev/shm
mkdir /dev/shm/tmp
chmod 1777 /dev/shm/tmp
sudo mount --bind /dev/shm/tmp /tmp

※ 註：為何是用 mount --bind 綁定，而不是 ln -s 軟連結，原因是 /tmp 目錄，系統不給刪除。

不過每次開機都要打指令才能用，這樣是行不通的，必須讓它開機時自動執行，才會方便。

用文書編輯器，建立 /etc/init.d/ramtmp.sh 內容如下：

#!/bin/sh
# RamDisk tmp
PATH=/sbin:/bin:/usr/bin:/usr/sbin

mkdir -p /dev/shm/tmp
mkdir -p /dev/shm/cache
mount --bind /dev/shm/tmp /tmp
mount --bind /dev/shm/cache /home/shihyu/.cache
chmod 1777 /dev/shm/tmp
chmod 1777 /dev/shm/cache


將此檔改權限為 755，使其可執行

sudo chmod 755 /etc/init.d/ramtmp.sh

在 /etc/rcS.d 中，建立相關軟連結(捷徑)，使其一開機就執行 以下指令僅能終端機操作

cd /etc/rcS.d
sudo ln -s ../init.d/ramtmp.sh S50ramtmp.sh
```



### 中文輸入法設定

```sh
sudo apt-get install fcitx-table-boshiamy (嘸蝦米）
sudo apt-get install fcitx-table-cangjie-big （倉頡大字集）
sudo apt-get install fcitx-table-zhengma-large （鄭碼大字集）
sudo apt-get install fcitx-table-wubi-large （五筆大字集）
sudo apt-get install fcitx-chewing （新酷音）
sudo apt-get install fcitx-sunpinyin （雙拼）
sudo apt-get install fcitx-table-easy-big （輕鬆大詞庫）
sudo apt-get install fcitx-m17n
sudo apt-get remove ibus

im-config

選fcitx為預設
重開機或登入
在有可輸入中文的框中，按Ctrl+Space，然後用Ctrl+Shift選輸入法輸入，預設的簡繁轉換為Ctrl+Shift+F
```

## 開發環境配置

### GitBook 安裝

```sh
sudo apt-get update
sudo apt-get install nodejs
sudo apt-get install npm

sudo npm install gitbook -g
```

### Node.js 安裝

```sh
https://nodejs.org/en/  

export N_PREFIX=$HOME/.mybin/node-v17.8.0-linux-x64/
export PATH=$N_PREFIX/bin:$PATH
```



### GitHub 多帳號 SSH 設定

```sh
$ cd ~/.ssh
$ ssh-keygen -t rsa -C "account1@email.com" -f id_rsa_account1
$ ssh-keygen -t rsa -C "account2@email.com" -f id_rsa_account2

建立 config 檔
$ cd ~/.ssh
$ touch config
$ gedit config

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
    
修改相對應 repo 的 remote url。例如：
ssh://git@github.com-account1/github account/repo1.git
github account 是github帳號 ex : jasonblog , ccccjason , shihyu
```



### Rust 程式語言安裝

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

更新 Rust 版本
rustup update
```

### CMake 編譯工具安裝

```sh
wget https://cmake.org/files/v3.26/cmake-3.26.0.tar.gz
./bootstrap --prefix=$HOME/.mybin/cmake
make 
make install
export PATH="$HOME/.mybin/cmake/bin:$PATH"
```



## 進階設定

### 虛擬記憶體 (Swap) 設定



1. 切割4GB空間做為swap使用。

   ```sh
   sudo fallocate -l 4G /swapfile
   ```

   4G：可視個人需求修改

   /swapfile：做為swap使用的檔案存放路徑，可修改

    

   這時你的硬碟空間就已被扣除4G保留為此檔案，做為虛擬記憶體使用。

   不過這時只是新增了一個容量4G大的檔案而已，系統並不知道要用他來做swap。

2. 告知系統使用此檔案，啟用swap功能。

   ```sh
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

3. 將swap設定為開機自動掛載。

   ```sh
   sudo vim /etc/fstab
   …
   
   開啟檔案，到最後加入此行
   
   /swapfile   none swap    sw 0 0
   ```

   這樣以後每次重開機就會固定載入這個檔案做為虛擬記憶體使用了。

    

   附註：其實在虛擬網站伺服器都是使用SSD的現在，舉個例，如Linode的Linode 2GB規格，記憶體2G硬碟30G，設定個6G~10G來做虛擬記憶體，就等於你擁有8~12G的記憶體可能還太多了，如果主機有特殊需求使用大量記憶體，可以參考看看這個做法。



### 時區設定

> ＃ **tzselect**
> Please identify a location so that time zone rules can be set correctly.
> Please select a continent, ocean, “coord", or “TZ".
> \1) Africa
> \2) Americas
> \3) Antarctica
> \4) Asia
> \5) Atlantic Ocean
> \6) Australia
> \7) Europe
> \8) Indian Ocean
> \9) Pacific Ocean
> \10) coord – I want to use geographical coordinates.
> \11) TZ – I want to specify the time zone using the Posix TZ format.
> ＃? **4**
>
> Please select a country whose clocks agree with yours.
> \1) Afghanistan 18) Israel 35) Palestine
> \2) Armenia 19) Japan 36) Philippines
> \3) Azerbaijan 20) Jordan 37) Qatar
> \4) Bahrain 21) Kazakhstan 38) Russia
> \5) Bangladesh 22) Korea (North) 39) Saudi Arabia
> \6) Bhutan 23) Korea (South) 40) Singapore
> \7) Brunei 24) Kuwait 41) Sri Lanka
> \8) Cambodia 25) Kyrgyzstan 42) Syria
> \9) China 26) Laos 43) Taiwan
> \10) Cyprus 27) Lebanon 44) Tajikistan
> \11) East Timor 28) Macau 45) Thailand
> \12) Georgia 29) Malaysia 46) Turkmenistan
> \13) Hong Kong 30) Mongolia 47) United Arab Emirates
> \14) India 31) Myanmar (Burma) 48) Uzbekistan
> \15) Indonesia 32) Nepal 49) Vietnam
> \16) Iran 33) Oman 50) Yemen
> \17) Iraq 34) Pakistan
> ＃? **43**
>
> The following information has been given:
>
> Taiwan
>
> Therefore TZ=’Asia/Taipei’ will be used.
> Local time is now: Tue Apr 3 12:07:13 CST 2018.
> Universal Time is now: Tue Apr 3 04:07:13 UTC 2018.
> Is the above information OK?
> \1) Yes
> \2) No
> ＃? **1**
>
> ＃ **cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime**

# 更新時間與測試

> ＃ **apt-get install ntpdate**
>
> ＃ **ntpdate [time.stdtime.gov.tw](http://time.stdtime.gov.tw/)**
>
> ＃ **hwclock -w**
>
> (將時間寫入 BIOS)
>
> ＃ **date**

# 加入排程

> ＃ **vim /etc/crontab**…(略)
>
> 
>
> SHELL=/bin/sh
> PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
>
> ＃ m h dom mon dow user command
> **10 5 \* \* \* root ntpdate [time.stdtime.gov.tw](http://time.stdtime.gov.tw/)**

或

> ＃ **crontab -e**
> **@daily /usr/sbin/ntpdate [time.stdtime.gov.tw](http://time.stdtime.gov.tw/) > /dev/null**
> 將對時寫進 crontab 每天做一次



### AdGuard VPN 安裝與設定

Linux

怎麼安裝登入使用在　ubuntu

在 Ubuntu 上安裝、登入和使用 AdGuard VPN（特別是 AdGuard VPN CLI）非常簡單，以下是完整步驟：

## 1. 安裝 AdGuard VPN CLI

打開終端機（Terminal），輸入以下指令安裝最新穩定版本：

```sh
curl -fsSL https://raw.githubusercontent.com/AdguardTeam/AdGuardVPNCLI/master/scripts/release/install.sh | sh -s -- -v
```

系統會要求你輸入管理員密碼。安裝過程中會詢問是否在 `/usr/local/bin` 建立連結，按 `y` 確認即可[^1][^2][^3]。

---

## 2. 登入 AdGuard VPN

安裝完成後，輸入以下指令登入（或註冊）帳號：

```sh
adguardvpn-cli login
```

依照提示輸入你的電子郵件和密碼。若還沒有帳號，系統會引導你註冊[^4][^5][^2]。

---

## 3. 連線到 VPN

- **快速連線**（自動選擇最快或上次使用的伺服器）：

```sh
adguardvpn-cli connect
```

- **查看可用伺服器位置**：

```sh
adguardvpn-cli list-locations
```

- **連線到指定位置**（例如 Tokyo）：

```sh
adguardvpn-cli connect -l Tokyo
```

或使用國家代碼（如 JP 或 US）[^4][^5][^2]。

---

## 4. 常用指令

- **登出**：

```sh
adguardvpn-cli logout
```

- **檢查更新**：

```sh
adguardvpn-cli check-update
```

- **查看所有可用指令**：

```sh
adguardvpn-cli --help-all
```


---

## 5. 注意事項

- **AdGuard VPN CLI 沒有圖形介面，所有操作都在終端機進行**[^2][^3]。
- **建議定期檢查更新**，確保安全性與穩定性[^4][^5]。

---

## 6. 移除 AdGuard VPN CLI

如需移除，請參考官方知識庫，通常可執行：

```sh
adguardvpn-cli uninstall
```

（若沒有此指令，請參考官方文件手動移除）

---

這樣你就可以在 Ubuntu 上順利安裝、登入及使用 AdGuard VPN CLI 了！


# Ubuntu 24.04 安裝庫注音與 fcitx5 指南

## 安裝 fcitx5 和相關組件

```bash
# 更新套件列表
sudo apt update

# 安裝 fcitx5 核心組件
sudo apt install fcitx5 fcitx5-chinese-addons fcitx5-frontend-gtk4 fcitx5-frontend-gtk3 fcitx5-frontend-qt5

# 安裝庫注音輸入法
sudo apt install fcitx5-chewing

# 安裝 fcitx5 設定工具
sudo apt install fcitx5-config-qt

# 安裝語言包（可選）
sudo apt install fcitx5-data
```

## 設定環境變數

編輯環境變數檔案：

```bash
# 編輯 .bashrc 或 .profile
nano ~/.bashrc
```

在檔案末尾加入以下內容：

```bash
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
export INPUT_METHOD=fcitx
export SDL_IM_MODULE=fcitx
export GLFW_IM_MODULE=ibus
```

## 設定開機自動啟動

```bash
# 將 fcitx5 加入自動啟動
cp /usr/share/applications/org.fcitx.Fcitx5.desktop ~/.config/autostart/
```

## 重新登入或重開機

完成上述設定後，登出再重新登入，或直接重開機讓設定生效。

## 設定輸入法

1. 開啟 fcitx5 設定工具：在應用程式選單中找到「Fcitx 5 Configuration」
2. 點擊左下角的「+」號新增輸入法
3. 取消勾選「Only Show Current Language」
4. 搜尋「Chewing」並加入
5. 可以調整輸入法的順序

## 切換輸入法

- **預設切換鍵**：`Ctrl + Space`
- 可在設定中自訂快捷鍵

## 故障排除

如果遇到問題，可以在終端機執行以下指令來診斷設定：

```bash
fcitx5-diagnose
```

## 注意事項

- 完成安裝後需要重新登入或重開機才能正常使用
- 確保所有環境變數都正確設定
- 如果在某些應用程式中無法使用輸入法，可能需要安裝對應的前端支援套件

---

完成以上步驟後，就可以在 Ubuntu 24.04 上正常使用庫注音輸入法了！
