# Guider 權限設置與配置完整指南

## 目錄
- [問題描述](#問題描述)
- [錯誤訊息分析](#錯誤訊息分析)
- [解決方案](#解決方案)
- [使用範例](#使用範例)
- [進階設置](#進階設置)
- [故障排除](#故障排除)
- [常見問題 FAQ](#常見問題-faq)

## 問題描述

在 Ubuntu/Linux 系統上使用 `guider` 性能監控工具時，遇到以下問題：
- 需要 root 權限才能執行
- 每次都要輸入 sudo 密碼很麻煩
- 命令路徑太長不方便使用
- Python 環境問題導致模組找不到

## 錯誤訊息分析

### 錯誤 1：權限不足
```
[ERROR] failed to get root permission
```
**原因**：guider 需要 root 權限來訪問系統資源

### 錯誤 2：命令找不到
```
sudo: guider：找不到指令
```
**原因**：guider 不在系統 PATH 中

### 錯誤 3：Python 模組找不到
```
/usr/bin/python3: No module named guider
[Error] failed to find Guider module in python3
```
**原因**：使用 sudo 時調用了系統 Python 而非 miniconda Python

## 解決方案

### 步驟 1：設置 sudo 免密碼權限

```bash
# 允許執行 guider 及其所有子命令
echo "shihyu ALL=(ALL) NOPASSWD: /home/shihyu/miniconda3/bin/python -m guider *" | sudo tee /etc/sudoers.d/guider

# 設置正確的文件權限（重要！）
sudo chmod 0440 /etc/sudoers.d/guider

# 驗證設置
cat /etc/sudoers.d/guider
ls -l /etc/sudoers.d/guider
```

### 步驟 2：創建命令別名 (alias)

#### 選項 A：Bash 用戶
```bash
# 添加 alias 到 .bashrc
echo 'alias guider="sudo /home/shihyu/miniconda3/bin/python -m guider"' >> ~/.bashrc

# 重新載入配置
source ~/.bashrc
```

#### 選項 B：Zsh 用戶
```bash
# 添加 alias 到 .zshrc
echo 'alias guider="sudo /home/shihyu/miniconda3/bin/python -m guider"' >> ~/.zshrc

# 重新載入配置
source ~/.zshrc
```

#### 選項 C：Fish Shell 用戶
```bash
# 添加 alias 到 config.fish
echo 'alias guider="sudo /home/shihyu/miniconda3/bin/python -m guider"' >> ~/.config/fish/config.fish

# 重新載入配置
source ~/.config/fish/config.fish
```

### 步驟 3：清理舊進程並測試

```bash
# 查看是否有停止的 guider 進程
ps aux | grep guider

# 清理之前停止的 guider 進程
pkill -f guider

# 測試新設置
guider --version
guider ftop -g nginx
```

## 使用範例

### 基本命令
```bash
# 查看版本信息
guider --version

# 顯示幫助
guider --help

# 顯示系統整體狀態
guider top
```

### 進程監控
```bash
# 監控特定進程（如 nginx）
guider ftop -g nginx

# 監控所有進程
guider ftop -g all

# 監控特定 PID
guider ftop -p 1234

# 監控多個進程
guider ftop -g "nginx|mysql|redis"
```

### 性能記錄與分析
```bash
# 開始記錄系統活動
guider rec -s

# 停止記錄
guider rec -e

# 分析記錄文件
guider rep -i /tmp/guider.dat

# 記錄指定時長（秒）
guider rec -s 60
```

### 系統資源監控
```bash
# CPU 使用率監控
guider top -o cpu

# 內存使用監控
guider top -o mem

# I/O 監控
guider top -o io

# 網絡監控
guider top -o net
```

## 進階設置

### 創建更多便捷 alias

```bash
# 編輯配置文件
vim ~/.bashrc  # 或 ~/.zshrc

# 添加以下 alias
alias gtop="sudo /home/shihyu/miniconda3/bin/python -m guider top"
alias gftop="sudo /home/shihyu/miniconda3/bin/python -m guider ftop"
alias grec="sudo /home/shihyu/miniconda3/bin/python -m guider rec"
alias grep="sudo /home/shihyu/miniconda3/bin/python -m guider rep"
alias gnginx="sudo /home/shihyu/miniconda3/bin/python -m guider ftop -g nginx"
alias gmysql="sudo /home/shihyu/miniconda3/bin/python -m guider ftop -g mysql"
alias gredis="sudo /home/shihyu/miniconda3/bin/python -m guider ftop -g redis"

# 重新載入配置
source ~/.bashrc  # 或 ~/.zshrc
```

### 創建全局命令（所有用戶可用）

```bash
# 創建包裝腳本
sudo tee /usr/local/bin/guider << 'EOF'
#!/bin/bash
exec sudo /home/shihyu/miniconda3/bin/python -m guider "$@"
EOF

# 設置執行權限
sudo chmod +x /usr/local/bin/guider

# 現在所有用戶都可以使用
guider ftop -g nginx
```

### 設置環境變數（替代方案）

```bash
# 添加到 .bashrc 或 .zshrc
export GUIDER_HOME=/home/shihyu/miniconda3
export PATH=$GUIDER_HOME/bin:$PATH

# 創建執行腳本
cat > ~/bin/guider << 'EOF'
#!/bin/bash
exec sudo $GUIDER_HOME/bin/python -m guider "$@"
EOF
chmod +x ~/bin/guider
```

## 故障排除

### 問題 1：仍然提示輸入密碼

**檢查步驟：**
```bash
# 1. 確認 sudoers 文件存在且內容正確
sudo cat /etc/sudoers.d/guider

# 2. 確認文件權限為 0440
ls -l /etc/sudoers.d/guider

# 3. 測試 sudo 規則
sudo -l | grep guider

# 4. 檢查語法錯誤
sudo visudo -c
```

### 問題 2：Python 模組仍然找不到

**解決方法：**
```bash
# 確認 guider 已安裝
/home/shihyu/miniconda3/bin/python -c "import guider; print(guider.__version__)"

# 如果未安裝，重新安裝
/home/shihyu/miniconda3/bin/pip install guider

# 或使用 conda 安裝
conda activate base
pip install guider
```

### 問題 3：進程顯示為 stopped 狀態

**解決步驟：**
```bash
# 1. 強制終止所有 guider 進程
sudo pkill -9 -f guider

# 2. 清理臨時文件
rm -f /tmp/guider.*

# 3. 重新啟動
guider ftop -g nginx
```

### 問題 4：權限錯誤 "Operation not permitted"

**可能原因與解決：**
```bash
# 1. SELinux 或 AppArmor 限制
# 檢查 SELinux 狀態
getenforce

# 臨時禁用（測試用）
sudo setenforce 0

# 2. 系統限制
# 檢查系統限制
ulimit -a

# 調整限制
ulimit -n 65536
```

## 驗證安裝

### 完整驗證腳本
```bash
#!/bin/bash
echo "=== Guider 設置驗證 ==="

# 1. 檢查 sudoers 設置
echo "1. Sudoers 設置："
if [ -f /etc/sudoers.d/guider ]; then
    echo "   ✓ 文件存在"
    sudo cat /etc/sudoers.d/guider
else
    echo "   ✗ 文件不存在"
fi

# 2. 檢查 alias 設置
echo "2. Alias 設置："
alias | grep guider && echo "   ✓ Alias 已設置" || echo "   ✗ Alias 未設置"

# 3. 檢查 Python 環境
echo "3. Python 環境："
/home/shihyu/miniconda3/bin/python --version

# 4. 檢查 guider 模組
echo "4. Guider 模組："
/home/shihyu/miniconda3/bin/python -c "import guider; print('   ✓ Guider version:', guider.__version__)" 2>/dev/null || echo "   ✗ Guider 未安裝"

# 5. 測試執行
echo "5. 測試執行："
guider --version && echo "   ✓ 可以執行" || echo "   ✗ 無法執行"
```

## 常見問題 FAQ

### Q1: 為什麼需要 root 權限？
**A:** Guider 需要訪問系統底層資源，包括：
- 進程詳細信息 (/proc/*)
- 性能計數器
- 網絡統計
- I/O 統計

### Q2: 可以不用 sudo 執行嗎？
**A:** 部分功能可以，但會有限制：
```bash
# 設置 capabilities（部分功能）
sudo setcap cap_sys_ptrace,cap_dac_read_search,cap_net_admin+ep /home/shihyu/miniconda3/bin/python
```

### Q3: 如何更新 guider？
```bash
# 使用 pip 更新
/home/shihyu/miniconda3/bin/pip install --upgrade guider

# 或使用 conda
conda activate base
pip install --upgrade guider
```

### Q4: 如何完全卸載設置？
```bash
# 1. 刪除 sudoers 規則
sudo rm /etc/sudoers.d/guider

# 2. 刪除 alias（編輯配置文件）
vim ~/.bashrc  # 刪除 guider 相關 alias

# 3. 刪除全局腳本（如果有）
sudo rm /usr/local/bin/guider

# 4. 卸載 guider
/home/shihyu/miniconda3/bin/pip uninstall guider
```

### Q5: 支援哪些 Linux 發行版？
- Ubuntu 18.04+
- Debian 9+
- CentOS 7+
- RHEL 7+
- Fedora 30+
- openSUSE Leap 15+

## 快速設置腳本

將以下內容保存為 `setup_guider.sh`：

```bash
#!/bin/bash
# Guider 快速設置腳本

PYTHON_PATH="/home/shihyu/miniconda3/bin/python"
USER_NAME="shihyu"

echo "開始設置 Guider..."

# 1. 設置 sudoers
echo "${USER_NAME} ALL=(ALL) NOPASSWD: ${PYTHON_PATH} -m guider *" | sudo tee /etc/sudoers.d/guider
sudo chmod 0440 /etc/sudoers.d/guider

# 2. 檢測 shell 並添加 alias
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

# 3. 添加 alias
echo "alias guider='sudo ${PYTHON_PATH} -m guider'" >> $SHELL_RC

# 4. 清理舊進程
pkill -f guider 2>/dev/null

echo "設置完成！請執行以下命令使設置生效："
echo "source $SHELL_RC"
echo ""
echo "然後可以使用: guider ftop -g nginx"
```

## 相關資源

- [Guider GitHub Repository](https://github.com/iipeace/guider)
- [Guider Documentation](https://github.com/iipeace/guider/wiki)
- [Performance Monitoring Best Practices](https://www.kernel.org/doc/html/latest/admin-guide/perf-security.html)

## 更新日誌

- **2024-12-28**: 初始版本，包含基本設置步驟
- **2024-12-28**: 添加故障排除章節和 FAQ
- **2024-12-28**: 添加快速設置腳本

---

**作者**: shihyu  
**最後更新**: 2024-12-28  
**版本**: 1.0.0