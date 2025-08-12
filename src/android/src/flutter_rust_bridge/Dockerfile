# Rust-Flutter Bridge Docker Image
FROM ubuntu:22.04

# 避免互動式安裝
ENV DEBIAN_FRONTEND=noninteractive

# 安裝基本工具和 Rust
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
    git \
    unzip \
    xz-utils \
    clang \
    cmake \
    ninja-build \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 安裝 Flutter
RUN curl -L https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.24.3-stable.tar.xz | tar -xJ -C /opt
ENV PATH="/opt/flutter/bin:${PATH}"

# 設置工作目錄
WORKDIR /app

# 複製專案文件
COPY . .

# 建置 Rust 函式庫
RUN cargo build --release

# 設置 Flutter 環境
RUN cd flutter_app && flutter pub get

# 預設命令
CMD ["make", "help"]