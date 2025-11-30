# Docker 基礎入門

> Docker 核心概念與基本操作指令。

## 🐳 Docker 基礎教學

### 完整教學
- [Docker Basic Tutorial](docker.md)

核心內容：
- Docker 架構
- 映像與容器概念
- 基本指令操作
- 容器生命週期
- 網路與存儲

### Hello World 範例
- [Hello Docker](docker_helloworld.md)

核心內容：
- 第一個 Dockerfile
- Python 容器化
- 建置與運行
- 容器管理指令

### 簡單範例
- [Simple Example](example.md)

核心內容：
- 實戰範例
- 常見使用場景
- 最佳實踐

## 💡 基本概念

### Docker 三大核心
1. **映像 (Image)**
   - 只讀模板
   - 包含應用程式與依賴
   - 分層儲存

2. **容器 (Container)**
   - 映像的運行實例
   - 可讀寫層
   - 隔離環境

3. **倉庫 (Registry)**
   - Docker Hub
   - 私有倉庫
   - 映像分發

## 🔧 基本指令

### 映像管理
```bash
# 拉取映像
docker pull python:3.9

# 列出映像
docker images

# 刪除映像
docker rmi image_name

# 建置映像
docker build -t myapp:latest .
```

### 容器操作
```bash
# 運行容器
docker run -d -p 8080:80 --name myapp nginx

# 列出容器
docker ps        # 運行中
docker ps -a     # 所有

# 停止容器
docker stop myapp

# 啟動容器
docker start myapp

# 刪除容器
docker rm myapp

# 進入容器
docker exec -it myapp bash
```

### 日誌與監控
```bash
# 查看日誌
docker logs myapp
docker logs -f myapp  # 跟隨模式

# 查看資源使用
docker stats

# 檢查容器詳情
docker inspect myapp
```

## 🚀 Hello World 實戰

### 建立 Dockerfile
```dockerfile
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 複製依賴文件
COPY requirements.txt .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["python", "app.py"]
```

### 建置與運行
```bash
# 建置映像
docker build -t hello-python .

# 運行容器
docker run -d -p 8000:8000 --name myapp hello-python

# 查看日誌
docker logs -f myapp

# 測試應用
curl http://localhost:8000
```

**最後更新**: 2025-12-01
