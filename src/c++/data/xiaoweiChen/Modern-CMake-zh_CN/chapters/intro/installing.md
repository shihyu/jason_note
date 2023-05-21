# 安裝 CMake

{% hint style='tip' %}
你的CMake版本應該比你的編譯器要更新，它應該比你使用的所有庫（尤其是Boost）都要更新。新版本對任何一個人來說都是有好處的。
{% endhint %}

如果你擁有一個CMake的內置副本，這對你的系統來說並不特殊。你可以在系統層面或用戶層面輕鬆地安裝一個新的來代替它。如果你的用戶抱怨CMake的要求被設置得太高，請隨時使用這裡的內容來指導他們。尤其是當他們想要3.1版本以上，甚至是3.21以上版本的時候......

#### 快速一覽（下面有關於每種方法的更多信息)

按作者的偏好排序：

* 所有系統
    - [Pip][PyPI] (官方的，有時會稍有延遲)
    - [Anaconda][] / [Conda-Forge][]
* Windows
    - [Chocolatey][]
    - [Scoop][]
    - [MSYS2][]
    - [Download binary][download] (官方的)
* macOS
    - [Homebrew][]
    - [MacPorts][]
    - [Download binary][download] (官方的)
* Linux
    - [Snapcraft][snap] (官方的)
    - [APT repository][apt] (僅適用於Ubuntu/Debian) (官方的)
    - [Download binary][download] (官方的)

## 官方安裝包

