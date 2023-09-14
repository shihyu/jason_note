# Wine的編譯方法

### 下載Wine原始碼

```sh
git clone https://github.com/wine-mirror/wine

# 如果只是使用wine，就選擇下載不帶git的wine原始碼。
wget https://github.com/wine-mirror/wine/archive/refs/heads/master.zip && unzip master.zip && mv wine-master wine

# 如果要回溯wine或者維護補丁，就選擇下載帶git的wine原始碼。
# git clone git://source.winehq.org/git/wine.git ~/wine
```

### 安裝依賴

手動安裝依賴，以下是編譯依賴+64位運行依賴+32位運行依賴:

```sh
sudo apt install gcc-multilib g++-multilib flex bison gcc make gcc-mingw-w64 libasound2-dev libpulse-dev libdbus-1-dev libfontconfig1-dev libfreetype6-dev libgnutls28-dev  libpng-dev libtiff-dev libunwind-dev libx11-dev libxml2-dev libxslt1-dev libfaudio-dev libgstreamer1.0-dev libmpg123-dev libosmesa6-dev libudev-dev libvkd3d-dev libvulkan-dev libcapi20-dev liblcms2-dev libcups2-dev libgphoto2-dev libsane-dev libgsm1-dev libkrb5-dev libldap2-dev ocl-icd-opencl-dev libpcap-dev libusb-1.0-0-dev libv4l-dev libopenal-dev  libasound2-dev:i386 libpulse-dev:i386 libdbus-1-dev:i386 libfontconfig1-dev:i386 libfreetype6-dev:i386 libgnutls28-dev:i386 libpng-dev:i386 libtiff-dev:i386 libunwind-dev:i386 libx11-dev:i386 libxml2-dev:i386 libxslt1-dev:i386 libfaudio-dev:i386 libgstreamer1.0-dev:i386 libgstreamer-plugins-base1.0-dev:i386 libmpg123-dev:i386 libosmesa6-dev:i386 libsdl2-dev:i386 libudev-dev:i386 libvkd3d-dev:i386 libvulkan-dev:i386 libcapi20-dev:i386 liblcms2-dev:i386 libcups2-dev:i386 libgphoto2-dev:i386 libsane-dev:i386 libgsm1-dev:i386 libkrb5-dev:i386 libldap2-dev:i386 ocl-icd-opencl-dev:i386 libpcap-dev:i386 libusb-1.0-0-dev:i386 libv4l-dev:i386 libopenal-dev:i386 libjpeg-turbo8-dev libjpeg-turbo8-dev:i386 libxcomposite-dev libxcomposite-dev:i386 libc6-i386
```

### 編譯及運行wine

```sh
如果是使用wine，選擇安裝到系統目錄。
bash
# 編譯並安裝到系統目錄
cd wine 
./configure --disable-tests 
make -j$(nproc) 
sudo make install

# 使用wine運行內建應用notepad。
wine notepad
```

```sh
如果是測試wine，選擇安裝到指定目錄。
# 編譯並安裝到指定目錄
mkdir build release 
cd build 
../wine/configure --disable-tests  
make -j$(nproc) 
make install DESTDIR=../release

# 使用wine運行內建應用notepad。
../release/usr/local/bin/wine notepad
```

### 編譯64位wine

```sh
# 假設wine原始碼在src目錄中，然後在src同級建立開始執行
mkdir src win32 win64 release

cd win64
../src/configure --disable-tests --enable-win64
make -j$(nproc)
make install DESTDIR=../release

cd ../win32
../src/configure --disable-tests --with-wine64=../win64
make -j$(nproc)
make install DESTDIR=../release
```

### 製作自包含依賴

因為源會影響依賴包的安裝，所以有時需要製作離線的依賴包，用於編譯或運行。 以下方法需要在純淨環境中執行：

```sh
sudo apt clean

sudo apt install gcc-multilib g++-multilib  gcc make gcc-mingw-w64 \
flex bison libasound2-dev libpulse-dev libdbus-1-dev libfontconfig1-dev libfreetype6-dev libgnutls28-dev  libpng-dev libtiff-dev libunwind-dev libx11-dev libxml2-dev libxslt1-dev libfaudio-dev libgstreamer1.0-dev libmpg123-dev libosmesa6-dev libudev-dev libvkd3d-dev libvulkan-dev libcapi20-dev liblcms2-dev libcups2-dev libgphoto2-dev libsane-dev libgsm1-dev libkrb5-dev libldap2-dev ocl-icd-opencl-dev libpcap-dev libusb-1.0-0-dev libv4l-dev libopenal-dev  libasound2-dev:i386 libpulse-dev:i386 libdbus-1-dev:i386 libfontconfig1-dev:i386 libfreetype6-dev:i386 libgnutls28-dev:i386 libpng-dev:i386 libtiff-dev:i386 libunwind-dev:i386 libx11-dev:i386 libxml2-dev:i386 libxslt1-dev:i386 libfaudio-dev:i386 libgstreamer1.0-dev:i386 libgstreamer-plugins-base1.0-dev:i386 libmpg123-dev:i386 libosmesa6-dev:i386 libsdl2-dev:i386 libudev-dev:i386 libvkd3d-dev:i386 libvulkan-dev:i386 libcapi20-dev:i386 liblcms2-dev:i386 libcups2-dev:i386 libgphoto2-dev:i386 libsane-dev:i386 libgsm1-dev:i386 libkrb5-dev:i386 libldap2-dev:i386 ocl-icd-opencl-dev:i386 libpcap-dev:i386 libusb-1.0-0-dev:i386 libv4l-dev:i386 libopenal-dev:i386 libjpeg-turbo8-dev libjpeg-turbo8-dev:i386 libxcomposite-dev libxcomposite-dev:i386 libc6-i386

cp -r /var/cache/apt/archives ~
cd archives; rm -rf partial
mkdir ../wine-depends
x=$(ls);for y in $x;do dpkg-deb -x $y ../wine-depends;done
```

```sh
為了不影響系統環境，採用手動新增目錄方式來新增庫的搜尋路徑：

bash
export LD_LIBRARY_PATH=<搜尋路徑>:$LD_LIBRARY_PATH
```

