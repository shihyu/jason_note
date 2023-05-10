# 30 天與鯨魚先生做好朋友

## 目錄

- [Day 1 - 簡介]()
- [Day 2 - 安裝 Docker 環境]()
- [Day 3 - Hello Docker World]()
- [Day 4 - 瞭解 docker run 指令]()
- [Day 5 - 使用 Port forwarding 開放服務]()
- [Day 6 - 使用 Volume 同步程式]()
- [Day 7 - 使用 Network 連結 container]()
- [Day 8 - 使用 environment 控制環境變數]()
- [Day 9 - Container 應用]()
- [Day 10 - 使用 Docker Compose 摻在一起做懶人包]()
- [Day 11 - 瞭解 Docker build 指令]()
- [Day 12 - 以 Laravel 為例，來 build image 吧！]()
- [Day 13 - 最佳化 Dockerfile - 調整 build context]()
- [Day 14 - 最佳化 Dockerfile - 活用 cache]()
- [Day 15 - 最佳化 Dockerfile - 精簡 image]()
- [Day 16 - 為各種框架 build image]()
- [Day 17 - Multi-stage Build]()
- [Day 18 - 使用 Public Registry 分享 image]()
- [Day 19 - 使用 Private Registry 分享 image]()
- [Day 20 - 使用 save / export 分享 image]()
- [Day 21 - Volume 進階用法]()
- [Day 22 - Network 手動配置]()
- [Day 23 - 瞭解 CMD 與 ENTRYPOINT]()
- [Day 24 - 活用 ENTRYPOINT]()
- [Day 25 - 活用 ENV 與 ARG]()
- [Day 26 - 瞭解 Docker 如何啟動 process]()
- [Day 27 - 要如何在 container 裡運行多個 process]()
- [Day 28 - 更詳細的 Docker 操作方法]()
- [Day 29 - The Twelve-Factor App]()
- [Day 30 - 學無止盡]()

# Day 1 - 簡介

