# Dockerfile 與映像管理

> Dockerfile 最佳實踐、Python 優化與自訂映像建置。

## 🐍 Python Dockerfile

### 完美範本
- [Perfect Python Dockerfile](creating-the-perfect-python-dockerfile.md)

核心內容：
- 多階段建置
- 映像大小優化
- 安全最佳實踐
- 快取策略
- 生產環境部署

### 從映像建立 Dockerfile
- [Dockerfile from Docker Image](dockerfile-from-docker-image.md)

核心內容：
- 反向工程映像
- 映像層分析
- 重建 Dockerfile
- 映像優化

## 🛠️ 自訂環境

### GCC 編譯環境
- [運行最新版 GCC](gcc.md)

核心內容：
- GCC 容器化
- 編譯環境配置
- C/C++ 開發環境
- 跨版本測試

## 💡 Dockerfile 最佳實踐

### 多階段建置
```dockerfile
# 建置階段
FROM python:3.9 AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 運行階段
FROM python:3.9-slim

WORKDIR /app

# 只複製必要文件
COPY --from=builder /root/.local /root/.local
COPY . .

# 設定 PATH
ENV PATH=/root/.local/bin:$PATH

CMD ["python", "app.py"]
```

### 映像大小優化
```dockerfile
FROM python:3.9-slim

# 使用 .dockerignore 排除不需要的文件
# 合併 RUN 指令減少層數
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/*

# 使用 COPY 替代 ADD
COPY requirements.txt .
COPY . .
```

### 快取策略
```dockerfile
# 先複製 requirements.txt，利用 Docker 快取
COPY requirements.txt .
RUN pip install -r requirements.txt

# 最後複製應用程式碼（經常變動）
COPY . .
```

### 安全最佳實踐
```dockerfile
# 使用非 root 使用者
FROM python:3.9-slim

RUN useradd -m -u 1000 appuser
USER appuser

WORKDIR /home/appuser/app

COPY --chown=appuser:appuser . .

CMD ["python", "app.py"]
```

## 🔧 映像管理

### 標籤管理
```bash
# 建置並標籤
docker build -t myapp:1.0.0 .
docker build -t myapp:latest .

# 多個標籤
docker tag myapp:1.0.0 myapp:stable
docker tag myapp:1.0.0 registry.example.com/myapp:1.0.0
```

### 映像檢查
```bash
# 查看映像歷史
docker history myapp:latest

# 檢查映像層
docker inspect myapp:latest

# 映像大小分析
docker images myapp
```

### 清理映像
```bash
# 刪除懸空映像
docker image prune

# 刪除所有未使用映像
docker image prune -a

# 查看映像大小
docker system df
```

## 🚀 GCC 開發環境

### Dockerfile 範例
```dockerfile
FROM gcc:latest

WORKDIR /workspace

# 安裝開發工具
RUN apt-get update && apt-get install -y \
    cmake \
    gdb \
    valgrind \
    && rm -rf /var/lib/apt/lists/*

# 複製程式碼
COPY . .

# 編譯
RUN g++ -std=c++17 -O3 -o app main.cpp

CMD ["./app"]
```

### 使用方式
```bash
# 建置映像
docker build -t gcc-dev .

# 編譯程式
docker run --rm -v $(pwd):/workspace gcc-dev g++ -std=c++17 -o app main.cpp

# 運行程式
docker run --rm -v $(pwd):/workspace gcc-dev ./app
```

**最後更新**: 2025-12-01
