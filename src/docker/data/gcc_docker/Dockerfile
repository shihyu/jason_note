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
