#!/bin/bash

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置變數
DRAGONFLY_PORT=${1:-6379}
DRAGONFLY_MEMORY=${2:-2gb}
DRAGONFLY_THREADS=${3:-4}
CONTAINER_NAME="dragonfly-main"

echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║          DragonflyDB 完整安裝與配置腳本                 ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# 顯示配置
echo -e "${BLUE}📋 安裝配置：${NC}"
echo -e "   • 端口: ${GREEN}$DRAGONFLY_PORT${NC}"
echo -e "   • 記憶體限制: ${GREEN}$DRAGONFLY_MEMORY${NC}"
echo -e "   • 執行緒數: ${GREEN}$DRAGONFLY_THREADS${NC}"
echo -e "   • 容器名稱: ${GREEN}$CONTAINER_NAME${NC}"
echo ""

# 檢查系統需求
echo -e "${YELLOW}步驟 1: 檢查系統需求${NC}"
echo -e "──────────────────────────────────────────"

# 檢查 Docker
check_docker() {
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
        echo -e "${GREEN}✓${NC} Docker 已安裝 (版本: $DOCKER_VERSION)"
        return 0
    else
        echo -e "${RED}✗${NC} Docker 未安裝"
        echo -e "${YELLOW}  正在嘗試安裝 Docker...${NC}"

        # 安裝 Docker
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh

        # 將當前用戶加入 docker 群組
        sudo usermod -aG docker $USER

        echo -e "${GREEN}✓${NC} Docker 安裝完成"
        echo -e "${YELLOW}  注意: 可能需要重新登入以使 docker 群組權限生效${NC}"
        return 0
    fi
}

check_docker

# 檢查 Python
echo -e "\n${YELLOW}步驟 2: 檢查 Python 環境${NC}"
echo -e "──────────────────────────────────────────"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python3 已安裝 (版本: $PYTHON_VERSION)"
else
    echo -e "${RED}✗${NC} Python3 未安裝"
    echo -e "${YELLOW}  正在安裝 Python3...${NC}"
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

# 檢查 pip
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo -e "${YELLOW}  正在安裝 pip...${NC}"
    sudo apt-get install -y python3-pip
    PIP_CMD="pip3"
fi
echo -e "${GREEN}✓${NC} pip 已安裝 (使用: $PIP_CMD)"

# 安裝 Python 套件
echo -e "\n${YELLOW}步驟 3: 安裝 Python 套件${NC}"
echo -e "──────────────────────────────────────────"

# redis-py
if $PIP_CMD show redis &> /dev/null; then
    REDIS_VERSION=$($PIP_CMD show redis | grep Version | awk '{print $2}')
    echo -e "${GREEN}✓${NC} redis-py 已安裝 (版本: $REDIS_VERSION)"
else
    echo -e "${YELLOW}  正在安裝 redis-py...${NC}"
    $PIP_CMD install redis
    echo -e "${GREEN}✓${NC} redis-py 安裝完成"
fi

# hiredis (可選，但推薦)
if $PIP_CMD show hiredis &> /dev/null; then
    HIREDIS_VERSION=$($PIP_CMD show hiredis | grep Version | awk '{print $2}')
    echo -e "${GREEN}✓${NC} hiredis 已安裝 (版本: $HIREDIS_VERSION)"
else
    echo -e "${YELLOW}  正在安裝 hiredis (C 加速器)...${NC}"
    $PIP_CMD install hiredis
    echo -e "${GREEN}✓${NC} hiredis 安裝完成"
fi

# 檢查並停止現有容器
echo -e "\n${YELLOW}步驟 4: 檢查現有 DragonflyDB 容器${NC}"
echo -e "──────────────────────────────────────────"

if docker ps -a | grep -q $CONTAINER_NAME; then
    echo -e "${YELLOW}⚠${NC}  發現現有容器 '$CONTAINER_NAME'"
    echo -e "${YELLOW}  正在停止並移除...${NC}"
    docker stop $CONTAINER_NAME 2>/dev/null
    docker rm $CONTAINER_NAME 2>/dev/null
    echo -e "${GREEN}✓${NC} 已清理現有容器"
else
    echo -e "${GREEN}✓${NC} 沒有發現衝突的容器"
fi

# 檢查端口占用
echo -e "\n${YELLOW}步驟 5: 檢查端口 $DRAGONFLY_PORT${NC}"
echo -e "──────────────────────────────────────────"

if nc -z localhost $DRAGONFLY_PORT 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  端口 $DRAGONFLY_PORT 被占用"
    echo -e "${YELLOW}  正在檢查占用進程...${NC}"

    # 顯示占用端口的進程
    sudo lsof -i:$DRAGONFLY_PORT 2>/dev/null | grep LISTEN | head -5

    read -p "是否要終止占用端口的進程？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo kill -9 $(sudo lsof -t -i:$DRAGONFLY_PORT) 2>/dev/null
        echo -e "${GREEN}✓${NC} 已釋放端口 $DRAGONFLY_PORT"
    else
        echo -e "${RED}✗${NC} 安裝中止"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} 端口 $DRAGONFLY_PORT 可用"
fi

# 拉取最新的 DragonflyDB 映像
echo -e "\n${YELLOW}步驟 6: 拉取 DragonflyDB Docker 映像${NC}"
echo -e "──────────────────────────────────────────"

echo -e "${YELLOW}  正在拉取最新版本...${NC}"
docker pull docker.dragonflydb.io/dragonflydb/dragonfly:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 成功拉取 DragonflyDB 映像"
else
    echo -e "${RED}✗${NC} 拉取映像失敗"
    exit 1
