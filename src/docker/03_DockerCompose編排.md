# Docker Compose 編排

> Docker Compose 多容器應用編排與服務管理。

## 📦 Docker Compose 基礎

### 完整指南
- [Docker Compose](docker_compose.md)

核心內容：
- Compose 檔案語法
- 服務定義
- 網路配置
- 存儲管理
- 環境變數
- 依賴關係

### 實戰範例
- [Docker Compose Example](docker_compse_example.md)

核心內容：
- 多容器應用範例
- 實際部署案例
- 常見配置模式
- 故障排除

## 💡 Compose 基本語法

### docker-compose.yml 範例
```yaml
version: '3.8'

services:
  # Web 應用
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://db:5432/mydb
    depends_on:
      - db
      - redis
    restart: always

  # 資料庫
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password

  # Redis 快取
  redis:
    image: redis:6
    ports:
      - "6379:6379"

volumes:
  postgres_data:

networks:
  default:
    name: myapp_network
```

## 🔧 常用指令

### 基本操作
```bash
# 啟動所有服務
docker-compose up

# 背景執行
docker-compose up -d

# 停止服務
docker-compose stop

# 停止並刪除容器
docker-compose down

# 停止並刪除容器、網路、映像
docker-compose down --rmi all --volumes
```

### 服務管理
```bash
# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs
docker-compose logs -f web  # 跟隨特定服務

# 重啟服務
docker-compose restart

# 重建並啟動
docker-compose up --build
```

### 進階操作
```bash
# 執行一次性命令
docker-compose run web python manage.py migrate

# 進入運行中的容器
docker-compose exec web bash

# 擴展服務實例
docker-compose up --scale web=3

# 驗證 compose 文件
docker-compose config
```

## 🌐 網路配置

### 自訂網路
```yaml
version: '3.8'

services:
  web:
    networks:
      - frontend
      - backend

  api:
    networks:
      - backend

  db:
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # 內部網路，不可對外
```

## 💾 存儲管理

### Volume 類型
```yaml
services:
  app:
    volumes:
      # 具名 volume
      - data:/app/data

      # 綁定掛載
      - ./config:/app/config:ro

      # 臨時 volume
      - /app/tmp

volumes:
  data:
    driver: local
```

## 🔐 環境變數

### 使用 .env 文件
```yaml
# docker-compose.yml
services:
  web:
    image: myapp:${TAG}
    environment:
      - DB_HOST=${DB_HOST}
      - DB_PASSWORD=${DB_PASSWORD}
```

```bash
# .env 文件
TAG=latest
DB_HOST=localhost
DB_PASSWORD=secret
```

## 🚀 完整應用範例

### Web + DB + Redis
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - web

  web:
    build:
      context: .
      dockerfile: Dockerfile
    expose:
      - "8000"
    volumes:
      - .:/app
      - static_volume:/app/static
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:13-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
```

**最後更新**: 2025-12-01