你可以從[KitWare][download]上下載CMake。如果你是在Windows上，這可能就是你獲得CMake的方式。在macOS上獲得它的方法也不錯（而且開發者還提供了支持Intel和Apple Silicon的Universal2版本），但如果你使用[Homebrew](https://brew.sh)的話，使用`brew install cmake`會帶來更好的效果（你應該這樣做；蘋果甚至支持Homebrew，比如在Apple Silicon的推出期間）。你也可以在大多數的其他軟件包管理器上得到它，比如Windows的[Chocolatey](https://chocolatey.org)或macOS的[MacPorts](https://www.macports.org)。

在Linux上，有幾種選擇。Kitware提供了一個[Debian/Ubunutu apt軟件庫][apt]，以及[snap軟件包][snap]。官方同時提供了Linux的二進制文件包，但需要你去選擇一個安裝位置。如果你已經使用`~/.local`存放用戶空間的軟件包，下面的單行命令[^1]將為你安裝CMake[^2]。

{% term %}
~ $ wget -qO- "https://cmake.org/files/v3.21/cmake-3.21.0-linux-x86_64.tar.gz" | tar --strip-components=1 -xz -C ~/.local
{% endterm %}

上面的名字在3.21版本中發生了改變：在舊版本中，包名是`cmake-3.19.7-Linux-x86_64.tar.gz`。如果你只是想要一個僅有CMake的本地文件夾：

{% term %}
~ $ mkdir -p cmake-3.21 && wget -qO- "https://cmake.org/files/v3.21/cmake-3.21.0-linux-x86_64.tar.gz" | tar --strip-components=1 -xz -C cmake-3.21
~ $ export PATH=`pwd`/cmake-3.21/bin:$PATH
{% endterm %}

顯然，你要在每次啟動新終端都追加一遍PATH，或將該指令添加到你的`.bashrc'或[LMod][]系統中。

而且，如果你想進行系統安裝，請安裝到`/usr/local`；這在Docker容器中是一個很好的選擇，例如在GitLab CI中。請不要在非容器化的系統上嘗試。

{% term %}
docker $ wget -qO- "https://cmake.org/files/v3.21/cmake-3.21.0-linux-x86_64.tar.gz" | tar --strip-components=1 -xz -C /usr/local
{% endterm %}

如果你在一個沒有wget的系統上，請使用`curl -s`代替`wget -qO-`。

你也可以在任何系統上構建CMake，這很容易，但使用二進制文件通常是更快的。

## CMake默認版本

下面是一些常見的構建環境和你會在上面發現的CMake版本。請自行安裝CMake，它只有1-2行，而且內置的版本沒有什麼 "特殊 "之處。它們通常也是向後兼容的。

### Windows

[![Chocolatey package](https://repology.org/badge/version-for-repo/chocolatey/cmake.svg)][chocolatey]
[![MSYS2 mingw package](https://repology.org/badge/version-for-repo/msys2_mingw/cmake.svg)][MSYS2]
[![MSYS2 msys2 package](https://repology.org/badge/version-for-repo/msys2_msys2/cmake.svg)][MSYS2]

另外[Scoop][scoop]一般也是最新的。來自CMake.org的普通安裝程序在Windows系統上通常也很常見。

### macOS

[![Homebrew package](https://repology.org/badge/version-for-repo/homebrew/cmake.svg)][homebrew]
[![Homebrew Casks package](https://repology.org/badge/version-for-repo/homebrew_casks/cmake.svg)][homebrew-cask]
[![MacPorts package](https://repology.org/badge/version-for-repo/macports/cmake.svg)][macports]

至少根據Google Trends的調查，如今Homebrew在macOS上的流行程度是相當高的。

### Linux

#### RHEL/CentOS

[![CentOS 7 package](https://repology.org/badge/version-for-repo/centos_7/cmake.svg?minversion=3.10.0)][centos]
[![CentOS 8 package](https://repology.org/badge/version-for-repo/centos_8/cmake.svg?minversion=3.10.0)][centos]
[![EPEL 7 package](https://repology.org/badge/version-for-repo/epel_7/cmake.svg?minversion=3.10.0)][centos]

CentOS 8上的默認安裝包不算太差，但最好不要使用CentOS 7上的默認安裝包。請使用EPEL包來代替它。

#### Ubuntu

[![Ubuntu 14.04 package](https://repology.org/badge/version-for-repo/ubuntu_14_04/cmake.svg?minversion=3.10.0)](https://launchpad.net/ubuntu/trusty/+source/cmake)
[![Ubuntu 16.04 package](https://repology.org/badge/version-for-repo/ubuntu_16_04/cmake.svg?minversion=3.10.0)](https://launchpad.net/ubuntu/xenial/+source/cmake)
[![Ubuntu 18.04 package](https://repology.org/badge/version-for-repo/ubuntu_18_04/cmake.svg?minversion=3.10.0)](https://launchpad.net/ubuntu/bionic/+source/cmake)
[![Ubuntu 20.04 package](https://repology.org/badge/version-for-repo/ubuntu_20_04/cmake.svg?minversion=3.10.0)](https://launchpad.net/ubuntu/focal/+source/cmake)
[![Ubuntu 22.04 package](https://repology.org/badge/version-for-repo/ubuntu_22_04/cmake.svg?minversion=3.10.0)](https://launchpad.net/ubuntu/jammy/+source/cmake)

你應該只在18.04以上的版本使用默認的CMake；它是一個LTS版本，並且有一個相當不錯的最低版本！

#### Debian

[![Debian 10 package](https://repology.org/badge/version-for-repo/debian_10/cmake.svg)][repology] 
[![Debian 10 backports package](https://repology.org/badge/version-for-repo/debian_10_backports/cmake.svg)][repology] 
[![Debian 11 package](https://repology.org/badge/version-for-repo/debian_11/cmake.svg)][repology] 
[![Debian 11 backports package](https://repology.org/badge/version-for-repo/debian_11_backports/cmake.svg)][repology] 
[![Debian Unstable package](https://repology.org/badge/version-for-repo/debian_unstable/cmake.svg)][repology]

#### 其它Linux發行版

[![Alpine Linux 3.15 package](https://repology.org/badge/version-for-repo/alpine_3_15/cmake.svg)](https://pkgs.alpinelinux.org/packages?name=cmake&branch=v3.15)
[![Arch package](https://repology.org/badge/version-for-repo/arch/cmake.svg)][repology]
[![Fedora 35 package](https://repology.org/badge/version-for-repo/fedora_35/cmake.svg)][repology]
[![FreeBSD port](https://repology.org/badge/version-for-repo/freebsd/cmake.svg)][repology]
[![OpenBSD port](https://repology.org/badge/version-for-repo/openbsd/cmake.svg)][repology]
[![Gentoo package](https://repology.org/badge/version-for-repo/gentoo/cmake.svg)][repology]
[![openSUSE Tumbleweed package](https://repology.org/badge/version-for-repo/opensuse_tumbleweed/cmake.svg)][repology]
[![Homebrew package](https://repology.org/badge/version-for-repo/homebrew/cmake.svg)][homebrew]


### 常用工具

[![ConanCenter package](https://repology.org/badge/version-for-repo/conancenter/cmake.svg)][repology]
[![PyPI](https://img.shields.io/pypi/v/cmake)][PyPI]
[![Conda-forge](https://img.shields.io/conda/vn/conda-forge/cmake.svg)][Conda-Forge]
[![Anaconda](https://anaconda.org/anaconda/cmake/badges/version.svg?style=flat)][Anaconda]


在許多系統上只需`pip install cmake`。如果需要的話，請添加`--user'（如果需要的話，modern pip會為你做好這個）。然而它目前還沒有提供Universal2的輪子（wheels）。


### CI

| 分佈情況 | CMake 版本 | 說明 |
|---------------|---------------|-------|
| [TravisCI Xenial](https://docs.travis-ci.com/user/reference/xenial/#compilers-and-build-toolchain) | 3.12.4 | 2018年11月中旬，這一映像已準備好廣泛使用 |
| [TravisCI Bionic](https://docs.travis-ci.com/user/reference/bionic/#compilers-and-build-toolchain) | 3.12.4 | 目前與Xenial一樣 |
| [Azure DevOps 18.04](https://docs.microsoft.com/en-us/azure/devops/pipelines/agents/hosted?view=azure-devops#use-a-microsoft-hosted-agent) | 3.17.0 | |
| [GitHub Actions 18.04](https://github.com/actions/virtual-environments/blob/main/images/linux/Ubuntu1804-README.md) | 3.17.0 | 大部分與Azure DevOps保持同步 |
| [GitHub Actions 20.04](https://github.com/actions/virtual-environments/blob/main/images/linux/Ubuntu2004-README.md) | 3.17.0 | 大部分與Azure DevOps保持同步 |

如果你在使用GitHub Actions，也可以查看[jwlawson/actions-setup-cmake](https://github.com/marketplace/actions/actions-setup-cmake)進行操作，它可以安裝你選擇的CMake，即使是在docker中也可以操作運行。

### 完整列表

小於3.10的版本用更深的紅色標記。

[![Full listing](https://repology.org/badge/vertical-allrepos/cmake.svg?columns=3&minversion=3.10.0)][repology]

也可參見[pkgs.org/download/cmake](https://pkgs.org/download/cmake)。

## Pip

[這][PyPI]也是一個官方軟件包，由CMake作者在KitWare進行維護。這是一種相當新的方法，在某些系統上可能會失敗（在我最後一次檢查時，Alpine還不被支持，但它有當時最新的CMake），但它工作的效果非常好（例如在Travis CI上）。如果你安裝了pip（Python的軟件包安裝程序），你可以這樣做：

```term
gitbook $ pip install cmake
```

只要你的系統中存在二進制文件，你便可以立即啟動並運行它。如果二進制文件不存在，它將嘗試使用KitWare的`scikit-build`包來進行構建。目前它還無法在軟件包系統中作為依賴項，甚至可能需要（較早的）CMake副本來構建。因此，只有在二進制文件存在的情況下我們才能使用這種方式，大多數情況下都是這樣的。

這樣做的好處是能遵從你當前的虛擬環境。然而，當它被放置在`pyproject.toml`文件中時，它才真正發揮了作用--它只會被安裝到構建你的軟件包中，而不會在之後保留下來！這簡直太棒了。

{% hint style='info' %}

就我個人而言，在Linux上時，我會把CMake的版本放入文件夾名中，比如`/opt/cmake312`或`~/opt/cmake312`，然後再把它們添加到[LMod][]。參見[`envmodule_setup`][envmodule_setup]，它可以幫助你在macOS或Linux上設置LMod系統。這需要花點時間來學習，但這是管理軟件包和編譯器版本的一個好方法。

[envmodule_setup]: https://github.com/CLIUtils/envmodule_setup
{% endhint %}

[^1]: 我想這是顯而易見的，但你現在正在下載和運行代碼，這會使你暴露在其他人的攻擊之下。如果你是在一個重要的環境中，你應該下載文件並檢查校驗碼。(注意，簡單地分兩步做並不能使你更安全，只有校驗和碼更安全)
[^2]: 如果你的主目錄中沒有`.local`，想要開始也很容易。只要建立這個文件夾，然後把`export PATH="$HOME/.local/bin:$PATH"`添加到你的`.bashrc`或`.bash_profile`或`.profile`文件中。現在你可以把你構建的任何軟件包安裝到`-DCMAKE_INSTALL_PREFIX=~/.local`而不是`/usr/local`!

[repology]:      https://repology.org/project/cmake/versions
[LMod]:          http://lmod.readthedocs.io/en/latest/
[apt]:           https://apt.kitware.com/
[snap]:          https://snapcraft.io/cmake
[PyPI]:          https://pypi.org/project/cmake/
[chocolatey]:    https://chocolatey.org/packages/cmake
[scoop]:         https://github.com/ScoopInstaller/Main/blob/master/bucket/cmake.json
[MSYS2]:         https://packages.msys2.org/base/mingw-w64-cmake
[anaconda]:      https://anaconda.org/anaconda/cmake
[conda-forge]:   https://github.com/conda-forge/cmake-feedstock
[download]:      https://cmake.org/download/
[homebrew]:      https://formulae.brew.sh/formula/cmake
[homebrew-cask]: https://formulae.brew.sh/cask/cmake
[macports]:      https://ports.macports.org/port/cmake/summary
[centos]:        https://rpms.remirepo.net/rpmphp/zoom.php?rpm=cmake
[下載]: 