fi

# 啟動 DragonflyDB
echo -e "\n${YELLOW}步驟 7: 啟動 DragonflyDB 容器${NC}"
echo -e "──────────────────────────────────────────"

echo -e "${YELLOW}  正在啟動容器...${NC}"

docker run -d \
    --name $CONTAINER_NAME \
    --ulimit memlock=-1 \
    -p $DRAGONFLY_PORT:6379 \
    --restart unless-stopped \
    -v dragonfly-data:/data \
    docker.dragonflydb.io/dragonflydb/dragonfly:latest \
    --proactor_threads=$DRAGONFLY_THREADS \
    --maxmemory=$DRAGONFLY_MEMORY \
    --dir /data \
    --logtostderr

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} DragonflyDB 容器啟動成功"
else
    echo -e "${RED}✗${NC} 容器啟動失敗"
    exit 1
fi

# 等待服務啟動
echo -e "\n${YELLOW}步驟 8: 等待服務就緒${NC}"
echo -e "──────────────────────────────────────────"

MAX_ATTEMPTS=30
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if docker exec $CONTAINER_NAME redis-cli ping 2>/dev/null | grep -q PONG; then
        echo -e "${GREEN}✓${NC} DragonflyDB 服務已就緒"
        break
    fi

    echo -e "${YELLOW}  等待服務啟動... ($ATTEMPT/$MAX_ATTEMPTS)${NC}"
    sleep 1
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
    echo -e "${RED}✗${NC} 服務啟動超時"
    echo -e "${YELLOW}  檢查容器日誌：${NC}"
    docker logs $CONTAINER_NAME --tail 20
    exit 1
fi

# 顯示服務信息
echo -e "\n${YELLOW}步驟 9: 服務信息${NC}"
echo -e "──────────────────────────────────────────"

# 獲取容器信息
CONTAINER_ID=$(docker ps -q -f name=$CONTAINER_NAME)
CONTAINER_STATUS=$(docker ps -f name=$CONTAINER_NAME --format "table {{.Status}}" | tail -n 1)

echo -e "${BLUE}📦 容器信息：${NC}"
echo -e "   • 容器 ID: ${GREEN}${CONTAINER_ID:0:12}${NC}"
echo -e "   • 狀態: ${GREEN}$CONTAINER_STATUS${NC}"

# 顯示版本信息
echo -e "\n${BLUE}🔧 DragonflyDB 版本信息：${NC}"
docker exec $CONTAINER_NAME redis-cli INFO server | grep -E "redis_version|uptime_in_seconds" | while IFS=: read -r key value; do
    echo -e "   • $key: ${GREEN}$value${NC}"
done

# 顯示資源使用
echo -e "\n${BLUE}📊 資源配置：${NC}"
docker exec $CONTAINER_NAME redis-cli CONFIG GET maxmemory | tail -n 1 | while read value; do
    echo -e "   • 最大記憶體: ${GREEN}$value${NC}"
done
echo -e "   • 執行緒數: ${GREEN}$DRAGONFLY_THREADS${NC}"

# 創建測試腳本
echo -e "\n${YELLOW}步驟 10: 創建連接測試${NC}"
echo -e "──────────────────────────────────────────"

cat > /tmp/test_connection.py << EOF
import redis
import sys

try:
    r = redis.Redis(host='localhost', port=$DRAGONFLY_PORT, decode_responses=True)
    r.ping()
    print("✅ Python 連接測試成功")

    # 簡單測試
    r.set('test_key', 'Hello DragonflyDB!')
    value = r.get('test_key')
    assert value == 'Hello DragonflyDB!'
    print("✅ 讀寫測試成功")

    r.delete('test_key')
    print("✅ 清理測試數據成功")

except Exception as e:
    print(f"❌ 測試失敗: {e}")
    sys.exit(1)
EOF

python3 /tmp/test_connection.py
rm /tmp/test_connection.py

# 顯示管理命令
echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    安裝完成！                            ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}🎯 常用管理命令：${NC}"
echo -e "${MAGENTA}查看狀態：${NC}"
echo -e "  ${GREEN}docker ps | grep $CONTAINER_NAME${NC}"
echo ""
echo -e "${MAGENTA}查看日誌：${NC}"
echo -e "  ${GREEN}docker logs $CONTAINER_NAME --tail 50${NC}"
echo ""
echo -e "${MAGENTA}進入容器：${NC}"
echo -e "  ${GREEN}docker exec -it $CONTAINER_NAME redis-cli${NC}"
echo ""
echo -e "${MAGENTA}停止服務：${NC}"
echo -e "  ${GREEN}docker stop $CONTAINER_NAME${NC}"
echo ""
echo -e "${MAGENTA}啟動服務：${NC}"
echo -e "  ${GREEN}docker start $CONTAINER_NAME${NC}"
echo ""
echo -e "${MAGENTA}重啟服務：${NC}"
echo -e "  ${GREEN}docker restart $CONTAINER_NAME${NC}"
echo ""
echo -e "${MAGENTA}查看統計：${NC}"
echo -e "  ${GREEN}docker exec $CONTAINER_NAME redis-cli INFO${NC}"
echo ""

echo -e "${BLUE}📝 連接信息：${NC}"
echo -e "  • 主機: ${GREEN}localhost${NC}"
echo -e "  • 端口: ${GREEN}$DRAGONFLY_PORT${NC}"
echo -e "  • Python 連接: ${GREEN}redis.Redis(host='localhost', port=$DRAGONFLY_PORT)${NC}"

echo -e "\n${GREEN}✨ DragonflyDB 已成功安裝並運行！${NC}"