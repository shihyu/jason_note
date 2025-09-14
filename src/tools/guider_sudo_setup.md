# Guider 免密碼執行設置指南

## 快速設置步驟

### 步驟 1：創建 sudoers 規則
```bash
# 創建 sudoers 規則檔案，允許你的用戶免密碼執行所有命令
echo "shihyu ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/guider
sudo chmod 0440 /etc/sudoers.d/guider
```

**說明**：
- `shihyu` - 你的用戶名
- `ALL=(ALL)` - 可以在任何主機上以任何用戶身份執行
- `NOPASSWD: ALL` - 執行所有命令都不需要密碼

### 步驟 2：創建 wrapper script
```bash
# 創建 wrapper script
cat > ~/.mybin/guider-sudo << 'EOF'
#!/bin/bash
# 設置 miniconda 環境變數
export PATH="/home/shihyu/miniconda3/bin:$PATH"
export PYTHONPATH="/home/shihyu/miniconda3/lib/python3.11/site-packages:$PYTHONPATH"
# 用 sudo 執行 guider，-E 保留環境變數
exec sudo -E /home/shihyu/miniconda3/bin/python -m guider "$@"
EOF

# 設置執行權限
chmod +x ~/.mybin/guider-sudo
```

**說明**：
- 設置正確的 Python 路徑（因為 sudo 會重置 PATH）
- 使用 `sudo -E` 保留環境變數
- 直接調用 python -m guider 確保找到模組
- `"$@"` 傳遞所有參數

### 步驟 3：使用
```bash
# 現在可以直接使用，不需要輸入密碼
guider-sudo printenv -g systemd

# 或任何其他 guider 命令
guider-sudo top
guider-sudo report
```

## 為什麼需要這樣設置？

### 問題
1. **guider 需要 root 權限** - 訪問系統級資源（如 systemd 環境變數）
2. **sudo 環境問題** - sudo 會重置 PATH，找不到 miniconda 的 python
3. **Python 模組路徑** - sudo 環境下找不到 guider 模組

### 解決方案
1. **sudoers 規則** - 讓 sudo 不需要密碼
2. **wrapper script** - 設置正確的環境變數
3. **直接調用 python** - 確保能找到 guider 模組

## 安全注意事項

⚠️ **警告**：`NOPASSWD: ALL` 允許執行所有命令而不需要密碼，有安全風險。

### 更安全的選項（如果只需要 guider）：
```bash
# 只允許特定的 python 命令
echo "shihyu ALL=(ALL) NOPASSWD: /home/shihyu/miniconda3/bin/python" | sudo tee /etc/sudoers.d/guider
sudo chmod 0440 /etc/sudoers.d/guider
```

## 驗證設置

```bash
# 檢查 sudoers 規則
sudo cat /etc/sudoers.d/guider

# 測試免密碼 sudo
sudo -n true && echo "免密碼成功" || echo "需要密碼"

# 測試 guider-sudo
guider-sudo --version
```

## 移除設置

如果要移除這些設置：
```bash
# 刪除 sudoers 規則
sudo rm /etc/sudoers.d/guider

# 刪除 wrapper script
rm ~/.mybin/guider-sudo
```