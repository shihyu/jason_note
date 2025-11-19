# linux-0.12 源碼學習

*參考《Linux內核完全剖析 --基於0.12內核》*

1. linux-0.12目錄為修改過的源代碼，其中加入了**中文註釋**，修改部分代碼使其能在現在的環境下**編譯**，並且支持**GDB調試**。

2. oslab為實驗目錄，切到oslab目錄下，運行該目錄下的`run.sh`腳本即可運行linux0.12操作系統。

![實驗截圖](/src/.pic/oslab.jpg)

### 一、環境搭建

#### 1.1 方式一

可以選擇已創建好的docker鏡像作為實驗環境（人生苦短，我用容器）。linux用戶可以通過掛載將本地項目目錄掛載到容器中，windows或mac用戶可以在容器內重新git clone一份（因為不區分文件名大小寫會導致掛載出錯）。->[Dockerfile](src/docker/Dockerfile)

1. docker方式

    ```shell
    # 1. 從docker hub中拉取鏡像
    docker pull ultraji/ubuntu-xfce-novnc
    # 2. 運行容器
    docker run -t -i -p 6080:6080 -v ${本地項目路徑}:${容器內項目路徑} ultraji/ubuntu-xfce-novnc
    ```

    或docker-compose方式

    ```shell
    # 1. 切到項目docker目錄下
    cd linux-0.12/src/docker
    # 2.修改docker-compose.yaml中的項目掛載路徑
    ...
    # 3.啟動容器
    docker-compose up -d
    ```

2. 通過瀏覽器輸入```http://localhost:6080```就訪問容器內的桌面系統了。

    - vnc登陸密碼: 123456
    - 默認用戶: ubuntu
    - 用戶密碼: 123456

#### 1.2 方式二

**ubuntu(64bit，>=14.04)** 的用戶也可以使用`src/code`目錄下的一鍵環境搭建腳本。->[setup.sh](src/code/setup.sh)

### 二、如何使用

該項目的oslab為實驗目錄，切到oslab目錄下，運行該目錄下的`run.sh`腳本即可運行linux0.12操作系統。

- `./run.sh -m` &emsp;編譯生成新的Image鏡像
- `./run.sh -g` &emsp;運行bochs模擬器，與gdb聯調
