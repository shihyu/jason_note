# 使用 Docker 運行最新版本 GCC 的完整指南

## 方法一：使用官方 GCC Docker 映像檔（推薦）

### 1. 建立 Dockerfile

```dockerfile
# 使用最新版本的 GCC 官方映像檔
FROM gcc:15

# 設置工作目錄
WORKDIR /app

# 更新套件管理器並安裝必要工具
RUN apt-get update && apt-get install -y \
    vim \
    nano \
    gdb \
    make \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# 建立程式碼目錄
RUN mkdir -p /app/src

# 設置環境變數
ENV CC=gcc
ENV CXX=g++

# 預設命令
CMD ["bash"]
```

### 2. 建立測試程式

建立一個簡單的 C++ 程式來測試：

**hello.cpp**
```cpp
#include <iostream>
#include <vector>
#include <string>

int main() {
    std::vector<std::string> messages = {
        "Hello from GCC 15!",
        "C++17 is the default standard",
        "Docker + GCC = 🚀"
    };
    
    for (const auto& msg : messages) {
        std::cout << msg << std::endl;
    }
    
    // 顯示 GCC 版本
    std::cout << "\nCompiled with GCC version: " << __VERSION__ << std::endl;
    
    return 0;
}
```

### 3. 建立並運行容器

```bash
# 建立 Docker 映像檔
docker build -t gcc-dev .

# 運行容器（掛載當前目錄到容器內）
docker run -it -v $(pwd):/app/src gcc-dev

# 或者在 Windows PowerShell 中
docker run -it -v ${PWD}:/app/src gcc-dev
```

### 4. 在容器內編譯和運行

```bash
# 進入容器後，切換到源碼目錄
cd /app/src

# 編譯 C++ 程式
g++ -std=c++17 -O2 -Wall -Wextra hello.cpp -o hello

# 運行程式
./hello

# 檢查 GCC 版本
gcc --version
g++ --version
```

## 方法二：從源碼編譯 GCC 15（進階用法）

### 1. 進階 Dockerfile

```dockerfile
# 使用 Ubuntu 作為基礎映像檔
FROM ubuntu:22.04

# 設置非互動模式
ENV DEBIAN_FRONTEND=noninteractive

# 安裝建構依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    tar \
    xz-utils \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    libisl-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 設置工作目錄
WORKDIR /tmp

# 下載並編譯 GCC 15.1
RUN wget https://ftp.gnu.org/gnu/gcc/gcc-15.1.0/gcc-15.1.0.tar.xz \
    && tar -xf gcc-15.1.0.tar.xz \
    && cd gcc-15.1.0 \
    && ./contrib/download_prerequisites \
    && mkdir build \
    && cd build \
    && ../configure \
        --prefix=/usr/local/gcc-15 \
        --enable-languages=c,c++,fortran \
        --disable-multilib \
        --with-system-zlib \
    && make -j$(nproc) \
    && make install \
    && cd / \
    && rm -rf /tmp/gcc-15.1.0*

# 設置環境變數
ENV PATH="/usr/local/gcc-15/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/gcc-15/lib64:${LD_LIBRARY_PATH}"

# 建立工作目錄
WORKDIR /app

# 預設命令
CMD ["bash"]
```

## 方法三：使用 docker-compose（推薦用於開發）

### 1. 建立 docker-compose.yml

```yaml
version: '3.8'

services:
  gcc-dev:
    build: .
    container_name: gcc-dev-container
    volumes:
      - .:/app/src
      - gcc-cache:/root/.cache
    working_dir: /app/src
    tty: true
    stdin_open: true
    environment:
      - CC=gcc
      - CXX=g++
      - MAKEFLAGS=-j$(nproc)

volumes:
  gcc-cache:
```

### 2. 使用 docker-compose 運行

```bash
# 建立並啟動容器
docker-compose up -d

# 進入容器
docker-compose exec gcc-dev bash

# 停止容器
docker-compose down
```

## 常用編譯指令

### 基本編譯
```bash
# 編譯 C 程式
gcc -std=c17 -O2 -Wall -Wextra program.c -o program

# 編譯 C++ 程式
g++ -std=c++17 -O2 -Wall -Wextra program.cpp -o program

# 編譯 C++23 程式（實驗性功能）
g++ -std=c++23 -O2 -Wall -Wextra program.cpp -o program
```

### 除錯編譯
```bash
# 包含除錯資訊
g++ -std=c++17 -g -Wall -Wextra program.cpp -o program

# 使用 GDB 除錯
gdb ./program
```

### 效能優化編譯
```bash
# 高度優化
g++ -std=c++17 -O3 -march=native -Wall -Wextra program.cpp -o program

# 連結時優化
g++ -std=c++17 -O3 -flto -Wall -Wextra program.cpp -o program
```

## 建議的專案結構

```
my-cpp-project/
├── Dockerfile
├── docker-compose.yml
├── src/
│   ├── main.cpp
│   ├── utils.cpp
│   └── utils.h
├── tests/
│   └── test_main.cpp
├── Makefile
└── README.md
```

## 範例 Makefile

```makefile
CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra
TARGET = app
SRCDIR = src
SOURCES = $(wildcard $(SRCDIR)/*.cpp)
OBJECTS = $(SOURCES:.cpp=.o)

$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $(TARGET)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)

.PHONY: clean
```

## 快速開始腳本

建立一個 `start.sh` 腳本：

```bash
#!/bin/bash

# 建立並運行 GCC 開發環境
echo "正在建立 GCC 開發環境..."
docker build -t gcc-dev .

echo "正在啟動容器..."
docker run -it -v $(pwd):/app/src gcc-dev

echo "環境已準備完成！"
```

使用方法：
```bash
chmod +x start.sh
./start.sh
```

這樣你就可以在 Docker 容器中使用最新版本的 GCC 15.1 來編譯和運行 C/C++ 程式了！
