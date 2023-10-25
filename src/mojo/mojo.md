# 支援 Python 語法、又有 C 速度的新程式語言 Mojo 環境配置筆記



## 介紹

Mojo 是一名比較新的語言，是由 LLVM 之父和 Swift 之父 Chris Lattner 所開發。

之所以開發 Mojo，據稱是為了填補『研究』與『生產』的鴻溝，所以 Mojo 擁有 Python 般簡易的語法以及 C 的執行速度。當然，最主要的可能還是對於 AI 的優化 —— 現在 AI 的市場已經值得一門全新的程式語言了。



當然，Mojo 到底有多少實力、有多少潛力待發掘，這個疑問只能留待日後了。總之我今天就來試用看看這個很紅的新程式語言吧！

一方面也是因為 Mojo SDK 現在已經支援 Ubuntu Linux 系統了（2023/09/13），至於 Windows 和 MacOS 等作業系統則可能還需要等上一段時間。

------



## 取得 Mojo SDK

首先，確認滿足系統需求。

**System requirements**
To use the Mojo SDK, you need a system that meets these specifications:

- Ubuntu 20.04/22.04 LTS
- x86-64 CPU (with SSE4.2 or newer) and a minimum of 8 GiB memory
- Python 3.8 – 3.10
- g++ or clang++ C++ compiler

確認為有以上環境後，就可以按照開始配置環境了。

```
curl https://get.modular.com | \
  MODULAR_AUTH=mut_368ff64729824e39b3413866bf6be10d \
  sh -


modular auth X &&
modular install mojo
```



如果這個方法不行，可以考慮使用手動安裝。我自己就是使用手動安裝的方式。因為我遇到了：

```
 ^^^^: ... Failed to update via apt-get update - Context above.
 !!!!: Oh no, your setup failed! :-( ... But we might be able to help. :-)
 !!!!: 
 !!!!: You can contact Modular for further assistance.
 !!!!: 
```



這樣的奇怪錯誤，之後在網路上查到了 https://github.com/modularml/mojo/issues/574 這個 issue，推薦可以試試手動安裝。

```
apt-get install -y apt-transport-https &&
  keyring_location=/usr/share/keyrings/modular-installer-archive-keyring.gpg &&
  curl -1sLf 'https://dl.modular.com/bBNWiLZX5igwHXeu/installer/gpg.0E4925737A3895AD.key' |  gpg --dearmor >> ${keyring_location} &&
  curl -1sLf 'https://dl.modular.com/bBNWiLZX5igwHXeu/installer/config.deb.txt?distro=debian&codename=wheezy' > /etc/apt/sources.list.d/modular-installer.list &&
  apt-get update &&
  apt-get install -y modular

modular auth mut_368ff64729824e39b3413866bf6be10d &&
modular install mojo
```



之後，還要設定 mojo 的路徑。

```
echo 'export MODULAR_HOME="$HOME/.modular"' >> ~/.bashrc

echo 'export PATH="$MODULAR_HOME/pkg/packages.modular.com_mojo/bin:$PATH"' >> ~/.bashrc

source ~/.bashrc
```



安裝好後，應該就可以使用 `mojo` 指令了。
更進一步的指令介紹可以看 [Mojo command-line interface (CLI)](https://docs.modular.com/mojo/cli/)

## 第一支程式: Hello World

好久沒有學習新語言了，遵循常見規則，總之先寫下一份 hello.mojo。

```
fn main():
    print("Hello World!")
```



接著我們要執行：

```
mojo hello.mojo
```



Output:

```
Hello World!
```



我們也可以使用 `mojo build` 來建立靜態連結的二進制檔案。

```
mojo build hello.mojo
```



會建立一個同名的 .mojo 執行檔。我們可以像編譯 C++ 檔案一樣使用 `-o` 來指定特定的輸出名稱。

------



### 心得

目前距離 Mojo 釋放出環境跟編譯器還不到一週的時間，看得出來這真的是很新的東西，安裝的時候其實踩了許多坑，都是慢慢看著 GitHub 上的 issues 解掉的。

語法也還需要熟悉，目標是拿 Mojo 來訓練模型，比較看看現在的各種加速方案，看看是不是真的有所幫助。

總之之後來學習下語法吧！