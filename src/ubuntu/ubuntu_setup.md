

# Ubuntu

### 開發環境安裝

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

### 選擇套件來源

```sh
sudo /usr/bin/software-properties-gtk
```

### ubuntu 22.04 package

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

##  ubuntu 24.04 package

```sh
sudo apt-get install autoconf automake linux-headers-`uname -r`  clang xdot git meld gparted cmake g++ pkg-config unzip xsel terminator universal-ctags cscope
```



## foliate 支持.epub，.mobi，.azw和.azw3文件。 它不支持PDF文件。

```sh
sudo add-apt-repository ppa:apandada1/foliate
sudo apt update
sudo apt install foliate
```

### ubuntu 有線連線不見（網路圖示不見）解決方法

```sh
sudo apt-get install gnome-control-center
sudo service network-manager stop
sudo rm /var/lib/NetworkManager/NetworkManager.state
sudo service network-manager start
sudo gedit /etc/NetworkManager/NetworkManager.conf
（把false改成true）
sudo service network-manager restart
```

### gnome-open

```sh
sudo ln -s /usr/bin/xdg-open ~/.mybin/o
```



### 將 /tmp 設到 RamDisk (tmpfs) 的方法

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



### im-config  新酷音

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

### Gitbook 安裝

```sh
sudo apt-get update
sudo apt-get install nodejs
sudo apt-get install npm

sudo npm install gitbook -g
```

### node 安裝

```sh
https://nodejs.org/en/  

export N_PREFIX=$HOME/.mybin/node-v17.8.0-linux-x64/
export PATH=$N_PREFIX/bin:$PATH
```



### 多個 SSH Key 對應多個 Github 帳號

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



## Rust

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

更新 Rust 版本
rustup update
```

## cmake Setup

```sh
wget https://cmake.org/files/v3.26/cmake-3.26.0.tar.gz
./bootstrap --prefix=$HOME/.mybin/cmake
make 
make install
export PATH="$HOME/.mybin/cmake/bin:$PATH"
```



## 新增虛擬記憶體(swap)



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



## 改時區

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