[Docker](https://www.docker.com/) 在 2013 年釋出，它把 container 標準化，有效降低使用 container 的難度，很快就成為一個火紅的技術。



更多資訊可以上[維基百科](https://zh.wikipedia.org/wiki/Docker)查詢，筆者在這裡提一下 Docker 帶來的好處：

- Docker 讓環境統一變得更容易，這有助於設計持續整合、持續部署的架構。
- 只要雲端服務或機器支援 Docker，就能運行 Docker 包裝好的服務。
- Docker 使用 `Dockerfile` 的純文字檔做為建置 image 的來源，這代表 Docker 實現了環境即程式碼（Infrastructure-as-code，IaC），環境資訊可以被版控系統記錄。
- 同為虛擬化技術，Docker（或指 container）的資源使用率較 VM 好，它直接跟底層共用作業系統，不需中間再隔一層作業系統虛擬層，因此啟動 container 非常快。
- Docker 應用場景橫跨開發與維運，也是 [DevOps](https://ithelp.ithome.com.tw/articles/10184557) 熱門技能之一。

筆者運氣很好，在 2015 年遇到了 Docker 並開始學習，算很早就趕上這班車。當時因為對 Docker 特性不理解而踩過非常多雷，這些都對於筆者瞭解 Docker 基本特性有非常大的幫助。

未來筆者將會用入門學習 Docker 的角度來跟大家分享，三十天會拆成三個階段各十天如下：

- *熟悉 Docker 基礎的十天* - 瞭解如何操作 Docker 完成簡單任務。
- *創造 Docker Image 的十天* - 網路上找到 Image 不滿意嗎？那就自己建一個！
- *深入瞭解 Docker 的十天* - 遇到越複雜的情境，就越需要更加基礎的知識。

本作定位為教學系列文，每篇文章固定有一個特殊段落為**今日自我回顧**，裡面是以讀者角度撰寫出來的行為，讓讀者可以快速瞭解自己是否瞭解該文章的內容。

Docker 是一個學無止盡的技術，只靠三十天是無法說明完，因此今天會先列出本系列文章的範圍與限制。

## 前置技能

類似 [Laravel 原始碼分析](https://ithelp.ithome.com.tw/users/20102562/ironman/1684)，閱讀未來三十天的文章，會預期讀者已具備以下基礎知識：

- 使用常見指令操作 Linux
- 瞭解在 Linux 如何控制 process 的狀態
- 網路底層相關知識，包含 router、mask
- 常見 server 的運作原理，如 NAT、DHCP、DNS 等
- 瞭解 HTTP 與 TLS 應用

## 以 Linux + CLI 為主

以 Linux 為主的原因是，Docker 應用在 Linux 相較還是比較成熟；另一個原因則是：筆者沒有 Windows 電腦可以測試。

以 CLI 為主的理由則跟學習 git 的狀況很類似，GUI 的背後都有對應的指令，因此瞭解指令還是非常重要的。如果文章有提到新指令或新參數，筆者會在當天最後加上**指令補充說明**的段落，讓讀者可以查詢或複習。

如果對 GUI 有興趣的可以參考下面的連結：

- [Portainer](https://www.portainer.io/)
- [Kitematic](https://kitematic.com/)
- [DockStation](https://dockstation.io/)

當對 Docker 原理了解清楚後，但又想在 CLI 方便管理 Docker 的話，則可以使用下面這個套件：

- [lazydocker](https://github.com/jesseduffield/lazydocker)

## 術語表

在介紹 Docker 原理時，會有非常多專有術語，下面是一個簡單的英中對照表（英文字母序）：

| 英文       | 中文               |
| ---------- | ------------------ |
| build      | 建置               |
| container  | 容器               |
| host       | 本機、主機、宿主   |
| image      | 映像檔             |
| registry   | 倉庫註冊伺服器 [1] |
| repository | 倉庫 [1]           |
| volume     | 資料卷 [2]         |

提供英中對照表的目的，是為了讓讀者在查詢資訊時，可以有不一樣的關鍵字選擇。

未來三十天的文章裡，若有要使用上面的術語，筆者會盡可能使用英文。

[1]: 參考[《Docker —— 從入門到實踐》正體中文版](https://philipzheng.gitbook.io/docker_practice/basic_concept/repository)翻譯
[2]: 參考[《Docker —— 從入門到實踐》正體中文版](https://philipzheng.gitbook.io/docker_practice/data_management/volume)翻譯

## Docker 版本參考

文章裡的範例都是筆者有試驗並成功的。Docker 有些功能不一定會向下相容，如果測試遇到問題時，建議可以先來對一下版本資訊。

```
$ docker version
Client: Docker Engine - Community
 Version:           19.03.12
 API version:       1.40
 Go version:        go1.13.10
 Git commit:        48a66213fe
 Built:             Mon Jun 22 15:41:33 2020
 OS/Arch:           darwin/amd64
 Experimental:      false

Server: Docker Engine - Community
 Engine:
  Version:          19.03.12
  API version:      1.40 (minimum version 1.12)
  Go version:       go1.13.10
  Git commit:       48a66213fe
  Built:            Mon Jun 22 15:49:27 2020
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v1.2.13
  GitCommit:        7ad184331fa3e55e52b890ea95e65ba581ae3429
 runc:
  Version:          1.0.0-rc10
  GitCommit:        dc9208a3303feef5b3839f4323d9beb36df0a9dd
 docker-init:
  Version:          0.18.0
  GitCommit:        fec3683

$ docker-compose version
docker-compose version 1.26.2, build eefe0d31
docker-py version: 4.2.2
CPython version: 3.7.7
OpenSSL version: OpenSSL 1.1.1g  21 Apr 2020
```

# Day 2 - 安裝 Docker 環境

開始學 [Docker](https://www.docker.com/) 前，需要先把環境建好。以下提供多種安裝方法，讀者可以依自己喜好自由選擇。



## 原生系統上安裝

若沒有特殊需求或限制，會建議使用這個方法。以下針對三個主流作業系統做簡單的說明：

### Linux

> **注意**：必須要是 64-bit 版本才能運行 Docker。

參考[官方文件](https://docs.docker.com/install/)，或使用懶人包安裝：

```
sudo curl -fsSL https://get.docker.com/ | sh
sudo usermod -aG docker your-user
```

筆者已使用 Vagrant 測試過 [`ubuntu/trusty64`](https://app.vagrantup.com/ubuntu/boxes/trusty64) 與 [`debian/jessie64`](https://app.vagrantup.com/debian/boxes/jessie64) 兩個作業系統可行；[`centos/7`](https://app.vagrantup.com/centos/boxes/7) 需手動啟動 docker daemon `sudo systemctl start docker`。

### Mac

參考[官方文件](https://docs.docker.com/docker-for-mac/)，下載並安裝 *Docker Desktop for Mac*（需要權限）。

或是使用 [Homebrew](https://docs.brew.sh/Installation) 的 [Cask](https://github.com/Homebrew/homebrew-cask) 安裝（需要權限）：

```
brew cask install docker
```

### Windows 10

> **注意**：需啟用 Hyper-V。

參考[官方文件](https://docs.docker.com/docker-for-windows/)，下載並安裝 *Docker Desktop for Windows*。

## 使用虛擬機安裝

有時候因為某些理由，可能會不想或無法（如 Windows 7）在原生系統上安裝 Docker，這時可以考慮使用虛擬機安裝。

### Docker Machine

[Docker Machine](https://docs.docker.com/machine/) 是官方提供 Docker 機器的建置工具。如果打算建置虛擬機的話，這應該是最適當的方案。

預設的 provider 包括以下選擇：

- [VirtualBox](https://docs.docker.com/machine/drivers/virtualbox/)
- [Hyper-V](https://docs.docker.com/machine/drivers/hyper-v/)（Windows only）
- 還有很多 provider，可以參考[官方文件](https://docs.docker.com/machine/drivers/)

> 使用雲端服務請注意防火牆要開通 local 機器的連線，Docker 使用 tcp 2376 port 連線，同時不要讓其他人能連到這個 port。

以 VirtualBox 為例，執行以下指令即可建立一個 Docker 虛擬機器：

```
# 建立 Docker 虛擬機
docker-machine create -d virtualbox my-docker
# 查看機器對應的環境參數
docker-machine env my-docker
# export 環境參數，執行 docker 指令將會連線到此虛擬機上
eval $(docker-machine env my-docker)
```

### Vagrant

[Vagrant](https://www.vagrantup.com/) 使用指令管理虛擬機，並使用程式碼來表達環境（Infrastructure-as-code，IaC）。

實際的做法，建立 `Vagrantfile` 檔案，並將下面的程式放入檔案裡：

```
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"

  # config.vm.network "forwarded_port", guest: 80, host: 8080
  # config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "1024"
  end

  config.vm.provision "shell", inline: <<-SHELL
    curl -fsSL https://get.docker.com/ | sh
    usermod -aG docker vagrant
  SHELL
end
```

再來使用 `vagrant up` 指令即可得到 Ubuntu trusty 64-bit + Docker CE 的乾淨環境：

```
vagrant up
vagrant ssh
```

### AWS Cloud9

使用 [AWS Cloud9](https://aws.amazon.com/tw/cloud9/) 服務：

1. 啟用 Cloud9 服務，設定直接用預設值即可
2. 在 Cloud9 服務，下 `curl ifconfig.co` 指令取得公開 IP
3. 如果想要從 local 連上並測試服務的話，必須到 EC2 服務裡，找到對應的 instance，再設定 security group

## Play with Docker

上述方法全部都不行的話，這就是最後一招了：申請好 [DockerHub](https://hub.docker.com/) 的帳號後，即可使用 [Play with Docker](https://labs.play-with-docker.com/) 服務。

它是使用 [DinD](https://hub.docker.com/_/docker/) 做成的線上服務，所以會有兩個很明顯的問題：

- 不保證系統一直都可以用，所以有時會壞掉。
- 因為使用 DinD，所以從本機是無法連上該服務建置出來的服務，不過可以在服務上使用 `curl` 或其他跟連線有關的指令測試

## 驗證

安裝完成後，打開終端機輸入下面指令，即可驗證是否安裝成功：

```
docker run hello-world
```

若沒出現錯誤訊息，且有出現 `Hello from Docker!` 文字的話，代表 Docker 有正常啟動，可以開始使用 Docker 了！

## 今日自我回顧

- 描述自己選擇的安裝方法，以及為何選擇這個方法。
- 建立 Docker 環境，並可正常執行指令 `docker run hello-world`。

## 參考資料

- [Docker Tutorials and Labs](https://github.com/docker/labs)

# Day 3 - Hello Docker World

今天要開始瞭解 Docker 世界了，首先會先說明 Docker 的基本概念，接著再以驗證指令 `docker run hello-world` 為例，解釋背後細節。



## 基本概念

Docker 的世界裡，有三個主要元件如下：

- 映像檔（image）
- 容器（container）
- 倉庫（repository）

執行 Docker 的主機，稱為 *Host*。

在 host 執行 `docker run` 指令時，Docker 會操作這三個元件來完成任務。首先來瞭解這三個元件。

### Image

*Image* 包裝了一個執行特定環境所需要的資源。

每個 image 都有獨一無二的 digest，這是從 image 內容做 sha256 產生的。這個設計能讓 image 無法隨意改變內容，維持資料一致性。

雖然 image 裡有必要的資源，但它無法獨立執行，必須要靠 container 間接執行。

### Container

基於 image 可以建立出 *Container*。

它的概念像是建立一個可讀寫內容的外層，架在 image 上。實際存取 container 會經過可讀寫層與 image，因此看到的內容會是兩者合併後的結果。

Container 特性跟 image 不一樣，因為有可讀寫層，所以 container 可以讀寫，也可以拿來執行。

### Repository

*Repository* 是存放 image 的空間。

Docker 設計類似[分散式版本控制](https://zh.wikipedia.org/wiki/分散式版本控制)的方法來存放各種 image。而分散式架構就會有類似 git 的 pull / push 行為，實際做的事也跟 git 類似：為了要跟遠端的 repository 同步。

另一個與 repository 很像，但容易混用的名詞為 *Registry*，後者涵蓋範圍更廣，包含了更多 repository 與身分驗證功能等，通常比較常討論的也是 registry。

目前 Docker 預設的 registry 為 [DockerHub](https://hub.docker.com/)，大多數程式或服務的 image 都能在上面找得到。

------

Image、container、repository 之間的關係就像光碟一樣：早期世紀帝國等光碟遊戲，會需要搭配其他可讀寫空間（如硬碟），才有辦法執行。

- Image 像光碟片一樣，唯讀且不能獨立執行
- Container 像硬碟一樣，可讀可寫可執行
- Repository 則是光碟盒，而 Registry 則是像光碟零售商

## 執行驗證指令

安裝好環境後，第一次執行驗證指令 `docker run hello-world` 範例如下：

```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
0e03bdcc26d7: Pull complete
Digest: sha256:7f0a9f93b4aa3022c3a4c147a449bf11e0941a1fd0bf4a8e6c9408b2600777c5
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
```

`docker run` 有明確執行的意思。回頭看一開始的元件說明可以瞭解，`docker run` 會建立一個 container 並執行；而因為 container 需要基於 image 建立，所以 `docker run` 有個必要的參數是 image 名稱，即 `hello-world`。

它的訊息非常長，但實際上可以分為兩個區塊：

### 確認 Image 存在 Repository

首先先確認 `hello-world` 是否存在於本機的 repository，本機找不到的話，就需要從遠端的 repository 下載。

下面即為找不到 image，並從遠端下載的訊息：

```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
0e03bdcc26d7: Pull complete
Digest: sha256:7f0a9f93b4aa3022c3a4c147a449bf11e0941a1fd0bf4a8e6c9408b2600777c5
Status: Downloaded newer image for hello-world:latest
```

> Docker 設計 image 名稱會包含 registry 的路徑，若沒有的話，則預設是 [DockerHub](https://hub.docker.com/)。

### 建立 Container 並執行

確認好 Image 存在或下載好後，即可建立 Container 並執行。

`docker run` 預設的行為是：

1. 前景建立並執行 container
2. 等待執行程式結束（exit）後，會回到前景的命令提示字元
3. 該 container 會被標記成結束狀態

以本範例來說，資訊顯示完回到命令提示字元時，上面三個步驟就都完成了。步驟二在執行過程很明顯，而步驟一與三所提到的 container 可以使用 `docker ps` 查看：

```
docker ps -a
```

裡面的訊息如下：

```
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS                      PORTS               NAMES
6d7e00198a56        hello-world         "/hello"            12 seconds ago      Exited (0) 11 seconds ago                       relaxed_bhabha
```

`docker ps` 可以看 container 的概況，除了列出有哪些 container 外，也有其他欄位瞭解 container 相關資訊。

首先可以注意到 `STATUS` 欄位狀態為 `Exited (0)`，後面的數字為程式結束後回傳的狀態碼，通常 0 為正常結束，非 0 則是有錯誤。

最開頭的 `CONTAINER ID` 與最後的 `NAMES` 是獨一無二的，可以多執行幾次 `docker run`，接著就會看到很多不一樣名字的 container。

### 移除 Container

若一直不斷執行 `docker run hello-world` 的話，就會造成 container 數量不斷成長。雖然使用到容量不多，但在管理上多少會造成困擾。

最簡單的方法是，沒有要再用的 container 就移除它。以上面的範例為例，移除 container 的指令如下：

```
# 使用 CONTAINER ID: 6d7e00198a56 或 NAMES: relaxed_bhabha 皆可
docker rm 6d7e00198a56

# 移除完使用 docker ps 再檢查一次
docker ps -a
```

`docker rm` 是移除 container 的指令，只要 container 不是處於 `Up` 正在執行中的狀態，即可使用 `docker rm` 移除。

## 指令補充說明

### `docker run`

使用 `IMAGE` 建立新的 container 並執行指令，用法如下：

```
docker run IMAGE
```

`IMAGE` 會先從本機 repository 找，有的話就執行；若沒有的話，會到遠端 repository 下載並執行。

### `docker ps`

列出已建立的 container。

```
docker ps
```

- `-a|--all` 列出所有的 container

### `docker rm`

移除指定的 container，用法如下：

```
docker rm CONTAINER [CONTAINER...]
```

`CONTAINER` 可以是 `docker ps` 查到的 CONTAINER ID 或 NAMES。若需要移除多個 container，可以使用空白隔開每個 container 名稱，如：

```
docker rm container_a container_b
```

## 今日自我回顧

Image、container、repository，三個元件之間的關係，可以畫成示意圖如下：

![img](https://mileschou.me/images/ironman/12th/docker-newbie/components.png)

今天的說明搭配此圖，相信讀者能更瞭解 `docker run` 與元件如何互動。

- 解釋 Docker 三種元件之間的關係
- 練習 `docker run` 指令執行 `hello-world` image
- 練習 `docker ps` 指令，觀察 container 狀態
- 練習 `docker rm` 指令，整理 container 列表

# Day 4 - 瞭解 docker run 指令



昨天從執行 [Hello Docker](https://mileschou.me/ironman/12th/docker-newbie/day03/) 的過程中，瞭解 Docker 的三個基本元件。今天會更進一步地說明 `docker run` 更多細節。



首先，先回顧這張示意圖：

![img](https://mileschou.me/images/ironman/12th/docker-newbie/components.png)

Hello Docker 使用的 `docker run` 指令，可以一條龍處理上圖所有任務。等等將會示範如何不使用 `docker run` 來達成執行 container，同時換用 [BusyBox](https://hub.docker.com/_/busybox) image 來做示範。

> BusyBox 是一個 Linux 指令工具包，它執行後會進到 container 的命令提示字元裡，接著就能使用 BusyBox 所提供的 Linux 指令。

執行 container 任務先簡單拆解如下：

1. [下載 image](https://mileschou.me/ironman/12th/docker-newbie/day04/#下載-image)
2. [建立 container](https://mileschou.me/ironman/12th/docker-newbie/day04/#建立-container)
3. [執行 container](https://mileschou.me/ironman/12th/docker-newbie/day04/#執行-container)
4. [停止 container](https://mileschou.me/ironman/12th/docker-newbie/day04/#停止-container)

## 下載 image

首先 Docker 會確認 image 是否存在，可以用 `docker images` 指令來查看本機的 image，接著使用 `docker pull` 指令下載 image：

```
# 查看本機 image
docker images busybox

# 下載 image
docker pull busybox
```

一開始執行 `docker images busybox` 會出現空列表，代表 host 沒有對應的 image，會需要下載。如果 image 存在，會跳到[建立 container](https://mileschou.me/ironman/12th/docker-newbie/day04/#建立-container)步驟。下載完成後，可以用一開始的指令 `docker images busybox` 再次確認是否有下載成功。

如果想確認這個 image 是否可以下載，可以上 [DockerHub](https://hub.docker.com/) 上找，或使用 `docker search` 指令查詢：

```
$ docker search busybox
NAME                      DESCRIPTION                                     STARS               OFFICIAL            AUTOMATED
busybox                   Busybox base image.                             1986                [OK]
...
```

這裡有個欄位 `OFFICIAL` 標示 OK，代表這個 image 是官方出品有掛保證的，通常會建議使用官方的 image，相較穩定可靠。

### 移除 image

若已下載的 image 已用不到，如 `hello-world`，可以使用 `docker rmi` 移除：

```
$ docker rmi hello-world
Untagged: hello-world:latest
Untagged: hello-world@sha256:7f0a9f93b4aa3022c3a4c147a449bf11e0941a1fd0bf4a8e6c9408b2600777c5
Deleted: sha256:bf756fb1ae65adf866bd8c456593cd24beb6a0a061dedf42b26a993176745f6b
Deleted: sha256:9c27e219663c25e0f28493790cc0b88bc973ba3b1686355f221c38a36978ac63
```

`docker rmi` 有可能會因為 container 未移除導致 image 移除失敗，先把對應的 container 移除，再執行 `docker rmi` 即可：

```
$ docker rmi hello-world
Error response from daemon: conflict: unable to remove repository reference "hello-world" (must force) - container 7aa21315f7ca is using its referenced image bf756fb1ae65
$ docker rm 7aa21315f7ca
7aa21315f7ca
$ docker rmi hello-world
```

> image 間如果有依賴關係，也有可能會無法正常移除，此情境未來會說明。

到這裡為止，image 已準備完成。

## 建立 container

Docker 提供建立 container 的指令為 `docker create`，實際執行範例如下：

```
# 建立 container
docker create -i -t --name foo busybox

# 使用 docker ps 確認 container 狀態
docker ps -a
```

說明 `docker create` 指令的選項與參數：

- `-i -t` 簡單來說，當需要跟 container 的 process 互動時，通常會加入這兩個參數。互動指的是像 `git add -i` 會跟使用者一問一答的行為。
- `--name` 可以幫 container 命名，這個名字會在 `docker ps` 列表的 `NAMES` 欄位出現。必須唯一，若撞名則 container 會創建失敗。
- 選項後的第一個參數為 image 名稱，本例為 `busybox`。

下 `docker create` 後會顯示一個 digest，這與 `docker ps` 列表裡的 `CONTAINER ID` 相同。另外可以注意到這次的 `STATUS` 不大一樣，是 `Created`，它表示 container 創建完成。

## 執行 container

執行 container 使用 `docker start` 指令：

```
# 執行 container，`foo` 是前一節創建 container 指定的名字。
docker start -i foo

# container 內執行 Linux 指令
whoami
ls
```

上面執行過程中，有出現兩個不一樣的命令提示字元，一個是筆者 host 客製化的提示字元，另一個則是 `/ #`，這已經在 container 的世界裡了。

在 container 執行 `whoami` 得到的結果，會是 Docker 指定的使用者。本範例並沒有特別指定，所以是 BusyBox 預設的 root。而像 `ls` 的示範則是看到 container 裡的檔案系統。因為這些特色，讓 container 能做到類似 VM 的效果。

執行 BusyBox 的過程中，可以使用 `Ctrl + P` 與 `Ctrl + Q` 的連續組合鍵來達成「離開 container」－－*detach* 的效果。離開後可以使用 `docker ps` 回來觀察 container 的狀態。container 還是 `Up` 的時候，可以使用 `docker attach` 再讓 container 回到前景：

```
# 使用 docker ps 可以觀察到狀態是 `Up`，正常運行中。
docker ps

# 將 container 裡輸入輸出綁回前景
docker attach foo
```

## 停止 container

停止 BusyBox container 有兩種方法，一種是在 container 裡下結束的指令 `exit`；另一種則是使用 `docker stop` 指令：

```
docker stop foo
```

注意這兩種方法有一點點差異，主要在於 `Exited` 後面的狀態碼不同，第一個方法是 0，代表正常結束。它使用正常流程 `exit` 指令結束 shell。

第二個方法使用 `docker stop` 會發送 `SIGTERM` 信號給 container 的主程序，等同於呼叫對主程序下 `kill -15` 指令一樣，是要求 process 強制結束。但因 process 結束遇到問題，因此才會出現不正常結束的狀態碼。

最後，使用 `docker rm` 指令移除 container，一切就會恢復成一開始還沒建 container 的狀態：

```
docker rm foo
```

以上詳細說明瞭 image 下載與移除的過程，以及 container 的生命週期。現在再看一次示意圖，應該會對整個流程更有感覺：

![img](https://mileschou.me/images/ironman/12th/docker-newbie/components.png)

建議讀者可以多瞭解今天的內容，因為不管是什麼 image，都會執行今天說明的流程。唯有熟悉整個流程，才有辦法在發生問題的時候，知道是哪個環節出問題與解決對應的問題。

## 指令說明

### `docker images`

查看本地目前有哪些 image，用法如下：

```
docker images [REPOSITORY[:TAG]]
```

`REPOSITORY` 沒給的話，會列出本機所有的 image；如果有給的話，則會把該 repository 所有 tag 都列出來；如果加給 `TAG`，則只會列出該 repository + tag 對應的 image。

> 今天的範例是隻有給 `REPOSITORY`。`TAG` 的用法類似版號，實際範例未來會有機會看到。

### `docker pull`

從遠端 repository 下載 image，用法如下：

```
docker pull NAME[:TAG|@DIGEST]
```

`TAG` 若沒有給的話，預設會使用 latest，因此下面這兩個指令是等價的：

```
docker pull busybox
docker pull busybox:latest
```

### `docker rmi`

`rmi` 即 rm image 之意，移除 image，用法如下：

```
docker rmi [OPTIONS] IMAGE [IMAGE...]
```

### `docker create`

建立 container。這個指令類似 `docker run`，但它只有建立 container 而沒有執行。兩個指令單純只差在有沒有執行，所以它們的參數幾乎都共用。

用法如下：

```
docker create [OPTIONS] IMAGE [COMMAND] [ARG...]
```

- `--name` 可指定 container 名稱
- `-i|--interactive` 是讓 container 的標準輸入保持打開
- `-t|--tty` 選項是告訴 Docker 要分配一個虛擬終端機（pseudo-tty）並綁定到 container 的標準輸入上

### `docker start`

啟動 container。

```
docker start [OPTIONS] CONTAINER [CONTAINER...]
```

- `-i|--interactive` 把標準輸入綁定到容器上。

> **注意**：這裡的 `--interactive` 參數與 `docker create` 的 `--interactive` 參數的意義不同，必須要兩個都有啟用才能與容器互動。而 `docker run` 的 `--interactive` 會同時兩個都啟用。

### `docker attach`

把前景「接」到 container 上，用法如下：

```
docker attach [OPTIONS] CONTAINER
```

只要處於 detach 的 container，都能使用這個指令回到 container 上。

### `docker stop`

強制停止指定的 container，用法：

```
docker stop [OPTIONS] CONTAINER [CONTAINER...]
```

此指令會送出 `SIGTERM` 信號給 container 的主程序，當 timeout（預設 10，可使用 `-t|--time` 參數調整）後會再送出 `SIGKILL`，也就是 `kill -9`。

> 類似地，`docker pause` 是送 `SIGSTOP`；`docker kill` 則是直接送 `SIGKILL`。

## 今日自我回顧

[Hello Docker](https://mileschou.me/ironman/12th/docker-newbie/day03/) 是使用 `docker run` 執行範例程式，今天則是瞭解如何操作各別指令執行 container。簡單來說，`docker run` 與其他指令的關係如下：

```
docker run = docker pull + docker create + docker start
```

另外也使用 `--interactive` 選項與 `--tty` 選項，成功進入 container 的環境，並在裡面執行指令（`whoami` 與 `ls`）。

- 瞭解 `docker run` 背後對應的細節
- 練習 `docker pull` 下載 image
- 練習 `docker create` 建立 container
- 練習 `docker start` 啟動 container
- 練習 `docker stop` 停止 container
- 練習 container 的 detach 與 attach

# Day 5 - 使用 Port forwarding 開放服務

今天將會使用 Docker 啟動 HTTP server，並讓瀏覽器能看得到 HTTP server 所提供的 hello world。



常見的 HTTP server 主要有兩種：[Nginx](https://hub.docker.com/_/nginx) 與 [Apache](https://hub.docker.com/_/httpd)，今天會以 Apache HTTP server（以下簡稱 Apache）為例。

## Container 管理小技巧

首先，先使用 `docker run` 跑 Apache container。

```
# Apache 的 image 名稱叫 httpd
docker run --name web httpd

# 停止 Apache 後，移除已停止的 container
docker ps -a
docker rm web
```

Apache 執行時，會停在前景等待收 request。若要中止它，可以按 `Ctrl + C` 快捷鍵強制中離。從訊息可以觀察到，`Ctrl + C` 跟 `docker stop` 一樣是發出 `SIGTERM` 信號給 process。狀態已經停止了，但 container 還存在，如果不需要的話得手動移除。

通常練習或測試的 container 都不需要保留，每次手動移除也很麻煩，這時可以使用參數 `--rm`，範例如下：

```
# 加帶 --rm 參數
docker run --rm --name web httpd

# 檢查是否移除
docker ps -a
```

`--rm` 選項的功能是，當 container 的狀態變成 `Exited` 時，會自動把這個 container 移除，在練習或測試的時候非常方便。

## 背景執行

前景執行 Apache 的時候，按下昨天提到的 `Ctrl + P` 與 `Ctrl + Q`，會發現一點用都沒有。但像今天是啟動 HTTP server，通常會希望它是背景執行，這時可以使用另一個參數 `-d`，範例如下：

```
# 執行完會馬上回到 host 上
docker run -d httpd

# 觀察 container 是否在運作中
docker ps
```

執行完 `docker run` 會回 `CONTAINER ID` 並回到原本的命令提示字元。這時再觀察 `docker ps` 會看到對應的 container 是運作中的狀態。

在 [Hello Docker](https://mileschou.me/ironman/12th/docker-newbie/day03/) 說明 `docker rm` 的時候有提到，container 的狀態不是 `Up` 才能移除。除了先使用 `docker stop` 再使用 `docker rm` 外，也可以使用 `docker rm` 的 `-f` 參數強制移除 container：

```
# 執行完會馬上回到 host 上
docker run -d --name web httpd

# 確認正在執行中
docker ps

# 因 container 還在運作中，所以直接 rm 會出現錯誤訊息
docker rm web

# 注意 rm -f 是發出與 docker kill 相同的 SIGKILL 信號，而不是 docker stop 的 SIGTERM
docker rm -f web
```

加 `--rm` 選項可以讓它結束後自動移除，但得先用 `docker stop` 停止 container 才會觸發移除，那倒不如使用 `docker rm -f` 指令還比較直接一點。

雖然 Docker 並沒有特別禁止，但筆者個人習慣是不會同時啟用 `--rm` 和 `-d` 這兩個選項；另外還有一個原因是，在 [Docker v1.13.0](https://github.com/moby/moby/releases/tag/v1.13.0) 版以前，是不能同時啟用 `--rm` 與 `-d` 的，詳細可參考 [Docker issue](https://github.com/moby/moby/issues/6003)。

## 存取服務

我們先把 container 都移除，然後背景執行一個 Apache container。

```
# 背景啟動 Apache
docker run -d httpd

# 確認 PORTS
docker ps

# curl 試試 HTTP 服務，也可以用瀏覽器測試
curl http://localhost/
```

`docker ps` 裡面有個欄位是 `PORTS`，上面寫著 `80/tcp`，看起來很像是可以透過本地的 80 port 來存取 HTTP server。但實際上用 curl 會回應連線被拒絕，這代表從 host 連到 container 的方法有問題。

說明解法前，大家可以先試看看下面的指令：run 3 個 Apache container：

```
docker run -d httpd
docker run -d httpd
docker run -d httpd

# 查看 container
docker ps
```

`docker ps` 可以觀察到，所有 port 都是 `80/tcp`，但奇妙的是，全部 container 都沒有遇到 port 衝突！？從這個實驗結果可以瞭解 container 具有隔離特性，也就是每個 container 都是獨立的個體，它們各自有屬於自己的 80 port 可以用，因此才不會相衝。

今天的目標是要從外界存取 container，因此要做點手腳才行－－正是標題提到的 port forwarding。Docker 使用 `-p` 選項設定 port forwarding，範例如下：

```
# 加上 -p 參數
docker run -d -p 8080:80 httpd

# 確認 port 有被開出來了
curl http://localhost:8080/
```

`-p` 後面參數 `8080:80` 的意思代表：當連線到 host 的 8080 port 會轉接到 container 的 80 port。以上面的指令為例，只要輸入 `http://localhost:8080/` 即可接到 container 所啟動的 HTTP 服務。

下面是簡單示意圖：

![img](https://mileschou.me/images/ironman/12th/docker-newbie/port-forwarding.png)

Container 啟動完後，8080 是被綁定在 host 上的。只要有另一個服務綁 8080 在 host 上的話，就會出現錯誤訊息 `port is already allocated.`：

```
docker run -d -p 8080:80 httpd
docker run -d -p 8080:80 httpd
```

## 指令補充說明

### `docker run`

補充說明其他參數：

- `--rm` 當 container 主程序一結束時，立刻移除 container
- `-d|--detach` 背景執行 container
- `-p|--publish` 把 container 的 port 公開到 host 上，格式為 `[[[IP:]HOST_PORT:]CONTAINER_PORT]`
  給完整格式的話，會把 `IP:HOST_PORT` 綁定到 `CONTAINER_PORT`；如果沒給 IP，則 IP 會代 0.0.0.0；如果連 HOST_PORT 也沒給，則會使用 0.0.0.0 加上隨機選一個 port，如 `0.0.0.0:32768`。

### `docker rm`

補充說明其他參數：

- `-f|--force` 如果是執行中的 container，會強制移除（使用 SIGKILL）

## 今日自我回顧

Container 具備了隔離機制，因此有辦法把它當作「輕量的 VM 」使用。

今天說明的 port forwarding，可以應用在任何有開 port 提供服務的 server，如：[MySQL](https://hub.docker.com/_/mysql)、[Redis](https://hub.docker.com/_/redis)、[Memcached](https://hub.docker.com/_/memcached) 等，有興趣可以參考官網範例自行試試。

- 瞭解 container 隔離的特性
- 練習使用 `docker run` 的 `--rm` 參數與 `-p` 參數
- 練習透過 port forwarding 存取 container 提供的 HTTP server 或其他 server

# Day 6 - 使用 Volume 同步程式

Volume 也是 Docker 的元件，它提供 container 保存資料或共享資料的機制。



## 情境說明

在開始說明 volume 前，先來看下面這個情境。

昨天學到了如何在背景開啟 HTTP server，指令如下：

```
$ docker run -d --name web -p 8080:80 httpd
c30dfb2d3261170cd3fc4ed012e8ac441261292b13b95c1f203b8b0b4138d75f
$ curl http://localhost:8080/
<html><body><h1>It works!</h1></body></html>
```

Server 是開好了，但如果 server 的內容不能依需求修改的話，最終只是拿來玩 Hello world 而已。

因此現在有了新的目標－－更新裡面的程式。可以使用 `docker exec` 加上 shell 進入 container：

```
# 啟動 Apache
docker run -d --name web -p 8080:80 httpd

# 確認 container 正在執行中
docker ps

# 使用 exec 進入 container
docker exec -it web bash

# 找出 Apache 回 curl 的 HTML
cat htdocs/index.html
```

`docker exec` 是在一個運行中的 container 上，再執行一個新的指令。參數為上例的 `CONTAINER ID` 與啟動 shell 的指令 `bash`，執行的結果是進入 Apache container 的世界裡，在裡面可以找得到 curl 取到的 HTML 原始文件。

只要修改這個檔案，即可讓 curl 獲得修改後的檔案。

```
# 使用 exec 進入 container
docker exec -it web bash

# 使用新的內容取代 index.html 並離開 container
echo Hello volume > htdocs/index.html && exit

# 離開並測試
curl http://localhost:8080/
```

上面這個範例，我們成功修改了 `index.html` 的內容。但先別開心，我們把舊的移除，然後用 `docker run` 跑一個新的 Apache container 看看：

```
# 確認內容
curl http://localhost:8080/

# 移除 container
docker rm -f web

# 再啟動一次
docker run -d --name web -p 8080:80 httpd

# 確認內容
curl http://localhost:8080/
```

這個實驗會發現，It works! 又回來了？原因很簡單，在介紹 [port forwarding](https://mileschou.me/ironman/12th/docker-newbie/day05/) 的時候，有提到隔離特性，也有提到每個 container 都是各自獨立的，這也代表剛剛被砍掉的 container 與現在建立的 container 是不同一個。而使用 `docker run` 指令產生的 container，每次都會是全新跟重灌好一樣，這就是一次性的特性。

## Bind Mount

只要開新的 container 就會被砍掉重練，那該如何讓我們寫好的程式出現在 container 裡面呢？方法有很多種，今天說明馬上就能使用的 *Bind Mount*。

Bind Mount 的概念很簡單，它可以把本機的某個目錄或檔案，綁定在 container 裡的某個目錄或檔案。比方說把目前開發的程式，綁在 container 的 `/source`，那 container 就能在它的 `/source` 裡看到本機的檔案。

綁定使用 `-v` 選項，下面範例是把目前目錄綁定在 Apache container 的 `/usr/local/apache2/htdocs` 目錄下：

```
# 執行 container
docker run -d -it -v `pwd`:/usr/local/apache2/htdocs -p 8080:80 httpd

# 測試對應路徑
curl http://localhost:8080/test.html
```

這個方法可以簡單解決 `docker run` 產生新的 container 的情境下保有舊的資料。

## 指令補充說明

### `docker exec`

在一個正在執行的 container 上執行指令，用法如下：

```
docker exec [OPTIONS] CONTAINER COMMAND [ARG...]
```

`docker run` 與 `docker exec` 做的事很相似，決定性差異在於：`docker run` 會產生新的 container，而 `docker exec` 需要運行中的 container。

`-i|--interactive` 和 `-t|--tty` 參數用法與 [`docker create`](https://mileschou.me/ironman/12th/docker-newbie/day04/) 相同。

### `docker run`

- `-v|--volume` 掛載 volume 到這個 container 上，格式為 `[/host]:[/container]:[參數]`

## 今日自我回顧

- 練習「進入」container 的方法
- 練習在 container 讀取修改目錄或檔案

# Day 7 - 使用 Network 連結 container

跟 [Volume](https://mileschou.me/ironman/12th/docker-newbie/day06/) 一樣，Network 也是 Docker 的元件。正如其名，它是在管理網路相關設定的指令。



有了 Docker 後，開 server 變得容易許多。但實務上的網路架構，通常是多層式的，如三層式架構（Three-Tier）需要 Application Server 與 RDBMS 兩種 server 連結起來，才能提供完整的服務。

## 觀察 container log

在看完 [`docker run`](https://mileschou.me/ironman/12th/docker-newbie/day04/) 的細節，與 [Port forwarding](https://mileschou.me/ironman/12th/docker-newbie/day05/) 的說明後，相信大家可以理解下面的 `docker run` 在做什麼了：

```
# Terminal 1
docker run --rm -it --name web -p 8080:80 httpd

# Terminal 2
curl http://localhost:8080/
```

這次 `docker run` 指令範例是開著觀察 log，然後開另外一個視窗與 `web` container 互動。

筆者通常先使用這樣的方法來測試 image 的功能，測完關閉就會自動移除。而當需要 `-d` 時，則會改用 `docker logs` 來觀察 log：

```
# Terminal 1 
docker run -d -it --name web -p 8080:80 httpd

# 加 -f 選項後，container log 只要有更新，畫面就會更新 
docker logs -f web

# Terminal 2
curl http://localhost:8080/
```

這兩個小技巧都可以用來觀察 container 內部運作的狀況，可以視情況運用。

## 連結 container

想把 container 連結在一起有兩種做法：使用 `--link` 參數與使用 Network。

### 使用 `--link` 參數

使用 `--link` 參數可以達成 container 連結的功能，指令也算直覺：

```
# wget 為 curl 的替代指令
docker run --rm busybox wget -q -O - http://web/

# 比較沒加 link 與有加 link 的差別
docker run --rm --link web busybox wget -q -O - http://web/

# 使用別名
docker run --rm --link web:alias busybox wget -q -O - http://alias/
```

這個範例先解釋指令的用法，`docker run` 可以在 `IMAGE` 的後面加上想在 image 裡執行的指令為何，如：

```
# BusyBox 裡面執行其他指令
docker run --rm busybox whoami
docker run --rm busybox ls
docker run --rm busybox wget -q -O - http://web/

# BusyBox 預設為執行 sh，因此下面兩個指令結果相同
docker run --rm busybox
docker run --rm busybox sh
```

執行 BusyBox 的 `wget -q -O - http://web/` 的 `web` 對應的是 Apache container 的 `--name web` 設定。另外，必須要使用 container 內部的 port（本例是 80）呼叫。

`--link` 選項的用法：`web:alias` 左邊是 container name，右邊是別名。設定完後，`web` 和 `alias` 都能通。

### 使用 Network

> 這是官方建議的做法

使用 Network 建立一個虛擬網路，container 在這個網路裡就可以使用 container name 或 hostname 互相連結。

```
# 建立 network
docker network create my-net

# Terminal 1 啟動 Apache
docker run --rm --name web -p 8080:80 --network my-net httpd

# Terminal 2 透過 BusyBox 連結 Apache
docker run --rm --network my-net busybox wget -q -O - web
```

### `--link` 的問題

`--link` 雖然在語意上是清楚的，但有個問題目前筆者無解，因此還是建議大家使用 Network 就好了。

```
# Terminal 1 啟動 main container
docker run --rm -it --name main busybox

# Terminal 2 啟動 sub container
docker run --rm -it --name sub --link main busybox

# Terminal 2 ping main
ping main

# Terminal 1 ping sub
ping sub
```

從這個範例裡可以發現，它的 link 會有先後順序之分，被 link 的會不知道誰 link 他。如果想做到雙向呼叫 API 的機制的話，就會很麻煩。

## 指令補充說明

### `docker network create`

建立網路設定，用法如下：

```
docker network create [OPTIONS] NETWORK
```

本範例並沒有帶任何參數，但需要了解的是下面這個：

- `-d|--driver` 使用的 driver，預設 `bridge`，其他參數可以參考[官網](https://docs.docker.com/network/#network-drivers)

### `docker run`

選項補充：

- `--link` 連結 container，參數為 container name 或 hostname，也可以設定 alias
- `--network` 指定網路設定

## 今日自我回顧

瀏覽器連接 Apache 時，必須使用 8080 port，但進容器連結 Apache 時，則得改回使用 80 port。這是虛擬機與 [Port Forwarding](https://mileschou.me/ironman/12th/docker-newbie/day06/) 的特性，必須要清楚瞭解，使用 Docker 或虛擬機才不會搞混目前要使用什麼連接埠。

- 使用 `--link` 連結 container
- 使用 `--network` 連結 container
- 使用 volume 與擅長的 container 做連結，如 PHP + volume link MySQL

# Day 8 - 使用 environment 控制環境變數

在說明 [Port forwarding](https://mileschou.me/ironman/12th/docker-newbie/day05/) 時，有個範例是同個 image 開啟多個 container。實務上通常是更複雜的情境，比方說同個 image 開多個 container 且要使用不同的 DB 連線設定，當然這可以透過 [volume](https://mileschou.me/ironman/12th/docker-newbie/day06/) 解決，但如果今天要管理上百個 container 與上百份設定，volume 的做法反而很難管理。



這時有另一個選擇是使用 `--environment|-e` 選項。

`-e` 用法很簡單，直接給 `key=value` 即可，它會設定到環境變數裡：

```
# 查看原本的 env
docker run --rm busybox env

# 給 env 設定後再看 env 的內容
docker run --rm -e DB_HOST=mysql busybox env
```

不同的程式語言則會有不同的方法取得環境變數，以下使用 PHP 與 node.js 為例

```
# PHP
docker run --rm php -r "echo getenv('DB_HOST');"
docker run --rm -e DB_HOST=mysql php -r "echo getenv('DB_HOST');"

# node.js
docker run --rm node node -e "console.log(process.env.DB_HOST)"
docker run --rm -e DB_HOST=mysql node node -e "console.log(process.env.DB_HOST)"
```

## 如何應用 environment？

直接使用 DockerHub 上的 image 作為範例，會比較有感覺。這裡用 [Percona](https://hub.docker.com/_/percona) 做範例，文件裡面有提到很多 environment 可以搭配設定。

首先先示範 `MYSQL_ROOT_PASSWORD`，它會在 Percona 啟動的時候設定 root 帳號的密碼：

```
# Terminal 1
docker run --rm -it --name db -e MYSQL_ROOT_PASSWORD=pass percona

# Terminal 2
docker run --rm -it --link db percona mysql -hdb -uroot -ppass

# MySQL 指令
show databases;
```

`MYSQL_DATABASE` 則是啟動後建立對應名稱的資料庫，注意 client 最後執行 `show databases;` 後的結果：

```
# Terminal 1
docker run --rm -it --name db -e MYSQL_ROOT_PASSWORD=pass -e MYSQL_DATABASE=some percona

# Terminal 2
docker run --rm -it --link db percona mysql -hdb -uroot -ppass

# MySQL 指令
show databases;
```

`MYSQL_USER` 和 `MYSQL_PASSWORD` 可以設定 root 以外的新帳號和密碼，同時給予 `MYSQL_DATABASE` 所有存取權限。

這裡注意 client 指令的帳號密碼跟剛不大一樣了。

```
# Terminal 1
docker run --rm -it --name db -e MYSQL_RANDOM_ROOT_PASSWORD=yes -e MYSQL_USER=miles -e MYSQL_PASSWORD=chou -e MYSQL_DATABASE=some percona

# Terminal 2
docker run --rm -it --link db percona mysql -hdb -umiles -pchou

# MySQL 指令
show databases;
```

最後的範例是，搭配[連結 container](https://mileschou.me/ironman/12th/docker-newbie/day07/) 所學，使用 [phpMyAdmin](https://hub.docker.com/_/phpmyadmin) 連結 Percona：

```
# Terminal 1，使用 MYSQL_ROOT_PASSWORD 與 MYSQL_DATABASE
docker run --rm -it --name db -e MYSQL_ROOT_PASSWORD=pass -e MYSQL_DATABASE=some percona

# Terminal 2
docker run --rm -it --link db -p 8080:80 phpmyadmin
```

## 指令說明

### `docker run`

選項補充

- `-e|--env` 設定該 container 的環境變數

## 今日自我回顧

今天的環境變數使用方法很單純，但應用可以千變萬化。上面四個範例都使用了 Percona image，搭配 Docker 的隔離特性與環境變數功能，可以同時提供四種不同設定的 container。

- 使用 `-e` 設定 container 的環境變數
- 參考 image 說明，搭配 `-e` 選項，改變 container 的行為

# Day 9 - Container 應用

到目前為止，已經說明瞭 `docker run` 幾個常用的選項和參數，也做了一些簡單的範例。今天將以情境的方式，介紹如何應用 `docker run` 指令完成任務。



## 資料庫 client 端

使用 container 連線資料庫，如：

```
docker run --rm -it percona mysql -h10.10.10.10 -umiles -pchou
```

筆者曾遇過在連線資料庫的時候，遇到版本不相容的問題，所以有做過下面的測試：

```
# 換用其他 fork 的 client
docker run --rm -it mysql mysql -h10.10.10.10 -umiles -pchou
docker run --rm -it mariadb mysql -h10.10.10.10 -umiles -pchou

# 換用其他版本
docker run --rm -it percona:5.6 mysql -h10.10.10.10 -umiles -pchou
docker run --rm -it percona:5.7 mysql -h10.10.10.10 -umiles -pchou
```

最終成功地完成測試了。如果要在本機安裝多個版本會是困難的，相較使用具隔離性的 Docker container 測試起來就非常容易。

Redis 也可以用一樣的方法：

```
docker run --rm -it redis redis-cli -h10.10.10.10
docker run --rm -it redis:4 redis-cli -h10.10.10.10
docker run --rm -it redis:3 redis-cli -h10.10.10.10
```

## 資料庫 server 端

開發階段在測試的時候，最怕遇到多人共用資料庫的情境，因為會互相傷害影響測試結果。最好的方法還是人人自備資料庫，自己的資料自己建。

但像筆者對機器管理不熟悉，就算照著網路教學自己建好資料庫，但遇到問題或開不起來，也只能重灌治萬病，這樣做的風險也不低。

Docker 在這種情境下，會是個非常好用的工具。container 砍掉重練的效果就等於重灌，而且常見的 image 幾乎都找得到，一個 `docker pull` 指令就搞定了，連學習安裝過程和踩雷的時間都可以省下來。配合 `-p` 選項把 port 開放出去，那就跟在本機安裝 server 幾乎完全一樣，非常方便。

```
docker run --rm -it -p 3306:3306 -e MYSQL_ROOT_PASSWORD=pass mysql
docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=pass postgres
docker run --rm -it -p 6379:6379 redis
docker run --rm -it -p 11211:11211 memcached
```

## 指令借我用一下

筆者主要語言為 PHP，建置環境時，偶爾會需要用到 node.js。因為極少用到 node.js，所以不想額外安裝 nvm 等相關套件，但要用的當下又很麻煩，這有什麼方法能解決呢？

Docker 提供了滿滿的大平臺，只要透過下面這個 `docker run` 指令，即可達成「不安裝工具還要能使用工具」的任性需求：

```
docker run --rm -it -v $PWD:/source -w /source node:14-alpine npm -v
```

來分解並複習一下這些選項與參數的用途：

1. `--rm` 執行完後移除。當要使用功能的時候開 container，功能處理完後移除 container
2. `-it` 通常需要跟 container 互動，因此會加這個選項
3. `-v $PWD:/source` 把本機目錄綁定到 container，`$PWD` 為執行指令時的當下目錄，`/source` 則是 container 裡的絕對路徑
4. `-w /source` 是進去 container 時，預設會在哪個路徑下執行指令
5. `node:14-alpine` image 名稱，這裡用了 Alpine 輕薄短小版
6. `npm -v` 在 container 執行的指令，可以視需求換成其他指令

步驟有點複雜，有個方法是將它拆解成「進 container」與「container 裡執行指令」兩個步驟執行。在不清楚 container 發生什麼事的時候，拆解指令是個非常好用的方法；相反地，瞭解 container 運作過程的話，合併指令則是方便又直接，大家可視情況運用。

```
# 先查看目前檔案列表
ls -l

# 使用 shell
docker run --rm -it -v $PWD:/source -w /source node:14-alpine sh

# 進入 container 執行指令
npm -v

# 進入做其他事看看
npm init

# 離開 container 看看，多了一個 packages.json 檔案
ls -l
```

上面這個範例可以看到，因為有做 [bind mount](https://mileschou.me/ironman/12th/docker-newbie/day06/)，所以指令在 container 做的事情會同步回 host。簡單來說即：Host 沒有安裝指令也不打緊，用 Docker 啟動 container 幫忙執行後，再把結果傳回給 host。

接著拿上面產生的 `packages.json` 來做一個正式的範例：

```
# 確認內容
cat packages.json

# 安裝套件
docker run --rm -it -v $PWD:/source -w /source node:14-alpine npm install

# 確認產生的檔案
ls -l

# 再執行一次觀察差異
docker run --rm -it -v $PWD:/source -w /source node:14-alpine npm install
```

這個範例主要可以觀察到兩件事：

1. 第一次執行 `docker run` 時，因為沒有 `packages-lock.json`，所以 npm 有產生這個檔案，`ls -l` 也有看到
2. 第二次執行 `docker run` 時，已經有 `packages-lock.json` 了，所以 npm 做的事跟第一次不一樣

上面這個 `docker run` 指令即可安裝 `packages.json` 所需套件。

### 工程師可以再懶一點

每次打落落長的指令也很逼人，有個簡單的解決方案－－設定 alias。

```
# 確認無法使用 npm
npm -v

# 設定 alias
alias npm="docker run -it --rm -v \$PWD:/source -w /source node:14-alpine npm"

# 確認可以透過 docker run 使用 npm
npm -v
```

設定好後，打 `npm` 就等於打了長長一串 `docker run` 指令了。到這裡讀者也能感受，最後用起來的感覺會跟平常使用 `npm` 一模一樣，幾乎可以取代安裝工具。

類似的概念可以做到非常多工具上，下面是筆者目前實驗過可行的。

```
# 使用 Composer
alias composer="docker run -it --rm -v \$PWD:/source -w /source composer:1.10"

# 使用 npm
alias npm="docker run -it --rm -v \$PWD:/source -w /source node:14-alpine npm"

# 使用 Gradle
alias gradle="docker run -it --rm -v \$PWD:/source -w /source gradle:6.6 gradle"

# 使用 Maven
alias mvn="docker run -it --rm -v \$PWD:/source -w /source maven:3.6-alpine mvn"

# 使用 pip
alias pip="docker run -it --rm -v \$PWD:/source -w /source python:3.8-alpine pip"

# 使用 Go
alias go="docker run -it --rm -v \$PWD:/source -w /source golang:1.15-alpine go"

# 使用 Mix
alias mix="docker run -it --rm -v \$PWD:/source -w /source elixir:1.10-alpine mix"
```

最後筆者要提醒一個重點：這個範例主要是想讓讀者知道 Docker 可以如何應用。實務上，跟安裝好工具的使用經驗還是有所差別的。

### 路徑差異

因工作目錄是設定 `-w /source`，也許會因專案設定不同而導致工具執行出錯；另外，工具如果跟某個絕對路徑有相依，如 `~/.npm`，這也可能導致出錯。

### Kernel 差異

Container Kernel 不同可能會導致無法預期的錯誤。

以 Mac + Docker Desktop for Mac 來說，實際執行 container 是使用 Linux kernel，因此若工具有產生 binary，通常會是 for Linux，這時回到 Mac 直接使用就會出錯。

另外，Container Kernel 不同，在做 bind mount 時會有效能問題，簡單來說就是會跑比較慢一點。

## Docker 上跑就沒問題

若讀者有個好習慣是時常用 `--rm` 的話，那大部分的情況可以把這個標題大聲說出來：「Docker 上跑就沒問題」。

舉個例，[`laravel-bridge/scratch`](https://github.com/laravel-bridge/scratch) 套件需要在 PHP >= 7.1 版的環境裡執行單元測試，可以使用下面指令來測試套件在各個環境是否正常：

```
# 在 laravel-bridge/scratch 上跑測試
docker run -it --rm -v $PWD:/source -w /source php:7.1-alpine vendor/bin/phpunit
docker run -it --rm -v $PWD:/source -w /source php:7.2-alpine vendor/bin/phpunit
docker run -it --rm -v $PWD:/source -w /source php:7.3-alpine vendor/bin/phpunit
docker run -it --rm -v $PWD:/source -w /source php:7.4-alpine vendor/bin/phpunit
```

全部 pass，這樣就比較有信心跟其他開發者說，在 PHP 7.1 ~ 7.4 上都是沒問題的！

同樣地，我們也可以在 PHP 8.0 beta 上測試，來確保套件在即將發布的最新版上也是能正常運作的：

```
docker run -it --rm -v $PWD:/source -w /source php:8.0.0beta4-alpine vendor/bin/phpunit
```

## 指令補充說明

### `docker run`

- `-w|--workdir` 指定預設執行的路徑

## 今日自我回顧

今天比較像是筆者如何使用 Docker 的小技巧，有些情境都是不想裝或筆者不會裝，所以才會直接拿別人包好的 image 來用；有些情境則是確認使用官方 image 執行可以正常，則不管在哪個用一樣的方法執行也要正常。

- 練習透過 Docker 建立資料庫，與連線資料庫
- 練習拆解指令和合併指令，這在下一輪十天說明 build image 會重複使用這個技巧
- 練習用 Docker 指令配合開發程式碼做測試

## 參考資料

- [Composer image](https://hub.docker.com/_/composer)
- [Elixir image](https://hub.docker.com/_/elixir)
- [Golang image](https://hub.docker.com/_/golang)
- [Gradle image](https://hub.docker.com/_/gradle)
- [Node image](https://hub.docker.com/_/node)
- [Maven image](https://hub.docker.com/_/maven)
- [PHP image](https://hub.docker.com/_/php)
- [Python image](https://hub.docker.com/_/python)

# Day 10 - 使用 Docker Compose 摻在一起做懶人包

第一階段的最後一天，來看看這個方便的工具－－[Docker Compose](https://docs.docker.com/compose/)。Docker Compose 是用來組合多個 container 成為一個完整服務的工具。先前在說明如何[連結 container](https://mileschou.me/ironman/12th/docker-newbie/day07/) 時，已經有示範過連結 container 的基本方法。雖然可行，但要執行非常多指令才能把 container 串起來。Docker Compose 不只可以做到一樣的事，而且它使用 YAML 描述檔定義 container 的關係，簡化定義的過程，同時也實現了 IaC，讓 container 的關係可以簽入版本控制。



Docker Compose 最終結果是啟動 container，底層一樣會使用 `docker run` 指令，因此 Docker Compose 的設定參數會與 `docker run` 的選項和參數非常相似，這也是筆者選擇先詳細說明指令後，才開始介紹 Docker Compose 的原因。

以下會拿過去幾天曾看過的範例，改寫成 Docker Compose 格式。讀者可以看看 Docker 與 Docker Compose 之間如何轉換。

## 單一 container

首先小試身手，以 [Container 應用](https://mileschou.me/ironman/12th/docker-newbie/day09/) 裡提到的 node.js + npm 為例。

```
docker run -it --rm -v \$PWD:/source -w /source node:14-alpine
```

Docker Compose 使用 `docker-compose.yml` 做為預設載入設定的檔名，首先建立這個檔案，並輸入以下內容：

```
# 使用 3.8 版的設定檔，通常新版本會有新的功能，並支援新的設定參數
version: "3.8"

# 定義 service 的區塊，一個 service 設定可以用來啟動多個 container
services:
  # 定義一個叫 npm 的 service
  npm:
    image: node:14-alpine
    stdin_open: true
    tty: true
    working_dir: /source
    volumes:
      - .:/source
```

主要架構的說明可參考上面的註解，從 container 定義裡可以發現，跟 `docker run` 指令的選項或參數非常像。

- `image` 是指 [IMAGE](https://mileschou.me/ironman/12th/docker-newbie/day03/) 參數
- `stdin_open` 是 `--interactive` 選項；`tty` 是 `--tty` 選項，這在[瞭解 docker run 指令](https://mileschou.me/ironman/12th/docker-newbie/day04/)有提過
- `working_dir` 是 [Container 應用](https://mileschou.me/ironman/12th/docker-newbie/day09/) 有提到的 `--workdir` 選項
- `volumes` 是[使用 volume 同步程式](https://mileschou.me/ironman/12th/docker-newbie/day06/)有提過的 `--volume` 選項

定義好後，使用 `docker-compose run` 指令，即可達成與 `docker run` 一樣的效果：

```
docker-compose run --rm npm npm -v
```

## 多環境測試

一樣是 [Container 應用](https://mileschou.me/ironman/12th/docker-newbie/day09/)裡有提到的多環境執行單元測試：

```
docker run -it --rm -v $PWD:/source -w /source php:7.1-alpine vendor/bin/phpunit
docker run -it --rm -v $PWD:/source -w /source php:7.2-alpine vendor/bin/phpunit
docker run -it --rm -v $PWD:/source -w /source php:7.3-alpine vendor/bin/phpunit
docker run -it --rm -v $PWD:/source -w /source php:7.4-alpine vendor/bin/phpunit
```

改使用 `docker-compose.yml` 的定義如下：

```
version: "3.8"

services:
  php71: &basic
    image: php:7.1-alpine
    stdin_open: true
    tty: true
    working_dir: /source
    volumes:
      - .:/source
    command: vendor/bin/phpunit
  php72:
    <<: *basic
    image: php:7.2-alpine
  php73:
    <<: *basic
    image: php:7.3-alpine
  php74:
    <<: *basic
    image: php:7.4-alpine
  php80:
    <<: *basic
    image: php:8.0.0beta4-alpine
```

> 這個設定檔用了 YAML 的語法，讓文件內容可以被參考與重用。

- `command` 定義了啟動 container 會執行的指令，以 `docker run` 的例子，這裡要填的是 `vendor/bin/phpunit`。

照上面[單一 container](https://mileschou.me/ironman/12th/docker-newbie/day10/#單一-container) 的範例，可以猜得出來指令應該要這樣下：

```
docker-compose run --rm php71
docker-compose run --rm php72
docker-compose run --rm php73
docker-compose run --rm php74
docker-compose run --rm php80
```

但一個一個執行還是有點麻煩，這裡改用另一個指令：

```
docker-compose up
```

這個指令可以看到它同時間併發執行五個 container，並能在最後看到全部的結果。

## 連結多個 container

跟執行單個 container 狀況不同，因為多個 container 的狀況下，無法同時綁定終端機的輸入在每個 container 上，所以通常這個情境都是觀察 log 或是背景執行。

以[使用 environment 控制環境變數](https://mileschou.me/ironman/12th/docker-newbie/day08/)裡提到的 phpMyAdmin + MySQL 為例。

```
# Terminal 1
docker run --rm -it --name db -e MYSQL_ROOT_PASSWORD=pass -e MYSQL_DATABASE=some percona

# Terminal 2
docker run --rm -it --link db -p 8080:80 phpmyadmin
```

轉換成 `docker-compose.yml` 檔如下：

```
version: "3.8"

services:
  database:
    image: percona
    environment:
      MYSQL_ROOT_PASSWORD: pass
      MYSQL_DATABASE: some

  phpmyadmin:
    image: phpmyadmin
    ports:
      - 8080:80
    links:
      - database:db
```

- `environment` 即 `--env`
- `ports` 為 `-p` 即開出去的 port 設定
- `links` 為[連接 container](https://mileschou.me/ironman/12th/docker-newbie/day07/)所提到的 `--link`

執行指令：

```
# 直接前景執行，當中斷的時候，會停止所有 container。GIF 範例使用下面的指令
# docker-compose up

# 背景執行
docker-compose up -d

# 查看 log
docker-compose logs -f
```

## 連結更多 container

延續[連結多個 container](https://mileschou.me/ironman/12th/docker-newbie/day10/#連結多個-container)，我們再加一個 [Wordpress](https://hub.docker.com/_/wordpress) 服務，這次來直接修改 `docker-compose.yml` 檔：

```
version: "3.8"

services:
  database:
    image: percona
    environment:
      MYSQL_ROOT_PASSWORD: pass
      MYSQL_DATABASE: some

  phpmyadmin:
    image: phpmyadmin
    ports:
      - 8080:80
    links:
      - database:db

  wordpress:
    image: wordpress
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: root
      WORDPRESS_DB_PASSWORD: pass
      WORDPRESS_DB_NAME: some
    ports:
      - 80:80
    links:
      - database:db
```

接著再次執行指令：

```
# 背景執行
docker-compose up -d

# 查看 wordpress 的 log
docker-compose logs wordpress
```

`docker-compose.yml` 檔有修改，所以它會針對修改的部分做更新，以本例來說是要啟動 wordpress。

## 指令補充說明

### `docker-compose run`

用法：

```
docker-compose run [options] SERVICE [COMMAND]
```

與 `docker run` 非常像，但大部分的選項或參數都是取自於 YAML 裡的設定。

- `COMMAND` 為啟動 service 後，要執行的指令
- `--rm` 與 `docker run` 的 `--rm` 用法一樣，當 container 結束的時候就移除 container

### `docker-compose up`

用法：

```
docker-compose up [options] [SERVICE...]
```

建立並啟動所有 YAML 定義裡所有的 container。

- `SERVICE` 為 YAML 定義的 service 名稱，當沒有帶參數時，會建立並啟動所有 service，有帶則僅建立啟動該 service
- `-d` 與 `docker run` 的 `-d` 用法一樣，讓 container 在背景執行

### `docker-compose logs`

用法：

```
docker-compose logs [options] [SERVICE...]
```

查看 container 的標準輸出內容，以到目前為止的範例，都是 log 居多。

- `SERVICE` 為 YAML 定義的 service 名稱，當沒有帶參數時，會顯示所有 service log，有帶則會僅顯示該 service 的 log
- `-f` 當 container log 有更新時，會自動更新到畫面上

## 今日自我回顧

到目前為止，`docker run` 以及 Docker Compose 已經能幫助開發者輕鬆建立與部署開發用的測試環境，而且砍掉重練都非常容易，就算壞掉也不需要太擔心。

- 瞭解 Docker Compose 基本用法
- 練習將過去的範例套用在 Docker Compose 上

# Day 11 - 瞭解 Docker build 指令

前十天，我們使用 Docker 官方的 image 作為執行指令或開服務的環境，以這個角度來介紹 Docker 可以如何使用。接下來十天，將介紹如何建置自定義 image。



## Docker image 基本概念

最開始，得先了解 Docker image 的基本概念。首先最基本的，Docker 是採用 [Union 檔案系統](https://en.wikipedia.org/wiki/UnionFS)（簡稱 UnionFS）來儲存 image。

UnionFS 的特色如下：

1. 分層式的檔案系統
2. 支援把「檔案系統的修改」作為 commit，讓多個 commit 一層層堆疊
3. 支援把多個目錄掛載到同一個虛擬檔案系統下

Docker 是如何利用 UnionFS 的呢？我們來做點小實驗就會知道了。

首先一樣拿 [BusyBox](https://hub.docker.com/_/busybox) 來實驗，首先先照下面的指令執行：

```
# Terminal 1
docker run --rm -it --name some busybox

# 進去建立一些檔案
echo new commit > file
cat file

# Terminal 2，commit 檔案系統成為新的 image
docker commit some myimage

# 執行新的 image
docker run --rm -it --name new myimage

# 檢查剛剛建立的檔案是否存在
cat file
```

這裡有個新指令 `docker commit`，它可以把 container 上對檔案系統的修改 commit 成新的 image。

- 參數 `some` 為 container 名稱
- 參數 `myimage` 為 commit 完成後的 image 名稱
- commit 後會產生一個 sha256 digest

還記得[三個主要元件](https://mileschou.me/ironman/12th/docker-newbie/day03/)的特性嗎？image 因為有 digest，所以是不可修改的；container 是可以執行且可讀可寫，所以上面會有對檔案系統的修改。

Container 原本是疊在 BusyBox 上的讀寫層，當下了 `docker commit` 後，container 的修改內容會變成了不可修改的 image，而原本的 BusyBox 因為不可修改的特性，所以它依然可以拿來 run container，不會因此而消失。

接著來看一個範例，如果讀者有實驗過的話，會發現很多 image 都沒有內建 Vim。的確大多數情境是不需要，但還是希望有個內建 Vim 比較方便。沒關係，今天就來做一個 Vim image：

```
# Terminal 1
docker run --rm -it --name some alpine

# 進去確認並安裝 Vim
apk add --no-cache vim

# Terminal 2
docker commit some vim

# 執行新的 vim image
docker run --rm -it --name new vim

# 執行剛剛安裝好的 vim
vim
```

照上面的範例執行完後，先恭喜大家，我們成功基於 [Alpine](https://hub.docker.com/_/alpine) 上做出一個內建 Vim 的 image 了。從這兩個簡單的範例，相信讀者已經瞭解「分層式的檔案系統」的基本樣貌，以及如何運用 `docker commit` 來建立自己要的 image。

接著再繼續延伸下去思考：因多個 container 可以基於同一個 image，所以多個 image 基於同個 image 也是可行的，這樣的設計可以減少非常多空間浪費。而「多個目錄掛載到同一個虛擬檔案系統下」這個特點，其實就是之前說明的[使用 volume 同步程式](https://mileschou.me/ironman/12th/docker-newbie/day06/)。

## `Dockerfile` 與 `docker bulid` 指令

啟動並進入 container 做建置後，再使用 `docker commit` 的方法，雖然可以完成客製化 image 的需求，但這並不是 Docker 官方建議的做法，最主要的原因是，建置過程無法記錄與自動化建置，這會造成我建的 image 跟你建的 image 有可能會不一樣。因此 Docker 另外設計了 `Dockerfile` 來描述與執行自動化建置。

在說明之前，我們先整理一下 image 和 container 之間轉換的關係：

- 使用 `docker run` 可由 image 產生 container。這個在一開始介紹[三個主要元件](https://mileschou.me/ironman/12th/docker-newbie/day03/)的時候有提到
- 使用 `docker commit` 可由 container 產生 image。這個指令是今天一開始提到的

`Dockerfile` 的原理很單純，裡面可以描述 `RUN` 指令，完成後立即 commit，簡單來說就是不斷執行 run & commit。還是用範例做說明，以剛剛 Vim image 為例，可以先建立 `Dockerfile` 內容如下：

```
FROM alpine

RUN apk add --no-cache vim
```

接著執行 `docker build` 指令：

```
# Build 一個新的 image，完成後 tag 為 vim
docker build -t vim .

# 使用新的 image 執行 container
docker run --rm -it --name new vim
```

跟使用 `docker commit` 比起來，改用 `Dockerfile` 後，建置 image 的指令變得非常地簡單，而且 `Dockerfile` 是純文字檔，可以簽入版本控制。

再來我們觀察裡面幾個訊息，`docker build` 會把 `Dockerfile` 拆解成一行一行指令，它的第一個指令是 `FROM`，指的是要從哪個 image 為基底開始建置，範例的 `a24bb4013296` 即為 Alpine image 的 digest。

```
Step 1/2 : FROM alpine
 ---> a24bb4013296
```

接著第二步是執行 `RUN` 指令，後面接的是安裝 Vim 的指令 `apk add --no-cache vim`。

```
Step 2/2 : RUN apk add --no-cache vim
 ---> Running in 4d5e354483b8
fetch http://dl-cdn.alpinelinux.org/alpine/v3.12/main/x86_64/APKINDEX.tar.gz
fetch http://dl-cdn.alpinelinux.org/alpine/v3.12/community/x86_64/APKINDEX.tar.gz
(1/5) Installing xxd (8.2.0735-r0)
(2/5) Installing lua5.3-libs (5.3.5-r6)
(3/5) Installing ncurses-terminfo-base (6.2_p20200523-r0)
(4/5) Installing ncurses-libs (6.2_p20200523-r0)
(5/5) Installing vim (8.2.0735-r0)
Executing busybox-1.31.1-r16.trigger
OK: 35 MiB in 19 packages
Removing intermediate container 4d5e354483b8
 ---> f17e5e8e4781
```

這裡可以看到 `Running in 4d5e354483b8`，因為是 running 關鍵字，所以 `4d5e354483b8` 指的正是 `CONTAINER ID`。在安裝完成後會將 container commit，範例的 digest 是 `f17e5e8e4781`，接著會把 container 移除。

最後完成的訊息，會提醒 tag 名與 commit digest：

```
Successfully built f17e5e8e4781
Successfully tagged vim:latest
```

在建置 image 完成後，中間任一 commit 還是可以拿來做為 image 使用。但單靠 digest 資訊，是無法找到想要的 image，因此 Docker image 有提供一個功能叫 tag，它可以在 commit 上標上有意義的文字，如 `debian`、`php`、`node`、`wordpress` 等，甚至是額外的版本資訊，如 `php:7.2`、`php:7.3` 等。而沒有 tag 資訊的時候，預設則會代 `latest`，如 `vim` 與 `vim:latest` 是相同的。

所以從範例和說明可以知道，下面這三個指令的結果是一模一樣的：

```
docker run --rm -it --name new vim
docker run --rm -it --name new vim:latest
docker run --rm -it --name new f17e5e8e4781
```

## 今日自我回顧

Docker 可以先建立 [Debian](https://hub.docker.com/_/debian) image，再從 Debian 上安裝 [PHP](https://hub.docker.com/_/php) 與 [node.js](https://hub.docker.com/_/node)。其中 PHP 上的 [Wordpress](https://hub.docker.com/_/wordpress) 非常多人使用，因此為它建立一個專用的 image。

上述過程的示意圖如下：

![img](https://mileschou.me/ironman/12th/docker-newbie/day11/04-image-layer.gif)

從這個示意圖可以發現，PHP 與 node.js 的 image 有共用到 Debian 的 image 內容。因 `docker pull` 是把 commit 各別下載的，所以如何在下載 image 時，先下載 PHP 再下載 node.js，剛好又遇到有共用 image 的話，它會有段訊息會提醒使用者 commit 已下載完成。

今天先有這些基本概念，明天就要正式為自己的服務建置 image 了

- 瞭解 UnionFS，以及它能做到什麼事
- 瞭解 image 與 container 之間的關係
- 練習 `docker build` 與 `Dockerfile`
- 練習 `docker commit`

# Day 12 - 以 Laravel 為例，來 build image 吧！

[Laravel](https://laravel.com/) 是目前 PHP 很流行的框架，今天以看到 Laravel 的預設歡迎頁為目標，建置 Laravel image。



1. [初始化 Laravel](https://mileschou.me/ironman/12th/docker-newbie/day12/#初始化-Laravel)
2. [事前準備](https://mileschou.me/ironman/12th/docker-newbie/day12/#事前準備)
3. [Dockerfile 的第一手](https://mileschou.me/ironman/12th/docker-newbie/day12/#Dockerfile-的第一手)
4. [設定路徑與原始碼](https://mileschou.me/ironman/12th/docker-newbie/day12/#設定路徑與原始碼)
5. [設定啟動 server 指令](https://mileschou.me/ironman/12th/docker-newbie/day12/#設定啟動-server-指令)

## 初始化 Laravel

首先一開始，要先把 Laravel 主程式先準備好。參考 [Installing Laravel](https://laravel.com/docs/8.x#installing-laravel) 文件，安裝 PHP 7.3 與 [Composer](https://getcomposer.org/)，然後執行下面指令即可把 Laravel 程式安裝至 `blog` 目錄。

```
composer create-project --prefer-dist laravel/laravel blog
```

接著進 blog 目錄啟動 server：

```
cd blog

php artisan serve
```

完成後，看到 Laravel 的預設歡迎頁，程式碼就準備完成了。

## 事前準備

先定義 Docker 要下什麼指令，會達到跟官方執行 `php artisan serve` 一樣的結果：

```
docker run --rm -it -p 8000:8000 laravel
```

轉換成 `docker-compose.yml` 如下：

```
version: "3.8"

services:
  laravel:
    image: laravel
    stdin_open: true
    tty: true
```

其中 `-p 8000:8000` 是配合預設開 8000 port；image 取名為 `laravel`。

撰寫 `Dockerfile` 的過程中，會不斷重複啟動與移除 container 測試，筆者會用下面 `Makefile` 來簡化指令，示範和說明也比較清楚一點：

```
#!/usr/bin/make -f
IMAGE := laravel
VERSION := latest

.PHONY: all build rebuild shell run

# ------------------------------------------------------------------------------

all: build

# 建置 day27
build:
	docker build -t=$(IMAGE):$(VERSION) .

# 不使用 cache 建置 day27
rebuild:
	docker build -t=$(IMAGE):$(VERSION) --no-cache .

# 執行並使用 shell 進入 container
shell:
	docker run --rm -it -p 8000:8000 $(IMAGE):$(VERSION) bash

# 執行 container
run:
	docker run --rm -it -p 8000:8000 $(IMAGE):$(VERSION)
```

## Dockerfile 的第一手

筆者認為寫 `Dockerfile` 跟 [TDD](https://zh.wikipedia.org/zh-tw/測試驅動開發) 一樣有三循環如下：

1. 新增 Dockerfile 指令
2. 執行 `docker build` 並驗證是否正確
3. 最佳化 Dockerfile

撰寫 `Dockerfile` 的第一手，是先寫一個可以驗證成功的 `Dockerfile`，後續就可以走上面的三循環。

[昨天範例](https://mileschou.me/ironman/12th/docker-newbie/day11/)有提到 `FROM` 也是一個步驟。只要 image 在 [DockerHub](https://hub.docker.com/) 能下載得到，`Dockerfile` 就能 build 成功，我們可以寫一個只有 `FROM` 的 `Dockerfile`。Laravel 官網的 [Server Requirements](https://laravel.com/docs/8.x#server-requirements) 要求 PHP >= 7.3，因此我們使用 `php:7.3` image：

```
FROM php:7.3
```

接著執行 `make build` 與 `make shell` 試看看：

```
make build
make shell
```

建置完成，並在 commit 上 tag `laravel`，同時進去 shell 確認 PHP 版本正確。

> 註：目前 `laravel` tag 與 `php:7.3` tag 在同個 commit 上。

## 設定路徑與原始碼

預設的路徑是根目錄 `/`，是個一不小心就會刪錯檔案的位置，可以換到一個比較安全的目錄，比方說 `/source`：

```
WORKDIR /source
```

- `WORKDIR` 可以設定預設工作目錄。它同時是 `docker build` 過程與 `docker run` 的工作目錄，跟 `-w` 選項的意義相同。

接著把 Laravel 原始碼複製進 container 裡，這裡使用 `COPY` 指令：

```
COPY . .
```

- `COPY` 是把本機的檔案複製到 container 裡，使用方法為 `COPY [hostPath] [containerPath]`

要注意這裡有個雷，單一檔案複製沒有問題，但目錄複製就得小心。它的行為跟 Linux 常見的 `cp` 不大一樣。

```
cp -r somedir /some/path
```

以 `cp` 指令來說，上面指令執行完會多一個目錄 `/some/path/somedir`。

```
COPY somedir /container/path
COPY somedir/* /container/path
```

以 `COPY` 指令來說，上面兩個指令是等價的。原本預期會多一個 `/container/path/somedir` 目錄，實際上是 `somedir` 目錄裡所有東西全複製到 `/container/path` 下。

解決方法是改成下面這個指令：

```
COPY somedir /container/path/somedir
```

## 設定啟動 server 指令

[Docker Compose](https://mileschou.me/ironman/12th/docker-newbie/day10/) 裡有提到一個設定是 `command`，它定義了 container 啟動預設會執行的指令。`Dockerfile` 也有一樣用法的指令－－`CMD`。而啟動 server 指令一開始 Laravel 建好的時候已經知道了，`php artisan serve`。

套用在 `CMD` 指令上的用法會有兩種如下：

```
# exec 模式，官方推薦
CMD ["php", "artisan", "serve"]
# shell 模式
CMD php artisan serve
```

未來會再解釋這兩個模式的差異，先用官方推薦來試試。

實際執行的時候會發現不能正常連到 server？原因很簡單，在說明 [Port forwarding](https://mileschou.me/ironman/12th/docker-newbie/day05/) 的時候，曾用了下面這張圖：

![img](https://mileschou.me/images/ironman/12th/docker-newbie/port-forwarding.png)

當時提到每個 container 有屬於自己的 port，因為每個 container 都是獨立的個體，包括 host 也是一個獨立的個體。

再回頭看 Laravel 啟動 server 的資訊，它綁定了 `127.0.0.1:8000` 在 container 上。

```
Starting Laravel development server: http://127.0.0.1:8000
```

不能連線的原因其實非常單純，host 與 container 要視為兩臺不一樣的機器，因為 container 僅綁定本機－－也就是隻有進 container 使用 `curl http://127.0.0.1:8000` 可以連線，而 host 連 container 會被視為外部連線，因此會連線失敗。

解決方法很單純，把綁定 IP 調整即可，下例是以 `0.0.0.0` 全部開放為例：

```
CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

建置服務成功！測試也完成了，恭喜大家成功用 `Dockerfile` 建置 Laravel image 成功！

## 今日自我回顧

今天 `Dockerfile` 最後長相如下：

```
FROM php:7.3

WORKDIR /source
COPY . .

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

目前這個內容有很多缺陷，接下來會開始做 `Dockerfile` 最佳化，會一步步讓讀者知道更多 image 與 container 相關的技巧。

- 瞭解 build image 的流程
- 演練實際程式 build image

# Day 13 - 最佳化 Dockerfile - 調整 build context

寫 Dockerfile 並不困難，但好用的 Dockerfile 就需要利用許多技巧，加上不斷嘗試，才有辦法寫出來。



接下來會以昨天的 Dockerfile 為例，說明要如何寫出好的 Dockerfile。

```
FROM php:7.3

WORKDIR /source
COPY . .

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

## 什麼是 build context？

一開始執行 `docker build` 指令時，Docker 會將建置目錄裡的檔案複製一份到 Docker daemon 裡，接著才會開始執行 build image。

```
Sending build context to Docker daemon  42.95MB
```

Build context 指的是複製到 Docker daemon 的檔案。

昨天完成的 Dockerfile 存在一個很明確的問題：建置過程從 build context 傳入了太多非必要的檔案（指 `COPY . .` 無腦複製法），這會有下面的問題：

1. 讓建置時間變久
2. 增加不穩定因素
3. 增加不必要的檔案

今天針對 build context 來看看該如何調整 `Dockerfile`。

## 減少不必要的 build context

在 build image 的過程，如果遇到了 `COPY` 指令時，會從 build context 複製進 container。（其他需要用到 host 檔案的指令也是相同概念）

build context 的某些檔案可能會跟 build image 的流程或結果毫無關係，如 `.git` 目錄或 `.vagrant` 目錄。若不做任何處理，一來啟動 `docker build` 會花時間在複製檔案到 Docker daemon；二來在使用懶人複製法 `COPY . .` 也會把這些用不到的檔案複製進 container 佔用空間，可說是百害無一利。

Docker 定義了 `.dockerignore` 檔案，可以直接在裡面定義不進 build context 的檔案，範例如下：

```
.git
.vagrant
```

## 減少與 host 環境的關聯

`.git` 或 `.vagrant` 跟 build 出 Laravel image 的過程或結果無關，所以全部排除是沒有問題的。有些檔案則是結果需要，但過程會不希望從 host 複製進去的，比方說 `vendor` 目錄。

舉個例子，當 host 是 PHP 7.3，image 是 PHP 7.2 的時候，就很有可能會出問題。如 host 的 PHP 7.3 可能會安裝 PHPUnit 9，但在 image PHP 7.2 是不能使用的。

這時也可以利用 `.dockerignore` 來排除 `vendor` 目錄，達到加速 build image 的目的：

```
.git
.vagrant
vendor
```

同樣的概念可以應用在 `node_modules` 或類似的目錄上。

因 `vendor` 裡有程式運作必要的檔案，而剛剛只提到了要排除 `vendor`，並沒有提到如何把 `vendor` 生出來，因此才會出現找不到檔案的錯誤。

## 安裝需要的工具與依賴

`vendor` 在 host 可能會因為開發者環境不同，而安裝到不一樣的套件。但依[昨天](https://mileschou.me/ironman/12th/docker-newbie/day12/) `Dockerfile` 第一手的測試結果可以知道，container 的環境是 PHP 7.3，因此我們在 container 裡執行，就能確保安裝的環境是 PHP 7.3。

`Dockerfile` 執行指令使用 `RUN` 指令，而 Composer 安裝套件指令為 `composer install`，再改一次 `Dockerfile` 檔如下：

```
FROM php:7.3

WORKDIR /source
COPY . .
RUN composer install

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

這裡發現還是有問題，關鍵訊息為 `/bin/sh: 1: composer: not found`，意思是 `composer` 這個指令在 container 裡面找不到。

即然找不到指令，先把指令安裝好再執行 `composer install` 總沒問題了吧？

```
FROM php:7.3

WORKDIR /source
COPY . .
# 安裝 Composer 指令
RUN curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer
RUN composer install

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

`composer install` 看起來可以執行，但執行過程有問題，關鍵訊息有兩個：

1. The zip extension and unzip command are both missing, skipping.
2. sh: 1: git: not found

從訊息上看起來，第一個訊息是因為 zip ext 和 unzip 指令找不到，所以 Composer 採用了替代方案，使用 git 指令，但也沒有安裝，所以出現第二個訊息。

接下來有三個選擇：

1. 安裝 zip ext
2. 安裝 unzip 指令
3. 安裝 git 指令

因為第一個選擇會需要提到更多 PHP 的細節，因此筆者採取第二個選擇。安裝指令視平臺，會用到 `apt`、`yum`、`apk` 等指令，PHP 7.3 是 Debian 系統，所以會用 `apt` 指令。

範例是進 shell 先嘗試安裝指令。一開始無法安裝，但只要 update 套件資訊後就可以安裝了。最終的 `Dockerfile` 如下：

```
FROM php:7.3

WORKDIR /source
COPY . .
RUN curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer
# 安裝 unzip 指令
RUN apt update && apt install unzip
RUN composer install

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

此 `Dockerfile` 筆者嘗試可以建置完成，並使用 `make run` 開瀏覽器可以看到網頁。

## 今日自我回顧

今天有多加了幾個 `Dockerfile` 指令，目的是為了減少 build context，這讓 build image 的效率加快非常多。

另外更重要的，為了讓 `composer install` 指令能在 container 裡正常執行，筆者花了非常多功夫在說明如何發現、以及安裝工具。當要 build 客製化的 image 時，常常會遇到這類問題，建議讀者可以多瞭解並嘗試這些過程，這對未來解決問題會很有幫助。

- 練習使用 `.dockerignore` 將不必要的 build context 排除
- 練習使用 `Dockerfile` 三循環的流程，來發現缺少的工具，以及安裝需要的工具

# Day 14 - 最佳化 Dockerfile - 活用 cache

今天來看看如何利用 cache 讓 build image 更加順利。



Build image 第一次會正常執行每一個指令，第二次如果發現是同一個 commit 上，執行同一個指令，且結果推測不會變的時候，會把前一次執行結果的 commit 直接拿來用，並標上 `Using cache` 訊息。

```
---> Using cache
```

有效利用 cache 可以提升開發或測試 build image 的效率，這也是最佳化 Dockerfile 的一環。

延續使用[昨天](https://mileschou.me/ironman/12th/docker-newbie/day13/)的 Dockerfile：

```
FROM php:7.3

WORKDIR /source
COPY . .
RUN curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer
RUN apt update && apt install unzip
RUN composer install

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

上面這個範例無法有效利用 cache，可以用以下指令做個實驗：

```
# 先確認 build image 可以抓 cache
make build

# 隨意新增檔案，修改檔案也會有一樣的效果
touch some

# 先確認 build image 無法抓 cache
make build
```

從這個範例可以發現，程式有做任何修改，build image 都會需要全部重跑，浪費時間也浪費網路頻寬。

而根據 cache 生效的規則，我們只要找到第一個沒有 `Using cache` 的指令，就有機會知道問題在哪。

```
Step 1/7 : FROM php:7.3
 ---> d9b8167b4a1c
Step 2/7 : WORKDIR /source
 ---> Using cache
 ---> 6db08839d8a0
Step 3/7 : COPY . .
 ---> 70a56357ee18
```

從這個輸出資訊來看，是 `COPY . .` 沒有使用 cache。這是因為 touch 新檔案也包含在 `COPY . .` 的範圍裡，但新檔案 Docker 也不知道跟 build image 過程有關係，因此會讓 `COPY . .` 重新執行，接著後面全部都需要一起重新執行。

類似的問題，`COPY` 是針對 host 檔案，另外還有一個很像的指令是 `ADD`，後面可以接下載檔案的端口，如：

```
ADD https://example.com/download.zip .
```

它會在 build image 的時候下載連結的檔案並複製進 container。這功能看似很方便，實際上是會嚴重拖累 build image 時間的。因為一開始有提到：「結果推測不會變的時候」才會使用 cache。上面 `ADD` 例子的問題點在於，必須要把檔案下載回來才知道檔案內容有沒有被修改過，於是變成每次 build image 都需要下載檔案。

回到範例的 Dockerfile，調整方法很簡單，記住一個原則：

```
不常變動的 能早做就早做
常變動的 能晚做就晚做
```

我們把 Dockerfile 分做幾個部分：

1. 全域設定
2. 安裝環境，如 unzip 指令
3. 安裝程式工具，如 composer 指令
4. 程式碼

概念上來說，環境與工具會是變動最少的，最常變動的則是程式碼。筆者通常全域設定會放在一開始，偶爾在常調整設定的時候，會放在最後方便測試，最終還是要看使用情境與習慣。

根據上述順序調整如下：

```
FROM php:7.3

# 全域設定
WORKDIR /source

# 安裝環境、安裝工具
RUN curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer
RUN apt update && apt install unzip

# 程式碼
COPY . .
RUN composer install

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

用一樣的流程測看看，會看到 `Using cache` 變多，速度也變快很多。

```
Step 1/7 : FROM php:7.3
 ---> d9b8167b4a1c
Step 2/7 : WORKDIR /source
 ---> Using cache
 ---> 6db08839d8a0
Step 3/7 : RUN curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer
 ---> Using cache
 ---> c5a5b2b80982
Step 4/7 : RUN apt update && apt install unzip
 ---> Using cache
 ---> ddf04cc99574
Step 5/7 : COPY . .
 ---> d1bc2db13e9f
```

但一樣卡在時間花最久的 `composer install`，它不能放到 `COPY . .` 的上面，因為它會需要複製進去的 `composer.json` 與 `composer.lock`。

咦？既然它需要這兩個檔，那就先複製進去再執行 `composer install` 就好了呀！改法如下：

```
FROM php:7.3

# 全域設定
WORKDIR /source

# 安裝環境、安裝工具
RUN curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer
RUN apt update && apt install unzip

# 安裝程式依賴套件
COPY composer.* ./
RUN composer install --no-scripts

# 複製程式碼
COPY . .
RUN composer run post-autoload-dump

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

這次會發現 `composer install` 有用到 cache，而且速度已經快到可以全程錄進 GIF 了。

```
Sending build context to Docker daemon  501.8kB
Step 1/9 : FROM php:7.3
 ---> d9b8167b4a1c
Step 2/9 : WORKDIR /source
 ---> Using cache
 ---> 6db08839d8a0
Step 3/9 : RUN curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer
 ---> Using cache
 ---> c5a5b2b80982
Step 4/9 : RUN apt update && apt install unzip
 ---> Using cache
 ---> ddf04cc99574
Step 5/9 : COPY composer.* ./
 ---> Using cache
 ---> 7e6b6308c79c
Step 6/9 : RUN composer install --no-scripts
 ---> Using cache
 ---> 6c8d6d6d168d
Step 7/9 : COPY . .
 ---> 63ab9135e738
```

這個 Dockerfile 對 cache 的最佳化就到此結束，從剛實驗看起來，目前改程式重 build image 都非常快速，已達成今天所預期的目標。

## 不使用 cache

最後補充一點，有些情況會希望 Docker 強制重新 build image 而不要使用 cache，這時可以使用之前提供的 [Makefile](https://mileschou.me/ironman/12th/docker-newbie/day12/) 裡的 `make rebuild` 指令：

```
rebuild:
	docker build -t=$(IMAGE):$(VERSION) --no-cache .
```

相信不需要解釋，`--no-cache` 正是不使用 cache。

## 今日自我回顧

今天介紹的最佳化方法，是著重在利用 cache 加速 build image。但不要忘了今天開頭提到的，**cache 就是 commit**，有時候必須要把它視為 commit 來做最佳化，這將會是明天的主題。

- 瞭解 `Using cache` 在 build image 是怎麼運作的
- 練習利用 cache 加速 build image 的方法

# Day 15 - 最佳化 Dockerfile - 精簡 image

最佳化 Dockerfile 還有很多方向，那筆者以精簡 image 做為結尾，有興趣可以參考文末的參考資料連結。



精簡 image 筆者分成兩個部分說明，一個是容量，另一個是 commit 數。到[昨天](https://mileschou.me/ironman/12th/docker-newbie/day14/)為止，Dockerfile 內容有點少，筆者先根據 Laravel 官網的 [Server Requirements](https://laravel.com/docs/8.x#server-requirements) 與 [Redis](https://laravel.com/docs/8.x/redis#introduction) 把 `bcmath` 和 `redis` PHP Extension 安裝也加入 Dockerfile：

```
FROM php:7.3

# 全域設定
WORKDIR /source

# 安裝環境、安裝工具
RUN curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer
RUN apt update && apt install unzip

# 安裝 bcmath 與 redis
RUN docker-php-ext-install bcmath
RUN pecl install redis
RUN docker-php-ext-enable redis

# 加速套件下載的套件
RUN composer global require hirak/prestissimo

# 安裝程式依賴套件
COPY composer.* ./
RUN composer install --no-scripts

# 複製程式碼
COPY . .
RUN composer run post-autoload-dump

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

接著就看筆者如何精簡這份 image

## 精簡容量

Docker 讓啟動 container 的流程變簡單，理論上啟動 container 應該是飛快的，但 image 如果又肥又大，那這件事就只能活在理論裡了。

### 移除暫存檔案

有的指令會在執行過程產生暫存檔案，如上例的 `apt` 和 `composer global require` 都會產生下載檔案的 cache 並 commit 進 image。這些檔案通常沒有必要保留，因此可以移除節省空間。

這裡要重新提醒一個 Dockerfile 產生 Docker image 的觀念：一個指令就是一個 commit，有多少 commit 就會佔用多少容量。比方說下面的寫法：

```
RUN curl -LO https://example.com/download.zip && dosomething
RUN rm download.zip
```

這個寫法會產生一個有 `download.zip` 檔案的 commit 與一個移除 `download.zip` 檔案的 commit，這樣是無法確實地把 `download.zip` 容量釋放出來的，需要改用下面的寫法：

```
RUN curl -LO https://example.com/download.zip && dosomething && rm download.zip
```

這個寫法，`RUN` 指令最後的結果會是 `download.zip` 檔案已移除，因此 commit 就不會有 `download.zip` 的內容。

總之，當看到移除檔案的指令是獨立一個 `RUN` 的話，那個指令通常是有像上面範例一樣的改善空間。

#### `apt` 調整寫法實測

`apt` 清除快取的寫法為：

```
apt clean && rm -rf /var/lib/apt/lists/*

# 或使用 apt-get
apt-get clean && rm -rf /var/lib/apt/lists/*
```

筆者實測下面兩種寫法：

```
RUN apt update && apt install unzip
RUN apt update && apt install unzip && apt clean && rm -rf /var/lib/apt/lists/*
```

結果如下：

```
$ docker images laravel
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
laravel             latest              ac4543dab760        37 minutes ago      502MB
laravel             optimized           c68838f961f0        43 seconds ago      485MB
```

可以看得出明顯的差異。

#### `composer global require` 調整寫法實測

Composer 清快取的指令為 `composer clear-cache`。實測下面兩種寫法：

```
RUN composer global require hirak/prestissimo
RUN composer global require hirak/prestissimo && composer clear-cache

RUN composer install --no-scripts
RUN composer install --no-scripts && composer clear-cache
```

結果如下：

```
$ docker images laravel
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
laravel             latest              ac4543dab760        41 minutes ago      502MB
laravel             optimized           5672f76be599        6 seconds ago       461MB
```

可以看出這個差異也非常多，兩個總合起來就能省掉 50MB 的空間，不無小省。

最終的 Dockerfile 如下：

```
FROM php:7.3

# 全域設定
WORKDIR /source

# 安裝環境、安裝工具
RUN curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer
RUN apt update && apt install unzip && apt clean && rm -rf /var/lib/apt/lists/*
RUN docker-php-ext-install bcmath
RUN pecl install redis
RUN docker-php-ext-enable redis

# 加速套件下載的套件
RUN composer global require hirak/prestissimo && composer clear-cache

# 安裝程式依賴套件
COPY composer.* ./
RUN composer install --no-scripts && composer clear-cache

# 複製程式碼
COPY . .
RUN composer run post-autoload-dump

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

雙管齊下的結果如下：

```
$ docker images laravel
REPOSITORY          TAG                 IMAGE ID            CREATED              SIZE
laravel             latest              097e4cc0805f        3 seconds ago        502MB
laravel             optimized           55d3a5fcfd3d        About a minute ago   443MB
```

### 移除非必要的東西

以最初的目標來看，是要啟動一個 Laravel 的 server 並看到歡迎頁，那其實有些套件就不是必要的，如單元測試套件。Composer 加上 `--no-dev` 參數即可排除開發階段安裝的套件。

```
RUN composer install --no-dev --no-scripts && composer clear-cache
```

結果如下：

```
$ docker images laravel
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
laravel             latest              097e4cc0805f        38 minutes ago      502MB
laravel             optimized           fd655c5532e0        3 seconds ago       426MB
```

其他常見非必要的工具如 vim、sshd、git 等，在 container 執行的時候，通常都用不到，這些都是可以移除的目標。

> 本範例沒有非必要的工具。

### 改使用容量較小的 image

剛開始使用 Docker 的時候，通常會找自己比較熟悉的 Linux 發行版，像筆者是 Ubuntu 派的。不同的發行版，其實容量也有點差異，以下是今天下載 [Ubuntu](https://hub.docker.com/_/ubuntu)、[Debian](https://hub.docker.com/_/debian)、[CentOS](https://hub.docker.com/_/centos)、[Alpine](https://hub.docker.com/_/alpine) 的容量比較：

```
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
ubuntu              latest              9140108b62dc        3 days ago          72.9MB
debian              stable-slim         da838f7eb4f8        2 weeks ago         69.2MB
debian              latest              f6dcff9b59af        2 weeks ago         114MB
centos              latest              0d120b6ccaa8        7 weeks ago         215MB
alpine              latest              a24bb4013296        4 months ago        5.57MB
```

這裡可以看到 Alpine 小到很不可思議，而 Debian 則是有普通版跟 slim 版，這些都是可以嘗試的選擇。以 PHP 官方 image 來說，主要版本是 Debian，但也有 Alpine 的版本，因此如果有需要追求極小 image 的話，也是可以多找看看有沒有已經做好的 Alpine 版本可以 `FROM` 來用，網路也比較多文章在討論使用 Alpine 的好處。

以下為改寫成 Alpine 的 Dockerfile，主要差異在 `apk` 安裝指令：

```
FROM php:7.3-alpine

# 全域設定
WORKDIR /source

# 安裝環境、安裝工具
RUN curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer
RUN apk add --no-cache unzip
RUN docker-php-ext-install bcmath
RUN apk add --no-cache --virtual .build-deps autoconf g++ make && pecl install redis && apk del .build-deps
RUN docker-php-ext-enable redis

# 加速套件下載的套件
RUN composer global require hirak/prestissimo && composer clear-cache

# 安裝程式依賴套件
COPY composer.* ./
RUN composer install --no-dev --no-scripts && composer clear-cache

# 複製程式碼
COPY . .
RUN composer run post-autoload-dump

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

改完之後的結果如下，差了 300MB：

```
$ docker images laravel
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
laravel             optimized           ce9f7438e818        14 seconds ago      102MB
laravel             latest              097e4cc0805f        53 minutes ago      502MB
```

雖然看起來很美好，但事實上改用 Alpine 並不是簡單的事，以下聊聊筆者從 Ubuntu 轉 Alpine 的一點心得。

#### shell 不是 bash

因筆者對寫腳本不熟，因此有發生 bash 指令在 sh 上不能使用的問題，當時處理了很久才解決。

#### 不同的套件管理工具

Ubuntu 為 `apt`，Alpine 為 `apk`。用途都是下載套件，使用概念大多都差不多，而實際使用上最大的困擾在於套件名稱不同。比方說，Memcached 的相關套件，apt 叫 `libmemcached-dev`，apk 則是 `libmemcached-libs`，這類問題都得上網查詢資料，以及做嘗試才能找到真正要的套件為何。

#### 系統使用的 libc 不同

Alpine 採用 [musl libc](https://musl.libc.org/) 而不是 [glibc](https://www.etalabs.net/compare_libcs.html) 系列，因此某些套件可能會無法使用。

> 更詳細的說明可參考 [PHP image](https://hub.docker.com/_/php) 或其他官方 image 對於 Alpine image 的解釋。

官方說法是大多數套件都沒有問題，但聽朋友說過確實踩過這個雷，只是筆者從來沒遇過，所以沒有範例可以說明。

## 精簡 commit

Docker 的 commit 數量是有限制的，為 127 個，這是精簡的理由之一。另一個更重大的理由是：如果檔案系統使用 [AUFS](https://docs.docker.com/storage/storagedriver/aufs-driver/) 的前提下，只要 commit 數越多，檔案系統的操作就會越慢，因此更需要想辦法來減少 commit 數。

> 參考 [DOCKER基礎技術：AUFS](https://coolshell.cn/articles/17061.html)

### 合併 commit

再次提醒，一個 Docker 指令就是一個 commit。通常能合併的會是 `RUN` 指令，如：

```
# 合併前
RUN apk add --no-cache git
RUN apk add --no-cache unzip

# 合併後
RUN apk add --no-cache git unzip
```

可是如果指令過長的話，就會失去維護性。通常筆者會改寫成像下面這樣：

```
RUN apk add --no-cache \
        git \
        unzip
```

這樣比較能一眼看出目前裝了什麼套件，但相對在 build 的過程，資訊相較就會比較雜亂。

筆者參考官方 Dockerfile，發現 `set -xe` 可以對查 log 有幫助：

```
FROM php:7.3-alpine

RUN set -xe && \
        apk add --no-cache \
            git \
            unzip
```

實際作用筆者沒有特別研究，但對於 build 過程的影響，最主要的差異在：不管串接幾個指令，它都會有一個像下面的 log：

```
+ apk add --no-cache git unzip
```

它還會同時把空白全部去除，這樣在看 build log 會非常清楚。

### 要如何決定合併的做法

追求極致，把所有 `RUN` 合併在一個 commit，那這樣就會喪失分層式可以共用 image 的優點，因此如何拿捏適點的 commit 大小，是很有藝術的。

以 PHP 為例，筆者通常會分成下面幾種類型：

1. 系統層的準備，如 `unzip`
2. PHP extension 的準備，如 `bcmath` 或 `redis`
3. 依賴下載，包括 Composer 執行檔
4. 執行程式初始化順序

這邊就不說明怎麼處理的，直接給結果吧：

```
FROM php:7.3-alpine

# 全域設定
WORKDIR /source

# 安裝環境
RUN apk add --no-cache unzip

# 安裝 extension
RUN set -xe && \
        apk add --no-cache --virtual .build-deps \
            autoconf \
            g++ \
            make \
        && \
            docker-php-ext-install \
                bcmath \
        && \
            pecl install \
                redis \
        && \
            docker-php-ext-enable \
                redis \
        && \
            apk del .build-deps \
        && \
            php -m

RUN set -xe && \
        curl -sS https://getcomposer.org/installer | php && \
        mv composer.phar /usr/local/bin/composer

# 加速套件下載的套件
RUN composer global require hirak/prestissimo && composer clear-cache

# 安裝程式依賴套件
COPY composer.* ./
RUN composer install --no-dev --no-scripts && composer clear-cache

# 複製程式碼
COPY . .
RUN composer run post-autoload-dump

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

## 今日自我回顧

會影響 container 啟動快與否，有一部分會取決於 image 下載時間，這也是今天能解掉的問題；另外則是 process 的調整，未來有機會再討論。

- 練習減少 image 的空間
- 練習整理 RUN 指令

## 參考資料

- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

# Day 16 - 為各種框架 build image

今天將會應用之前 build image 的技巧，來為以下框架的 hello world 寫 Dockerfile。



1. [Phoenix](https://www.phoenixframework.org/)
2. [Amber](https://amberframework.org/)
3. [Rocket](https://rocket.rs/)
4. [Lapis](https://leafo.net/lapis/)

這幾個框架在臺灣應該都很冷門，主要是想展示：只要有 image 就有辦法初始化程式；只要有程式和 Dockerfile，讀者就可以建得出跟筆者一樣的環境與 server，這正是 Docker 實現 IaC 特性的方便之處。

以下示範四種框架的方法都大同小異，初始化程式是使用了[應用 Container](https://mileschou.me/ironman/12th/docker-newbie/day09/) 裡提到的借用指令技巧來做；寫 Dockerfile 則是與 [Laravel 建 image](https://mileschou.me/ironman/12th/docker-newbie/day12/) 做法一樣，一步一步寫出來。筆者會直接把結果放上來，但會說明哪個地方讓筆者撞牆很久。

## Phoenix

Phoenix 使用 [Elixir](https://hub.docker.com/_/elixir) 語言撰寫，參考官網的 hello world 建置與執行指令如下：

```
mix archive.install hex phx_new 1.5.5
mix phx.new --no-ecto --no-webpack --app ironman phoenix

# 啟動 server
mix phx.server
```

> `mix` 是 Elixir 內建的套件管理工具。

從這裡可以看得出，它框架初始化的做法與 Laravel 或 Node 類似：透過套件管理工具下載框架提供的工具，再用這個工具來初始化程式。因此可以直接使用 Elixir image，進入 container 直接執行上面兩個指令，即可產生 Phoenix 的初始化程式碼在 host 裡。

```
docker run --rm -it -v $PWD:/source -w /source elixir:1.10-alpine sh
```

### Dockerfile

```
FROM elixir:1.10-alpine

WORKDIR /usr/app/src

# 準備套件工具的設定
RUN set -xe && \
        mix local.hex --force && \
        mix local.rebar --force

# 安裝套件
COPY mix.* ./
RUN mix deps.get

# 原始碼與編譯
COPY . .
RUN mix compile

# 啟動 server 的指令
CMD ["mix", "phx.server"]
```

最後是 run image：

```
docker build -t=phoenix .
docker run --rm -it -p 4000:4000 phoenix
```

> 其他框架因為只是名稱和 port 不同，所以就不重覆此段範例了。

### 小結

Phoenix 是編譯語言，所以會比 Laravel 多了編譯的過程。另外啟用 [hex](https://hex.pm/) 與 [rebar](http://rebar3.org/) 套件在建 image 過程就有明顯的提示訊息，所以都很容易解決。

## Amber

Amber 使用 [Crystal](https://hub.docker.com/r/crystallang/crystal/) 撰寫。先找到如何產生初始化程式的指令：

```
amber new --minimal amber
```

這裡會發現它跟 Phoenix 不一樣，有自己專屬的指令 `amber` 在處理初始化。而這個指令需要編譯，且需要 Crystal 的環境，有點麻煩。幸好 Amber 官方已經建好 [Amber image](https://hub.docker.com/r/amberframework/amber) 可以直接使用了。

```
docker run --rm -it -v $PWD:/source -w /source amberframework/amber:0.35.0 bash
```

### Dockerfile

產生出來的程式裡面就有 Dockerfile 了，真的很貼心：

```
FROM amberframework/amber:0.35.0

WORKDIR /app

# shards 是 Crystal 的套件管理工具
COPY shard.* /app/
RUN shards install

COPY . /app

RUN rm -rf /app/node_modules

# Amber 起本機測試服務，並開啟動態編譯功能
CMD amber watch
```

### 小結

Amber 因為有提供 Dockerfile，所以就相較單純了點，只有特別去了解 `shards` 指令是套件管理工具（之前的版本是 `crystal deps`），以及瞭解 `amber` 指令有什麼功能。

## Rocket

Rocket 使用 [Rust](https://hub.docker.com/_/rust) 撰寫。Phoenix、Amber 與 Lapis 都有提供框架專屬的整合指令，但 Rocket 沒有，但 Rust 內建的套件管理工具 Cargo 有基本專案初始化指令，可以從這裡開始建立專案：

```
# 使用 cargo 建立專案
cargo new rocket --bin
```

再來 `Cargo.toml` 與 `main.rs` 檔，照著[官方教學](https://rocket.rs/v0.4/guide/getting-started/)輸入內容，最後執行即可啟動開發用的 server：

```
cargo run
```

主要都是用 Cargo，所以可以直接拿 Rust image 來執行指令：

```
docker run --rm -it -v $PWD:/source -w /source rust:1.46 bash
```

### Dockerfile

```
FROM rust:1.46

WORKDIR /usr/src/app

ENV USER=dummy

# Rocket 官方教學有提到要開 nightly
# 會在這裡執行 cargo init，這是 cargo build 一個 issue
RUN rustup default nightly && cargo init --bin --name dummy .

COPY Cargo.* ./

# 下載並編譯依賴
RUN cargo build

COPY . .

# 編譯主程式
RUN cargo build

CMD ["cargo", "run"]
```

### 小結

這個框架遇到了兩個麻煩事，第一個是昨天提的 [Alpine](https://mileschou.me/ironman/12th/docker-newbie/day15/) 問題，筆者總算遇到了，在 `cargo build` 編譯的時候出錯，改成 Debian 就正常了。

另一個則是，原本想跟其他框架一樣，把依賴 `COPY Cargo.* ./` 跟複製檔案 `COPY . .` 切成兩個階段，但 `cargo build` 會需要存在一個 `src/main.rs` 檔，才能正常執行。一個很笨，但很有效的方法：`cargo init` 一個 dummy 專案即可。

## Lapis

Lapis 使用 [Lua](https://www.lua.org/) 撰寫。Docker 官方並沒有出 Lua image，因此筆者有手癢寫了 [Lua image](https://hub.docker.com/r/mileschou/lua)。

Lapis 參考[官方文件](https://leafo.net/lapis/reference/moon_getting_started.html)，建置與執行的指令如下：

```
lapis new

# 使用 MoonScript 需要編譯
moonc *.moon

lapis server
```

Lapis 官方也沒出 image，筆者自己有寫了一個 [Lapis image](https://hub.docker.com/r/mileschou/lapis)，可以直接拿來用：

> Lapis 的 Dockerfile 比較複雜，有興趣可以看 [Dockerfile](https://github.com/MilesChou/docker-lua/blob/master/5.3/Dockerfile)。

```
docker run --rm -it -v $PWD:/source -w /source mileschou/lapis:alpine sh
```

### Dockerfile

```
FROM mileschou/lapis:alpine

WORKDIR /usr/src/app

COPY . .

RUN moonc *.moon

CMD ["lapis", "server"]
```

### 小結

Lapis 因為最麻煩的環境，筆者以前已經搞定了，所以這邊的 Dockerfile 就能寫得很簡單。

## 今日自我回顧

今天的程式碼有放上 [GitHub](https://github.com/MilesChou/ironman2020-sample)，有興趣可以去下載回來 build 看看。

雖然開頭有提到，今天要示範 Docker 的 IaC 特性，但筆者額外想提的觀念是：身為開發人員，想要使用既有的 Docker image 或是撰寫 Dockerfile，不只是要學好 Docker 而已，對程式工具、執行流程以及相關錯誤訊息都要有清楚的認知，才能真正有效發揮出 Docker 的優點。

# Day 17 - Multi-stage Build

在說明 Multi-stage Build 之前，先來簡單瞭解持續整合（Continuous Integration，以下簡稱 CI）的 Build 與 DevOps 的 Pipeline。



CI 裡面用了 [Build](https://mileschou.me/ironman/2017/start-to-ci/day06/) 這個關鍵字，實際它背後做的事包含了 compilation、testing、inspection 與 deployment 等；而 DevOps [Pipeline](https://mileschou.me/ironman/2017/start-to-ci/day21/) 則提到軟體生命週期有 development、testing、deployment 不同的階段（stage），同時每個階段都有可能會產生 artifacts。

> 對 CI 有興趣可以參考筆者過去寫的鐵人賽：[CI 從入門到入坑](https://mileschou.me/ironman/2017/start-to-ci)

綜合上述說明，在 build 的過程會做不同的任務，並產生 artifacts，而在不同階段又會做不同的任務。

接著來看範例，延續[最佳化 Dockerfile](https://mileschou.me/ironman/12th/docker-newbie/day15/) 完之後的結果如下：

```
FROM php:7.3-alpine

# 全域設定
WORKDIR /source

# 安裝環境
RUN apk add --no-cache unzip

# 安裝 extension
RUN set -xe && \
        apk add --no-cache --virtual .build-deps \
            autoconf \
            g++ \
            make \
        && \
            docker-php-ext-install \
                bcmath \
        && \
            pecl install \
                redis \
        && \
            docker-php-ext-enable \
                redis \
        && \
            apk del .build-deps \
        && \
            php -m

RUN set -xe && \
        curl -sS https://getcomposer.org/installer | php && \
        mv composer.phar /usr/local/bin/composer

# 加速套件下載的套件
RUN composer global require hirak/prestissimo && composer clear-cache

# 安裝程式依賴套件
COPY composer.* ./
RUN composer install --no-dev --no-scripts && composer clear-cache

# 複製程式碼
COPY . .
RUN composer run post-autoload-dump

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

這個 Dockerfile 已可以建置出 Laravel image，但思考以下這兩個奇妙的問題：

1. Image 最終要部署到線上環境，任何開發或建置工具（如 Composer）都不需要，該怎麼做？
2. Image 若需要做為開發測試共用環境，需要開發工具（如 PHPUnit），該怎麼辦？

目前 Dockerfile 的最佳化方法，面對這兩個問題會是矛盾大對決，要嘛偏維運，要嘛偏開發，無法同時解決。

> 幾乎所有語言都會有這個問題，所以回頭看完[各種框架如何 build image](https://mileschou.me/ironman/12th/docker-newbie/day16/) 後，現在再來看這個問題，相信更有感覺。

## Dapper

最單純直接的解決方法，就是針對維運與開發寫兩個 Dockerfile，但這在使用上非常不方便，於是第三方 Rancher 就寫了一個工具－－[Dapper](https://mileschou.me/ironman/2017/start-to-ci/day23/)，主要 Dockerfile 作為維運用，而用另一個指令來處理開發用的 Dockerfile。

## Multi-stage Build 概念

若需要在開發用的環境上，處理不固定的任務（如：依狀況進入 container 下不同的指令），Dapper 是非常好用的；如果在 container 上是處理固定的任務（如：執行 `phpunit`），則使用 Docker 17.05 開始推出的 [Multi-stage Build](https://docs.docker.com/develop/develop-images/multistage-build/) 會更方便。

概念其實很簡單，參考下面的 Dockerfile：

```
FROM alpine AS build
RUN touch test

FROM alpine
COPY --from=build /test .
RUN ls -l /test
```

這個 Dockerfile 有三個特別的地方跟過去不大一樣：

1. 有兩個 `FROM` 指令，每個 `FROM` 指令都代表一個 stage，每個 stage 的結果都是 image
2. 第一個 `FROM` 指令使用 `AS` 可以為 image 取別名
3. `COPY` 多了一個選項 `--from`，選項要給的值是 image，實際行為是從該 image 把對應路徑的檔案或 artifacts，複製進 container

執行過程如下：

1. 第一個 stage 產生了 test 檔案
2. 第二個 stage 把第一個 stage 產生的 test 檔案複製過來，並使用 ls 觀察

這兩個 stage 是有互相依賴的，因此 `touch test` 指令若移除的話，就會出現找不到檔案的錯誤。

### COPY image 檔案

上面有提到 `COPY` 的 `--form` 選項要給值是 image，實際上不只可以使用 stage image，而是連 remote repository 都能使用。因此像 [Composer](https://hub.docker.com/_/composer) 有 image，且執行檔單一檔案，所以安裝 Composer 的方法，可以改成下面這個寫法：

```
COPY --from=composer:1 /usr/bin/composer /usr/bin/composer
```

### FROM stage image

因 stage image 的 alias 可以當作 image 用，所以下面這個寫法是可行的：

```
FROM alpine AS curl
RUN apk add --no-cache curl

FROM curl AS build1
RUN curl --help

FROM curl AS build2
RUN curl --version
```

## 實作 Multi-stage Build

最後這裡就舉複雜的範例：一開始提的[最佳化 Dockerfile](https://mileschou.me/ironman/12th/docker-newbie/day15/)，我們把拿它套用 Multi-stage Build。這個 Dockerfile 它可以分作下面幾個 stage：

```
# PHP 環境基礎
FROM php:7.3-alpine AS base

# npm 建置 stage
FROM node:12-alpine AS npm_builder

# Composer 安裝依賴
FROM base AS composer_builder

# 上線環境
FROM base
```

Composer 與上線環境依賴 base 是因為像 `bcmath` 和 `redis` 套件依賴是屬於底層共用的套件，所以打一個共用 image 會比較方便一點；另外 Laravel 框架 skeleton 有內帶 npm 相關檔案，這次也加入成一個 stage。

先看 base image，這段應該沒問題，因為它只做安裝 extension：

```
FROM php:7.3-alpine AS base

# 安裝 extension
RUN set -xe && \
        apk add --no-cache --virtual .build-deps \
            autoconf \
            g++ \
            make \
        && \
            docker-php-ext-install \
                bcmath \
        && \
            pecl install \
                redis \
        && \
            docker-php-ext-enable \
                redis \
        && \
            apk del .build-deps \
        && \
            php -m
```

再來 npm image 應該也沒有太大問題：

```
FROM node:14-alpine AS npm_builder

WORKDIR /source

COPY package.* ./
# 依照 npm run production 提示把 vue-template-compiler 先安裝進去
RUN npm install && npm install vue-template-compiler --save-dev --production=false

COPY . .

RUN npm run production
```

Composer image，包括安裝 Composer 的調整，與安裝依賴套件。在這個 stage 還可以做單元測試：

```
FROM base AS composer_builder

WORKDIR /source

COPY --from=composer:1 /usr/bin/composer /usr/bin/composer

# 加速套件下載的套件
RUN composer global require hirak/prestissimo && composer clear-cache

# 安裝所有程式依賴的套件，含測試套件
COPY composer.* ./
RUN composer install --no-scripts && composer clear-cache

# 複製程式碼
COPY . .

RUN composer run post-autoload-dump

# 執行測試
RUN php vendor/bin/phpunit

# 移除測試套件
RUN composer install --no-dev
```

最後是最難的，正如[昨天最後的回顧](https://mileschou.me/ironman/12th/docker-newbie/day16/)所提到的，對框架要非常瞭解，才知道如何哪些檔案該複製，還有先後順序等。

```
FROM base

WORKDIR /var/www/html

COPY --from=composer_builder /source/vendor ./vendor
COPY --from=npm_builder /source/public/js ./public/js
COPY --from=npm_builder /source/public/css ./public/css
COPY --from=npm_builder /source/public/mix-manifest.json ./public

COPY . .

COPY --from=composer_builder /source/bootstrap ./bootstrap

CMD ["php", "artisan", "serve", "--host", "0.0.0.0"]
```

Build image 是以最後一個 stage 為主。結果又會再更小一些。

```
$ docker images laravel
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
laravel             latest              02b76d8ded9b        12 minutes ago      99.5MB
```

## 今日自我回顧

使用 Multi-stage Build 不但可以減少容量，同時還能使用 Docker 創造多個環境執行建置階段的任務。

當建置階段與執行階段間，使用 artifacts 做區隔的時候，通常都適合使用 Multi-stage Build。如：Golang、Java 等，所有編譯語言，需要編譯並產生 artifacts 才能執行。

- 瞭解 Multi-stage Build 的概念
- 練習使用 Multi-stage Build 最佳化 Dockerfile

# Day 18 - 使用 Public Registry 分享 image

了。

不過 Docker Hub 有強大的自動建置設定與 image 整合測試功能，可以輕鬆設定多種版本的 base image，就這點來說，還是比其他平臺強上許多。

![img](https://mileschou.me/ironman/12th/docker-newbie/day18/01-docker-hub-auto-build.png)

### 建立 repository

申請好帳號並登入後，即可在 Docker Hub 個人 dashboard 頁面上找到 [Create Repository](https://hub.docker.com/repository/create) 按鈕。按下後，需要輸入 repository 的基本資訊，如名稱與說明等。

![img](https://mileschou.me/ironman/12th/docker-newbie/day18/02-docker-hub-create-repository.png)

下面的 *Build Setting* 就是 Docker Hub 方便的地方了：

![img](https://mileschou.me/ironman/12th/docker-newbie/day18/03-docker-hub-build-setting.png)

它可以與 GitHub 或 Bitbucket 串接 Git repository，在 Git push 的時候，觸發 Docker Hub 的 build event。從範例可以看得出，它可以依照 Git branch 或 Git tag 觸發 Docker build，並產生對應的 Docker tag，甚至還可以使用 regex 來處理。

提供筆者寫過的 image [mileschou/lua](https://hub.docker.com/repository/docker/mileschou/lua)，裡面的 build 設定做為範例參考：

![img](https://mileschou.me/ironman/12th/docker-newbie/day18/04-docker-hub-lapis-setting.png)

筆者目前只有設定 branch，沒設定過 tag。主要是因為筆者 Docker image 的原始碼都是其他人的既有專案，如範例的 [Lua](https://github.com/lua/lua)。

當原始碼不是自己控制的時候，使用 branch 控制會比較單純一點，畢竟我們不會知道原始碼何時會發生 Git tag。使用 master branch 控制的話，當 master 更新時，所有版本 image 都會跟著更新，相較簡單很多。但所有版本都放在 master branch 的話，就需要在一個 branch 放所有版本的 Dockerfile，目錄規劃可以參考 [MilesChou/docker-lua][https://github.com/MilesChou/docker-lua] 原始碼。

當原始碼自己可以控制的時候，即可參考 Docker Hub 官方的 tag 設定範例，只要 Regex 設定好即可正常運作。

### 多版本 Dockerfile 更新

不同版本的差異（如 Lua 5.1、5.2、5.3），通常只有版號的差別，Dockerfile 差異不大。筆者會額外寫腳本用來產對應版本的 Dockerfile。

> 詳細腳本可參考原始碼，原理單純只是使用取代指令達成的。

### Build image

完成設定後，點選 *Create & Build*，Docker Hub 就會開始使用 GitHub 上的 Dockerfile 執行 build image 了。可能因為維運考量，所以 Docker Hub build image 的效率越來越差，如果像筆者一個 push 會 build 十多個 image，這樣就得等上好一陣子。

完成後，即可使用 `docker pull yourname/yourimage` 下載自己建好的 image 了！

## GitHub

Docker Hub 限制公佈沒多久，GitHub 推出了新服務 [Container Registry](https://github.blog/2020-09-01-introducing-github-container-registry/)。它的設計概念為，repository 不再只限 Git 原始碼，artifacts 也可以做為 repository 保存在 GitHub 上，而 Container 是其中一種 artifacts。

筆者有寫了 [Composer Action](https://github.com/MilesChou/composer-action)，有調整了一下，做為今天的範例介紹。

上面有提到 Docker Hub 最大的優勢在於 build 設定可以透過網頁，比較直覺。使用 GitHub 的話則需要調整 CI 流程才能完成複雜的 build 設定。因為是 GitHub 的產品，所以這裡使用 GitHub Actions（以下簡稱 Actions）來做為範例：

```
# /.github/workflows/registry.yml
name: Publish Docker

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        version: ["7.4", "7.3", "7.2", "7.1", "7.0", "5.6", "5.5"]
    steps:
      - uses: actions/checkout@master
      - name: Build PHP ${{ matrix.version }} and publish to GitHub Registry
        uses: elgohr/Publish-Docker-Github-Action@2.22
        with:
          name: mileschou/composer-action/runner:${{ matrix.version }}
          dockerfile: ${{ matrix.version }}/Dockerfile
          username: ${{ secrets.GITHUB_USERNAME }}
          password: ${{ secrets.GITHUB_TOKEN }}
          registry: docker.pkg.github.com
```

> 筆者對 Actions 沒特別研究，加上這次主題是 Docker，所以就不細講 Actions 運作原理了。

Docker image 建置與推上 GitHub 是在第二個 steps [`elgohr/Publish-Docker-Github-Action@2.22`](https://github.com/marketplace/actions/publish-docker?version=2.22)。這個套件筆者認為已經非常好用了，`with` 後的參數，以下特別說明一下。

### `name` 與 `dockerfile`

`name` 是 image name，跟 Docker Hub 用途一樣，在 `docker pull` 的時候會使用到。比較討厭的是，GitHub 規定 name 的格式如下：

```
:user_name/:repository_name/:image_name
```

這個格式比 Docker Hub 多出一層子類，而且是強制要求。目前筆者用來做 Docker image 的 Git repository，都是以 image 來命名的，像是 `docker-lua` 等，若要強制多一層，也只能叫 `runner` 了。

這裡有用到 `matrix.version` 這個特殊變數，它對應到上面的設定：

```
strategy:
  matrix:
    version: ["7.4", "7.3", "7.2", "7.1", "7.0", "5.6", "5.5"]
```

這個設定會同時開 7 個對應 version 的 job，而每個 job 的 `matrix.version` 都會帶入對應的值，有點像在 for loop 一樣。像本例是不同版本要標不同的 tag，與跑不同的 Dockerfile，這個功能就非常地好用。

`dockerfile` 參數與 Docker Hub 設定一樣，可以指定 Dockerfile 位置。

### `username` `password`

這裡使用了兩個環境變數：`secrets.GITHUB_USERNAME` 與 `secrets.GITHUB_TOKEN`，Actions 的環境變數設定可以到 Git repository setting 裡調整：

![img](https://mileschou.me/ironman/12th/docker-newbie/day18/06-github-secrets.png)

`GITHUB_USERNAME` 就是帳號，本例會是筆者的帳號。

而這裡會發現沒有 `GITHUB_TOKEN` 的設定。`GITHUB_TOKEN` 是 Actions 內建 secret 變數，它會自動生成對應 Git repository 權限的 token 代入，所以 Actions 會有權限可以讀寫 repository，包括推 image 上 GitHub Container Registry。

### `registry`

之前在說明 [Hello World](https://mileschou.me/ironman/12th/docker-newbie/day03/) 的時候有提過，registry 是存放一堆 image 與驗證身分的地方，本例的 `docker.pkg.github.com` 即為 GitHub 的 registry domain。搭配上面提到的 image name，要下載 7.4 版的 image 需執行下面這個指令：

```
docker pull docker.pkg.github.com/mileschou/composer-action/runner:7.4
```

這裡可以發現，完整的 repository 名稱是包含 registry 的。

那 Docker Hub 呢？與 GitHub 一樣是 registry，Docker Hub 也有自己的驗證中心與網域－－`docker.io`。換句話說，下面這幾個指令會到一樣的位置，下載一樣的 image。

```
docker pull alpine
docker pull docker.io/alpine
docker pull docker.io/library/alpine
```

瞭解這點，相信大家就能知道該如何去別的 registry 下載 image 了。

### Build image

Actions 只要 workflow 檔案 commit 並 push 就會自動執行了。最後完成即可在 Git repository 主頁或個人的 [packages 頁面](https://github.com/MilesChou?tab=packages)找到對應的 image。

## 今日自我回顧

今天的內容比較單純，在網頁設定一下以及 Dockerfile commit 上 GitHub，應該就能 work 了。

- 練習使用公開的 Registry 服務分享 image

# Day 19 - 使用 Private Registry 分享 image

若要寫開源的 Docker image，使用 Docker Hub 或 GitHub 分享 image 會非常方便。而今天要來聊聊，如果 image 只打算在企業內部共享的話，該如何做？



當然，Docker 官方有[解決方案](https://docs.docker.com/registry/)：使用 [registry image](https://hub.docker.com/_/registry)，這可以建立一個自架的 registry 服務，就像 `docker.io` 一樣。

## 啟動 registry 服務

使用 Docker 啟動 registry 服務就像啟動 MySQL 一樣簡單：

```
docker run -d -p 5000:5000 --restart=always --name registry registry:2
```

> 此為[官方範例](https://docs.docker.com/registry/deploying/)

接著昨天有提到下載 image 的方法，現在再複習一次：下面這幾個指令會到一樣的位置，下載一樣的 image。

```
docker pull alpine
docker pull docker.io/alpine
docker pull docker.io/library/alpine
```

這次 registry 位置為 `localhost:5000`，標版號的方法如下：

```
# build 的時候直接給 tag
# docker build -t localhost:5000/laravel .

# 標 tag 在現有的 image 上
docker tag laravel localhost:5000/laravel
```

接著使用 `docker push` 推到 registry 裡：

```
docker push localhost:5000/laravel
```

測試看看是否能正常下載：

```
# 確認 SHA256 值為 16318b4b39f2
docker images laravel
docker images localhost:5000/laravel

# 移除本機所有 image
docker rmi localhost:5000/laravel laravel

# 重新下載 image
docker pull localhost:5000/laravel

# 確認 SHA256 值一樣為
docker images laravel
```

### 加上 TLS

Server 準備好了，下一步是為這個 server 加上基本的防護－－[TLS](https://mileschou.me/ironman/11th/authentication/day06/)。

筆者是使用[mkcert](https://github.com/FiloSottile/mkcert)產生 certificate 來做示範的，詳細 TLS certificate 怎麼產生或匯入，筆者就不特別說明瞭。

安裝好 mkcert 後，初始化 mkcert 並新增 localhost certificate：

```
# 初始化
mkcert -install

# 建立與匯入本機憑證
mkcert localhost

# 會產生 localhost.pem 與 localhost-key.pem 兩個檔，要給 Web server 設定用的
ls *.pem
```

可以使用 Nginx 做測試，先建立設定檔 `nginx.conf`

```
server {
    server_name localhost;
    listen 80;
    listen 443 ssl;
    ssl_certificate /etc/mkcert/localhost.pem;
    ssl_certificate_key /etc/mkcert/localhost-key.pem;
    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }
}
```

接著啟動 Nginx container

```
# 啟動 Nginx
docker run -d -v $PWD/localhost-key.pem:/etc/mkcert/localhost-key.pem -v $PWD/localhost.pem:/etc/mkcert/localhost.pem -v $PWD/nginx.conf:/etc/nginx/conf.d/default.conf -p 443:443 nginx:alpine

# 驗證
curl https://localhost/
```

只要能正常 curl 到內容，就算驗證完成了，用瀏覽器也可以看到 TLS 正常運作的標示：

![img](https://mileschou.me/ironman/12th/docker-newbie/day19/03-tls.png)

到目前為止，確認 certificate 可以正常運作，下一步是把 certificate 用在 registry 裡

```
docker run -d \
  --restart=always \
  --name registry \
  -v $PWD/localhost.pem:/etc/mkcert/localhost.pem \
  -v $PWD/localhost-key.pem:/etc/mkcert/localhost-key.pem \
  -e REGISTRY_HTTP_ADDR=0.0.0.0:443 \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/etc/mkcert/localhost.pem \
  -e REGISTRY_HTTP_TLS_KEY=/etc/mkcert/localhost-key.pem \
  -p 443:443 \
  registry:2
```

這裡把 port 換成 443 了，所以 image 的名稱也得跟著換成 `localhost/laravel`：

```
# tag 新的名字
docker tag localhost:5000/laravel localhost/laravel

# push registry
docker push localhost/laravel
```

### 加上身分驗證

若沒有驗證身分功能，registry 等於是免費倉庫任人塞爆，因此來實做看看官方提到的[身分驗證](https://docs.docker.com/registry/deploying/#restricting-access)。

> 官方提醒：必須要有 TLS，身分驗證才會生效

首先先照官方提示的指令建立 basic auth 的帳密：

```
# 使用 htpasswd 指令
htpasswd -Bbn user pass > auth/htpasswd

# 沒有 htpasswd？跟 Docker 借用一下
docker run --rm -it httpd htpasswd -Bbn user pass > auth/htpasswd
```

接著一樣移除 container 重新啟動一個新的

```
docker run -d \
  --restart=always \
  --name registry \
  -v $PWD/localhost.pem:/etc/mkcert/localhost.pem \
  -v $PWD/localhost-key.pem:/etc/mkcert/localhost-key.pem \
  -e REGISTRY_HTTP_ADDR=0.0.0.0:443 \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/etc/mkcert/localhost.pem \
  -e REGISTRY_HTTP_TLS_KEY=/etc/mkcert/localhost-key.pem \
  -v $PWD/auth:/auth \
  -e REGISTRY_AUTH=htpasswd \
  -e REGISTRY_AUTH_HTPASSWD_REALM="Registry Realm" \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  -p 443:443 \
  registry:2
```

接下來會需要用到 `docker login` 指令，它的用法是

```
docker login [OPTIONS] [SERVER]
```

但目前它有個小問題是，當 `SERVER` 沒有 `.` 的時候，Docker 會認為它不是一個合法的 server，會回下面這個錯誤：

```
$ docker login localhost
unknown backend type for cloud login: localhost
```

[GitHub issue](https://github.com/docker/compose-cli/issues/712) 也有人提到這個問題，Docker 維護者的回應是，把 `enable cloud experience` 關掉即可：

以下為測試過程：

```
# 登入前 push 會回 no basic auth credentials 錯誤
docker push localhost/laravel

# 登入剛剛設定的 user / pass
docker login localhost

# 再一次就會成功
docker push localhost/laravel

# 使用 logout 把帳密清除
docker logout localhost
```

官方也有提供其他[進階的身分驗證](https://docs.docker.com/registry/deploying/#more-advanced-authentication)，有興趣的讀者可以再上官網參考。

自建 registry 還有很多地方要注意的，像是[儲存空間設定](https://docs.docker.com/registry/deploying/#storage-customization)，或是[負載均衡器設定](https://docs.docker.com/registry/deploying/#load-balancing-considerations)等，Docker registry 已經把大多數困難的事都參數化了，若沒有很奇怪的需求，直接使用都不會有問題的。

## 其他 private registry 服務

到目前為止，這個服務已經有簡單的安全防護機制，可以實驗登入登出的過程。反過來說，當我們使用雲端的 registry 服務，正是需要登入登出過程，才能正常使用別人家開好的服務。

包括昨天提到的，目前筆者已知的 private registry 服務如下：

- [Docker Hub](https://hub.docker.com/)
- [GitHub Container Registry](https://github.com/)
- [GitLab Container Registry](https://gitlab.com/)
- [AWS Container Registry](https://aws.amazon.com/tw/ecr/)（ECR）
- [GCP Container Registry](https://cloud.google.com/container-registry)（GCR）
- [Azure Container Registry](https://azure.microsoft.com/zh-tw/product-categories/containers/)

不同家提供的內容差異，主要都在價錢或存放位置的差異，而使用上都沒有差－－把它們當成自己建的 private registry 來用就對了！

只要知道各家提供的 registry host 名稱，剩下的就是 login 與 push 到正確的 path 即可。而 `docker login` 指令的詳細過程都在上面了，因此持續整合串接 push 至 registry，或持續部署 pull 進機器，相信都不是問題了！

## 今日自我回顧

- 建立一個測試用的 registry
- 串接雲端 registry 也是使用相同的概念

# Day 20 - 使用 save / export 分享 image

不久前，曾聽到一個神奇的需求：希望在無網路的環境下使用 Docker。這種需求，筆者學 Docker 以來還是第一次聽到。



第二階段的最後一天，來說明如何在無網路的環境下分享 Docker image 與啟動 container。

## 安裝 Docker

第一步就是麻煩事了，筆者個人會使用 [Vagrant](https://www.vagrantup.com/) 包 Docker box 再到機器上匯入，接著啟動 VM 後，如果搞砸了，只要 VM 砍掉重練即可。

Vagrant 有安裝檔案，另外再配上 [VirtualBox](https://www.virtualbox.org/) 安裝檔，即可完成虛擬機環境的準備。

再來是 Vagrant Box 準備，參考[安裝 Docker 環境](https://mileschou.me/ironman/12th/docker-newbie/day02/)提到的 Vagrant 環境建置。使用 `vagrant up` 建好 VM 後，再使用 `vagrant package` 指令打包成 .box 檔：

```
$ vagrant package
==> default: Attempting graceful shutdown of VM...
==> default: Clearing any previously set forwarded ports...
==> default: Exporting VM...
==> default: Compressing package to: /Users/miles/GitHub/MilesChou/docker/package.box
```

> 這個動作跟 `docker commit` 非常像。

到目前為止會有三份檔案如下：

1. Vagrant 安裝檔
2. VirtualBox 安裝檔
3. Docker VM 檔（package.box）

接著放入隨身碟後，就可以移架到主機上安裝 Vagrant 與 VirtualBox 了。

### 匯入 box 檔

Docker VM 檔是 .box 格式，匯入 Vagrant 使用 `vagrant box add` 指令：

```
$ vagrant box add --name docker ./package.box
==> box: Box file was not detected as metadata. Adding it directly...
==> box: Adding box 'docker' (v0) for provider:
    box: Unpacking necessary files from: file:///Users/miles/GitHub/MilesChou/docker/package.box
==> box: Successfully added box 'docker' (v0) for 'virtualbox'!
```

完成匯入後，因 box 名稱不同，因此要換一個名字。依上面的範例，要使用 `docker` 這個 box 名稱：

```
Vagrant.configure("2") do |config|
  config.vm.box = "docker"

  # config.vm.network "forwarded_port", guest: 80, host: 8080
  # config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "1024"
  end
end
```

這裡要注意的是，`forwarded_port` 與之前提到的 [Port forwarding](https://mileschou.me/ironman/12th/docker-newbie/day05/) 概念完全相同，只是 container 換成了 VM。以下是設定範例參考：

| Image                                         | Container port | Docker Run | Vagrantfile             | Host port |
| --------------------------------------------- | -------------- | ---------- | ----------------------- | --------- |
| [httpd](https://hub.docker.com/_/httpd)       | 80             | 8080:80    | guest: 8080, host: 8080 | 8080      |
| [mysql](https://hub.docker.com/_/mysql)       | 3306           | 3306:3306  | guest: 3306, host: 3306 | 3306      |
| [registry](https://hub.docker.com/_/registry) | 5000           | 443:5000   | guest: 443, host: 1443  | 1443      |

當調整完設定後，只要下 `vagrant reload` 即可重載設定。

再來就是 Docker image 檔該如何產生與匯入了，Docker 提供兩種方法可以產生與匯入 tar 檔，以下簡單做說明。

## `docker save` 與 `docker load`

昨天有說明如何把 Docker image push 到 registry 上。類似的原理，image 的內容是可以被打包起來的。這裡準備了一個簡單的 Dockerfile 來實驗：

```
FROM alpine

RUN apk add --no-cache vim
# 使用上面的 Dockerfile build image
docker build -t vim .
```

Build image 後，使用 `docker save` 可以將 image 內容輸出成 tar 檔：

```
# 確認 image 的 SHA256 為 bcdbe56cd759
docker images vim

# 將 image 保存成 tar
docker save vim > vim.tar

# 移除 image
docker rmi vim

# 確認 image 不在
docker images vim

# 把剛剛保存的 image 再載入 repository
docker load < vim.tar

# 確認 image 的 SHA256
docker images vim
```

這裡可以看到 SHA256 完全一致，這代表 image 內容有被完整保存下來的，而且大小是很接近的：

```
$ ls -lh vim.tar
-rw-r--r--  1 miles  staff    32M 10  5 01:34 vim.tar

$ docker images vim
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
vim                 latest              bcdbe56cd759        17 hours ago        32.5MB
```

Docker 有提供 `docker history` 指令可以查看 image layer 的資訊：

```
$ docker history vim
IMAGE               CREATED             CREATED BY                                      SIZE                COMMENT
bcdbe56cd759        21 hours ago        /bin/sh -c apk add --no-cache vim               26.9MB
<missing>           4 months ago        /bin/sh -c #(nop)  CMD ["/bin/sh"]              0B
<missing>           4 months ago        /bin/sh -c #(nop) ADD file:c92c248239f8c7b9b…   5.57MB
```

最上面很明顯是 Vim 的，而下面兩行 missing 即為 Alpine 的 layer，可以用同樣的指令查 Alpine 會更清楚：

```
$ docker history alpine
IMAGE               CREATED             CREATED BY                                      SIZE                COMMENT
a24bb4013296        4 months ago        /bin/sh -c #(nop)  CMD ["/bin/sh"]              0B
<missing>           4 months ago        /bin/sh -c #(nop) ADD file:c92c248239f8c7b9b…   5.57MB
```

這裡再做另一個實驗，把 Vim image 與 Alpine image 都移除，再匯入 `vim.tar`：

```
# 移除 image
docker rmi vim alpine

# 把剛剛保存的 image 再載入 repository
docker load < vim.tar

# 確認 image 的 SHA256
docker images vim
```

這代表匯出的 `vim.tar` 會完整地包含所有 FROM 的 image 資訊。

為什麼要特別確認這件事，因為下一個指令會不一樣。

## `docker export` 與 `docker import`

一樣是輸出 tar 檔，但 `docker export` 的目標是 container，它能將 container 輸出成 tar 檔：

```
# 執行一個 container，注意這裡沒有 --rm
docker run -it --name vim alpine

# 做點檔案系統的改變再離開
apk add --no-cache vim && exit

# 把 container 的檔案系統匯出 tar
docker export vim > vim-export.tar

# 從 tar 導入檔案系統
docker import - vim < vim-export.tar

# 再多做一次看看
docker import - vim < vim-export.tar
```

最後的 `docker import` 可以發現，執行兩次的 digest 是不一樣的。這代表 `docker export` 產出的 tar 檔，其實是沒有包含 FROM image 資訊的。

`docker history` 資訊如下：

```
$ docker history vim
IMAGE               CREATED             CREATED BY          SIZE                COMMENT
407b5b2c246a        4 hours ago                             32.5MB              Imported from -
```

只有一層 layer，Alpine 的檔案系統已經被包含在這裡面了。

## `save` v.s. `export`

`docker save` 與 `docker export` 的目的都一樣是把 Docker 的系統保存成檔案，但結果是不大一樣的。以下做個簡單的比較：

| `docker save`                      | `docker export`                        |
| ---------------------------------- | -------------------------------------- |
| 將 image 打包                      | 將 container 打包                      |
| 完整保留 image layer 資訊          | 只會有一層 layer                       |
| 可以保存多個 image 在一個 tar 檔裡 | 只能保存一個 container 在一個 tar 檔裡 |

使用上，筆者認為 `docker save` 用途很明確是分享 image。而 `docker export` 比較像是想把目前運作中的 container 狀態保存下來，拿到別臺機器上做別的用途，比方說 debug 等。

> 上面的範例是有把 container 停止才下 `docker export` 指令，實際上也可以用在執行中的 container。

## 指令補充說明

### `docker save`

把 image 使用 tar 打包輸出。預設會使用標準輸出（STDOUT），用法：

```
docker save [OPTIONS] IMAGE [IMAGE...]
```

因為是使用標準輸出，所以會使用導出（`>`）的方法輸出檔案，也可以使用下面這個參數來取代導出：

- `-o|--output` 不使用標準輸出，改使用輸出檔案，後面接檔案名稱即可

### `docker load`

把打包的 tar 檔載入到 Docker repository 裡。預設會使用標準輸入（STDIN），用法：

```
docker image load [OPTIONS]
```

類似 save，只是它是使用導入（`<`）來讀取檔案內容，一樣可以使用參數來取代導入：

- `-i|--input` 不使用標準輸入，改成直接指定檔案

### `docker export`

把 container 的檔案系統使用 tar 打包輸出。預設會使用標準輸出（STDOUT），用法：

```
docker export [OPTIONS] CONTAINER
```

與 `docker save` 類似，也有使用導出（`>`）的方法輸出檔案，也有參數可以取代導出：

- -o|–output 不使用標準輸出，改使用輸出檔案，後面接檔案名稱即可

### `docker import`

把打包的 tar 檔的檔案系統導入到 Docker repository 裡。預設會使用標準輸入（STDIN），用法：

```
docker image import [OPTIONS] file|URL|- [REPOSITORY[:TAG]]
```

與 `docker load` 類似，使用導入（`<`）來讀取檔案內容，但它沒有選項可以取代導入，而是改成使用參數的方法。下面是使用導入與不使用的對照範例：

```
docker image import myimage < my-export.tar
docker image import my-export.tar myimage
```

## 今日自我回顧

基本操作 container 的方法，與 build image 的方法在這二十天裡已說明完了，這樣已可應付八成開發上遇到的問題。

明天會開始說明更詳細的部分，包括各元件的細節，或是維運相關的功能等。

## 參考資料

- [比較 save, export 對於映象檔操作差異](https://blog.hinablue.me/docker-bi-jiao-save-export-dui-yu-ying-xiang-dang-cao-zuo-chai-yi/)

# Day 22 - Volume 進階用法

今天開始，會說明 Docker 更多的細節。未來如果需要維運 container 或用到 container 調度系統（如 K8S），則接下來十天的內容，將有可能幫上一點忙。



首先第一天要介紹的是 Volume 的進階用法。說是進階用法，其實只是比一開始提到的[同步程式](https://mileschou.me/ironman/12th/docker-newbie/day06/)操作複雜了點而已。

## Volume 概念

原本同步程式的做法很單純，只是把本機的某個位置綁在 container 的某個路徑上，如：

```
docker run -d -it -v $PWD:/usr/local/apache2/htdocs -p 8080:80 httpd
```

這樣會把 host 下指令的路徑綁在 container 的 `/usr/local/apache2/htdocs` 上。

上面的方法達成了 host 共享資料給 container，但有時候會是 container 之間需要共用資料。可以試著執行下面的指令來瞭解如何做到這件事：

```
# 建立 volume，並命名為 code
docker volume create --name code

# 執行 BusyBox container 綁定 volume 在 source，並查看裡面的內容，並新增檔案
docker run --rm -it -v code:/source -w /source busybox sh
ls -al && echo Hi volume > /source/volume.html && exit

# 執行新的 BusyBox container 查看 volume 的內容
docker run --rm -it -v code:/source busybox ls -l /source

# 執行 Nginx container 綁定到 html 目錄裡
docker run -d -v code:/usr/share/nginx/html -p 8080:80 --name my-web nginx:alpine

# 查看 html
curl http://localhost:8080/volume.html

# 執行新的 Nginx container，並把 my-web 容器綁定的 volume 綁到這個容器上
docker run -d --volumes-from my-web -p 8081:80 --name my-web2 nginx:alpine

# 查看 html
curl http://localhost:8081/volume.html
```

這段指令很長，仔細說明如下：

1. 先開一個空的目錄叫 `code` 然後掛載到 BusyBox 的 `/source` 下，並產生程式碼。
2. 注意這裡使用 BusyBox 都有加 `--rm` 參數，所以每次 container 都會移除，但 `code` 裡面的資料不會消失
3. Nginx container `my-web` 把 `code` 拿來掛載到，且可以正常使用
4. Nginx container `my-web2` 把 `my-web` 的掛載設定拿來用，且可以正常使用

### `-v` 參數掛載

這次掛載的參數使用方法如下：

```
-v [VOLUME_NAME]:[CONTAINER_PATH]
```

`VOLUME_NAME` 若不存在，會建立一個同名 volume（背後執行 `docker volume create --name VOLUME_NAME`）；若存在，則會做掛載。

Volume 的名字有限定不能有斜線 `/`：

```
$ docker volume create --name a/b
Error response from daemon: create a/b: "a/b" includes invalid characters for a local volume name, only "[a-zA-Z0-9][a-zA-Z0-9_.-]" are allowed. If you intended to pass a host directory, use absolute path
```

所以有斜線，且是絕對路徑的話，就代表的是 bind mount，沒有斜線代表的是 volume。

`-v` 也可以不指定 `VOLUME_NAME` 如下：

```
-v [CONTAINER_PATH]
```

Docker 會使用 `docker volume create` 建立 volume，名稱會是一個隨機亂數，並掛載到 `CONTAINER_PATH`。

### `--volumes-from` 參數

有時候會需要跟其他 container 共同相同的 volume 設定，比方像上例，同樣的 web 服務，都會有相同的設定。

`--volumes-from` 這時候就會非常好用，它後面要接的參數是 `CONTAINER_ID`。它會把該 container 的 volume 設定原封不動的複製過去，包括 bind mount。

## 應用

可以想像，在 Docker 的世界裡，container 跟 volume 是兩個不同且獨立元件，然後可以使用 docker run 組裝起來。

![img](https://mileschou.me/ironman/12th/docker-newbie/day21/02-volumn.png)

以上面這個圖來說，兩個 Web container 共同使用 Code volume，而 DB container 使用 Data volume。因 volume 是獨立的元件，所以我們可以執行其他 container，把對應的 volume 拿來讀取做其他應用。

### DB 備份

> 筆者不會 MySQL，就當 MySQL 要停止才能備份好了。

```
# 啟動 MySQL
docker run -d -e MYSQL_ROOT_PASSWORD=password --name db mysql

# 停止 MySQL
docker stop db

# 使用 BusyBox container 做備份
docker run --rm -it --volumes-from db -v $PWD:/backup busybox tar cvf /backup/backup.tar /var/lib/mysql
```

這是個簡單的範例，裡面有兩個重點：

1. 啟動 MySQL 的時候，其實已經內帶 volume 了，它的行為會是加上 `-v /var/lib/mysql` 參數
2. BusyBox 會把 `-v /var/lib/mysql` 複製過來，因此 tar 指令後面要接 `/var/lib/mysql` 路徑

MySQL 內帶 volume 是由 Dockerfile 指令設定的：

```
VOLUME /var/lib/mysql
```

其他 DB 像 Redis 也有類似的設定：

```
VOLUME /data
```

主要是因為這類需要 persistent 資料的服務，都會設定 `VOLUME` 讓其他 container 可以共用並做其他處理，如備份。

### Nginx + PHP-FPM

除了 DB 會用到 volume 外，筆者也遇過這個情境需要用到 volume 設定。主要是因為 Nginx 需要對應路徑要真的有 .php 檔案，它才會往 FPM 送出請求。Docker Compose 檔範例如下：

```
web:
  image: nginx
  working_dir: /usr/share/nginx/html
  volumes_from:
    - php

php:
  image: php-fpm
  working_dir: /usr/share/nginx/html
  volumes:
    - .:/usr/share/nginx/html
    - /usr/share/nginx/html
```

## 屬性設定

Container 共享檔案雖然很方便，但有時候會希望限制權限。比方說回頭看第一個範例，假設我們只希望 BusyBox 才能有寫入權限，Nginx 只有唯讀權限，則可以加上屬性參數如下：

```
# BusyBox 不變
docker run --rm -it -v code:/source -w /source busybox sh

# Nginx volume 設定加上 :ro
docker run -d -v code:/usr/share/nginx/html:ro -p 8080:80 --name my-web nginx:alpine
```

屬性設定格式如下：

```
-v [VOLUME_NAME]:[CONTAINER_PATH]:[PROPERTIES]
```

此外 [Mac 的效能問題](https://docs.docker.com/docker-for-mac/osxfs-caching/)也可以調整屬性設定解決。

## Volume driver

以上都是以 container 共用檔案的前提在說明如何運用 volume。事實上，volume 獨立元件設計，更好用的地方在於，它可以使用不同的 driver 來替換實體的儲存位置。比方說，直接透過 volume driver 掛載 SSH 上的某個目錄－－[sshfs](https://github.com/vieux/docker-volume-sshfs)。

> 這部分筆者僅知道概念，但沒有經驗，有興趣可以參考[官網說明](https://docs.docker.com/storage/volumes/#use-a-volume-driver)。

## 指令補充說明

### `docker volume create`

建立 volume

- `--name` 指定 volume 名稱

### `docker run`

- `-v|--volume` 掛載 volume 到 container 裡面的某個目錄
- `--volumes-from` 新的 container 會共享舊的 container 的 volume 設定。

## 今日自我回顧

知道 volume 的設定方法，雖然在開發上沒有什麼影響，但在維運應用上就能有更多變化。

比方說，假設有一群 container cluster，而 container 不知道會在哪臺機器啟動的時候，volume 設定就變很重要。另外架一臺 storage 然後讓 container 機器設定 volume driver 存取 storage，這樣的設計就會非常有彈性。

# Network 手動配置

Docker Network 可以調整非常多設定，而在[使用 Network 連結 container](https://mileschou.me/ironman/12th/docker-newbie/day07/) 使用的是預設的 bridge 模式，這個模式符合大多數開發階段的情境，所以通常不會調整它。但如果想要將 Docker 活用在更多地方的話，那就勢必要了解 Docker Network 是如何配置的。



> 筆者對網路架構不熟，因此單純就從 docker 指令來瞭解架構。

## docker0

安裝好 Docker 後，可以使用 `docker network ls` 指令來查看目前的網路設定配置：

```
$ docker network ls
NETWORK ID          NAME                DRIVER              SCOPE
2017cca0027d        bridge              bridge              local
1b1c05935480        host                host                local
8b9319cd142e        none                null                local
```

預設的 `bridge` 網路配置，即很多文章會提到的 docker0。

### bridge

使用 `docker network create`，預設會是 bridge 模式：

```
$ docker network create my-net
78ad7c4ad6a0f9a42dcd7c08c874fd532140ea0a7c07bca2c28889b97fe49c47

$ docker network ls
NETWORK ID          NAME                DRIVER              SCOPE
2017cca0027d        bridge              bridge              local
1b1c05935480        host                host                local
78ad7c4ad6a0        my-net              bridge              local
8b9319cd142e        none                null                local
```

它能滿足大多數的情境，所以才會做為預設設定。

### host

當使用 container 設定成 `host` 時，Docker 會與 host 共享網路資源，但檔案系統依然是分開獨立的。

> **注意**：下面這個範例需要在 Linux 上才能 work。

```
# 啟動 Nginx 並開啟 80 port，注意這裡沒有 -p 參數
docker run -d -it --net=host nginx:alpine

# 確認 localhost 80 port 正常
curl http://localhost

# 啟動新的 Nginx 但這次就無法啟動，因為 80 port 被佔走了
docker run --rm -it --net=host nginx:alpine
```

因不需要做 port forwarding，其實蠻方便的。但缺點就是 container 開了任何 port，都會佔用到 host 資源，反之亦然，這樣隔離性就會降低。

### container

與 `host` 類似，不同點在於網路配置會與指定的 container 共享。

```
# 啟動 web server
docker run -d -it --name web nginx:alpine

# 啟動 BusyBox 並把它網路設定成 web
docker run --rm -it --net=container:web busybox

# 這裡的回傳的結果即 Nginx container 回應
wget -q -O - http://localhost
```

特色也跟 `host` 一樣，某些情境非常好用，但隔離性就會變差。

### none

顧名思義，它就是沒有設定網路，必須要手動為它配置網卡才能正常運作。

## 今日自我回顧

清楚知道 Network，才能順利在許多 host 的環境下串接 container。它甚至就像一個迷你的 VPC 一樣，可以建構出簡單網路架構的私有雲。

對開發階段來說，善用 Network 也有辦法模擬出一般線上實際環境，對於除錯會非常有幫助。

## 參考資料

- [設定 docker0 橋接器](https://philipzheng.gitbook.io/docker_practice/advanced_network/docker0)

# Day 23 - 瞭解 CMD 與 ENTRYPOINT

在寫 Dockerfile 或使用 `docker run` 時，我們使用 `CMD` 來執行指令。Docker 還設計了另一個類似的設定叫 `ENTRYPOINT`。活用這兩個設定將能讓 Docker image 使用更加靈活。



## `CMD` 的設計

首先要強調一個重要的概念－－container 就是 process。啟動 container 背後的原理就是啟動 process。

因此 Docker `CMD` 有個特性是，後面的設定會覆蓋前面的設定。比方說，以 alpine:3.12 的 [Dockerfile](https://github.com/alpinelinux/docker-alpine/blob/90788e211ec6d5df183d79d6cb02e068b258d198/x86_64/Dockerfile) 為例

```
FROM scratch
ADD alpine-minirootfs-3.12.0-x86_64.tar.gz /
CMD ["/bin/sh"]
```

這裡 `CMD` 的設定是 `/bin/sh`。FROM 它的 image 如 [php:7.4-alpine](https://github.com/docker-library/php/blob/c257144e4bf191d6bb12927c8fd1f3df6ea6c570/7.4/alpine3.12/cli/Dockerfile#L192-L193)：

```
FROM alpine:3.12

# 略

CMD ["php", "-a"]
```

有設定新的 `CMD` 時，它會以後設定的為主。

`docker run` 是類似的情境，它是最後一關，先再看一次 `docker run` 的語法：

```
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

這裡的 `[COMMAND]` 指的就是 `CMD`。在下 `docker run` 沒有帶 `COMMAND` 的時候，它會使用 Dockerfile 定義的 `CMD`；如果有給，它就會覆蓋 `CMD` 設定。

也就是，下面這幾個例子結果是一樣的：

```
# Alpine
docker run --rm -it alpine:3.12
docker run --rm -it alpine:3.12 /bin/sh

# Node
docker run --rm -it php:7.4-alpine
docker run --rm -it php:7.4-alpine php -a
```

若想在 container 上執行其他指令，只要在後面接 COMMAND 即可：

```
# Alpine
docker run --rm -it alpine:3.12 ls

# Node
docker run --rm -it node:14-alpine node -v
```

這招在過去幾天裡很常拿來用，實際的意義就是取代 `CMD` 設定。

## `ENTRYPOINT` 的設計

`ENTRYPOINT` 跟 `CMD` 很像，一樣是啟動 container 的時候會用到，所以一樣也會有後面設定覆蓋的狀況。

以 [mysql:8](https://github.com/docker-library/mysql/blob/285fd39122e4b04fbe18e464deb72977df9c6a45/8.0/Dockerfile#L82-L85) 為例：

```
# 略
ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 3306 33060
CMD ["mysqld"]
```

若將啟動 container 當成是執行指令的話，那 `docker run` 與 `ENTRYPOINT` 的關係就像下面這樣

```
# 等於在容器內執行 docker-entrypoint.sh mysqld
docker run --rm -it mysql:8

# 等於在容器內執行 docker-entrypoint.sh bash
docker run --rm -it mysql:8 bash
```

這時，我們可以做一個實驗：

```
# 使用 bash 進入 container
docker run --rm -it mysql:8 bash

# 在 container 裡執行 ENTRYPOINT + bash
docker-entrypoint.sh bash

# 在 container 裡執行 ENTRYPOINT + mysqld
docker-entrypoint.sh mysqld
```

沒錯，這就跟上面直接執行 `docker run` 結果一樣。相信這個實驗做完，就能理解 CMD 與 ENTRYPOINT 的差異與用法了。

## 今日自我回顧

瞭解 CMD 與 ENTRYPOINT 的設計後，接著就能開始設計更多變化的 image 了。

# Day 24 - 活用 ENTRYPOINT

[ENTRYPOINT 的設計](https://mileschou.me/ironman/12th/docker-newbie/day23/)，可以保證 container 啟動執行指令的時候，都一定會包含 ENTRYPOINT 設定。因此可以藉由這個特性讓 image 用起來更靈活。



以下會介紹幾個還不錯的設計，讓讀者參考。

## 純執行指令類型的 image

以 [Composer](https://github.com/composer/docker/blob/aace87229d5c3f988cb19e1dbac0567c2c503c58/1.10/docker-entrypoint.sh) 為例：

```
#!/bin/sh

isCommand() {
  # sh 需要特別例外，因為 composer help 會誤以為是 show 指令
  if [ "$1" = "sh" ]; then
    return 1
  fi

  composer help "$1" > /dev/null 2>&1
}

# 當第一個參數看起來像 option 的話（如：-V、--help）
if [ "${1#-}" != "$1" ]; then
  set -- /sbin/tini -- composer "$@"

# 當第一個參數就是 composer 的話
elif [ "$1" = 'composer' ]; then
  set -- /sbin/tini -- "$@"

# 當第一個參數是 composer 的子指令（如：install、update 等）
elif isCommand "$1"; then
  set -- /sbin/tini -- composer "$@"
fi

# 其他全部都照舊執行
exec "$@"
```

依照上面的腳本，可以轉換出以下 Docker 指令與實際執行指令的對照表：

| docker run                                 | actual                           |
| ------------------------------------------ | -------------------------------- |
| `docker run composer:1.10 --help`          | `/sbin/tini -- composer --help`  |
| `docker run composer:1.10 composer --help` | `/sbin/tini -- composer --help`  |
| `docker run composer:1.10 install`         | `/sbin/tini -- composer install` |
| `docker run composer:1.10 sh`              | `sh`                             |

> 為節省版面，把 `--rm` 先省略。

從這個對照表可以看得出來，平常我們能把 `docker run composer` 作為取代 Composer 的指令，若需要使用 sh 進入 container 也可以順利執行，因為 ENTRYPOINT 都幫我們處理好了。

我們再回頭看一下 [Container 應用](https://mileschou.me/ironman/12th/docker-newbie/day09/)是怎麼設定 `alias` 的：

```
# 使用 Composer
alias composer="docker run -it --rm -v \````$PWD:/source -w /source composer:1.10"
```

這個 alias 設定，正是把 `docker run` 取代原指令，但這也必須 image 的 ENTRYPOINT 配合才行。ENTRYPOINT 設計可以有兩種方向：

1. 額外寫 shell script 做為 ENTRYPOINT，可以同時處理原指令，與系統的指令。官方的 image 大多都有這樣設計。
2. 直接把指令設定為 ENTRYPOINT，這個 image 就只能用來執行它的子指令，不能做其他用途，如 [oryd/hydra](https://github.com/ory/hydra/blob/v1.8.5/Dockerfile)。

## 服務類型的 image

以 [MySQL](https://github.com/docker-library/mysql/blob/285fd39122e4b04fbe18e464deb72977df9c6a45/8.0/docker-entrypoint.sh) 為例，它的 shell script 寫得比較複雜，這裡單純截取 _main() function：

```
_main() {
  # 當第一個參數看起來像 option 的話，就用 mysqld 執行它
  if [ "${1:0:1}" = '-' ]; then
    set -- mysqld "$@"
  fi

  # 當是 mysqld 且沒有會讓 mysqld 停止的參數時，執行 setup
  if [ "$1" = 'mysqld' ] && ! _mysql_want_help "$@"; then
    mysql_note "Entrypoint script for MySQL Server ${MYSQL_VERSION} started."

    mysql_check_config "$@"
    # 取得 Docker ENV 以及初始化目錄
    docker_setup_env "$@"
    docker_create_db_directories

    # 若是 root 身分，則強制使用 mysql 身分啟動
    if [ "$(id -u)" = "0" ]; then
      mysql_note "Switching to dedicated user 'mysql'"
      exec gosu mysql "$BASH_SOURCE" "$@"
    fi

    # 如果資料庫是空的，就建一個起來吧
    if [ -z "$DATABASE_ALREADY_EXISTS" ]; then
      docker_verify_minimum_env

      ls /docker-entrypoint-initdb.d/ > /dev/null

      docker_init_database_dir "$@"

      mysql_note "Starting temporary server"
      docker_temp_server_start "$@"
      mysql_note "Temporary server started."

      # 初始化資料庫，這裡將會用到 MYSQL_ROOT_PASSWORD、MYSQL_DATABASE、MYSQL_USER、MYSQL_PASSWORD 等環境變數
      docker_setup_db

      # 初始化資料庫目錄
      docker_process_init_files /docker-entrypoint-initdb.d/*

      mysql_expire_root_user

      mysql_note "Stopping temporary server"
      docker_temp_server_stop
      mysql_note "Temporary server stopped"

      echo
      mysql_note "MySQL init process done. Ready for start up."
      echo
    fi
  fi

  # 不是 mysqld 就直接執行了
  exec "$@"
}
```

雖然有點長，不過概念簡單來說，ENTRYPOINT 的任務主要是：

1. 以執行 mysqld 指令優先
2. 準備環境、切換使用者
3. 初始化資料庫、使用者、資料表等任務

ENTRYPOINT 會寫這麼複雜，正是為了 mysqld 與環境變數（`MYSQL_ROOT_PASSWORD`）的搭配下能正常執行。

## 今日自我回顧

若有想寫 Dockerfile 的話，瞭解 ENTRYPOINT 會是必要的。因為 ENTRYPOINT 是啟動 container 的必經之路，善用它將可以讓 image 用起來更加靈活。

# Day 25 - 活用 ENV 與 ARG

ENV 與 ARG 是 Dockerfile 的指令，它們能定義變數並且在後面的流程中使用。



## ENV 的設計

ENV 比較容易理解，它其實就是設定 [environment](https://mileschou.me/ironman/12th/docker-newbie/day08/)，因此概念上，它會是一個全域變數－－直到 `docker run` 的時候都還會存在的變數。

Docker 官方的底層 image，如 [PHP](https://github.com/docker-library/php/blob/c257144e4bf191d6bb12927c8fd1f3df6ea6c570/7.4/alpine3.12/cli/Dockerfile#L61) 或 [Java](https://github.com/docker-library/openjdk/blob/master/16/jdk/alpine3.12/Dockerfile#L12) 等，會版本資訊、安裝路徑等設定成 ENV，在後續的流程可以拿來使用。

至於是應用層級的 image 如 [Laravel image](https://mileschou.me/ironman/12th/docker-newbie/day12/)，environment 大多都會是執行時期才提供，而 Dockerfile 則可以設定預設值。至於要怎麼設定，則是看 image 最終是否有要拿到線上部署，如果有的話，建議預設 production 設定會比較好：

```
ENV APP_ENV=production
ENV APP_DEBUG=false
```

而連線設定則建議不要有預設值，否則部署錯環境加上設定也錯，若網路層沒有防呆的話，將會發生錯寫資料的悲劇。

## ARG 的設計

ARG 是一個很像 ENV 的指令，不一樣的點主要在於，它只能活在 build image 的過程裡。可以從下面這個例子看得出來：

```
FROM alpine

ENV foo=1
ARG bar=2

# Build day27 時 echo
RUN echo ${foo} , ${bar}

# Run day27 時 echo
CMD echo ${foo} , ${bar}
```

build image 過程可以看到 ENV 與 ARG 有正常取值，但 `docker run` 的時候，則只剩下 ENV 而 ARG 不見了。這代表 ARG 只能活在 build image 階段而已。

ARG 不只是 build image 階段的變數，它可以在下指令的時候一併設值：

```
docker build --build-arg bar=3 .
```

ARG 的使用情境在，有時候需要寫很多 Dockerfile，如：

```
FROM php:7.3-alpine

RUN apk add --no-cache unzip
COPY --from=composer:1.10 /usr/bin/composer /usr/bin/composer
FROM php:7.4-alpine

RUN apk add --no-cache unzip
COPY --from=composer:1.10 /usr/bin/composer /usr/bin/composer
```

兩個 Dockerfile 差異只在於 PHP 版本，若以這個寫法來看，若未來新增 PHP 版本，就得多一個 Dockerfile。

這個情境就很適合使用 ARG 改寫：

```
ARG PHP_VER
FROM php:${PHP_VER}-alpine

RUN apk add --no-cache unzip
COPY --from=composer:1.10 /usr/bin/composer /usr/bin/composer
docker build --build-arg PHP_VER=7.4 .
docker build --build-arg PHP_VER=7.3 .
```

這裡的 ARG 寫法是沒有預設值的，這時 `${PHP_VER}` 會取到的是空值。以這個例子，`FROM` 指令會出現 image 名稱格式錯誤訊息（`php:-alpine`）：

```
$ docker build .
Sending build context to Docker daemon  111.6kB
Step 1/4 : ARG PHP_VER
Step 2/4 : FROM php:${PHP_VER}-alpine
invalid reference format
```

## ARG 與 ENV 混用

如果在 ARG 設值的時候使用 ENV 的值，或是反過來的話，可以正常 work 的：

```
FROM alpine

ENV foo=is_env
ARG bar=is_arg

ARG foo_env=${foo}
ENV bar_arg=${bar}

RUN echo ${foo_env} , ${bar_arg}
CMD echo ${foo_env} , ${bar_arg}
```

可以看到 ARG 有正常取得 ENV，ENV 也有正常取得 ARG。

另一種情境是撞名：

```
FROM alpine

ENV foo=is_env
ARG foo=is_arg

ARG bar=is_arg
ENV bar=is_env

RUN echo ${foo} , ${bar}
CMD echo ${foo} , ${bar}
```

若取一樣的名字會發現，它最後都會以 ENV 為主。雖然不會出錯，但建議還是盡可能不要撞名比較好。

## 與 Multi-stage build 合併使用

下面做一個簡單的實驗，在第一個 stage 設定好值後，在第二個 stage 使用：

```
FROM alpine

ENV foo=1
ARG bar=2

FROM alpine

RUN echo ${foo} , ${bar}
CMD echo ${foo} , ${bar}
```

這個實驗非常簡單，一做就馬上理解：每個 stage 要用的 ARG 與 ENV 都需要各自定義的，因此兩個 stage 可以設定兩個同名不同值的 ENV；若兩個 stage 都使用同名的 ARG，則兩個 ARG 在 `--build-arg` 給值的時候都拿得到。

```
FROM alpine

ARG foo
RUN echo ${foo}

FROM alpine

ARG foo
RUN echo ${foo}
```

## 今日自我回顧

今天一連串的實作，相信讀者能更瞭解 ENV 與 ARG 的差異，以及適用的情境。

使用 ENV 可以讓 Dockerfile 更好維護，而 ARG 則是可以讓同一份 Dockerfile 產生更多不一樣的 image。讀者可以視情況運用這兩個指令。

# Day 26 - 瞭解 Docker 如何啟動 process

[瞭解 CMD 與 ENTRYPOINT](https://mileschou.me/ironman/12th/docker-newbie/day23/) 曾提到 container 即 process，那接下來就要了解 Docker 是如何啟動 process 的。



## exec 模式與 shell 模式

在 [build Laravel image](https://mileschou.me/ironman/12th/docker-newbie/day12/) 有提到 CMD 在執行指令的模式有分 exec 模式與 shell 模式，先回顧這兩個模式在寫法上的差異如下：

```
# exec 模式
CMD ["php", "artisan", "serve"]
# shell 模式
CMD php artisan serve
```

> 因為是執行指令，所以 RUN 與 ENTRYPOINT 也有一樣的模式。

雖然最終都會跑 `php artisan serve` 指令，但跑的方法不大一樣。以下使用 [ubuntu](https://hub.docker.com/_/ubuntu) image 來做說明

### exec 模式

簡單來說，就是直接執行指令，因此會是 PID 1 process。使用 PID 1 process 的好處是，使用 `docker stop` 指令發出 `SIGTERM` 後，會是由 PID 1 process 收到，做 graceful shutdown 相容比較簡單。

```
FROM ubuntu
CMD ["ps", "-o", "ppid,pid,user,args"]
```

因 CMD 設定的指令是要執行 `ps -o ppid,pid,user,args`，所以 ps 出來的結果，ps 指令為 PID 1。

這是官方建議的方法。

### shell 模式

Shell 模式是透過 `/bin/sh -c` 執行指令，因此會先有 `/bin/sh -c` 的 PID 1 process，然後在底下開子 process。在這個情況下，`docker stop` 指令發出的 `SIGTERM` 信號將會由 shell 收到。

```
FROM ubuntu
CMD ps -o ppid,pid,user,args
```

這次 ps 指令為 PID 7。

當然，使用 shell 也是有方便的地方，它可以直接在指令上使用環境變數，比方說：

```
FROM node_project
CMD npm run $NODE_ENV
```

這在 exec 是辦不到的。有些討論會提到 exec 如果要取環境變數，可以改成下面的寫法：

```
FROM ubuntu
CMD ["/bin/sh", "-c", "cd $HOME && ps -o ppid,pid,user,args"]
```

相信現在讀者應該知道了，其實改成 shell 的寫法就行了：

```
FROM ubuntu
CMD cd $HOME && ps -o ppid,pid,user,args
```

> 反過來說，exec mode 才能自行決定要用什麼 shell 來執行指令。

### image 差異

上面使用 ubuntu image 做範例，說明瞭 exec 模式和 shell 模式的差異。但不同 image 在 shell 模式下又會不大一樣，原因是 `/bin/sh` 在大多數 image 都是用 link 的形式連結到其他 shell：

```
$ docker run --rm -it ubuntu ls -l /bin/sh
lrwxrwxrwx 1 root root 4 Jul 18  2019 /bin/sh -> dash

$ docker run --rm -it debian ls -l /bin/sh
lrwxrwxrwx 1 root root 4 Sep  8 07:00 /bin/sh -> dash

$ docker run --rm -it centos ls -l /bin/sh
lrwxrwxrwx 1 root root 4 Nov  8  2019 /bin/sh -> bash

$ docker run --rm -it alpine ls -l /bin/sh
lrwxrwxrwx    1 root     root            12 May 29 14:20 /bin/sh -> /bin/busybox
```

從上面範例可以看到，四個 image 就有三種不同的 shell：[bash](https://zh.wikipedia.org/wiki/Bash)、[dash](https://zh.wikipedia.org/wiki/Debian_Almquist_shell)、[ash](https://zh.wikipedia.org/wiki/BusyBox)（BusyBox）

這些 shell 執行 `/bin/sh -c` 在 process 表現的行為又不大一樣，可以參考以下範例：

> Debian 因沒有內建 ps，且與 Ubuntu 一樣是使用 dash，因此就不做為範例

```
docker run --rm -it ubuntu /bin/sh -c ps
docker run --rm -it ubuntu ps

docker run --rm -it centos /bin/sh -c ps
docker run --rm -it centos ps

docker run --rm -it alpine /bin/sh -c ps
docker run --rm -it alpine ps
```

這裡可以發現，只有 ubuntu 才會多卡一層 process，其他不會。就這個範例來看，其實只有 dash 才會有 PID 1 process 被 shell 佔走的問題。筆者建議若要使用 shell 模式的話，還是拿 base image 實驗一下比較保險。

## `docker exec`

除了 `docker run` 以外，還有 `docker exec` 也是透過 Docker 啟動 process 的，我們來看看它啟動會發生什麼事：

```
# Terminal 1
docker run --rm -it --name test alpine

# 使用 top 指令查看目前的 process
top

# Terminal 2
docker exec -it test sh

# 安裝 Vim
apk add --no-cache vim

# Terminal 1 離開的時候，Terminal 2 的 process 也會跟著結束
exit
```

首先 Terminal 1 啟動 container 進入 shell，然後啟動 top，可以看到目前 PID 1 為 `/bin/sh`－－也就是啟動 container 那時的 shell。而 top 的 PPID 是 PID 1。

接著切換 Terminal 2 使用 `docker exec` 進入 container 並下安裝指令，這時 top 裡面看到多出兩個 process，一個是 `docker exec` 的 `sh` 指令 PID 7，它的 PPID 跟啟動 container 的 `/bin/sh` 一樣為 0，筆者推測這應該代表都是從 Docker 直接啟動的 process。另一個 process 則是安裝指令的 process。

最後 Terminal 1 執行 exit 把 PID 1 結束後，沒有父子關係的 PID 7 還是一樣被結束掉了。筆者推測 Docker 主要是因為要把 container 移除，所以會把裡面全部的 process 都淨空，只是使用什麼信號就不確定了，照範例的執行速度來看，很有可能是 `SIGKILL`。

> 因筆者對發信號實際運作不熟悉，因此這裡僅能做推測。

## 今日自我回顧

因為 container 即 process，所以瞭解 process 的生命週期非常重要，包括如何啟動，以及什麼時候要回收資源等。

# Day 27 - 要如何在 container 裡運行多個 process

延續 [Docker 啟動 process](https://mileschou.me/ironman/12th/docker-newbie/day26/) 的主題，因 container 即 process，因此合理的設計方法會是一個 container 只執行一個 process。而且 Dockerfile 也只能設定一個 ENTRYPOINT 和 CMD，實際上也很難跑多個 process。



但如果真的需要一個 container 同時跑多個 process 的話，該怎麼做呢？

開始前，先來定義簡單的目標：

1. 使用 [httpd](https://hub.docker.com/_/httpd) image，Alpine 版本
2. 在同一個 container 裡，同時啟動 httpd 與 top 兩個指令

## 使用 docker exec

山不轉，路轉。即然 Dockerfile 或 `docker run` 不行的話，那就先 `docker run` 再 `docker exec` 吧！

```
# 啟動 Apache
docker run --rm -it --name test httpd:2.4-alpine

# 啟動 top
docker exec -it test top
```

這個方法非常單純易懂，但代價也是龐大的。這個做法的問題點昨天有提到，主要是 `docker exec` 的 process 在 PID 1 process 結束的時候，沒有辦法正常地收到 `SIGTERM` 通知。

再來另一個也非常麻煩的問題是，無法使用「一個」 Docker 指令完成啟動兩個 process，即使是 Docker Compose 也一樣。代表這需要靠腳本或其他方法來組合 Docker 指令，這將會讓維運 container 的人吃盡苦頭。

------

若 `docker exec` 不適合的話，那接下來也只剩一種方向：在 CMD 或 ENTRYPOINT 執行某個特別的腳本或程式，由它來啟動所有需要的 process。

## 使用 shell script

寫一個 shell script，讓它去啟動每個 process ，然後在結尾跑一個無窮迴圈即可：

```
#!/bin/sh

# 啟動 Apache
httpd-foreground &

# 啟動 top
top -b

# 無窮迴圈
while [[ true ]]; do
    sleep 1
done
```

這個方法有一樣的問題－－process 無法收到 `SIGTERM` 信號，而且比 `docker exec` 更加嚴重。`docker exec` 的方法，至少還會有一個 process 收到信號，而 shell script 方法則是所有 process 都收不到信號。

筆者有用類似的概念實作 [Chromium + PHP for Docker](https://github.com/MilesChou/docker-chromium-php)：

```
#!/bin/sh

set -e

# 若有帶參數的話，則 chromedriver 會作為背景執行，然後再直接執行需要的 process。
if [ "$1" != "" ]; then
    chromedriver > /var/log/chromedriver.log 2>&1 &
    exec $@
fi

chromedriver
```

## 使用 Supervisor

[Supervisor](http://supervisord.org/) 是一個能控制多個 process 執行的管理器。以 Supervisor 改寫 Dockerfile 如下：

```
FROM httpd:2.4-alpine

RUN apk add --no-cache supervisor

COPY ./supervisord.conf /etc/supervisor.d/supervisord.ini
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
```

這裡看到還有個設定是 `supervisord.conf`，內容如下：

```
[supervisord]
nodaemon=true

[program:apache2]
command=httpd-foreground
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0

[program:top]
command=top -b
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
```

從執行結果的 log 可以看到 Supervisor 是跑在 PID 1，而 Apache 跑在 PID 8、top 跑在 PID 9 ，兩個 process 都有正常啟動。

```
2020-10-12 15:24:38,955 INFO supervisord started with pid 1
2020-10-12 15:24:39,961 INFO spawned: 'apache2' with pid 8
2020-10-12 15:24:39,965 INFO spawned: 'top' with pid 9
```

接著故意使用 Ctrl + C 來中止程式，可以發現 Supervisor 有把 SIGTERM 信號傳送給 Apache 與 top，並把中止程式的任務完成：

```
2020-10-12 15:24:52,055 WARN received SIGINT indicating exit request
2020-10-12 15:24:52,057 INFO waiting for apache2, top to die
2020-10-12 15:24:52,059 INFO stopped: top (terminated by SIGTERM)
2020-10-12 15:24:52,088 INFO stopped: apache2 (exit status 0)
```

## 今日自我回顧

從今天的範例可以發現，想要在同一個 container 跑多個 process 是很困難的。因此，最好的方法就是：

**一個 container 只執行一個 process！**

## 參考資料

- [Run multiple services in a container](https://docs.docker.com/config/containers/multi-service_container/)
- [如何在一個Docker中同時運行多個程序進程?](https://www.itdaan.com/tw/b130276434228a9548f6652ae396cc99)

# Day 28 - 更詳細的 Docker 操作方法

到目前為止，介紹了許多操作 Docker 的方法，現在來瞭解更詳細的操作方法。



說穿了，其實還是下指令，今天指令將會介紹三個部分如下：

1. Docker 子指令
2. 操作 container
3. 建立 container 的參數
4. 檢視元件的指令

## Docker 子指令

目前已知道的元件有 image、container、volume、network 四種，其實它們分別有個自的子指令如下：

- `docker image`
- `docker container`
- `docker volume`
- `docker network`

今天簡單介紹一下 `docker image` 與 `docker container` 這兩個子指令，這裡同時複習過去提到的指令。

### `docker image`

這個指令是用來管理 image 的，過去有提到的指令如下：

| Docker image 子指令  | 對應過去提過的指令                                           |
| -------------------- | ------------------------------------------------------------ |
| docker image build   | [docker build](https://mileschou.me/ironman/12th/docker-newbie/day11/) |
| docker image history | [docker history](https://mileschou.me/ironman/12th/docker-newbie/day20/) |
| docker image import  | [docker import](https://mileschou.me/ironman/12th/docker-newbie/day20/) |
| docker image load    | [docker load](https://mileschou.me/ironman/12th/docker-newbie/day20/) |
| docker image ls      | [docker images](https://mileschou.me/ironman/12th/docker-newbie/day04/) |
| docker image pull    | [docker pull](https://mileschou.me/ironman/12th/docker-newbie/day04/) |
| docker image push    | [docker push](https://mileschou.me/ironman/12th/docker-newbie/day19/) |
| docker image rm      | [docker rmi](https://mileschou.me/ironman/12th/docker-newbie/day04/) |
| docker image save    | [docker rmi](https://mileschou.me/ironman/12th/docker-newbie/day20/) |
| docker image tag     | [docker tag](https://mileschou.me/ironman/12th/docker-newbie/day19/) |

這裡有個很好用的指令是 `docker image prune`，它會把同時符合下面條件的「孤兒」image 移除。

1. `REPOSITORY` 與 `TAG` 標 `<none>`
2. 沒有其他 image 或 container 依賴這個孤兒 image

```
REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
<none>                       <none>              f9bb75ff4a9c        13 hours ago        56.2MB
```

以上面這個例子來說：

1. 符合 `REPOSITORY` 與 `TAG` 標 `<none>` 條件
2. 是否跟 image 有依賴關係可以用 `docker image ls -f dangling=true | grep f9bb75ff4a9c` 指令檢查
3. 是否跟 container 有依賴關係可以用 `docker ps -a -f ancestor=f9bb75ff4a9c` 指令檢查

### `docker container`

這個子指令也很直白，就是管理 container：

| Docker container 子指令 | 對應過去提過的指令                                           |
| ----------------------- | ------------------------------------------------------------ |
| docker container attach | [docker attach](https://mileschou.me/ironman/12th/docker-newbie/day04/) |
| docker container commit | [docker commit](https://mileschou.me/ironman/12th/docker-newbie/day11/) |
| docker container create | [docker create](https://mileschou.me/ironman/12th/docker-newbie/day04/) |
| docker container exec   | [docker attach](https://mileschou.me/ironman/12th/docker-newbie/day06/) |
| docker container export | [docker export](https://mileschou.me/ironman/12th/docker-newbie/day20/) |
| docker container kill   | [docker kill](https://mileschou.me/ironman/12th/docker-newbie/day04/) |
| docker container logs   | [docker logs](https://mileschou.me/ironman/12th/docker-newbie/day07/) |
| docker container ls     | [docker ps](https://mileschou.me/ironman/12th/docker-newbie/day03/) |
| docker container rm     | [docker rm](https://mileschou.me/ironman/12th/docker-newbie/day03/) |
| docker container run    | [docker run](https://mileschou.me/ironman/12th/docker-newbie/day05/) |
| docker container start  | [docker start](https://mileschou.me/ironman/12th/docker-newbie/day04/) |
| docker container stop   | [docker stop](https://mileschou.me/ironman/12th/docker-newbie/day04/) |

過去已停止的 container 都是靠人工刪，或是 `--rm` 讓 Docker 自動刪。現在介紹 `docker container prune` 指令，它可以清除沒用的 container。清除的條件是所有停止的 container，包括剛建立未啟動的狀態也算停止的 container。

另外再介紹，如果是 Bash 的話，可以用下面這個指令無條件清除所有 container：

```
# -v 參數代表要順便移除 volume。
docker rm -vf $(docker ps -aq)
```

## 操作 container

`docker image` 的操作方法幾乎都說明過了，但 `docker container` 還有很多指令都沒看過，下面會繼續介紹。

### `docker container cp`

這個指令與 Dockerfile COPY 有一半像，`docker container cp` 與 `COPY` 都可以把 host 的檔案複製到 container，而只有 `docker container cp` 可以把 container 的檔案複製到 host。

用法如下：

```
docker container cp [OPTIONS] CONTAINER:SRC_PATH DEST_PATH|-
docker container cp [OPTIONS] SRC_PATH|- CONTAINER:DEST_PATH
```

一個例子如下：

```
# 把 container 裡 build 好的 JAR 檔複製出來
docker container cp jdk_container:/source/target ./
```

### `docker container diff`

在 [Hello Docker World](https://mileschou.me/ironman/12th/docker-newbie/day03/) 有提到，image 的內容是唯讀的，而 container 內容是可讀寫。

這個指令可以查 container 檔案系統，與 image 檔案系統的差異，也就是 container 啟動後，到底對檔案系統做了哪些修改。

### 操控 process 狀態

之前曾提到 `docker stop` 是送出 `SIGTERM` 信號、`docker kill` 則是送出 `SIGKILL`。這裡筆者把相關的指令和對應的信號都列出來：

| Docker 指令              | 信號                                   |
| ------------------------ | -------------------------------------- |
| docker container kill    | SIGKILL                                |
| docker container pause   | SIGSTOP                                |
| docker container stop    | 先 SIGTERM，timeout 到了會改送 SIGKILL |
| docker container unpause | SIGCONT                                |

### 其他雜七雜八的指令

| Docker 指令              | 用途                                                         |
| ------------------------ | ------------------------------------------------------------ |
| docker container port    | 查目前 host 與 container 有設定哪些 port forwarding          |
| docker container rename  | 改 container 名稱                                            |
| docker container restart | 先 stop 再 start                                             |
| docker container stats   | 查看 container 的 CPU 與記憶體使用量                         |
| docker container top     | 觀察 container process 狀態，其實等於在 container 裡下 ps 指令 |
| docker container wait    | 執行後，會等到 container 結束，然後再把 exit code 印出       |

## 建立 container 的參數

使用 `docker container create --help` 指令，可以看到非常多參數可以使用。筆者也介紹蠻多參數了，這裡列幾個出來參考：

| 參數           | 用途                                               |
| -------------- | -------------------------------------------------- |
| –add-host      | 新增 host 與 ip 的對照表，也就是 `/etc/hosts` 的表 |
| –cpus          | 分配 CPU 資源                                      |
| –device        | 分配 host 的裝置                                   |
| –dns           | 自定義 DNS server                                  |
| –entrypoint    | 覆寫 ENTRYPOINT 設定，注意這裡會是 exec mode       |
| –env-file      | 如果 env 族繁不及備載的話，可改用檔案              |
| –expose        | 揭露可以使用的 port                                |
| –gpus          | 分配 GPU 資源                                      |
| –hostname      | 自定義 hostname                                    |
| –ip            | 自定義 IP                                          |
| –label         | 設定 metadata                                      |
| –mac-address   | 自定義 MAC address                                 |
| –memory        | 設定記憶體上限                                     |
| –restart       | 設定自動重啟機制                                   |
| –volume-driver | 使用 volume driver                                 |

以上面的例子可以發現幾件事：

1. Dockerfile 很多設定都可以在 `docker run` 階段再覆蓋
2. CPU 與記憶體設定可以調整使用上限
3. 網路設定幾乎都可以客製化－－網路是 container 對外溝通的重要管道之一
4. Volume 設備也可以客製化－－也是 container 對外溝通的管道

建議讀者可以看過一輪，大致瞭解 Docker 可以控制 container 什麼樣的設定。

### `docker container update`

動態調整 container 的 CPU、memory、restart 機制等。

是的，volume 設定與網路設定是無法調整的，只能砍掉重練。但只要 [docker volume](https://mileschou.me/ironman/12th/docker-newbie/day21/) 與 [docker network](https://mileschou.me/ironman/12th/docker-newbie/day22/) 有配置好，砍掉重練是非常簡單的。

## 檢視元件的指令

四種元件都有各自的 inspect 指令：

```
docker image inspect
docker container inspect
docker volume inspect
docker network inspect
```

如 container，可以查出非常詳細的 Volume 設定、網路設定、CPU、Memory 等資訊。

```
# Volume 設定
docker container inspect -f '{{json .Mounts}}' fdad097c5781

# 網路設定
docker container inspect -f '{{json .NetworkSettings}}' fdad097c5781

# CPU、Memory 資訊
docker container inspect -f '{{json .HostConfig}}' fdad097c5781
```

## 今日自我回顧

今天介紹的指令或參數，可以做更詳細的設定，或查到更詳細的資訊。Kubernetes 或其他 container orchestration 工具，其實就是用這些方法與資訊在管理 container 的，因此瞭解這些內容對於開發出適用於 container orchestration 工具的程式或 image，是非常有幫助的。

# Day 29 - The Twelve-Factor App

三十天很快要到了尾聲了，今天要來介紹 [The Twelve-Factor App](https://12factor.net/)（下稱 12 Factor），它是開發 SaaS 的方法論，適用於 Web 或網路相關服務等軟體開發。怎麼突然討論起如何開發軟體呢？這跟 Docker 好像沒有什麼關係？可能有點奇怪，不過這個開發軟體的方法論，確實跟 Docker 有很大的關係。



筆者是先接觸 Docker 之後，再接觸 12 Factor 的。當時筆者還處在把 Docker 當輕量 Vagrant 用的時期，當時只感到阻礙重重。比較經典的例子像是：搞不懂為什麼 Apache container 一定要在 running Apache 的時候，才能透過 `docker exec` 進入 container。

後來在看 12 Factor 的時候，才發現錯把 container 當 VM 使用了。當時的感受是，原來 Docker 是實踐 12 Factor 的好例子；而反過來說，我們撰寫程式遵守了 12 Factor 方法，會讓使用 Docker 更順利。

今天帶讀者簡單瞭解 12 Factor 與 Docker 相關聯的地方，有興趣的讀者可以閱讀原文。

## [I. Codebase](https://12factor.net/codebase)

> One codebase tracked in revision control, many deploys

一份原始碼，可以創造出多份部署。下圖是官方提供的示意圖：

![img](https://12factor.net/images/codebase-deploys.png)

> 來源：12 Factor

Docker 也有一樣的概念，若把 Dockerfile 作為原始碼，則相同的 Dockerfile 可以在不同環境建置並使用 `docker run` 執行；若把 image 作為原始碼又會更精簡－－不同的環境都能直接使用 `docker run` 執行。

## [II. Dependencies](https://12factor.net/dependencies)

> Explicitly declare and isolate dependencies

明確地聲明與隔離依賴。什麼是不明確地聲明？比方說，直接在環境安裝了全域都可以直接使用的套件，這就很容易踩到不明確聲明。

Dockerfile 的流程中，必須明確寫出安裝依賴的過程，才有辦法正常執行應用程式，如 [Laravel image](https://mileschou.me/ironman/12th/docker-newbie/day15/) 的範例 Dockerfile：

```
# 安裝 bcmath 與 redis
RUN docker-php-ext-install bcmath
RUN pecl install redis
RUN docker-php-ext-enable redis

# 安裝程式依賴套件
COPY composer.* ./
RUN composer install --no-dev --no-scripts && composer clear-cache
```

有了明確聲明依賴後，任何人都可以依照這個流程打造出一模一樣的環境－－執行 [docker build](https://mileschou.me/ironman/12th/docker-newbie/day11/)。

## [III. Config](https://12factor.net/config)

> Store config in the environment

把設定存放在環境裡。設定包含下面幾種：

- *IV. Backing services* 的設定，如 DB / Redis 等。
- 第三方服務的 credentials，如 AWS。
- Application 在不同環境下，會有特別的設定，如域名。

不同環境的設定可能差異非常大，但它們都可以在同一份原始碼上正常運作。這樣的做法有幾個好處：

1. 安全，像 credentials 就不會隨著原始碼外流
2. 若設定放在原始碼，則調整設定就勢必得從修改原始碼開始；若設定放在環境，則直接修改環境上的設定即可。

[MySQL environment 的範例](https://mileschou.me/ironman/12th/docker-newbie/day08/)正是綜合了 *I. Codebase* 方法與 *III. Config* 來達成同一份原始碼，不同設定的部署實例。

## [IV. Backing services](https://12factor.net/backing-services)

> Treat backing services as attached resources

後端服務作為附加資源。後端服務包括了 MySQL、Redis 等常見的第三方服務，當然也包括了我們依本篇文章設計的 12 Factor App。

![img](https://12factor.net/images/attached-resources.png)

> 來源：12 Factor

這樣設計的好處即容易替換服務，比方說想把 MySQL 換成 MariaDB，或是 Redis 3.0 升級成 Redis 5，只要把連線設定調整即可。

若使用 Docker Compose 會更方便，只要更新完定義檔，重新執行啟動指令就可以立即替換了：

```
docker-composer up -d
```

## [V. Build, release, run](https://12factor.net/build-release-run)

> Strictly separate build and run stages

嚴格區分 build 和 run。build 階段才能調整程式與整合依賴成 artifacts；run 階段則非常單純，把 artifacts 拿來執行就行了。

![img](https://12factor.net/images/release.png)

> 來源：12 Factor

在 Docker container 修改程式碼，其實是非常麻煩的，要做非常多前置準備。但如果遵守 build / run 分離的方法，就會變得非常簡單。

## [VI. Processes](https://12factor.net/processes)

> Execute the app as one or more stateless processes

使用一個以上的無狀態 process 來執行應用程式。這裡的關鍵在於要設計成無狀態，如果有狀態或資料要保存，可以透過 *IV. Backing services* 的資料庫保存。

Docker 每次啟動 container 都是全新的沒有過去狀態的，之前提到的[一次性](https://mileschou.me/ironman/12th/docker-newbie/day06/)。換句話說，設計一個能在 Docker 上運作良好的 container，就代表有符合此方法－－[Container 應用](https://mileschou.me/ironman/12th/docker-newbie/day09/)正是活動此特性的範例參考。

## [VII. Port binding](https://12factor.net/port-binding)

> Export services via port binding

透過 port 綁定來提供服務。

Docker 可以用 [port forwarding](https://mileschou.me/ironman/12th/docker-newbie/day05/) 來對外提供服務，Dockerfile 則可以使用 `EXPOSE` 指令讓 container 之間也可以互相使用 port 存取服務

```
EXPOSE 80

CMD ["php", "artisan", "serve", "--port", "80"]
```

## [VIII. Concurrency](https://12factor.net/concurrency)

> Scale out via the process model

透過 process model 做水平擴展。12 Factor 是以工作類型來分類 process，如 HTTP 請求給 web process 處理，背景則是使用 worker process。

![img](https://12factor.net/images/process-types.png)

> 來源：12 Factor

配合 *VI. Processes* 提到的無狀態特性，可以讓應用程式非常容易做水平擴展，甚至是跨 VM、跨實體機器的擴展。

Container 即 process，因此 Docker 要做水平擴展是非常簡單的－－多跑幾次 `docker run` 就行了，甚至 Docker Compose 還提供專用的 [scale](https://docs.docker.com/compose/reference/scale/) 指令：

```
docker-compose scale web=2 worker=3
```

## [IX. Disposability](https://12factor.net/disposability)

> Maximize robustness with fast startup and graceful shutdown

快速啟動，優雅終止，最大化系統的強健性。

將應用程式設計成可以快速啟動並開放服務，好處就在於擴展和上線變得非常容易。收到終止信號 `SIGTERM` 並優雅終止，則要求 process 停止接收任務，並把最的任務完成後，才真正結束 process。

Docker 在管理啟動或終止都做的很完整，主要還是程式設計要得當。

## [X. Dev/prod parity](https://12factor.net/dev-prod-parity)

> Keep development, staging, and production as similar as possible

盡可能保持環境一致，環境一致最大的好處還是在於開發除錯的效率。「我的電腦上就沒問題」這句話正是這個方法的反指標，正因個人環境上有做了特別安裝，才讓程式有辦法正常運作，這個安裝過程就得考慮是否要同步到其他人或測試環境上。

Dockerfile 是一個 IoC 很好的實踐，因此非常容易做到環境一致。

## [XI. Logs](https://12factor.net/logs)

> Treat logs as event streams

使用 event stream 輸出 log。正如 *IV. Backing services* 與 *VI. Processes* 所提到的，12 Factor App 不應該保存狀態，類似的，它也不應該保存 log，而是要把 log 作為 event stream 輸出。

Docker 可以截取 process 的標準輸出（`STDOUT`），並透過內部機制轉到 [log driver](https://docs.docker.com/config/containers/logging/configure/)，因此程式只要處理好標準輸出即可。

## [XII. Admin processes](https://12factor.net/admin-processes)

> Run admin/management tasks as one-off processes

管理與維護任務作為一次性的 process 執行，像 migration 正是屬於這一類的任務。

對 Docker 而言，要在已啟動的 container 上執行 process 太簡單了，使用 `docker exec` 即可達成任務。

```
docker exec -it web php artisan migrate
```

## 12 Factor 的目標

最後回頭來看 12 Factor 當初設計的目標：

> 這段原文很長，但因為是必要的，所以還是無斷複製過來

> - Use **declarative** formats for setup automation, to minimize time and cost for new developers joining the project;
> - Have a **clean contract** with the underlying operating system, offering **maximum portability** between execution environments;
> - Are suitable for **deployment** on modern **cloud platforms**, obviating the need for servers and systems administration;
> - **Minimize divergence** between development and production, enabling **continuous deployment** for maximum agility;
> - And can **scale up** without significant changes to tooling, architecture, or development practices.

簡單整理如下：

1. 使用描述的格式設定自動化流程，讓新人能用更小的成本加入專案。在[為各種框架 build image](https://mileschou.me/ironman/12th/docker-newbie/day16/) 的時候有提到「只要有程式和 Dockerfile，讀者就可以建得出跟筆者一樣的環境與 server」。不僅如此，因為 Dockerfile 正是描述如何建置環境，因此對任何理解描述的開發者，都有辦法調整裡面的流程，並同步給其他開發者。
2. 與 OS 之間有更清楚的介面，這樣就能具備更高的移植性，因此 12 Factor App 不僅能在很多機器上執行，甚至是雲端服務上也能運作良好。
3. 追求環境一致性，因此能有更快的交付速度，在實現持續整合與持續部署會更加容易
4. Process model 設計，讓擴展服務變得非常容易，甚至不需要動到任何工具架構，或開發流程。

## 今日自我回顧

曾有人問筆者：身為一個開發者，學完 run container，學完 build image，之後要學什麼呢？

**學習寫出符合 12 Factor 的程式。**

能在 Docker 上運作良好的，正是符合 12 Factor 的應用程式。

# Day 30 - 學無止盡

Docker 學習的道路真的是學無止盡，以下筆者列出三十天裡沒有提到的東西，有興趣的讀者可以用關鍵字查詢。



- Container orchestration，如 [Kubernetes](https://kubernetes.io/)、[Swarm](https://docs.docker.com/engine/swarm/)
- [Windows Container](https://docs.microsoft.com/zh-tw/virtualization/windowscontainers/about/)
- [Docker 安全議題](https://docs.docker.com/engine/security/)，裡面洋洋灑灑就列了六點注意事項
- [scratch](https://docs.docker.com/develop/develop-images/baseimages/) 讓你可以 build 出真正的 base image
- [Best Practice](https://docs.docker.com/develop/dev-best-practices/)

最後，來個小測驗考考大家是不是對 Docker 更瞭解：

> 本測試有參考 [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)。

1. Docker image 與 container 之間的關係，下列哪種描述「錯誤」？
   - (A) Container 必須基於 image 產生；但相對地，image 無法藉由 container 產生。
   - (B) 同個 image ID 內容是不可變的（immutable），而 container 內容是可變的（mutable）。
   - (C) 若使用某個 image 運行一個 container，則想移除 image 前，必須先移除 container 才能移除 image。
   - (D) 上述 ABC 都正確。
   - (E) 上述 ABC 都「錯誤」。
2. 考慮部署「線上環境」，VM 與 container 的選擇與比較，下列哪種描述「錯誤」？
   - (A) Container 啟動速度比 VM 快。
   - (B) Container 記憶體使用量比 VM 小。
   - (C) 若過去是使用 VM，想改用 Container 就必須使用與 VM 一樣的作業系統建置，才能確保系統運作正常。
   - (D) 上述 ABC 都正確。
   - (E) 上述 ABC 都「錯誤」。
3. 在符合 Docker 官方的最佳實踐（Docker best practices）與 12 Factor 原則的前提下，有一個 load balance 後面接多個 container 部署在「線上環境」，平常好好的，今天發現某一個 container 程式運作異常（如：即將 OOM），但後端服務（backing service）沒異狀。此時最「不」應該採取下列哪種做法？
   - (A) 啟動一個新的 container 接到 LB，然後中斷有問題的 container 流量。
   - (B) 透過 rolling update 機制，將該 container 砍掉重練。
   - (C) 嘗試進入有問題的 container，利用工具 debug。
   - (D) 上述 ABC 做法都符合。
   - (E) 上述 ABC 做法都「不」符合。
4. 下列都是兩個 container 組合的架構，皆可正常運行。以單一 container 作為一個 SaaS 來看，哪一種「比較不」符合 Docker 官方的最佳實踐（Docker best practices）？
   - (A) Nginx container + Apache with PHP-FPM（FastCGI）container。
   - (B) Apache container + Tomcat container。
   - (C) Nginx container + Node container。
   - (D) 以上 ABC 皆符合。
   - (E) 以上 ABC 皆「不」符合。
5. 考慮部署「線上環境」，下列建置 Docker image 與運行 container 的描述，何種做法「不」符合 Docker 官方的最佳實踐（Docker best practices）？
   - (A) 持續整合（Continuous Integration）有提到要經常做驗證，因此部署上線後的第一件事是在 container 上先跑單元測試，再啟動應用程式。
   - (B) 利用 Docker VOLUME 參數設定，可以直接進上線用的 container，到共用 volume 目錄裡更新程式。
   - (C) 使用 ARG 參數，在建置 image 階段過程才能機敏資訊加入 image 裡，如此一來，機敏資訊就可以不用放原始碼裡了。
   - (D) 上述 ABC 做法都符合。
   - (E) 上述 ABC 做法都「不」符合。

## Image 與 Container 之間的關係

第一題的答案是 (A)

A 描述錯誤：`docker run` 可以基於 image 產生 container，所以第一句話是正確的；相對地，`docker commit` 可以藉由 container 產生 image，所以第二句話是錯誤的。

B 描述正確：`docker run <IMAGE ID>` 指令中，![img]()為 SHA256 digest，同個 digest 的內容無法改變。而 container 內容則是可變的，比方說進入 Nginx container 新增 HTML 檔，即可立刻使用瀏覽器看到內容。

C 描述正確：Image 上 run 一個 container 時，可以使用 `docker rmi -f <IMAGE ID>` 強制把 image 移除。雖然無法再使用該 Digest 再次啟動 container，但實際上 image 內容依然是存在的，因為重新 pull image 會發現 `Already exists` 的關鍵字。實際測試指令如下：

```
$ docker run php:7.4 php -v
Unable to find image 'php:7.4' locally
7.4: Pulling from library/php
...
$ docker rmi -f php:7.4
Untagged: php:7.4
Untagged: php@sha256:...
Deleted: sha256:...
$ docker pull php:7.4
7.4: Pulling from library/php
xxxxxxxxxxxx: Already exists
xxxxxxxxxxxx: Already exists
...
```

瞭解 image 與 container 的關係後，才能進一步瞭解 Docker 是如何建置、如何加速建置、啟動 container 等。

### VM 與 Container 的比較與選擇

第二題的答案是：(C)

此題目要考慮下列兩件事：

1. 「考慮部署線上環境」，因此沒有環境一致的問題，只要考慮 VM 或 container 放到線上的選擇或比較即可。
2. 因情境是「考慮部署」與「VM 與 container 的選擇與比較」，因此是在討論 guest 而不是 host。

A 與 B 很明顯正確，container 因為少了 OS 層，當然啟動速度與記憶體使用量，都相較 VM 來的有優勢。

C 假設過去 VM 習慣使用 Ubuntu 或是任一種 OS，現在 container 是否必須要用相同的 OS 才能正常運行（VM 跟 Container 也可以交換反過來看）？答案當然是「非必要」的，如官方 [Redis image](https://hub.docker.com/_/redis/) 就提供了 Debian 和 Alpine 等選擇，即使作業系統不一樣，只要把程式或設定做好，系統一樣能正常運作。

Container 用起來跟 VM 很類似，但要記得它們本質是不同的。而不管 VM 或 container 都得經過調校才能發揮最大的優勢。

## Container 是一次性的（disposable）

第三題的答案是：(C)

A 與 B 其實是差不多的，差別是 B 會把 container 砍掉。

C 很明顯是不能做的。進去安裝 Vim 或相關除錯工具明顯錯誤就不提了，如果是為了看 log，參考 [12 Factor Logs](https://12factor.net/logs)，它應該能在其他地方查得到，而不是進 container 查；如果是進去調整參數等行為，則會不符合 [12 Factor Build, release, run](https://12factor.net/build-release-run) 嚴格分離的原則。

現在 container 都是交由 Kubernetes 等 container orchestration 系統負責這些維運任務，但開發者也有必要了解這類問題的處理方法，才有辦法寫出符合 container 架構的程式。

> 一次性的特色可以參考 [Create ephemeral containers](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#create-ephemeral-containers)。

## Container 盡可能只做一件事

第四題的答案是：(A)

參考 [Decouple applications](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#decouple-applications)，Docker 官方是這麼說的：

> Limiting each container to one process is a good rule of thumb, but it is not a hard and fast rule.

上面五種 container，唯獨 **Apache with PHP-FPM（FastCGI）container** 是比較不符合的，因為它必須啟動做兩件不同任務的 process。可以注意到在 DockerHub 找到類似的 image 的 CMD，都必須要使用 Supervisor 或類似的工具來管理 process。

順帶一提，官方也沒有提供 Apache + PHP-FPM 或 Nginx + PHP-FPM 的 image，而是提供只有 PHP-FPM 的 image，或是 Apache + PHP-CGI 的 image。

這概念與 SOLID 裡 SRP 的優點一樣：只做一件事，架構不會複雜，除錯會更容易。

## Container 應該怎麼應用？

第四題的答案是：(E)

A 的問題：部署上線後居然可以跑單元測試？這代表測試程式碼和單元測試套件也一併被部署上線，這不符合 [Don’t install unnecessary packages](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#dont-install-unnecessary-packages)。

正確的做法：在建置 image 前或是 [Use multi-stage builds](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#use-multi-stage-builds) 在一開始的階段做單元測試，最終僅部署做完單元測試後的程式碼。

> 相對地，部署上線後，可以做冒煙測試（[smoke testing](https://en.wikipedia.org/wiki/Smoke_testing_(software))）。

B 的問題：[VOLUME](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#volume) 官方不建議用來放程式，而是放額外要保存的資料，如 MySQL 的 Dockerfile 就有設定 [`VOLUME /var/lib/mysql`](https://github.com/docker-library/mysql/blob/3dfa7a3c038f342b9dec09fa85247bef69ae2349/8.0/Dockerfile#L67) 是存放資料庫檔案。

正確的做法：程式上線應該透過建置新的 image，跑新的 container 來取代舊的。

> 可以試著反過來思考，為何我們會覺得 Docker 上跑 MySQL / Redis / Apache 很快速方便？因為它們把程式都包在 image 裡了。

C 的問題：「把機敏資訊加入 image 裡」這句話的意思就是，只要有辦法下載 image 就能得到機敏資訊。當然可以限制下載 image 的權限，但還是有另一個問題是難以做到環境同步，因為線上環境跟測試環境會是不同的 image－－因為機敏資訊設定通常是不一樣的。

正確的做法：使用 `ENV` 環境參數（參考 [12 Factor Config](https://12factor.net/config)），把機敏資訊存在環境。

## 寫在最後

Docker 真的是學無止盡，雖然筆者跟他相處了很久，但要寫的時候，還是得東查西查。

希望這次的鐵人賽能幫助到大家，感謝收看。
