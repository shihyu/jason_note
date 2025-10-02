#!/bin/bash

# Docker 安裝腳本 for Ubuntu
# 支援 Ubuntu 20.04, 22.04, 24.04 等版本

set -e  # 遇到錯誤立即停止

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 顯示訊息函數
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 檢查是否為 root 或使用 sudo
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        # 檢查是否設定了 SUDO_PASSWORD 環境變數
        if [ -n "$SUDO_PASSWORD" ]; then
            print_message "使用 SUDO_PASSWORD 環境變數執行..."
            echo "$SUDO_PASSWORD" | sudo -S bash "$0" "$@"
            exit $?
        else
            # 提示使用者輸入密碼
            print_message "需要 sudo 權限，請輸入密碼："
            sudo bash "$0" "$@"
            exit $?
        fi
    fi
}

# 檢查 Ubuntu 版本
check_ubuntu_version() {
    print_message "檢查 Ubuntu 版本..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        print_message "檢測到 $NAME $VERSION"
        if [[ ! "$ID" == "ubuntu" ]]; then
            print_warning "此腳本是為 Ubuntu 設計的，在其他發行版上可能無法正常工作"
            read -p "是否要繼續？(y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    else
        print_error "無法檢測作業系統版本"
        exit 1
    fi
}

# 移除舊版本 Docker
remove_old_docker() {
    print_message "移除舊版本 Docker (如果存在)..."
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    apt-get autoremove -y
}

# 更新套件索引
update_packages() {
    print_message "更新套件索引..."
    apt-get update
}

# 安裝必要的套件
install_prerequisites() {
    print_message "安裝必要的套件..."
    apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        software-properties-common
}

# 新增 Docker 官方 GPG 金鑰
add_docker_gpg_key() {
    print_message "新增 Docker 官方 GPG 金鑰..."
    
    # 建立 keyrings 目錄（如果不存在）
    install -m 0755 -d /etc/apt/keyrings
    
    # 下載並新增 GPG 金鑰
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
}

# 設定 Docker 儲存庫
setup_docker_repository() {
    print_message "設定 Docker 儲存庫..."
    
    # 新增 Docker 儲存庫
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 更新套件索引
    apt-get update
}

# 安裝 Docker Engine
install_docker() {
    print_message "安裝 Docker Engine..."
    
    # 安裝最新版本的 Docker
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    print_message "Docker 安裝完成！"
}

# 設定 Docker 服務
configure_docker_service() {
    print_message "設定 Docker 服務..."
    
    # 啟動 Docker 服務
    systemctl start docker
    
    # 設定開機自動啟動
    systemctl enable docker
    
    print_message "Docker 服務已啟動並設定為開機自動啟動"
}

# 將使用者加入 docker 群組
add_user_to_docker_group() {
    local ACTUAL_USER="${SUDO_USER:-$USER}"
    
    if [ "$ACTUAL_USER" != "root" ]; then
        print_message "將使用者 '$ACTUAL_USER' 加入 docker 群組..."
        usermod -aG docker "$ACTUAL_USER"
        print_warning "請登出並重新登入，或執行 'newgrp docker' 以使群組變更生效"
    fi
}

# 設定 Docker daemon (選擇性配置)
configure_docker_daemon() {
    print_message "設定 Docker daemon..."
    
    # 建立 Docker 設定目錄
    mkdir -p /etc/docker
    
    # 建立 daemon.json 配置檔案
    cat > /etc/docker/daemon.json <<EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    },
    "storage-driver": "overlay2",
    "live-restore": true,
    "default-address-pools": [
        {
            "base": "172.16.0.0/12",
            "size": 24
        }
    ]
}
EOF
    
    # 重新載入 daemon 設定
    systemctl daemon-reload
    systemctl restart docker
    
    print_message "Docker daemon 設定完成"
}

# 驗證安裝
verify_installation() {
    print_message "驗證 Docker 安裝..."
    
    # 檢查 Docker 版本
    echo -e "\n${GREEN}Docker 版本資訊:${NC}"
    docker version
    
    # 執行測試容器
    print_message "執行 hello-world 測試容器..."
    if docker run --rm hello-world; then
        print_message "Docker 安裝驗證成功！"
    else
        print_error "Docker 測試失敗，請檢查安裝"
        exit 1
    fi
}

# 顯示安裝摘要
show_summary() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}       Docker 安裝完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo
    echo "已安裝的元件："
    echo "  ✓ Docker CE"
    echo "  ✓ Docker CLI"
    echo "  ✓ containerd.io"
    echo "  ✓ Docker Compose Plugin"
    echo "  ✓ Docker Buildx Plugin"
    echo
    echo "常用指令："
    echo "  docker version          # 查看 Docker 版本"
    echo "  docker ps              # 查看執行中的容器"
    echo "  docker images          # 查看映像檔"
    echo "  docker compose version  # 查看 Docker Compose 版本"
    echo "  systemctl status docker # 查看 Docker 服務狀態"
    echo
    
    local ACTUAL_USER="${SUDO_USER:-$USER}"
    if [ "$ACTUAL_USER" != "root" ]; then
        echo -e "${YELLOW}注意：${NC}"
        echo "  使用者 '$ACTUAL_USER' 已加入 docker 群組"
        echo "  請執行以下命令以使群組變更生效："
        echo "    newgrp docker"
        echo "  或登出並重新登入"
    fi
}

# 主函數
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}     Ubuntu Docker 安裝腳本${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo
    
    # 執行安裝步驟
    check_sudo
    check_ubuntu_version
    
    print_message "開始安裝 Docker..."
    
    remove_old_docker
    update_packages
    install_prerequisites
    add_docker_gpg_key
    setup_docker_repository
    install_docker
    configure_docker_service
    configure_docker_daemon
    add_user_to_docker_group
    verify_installation
    show_summary
    
    print_message "安裝程序完成！"
}

# 錯誤處理
trap 'print_error "安裝過程中發生錯誤！"; exit 1' ERR

# 執行主函數
main "$@"