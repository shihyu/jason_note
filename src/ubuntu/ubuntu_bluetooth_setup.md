# 安裝圖形界面管理工具（如果還沒裝的話）
sudo apt install blueman# Ubuntu 藍牙設備設定指南

## 安裝必要套件

```bash
# 更新系統套件
sudo apt update && sudo apt upgrade

# 安裝基本藍牙支援
sudo apt install bluetooth bluez bluez-tools blueman

# 安裝除錯工具
sudo apt install bluez-hcidump

# 安裝藍牙開發庫
sudo apt install libbluetooth-dev
```

## 啟動藍牙服務

```bash
# 啟動並啟用藍牙服務
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# 檢查服務狀態
sudo systemctl status bluetooth
```

## 設定用戶權限

```bash
# 確保用戶在藍牙群組中
sudo usermod -a -G bluetooth $USER

# 檢查群組設定
groups $USER
```

## 基本操作指令

```bash
# 檢查藍牙適配器
bluetoothctl list
hciconfig

# 檢查已配對設備
bluetoothctl devices

# 進入藍牙控制模式
bluetoothctl
# 在 bluetoothctl 中可用指令：
# show - 顯示適配器信息
# devices - 列出設備
# info [MAC地址] - 查看設備詳細信息
# connect [MAC地址] - 連接設備
# disconnect [MAC地址] - 斷開設備
```

## Chrome 藍牙功能設定

### 啟用 Chrome 藍牙 API
1. 在 Chrome 位址欄輸入：
   ```
   chrome://flags
   ```

2. 搜尋並啟用以下功能：
   - `#enable-web-bluetooth` - 啟用 Web Bluetooth API
   - `#enable-experimental-web-platform-features` - 啟用實驗性網頁平台功能
   - `#bluetooth-web-api` - 啟用藍牙網頁 API

3. 重新啟動 Chrome 瀏覽器

### Chrome 開啟方法

### 方法一：終端機啟動
```bash
# 直接啟動 Chrome
google-chrome

# 或者使用 chromium
chromium-browser

# 在背景執行
google-chrome &
```

### 方法二：桌面環境
- 點擊應用程式選單
- 搜尋 "Chrome" 或 "Chromium"
- 點擊圖示開啟

### 方法三：快捷鍵（如果有設定）
- `Super + Space`（搜尋應用程式）
- 輸入 "chrome" 後按 Enter

## 疑難排解

如果藍牙設備連接有問題：

```bash
# 重新啟動藍牙服務
sudo systemctl restart bluetooth

# 重新載入藍牙模組
sudo modprobe -r bluetooth
sudo modprobe bluetooth
sudo modprobe btusb

# 檢查藍牙硬體
lsusb | grep -i bluetooth
hciconfig -a
```

## 注意事項

- 重新登入系統以確保群組權限生效
- 某些特殊功能設備可能需要額外的驅動程式
- 公司網路環境可能有安全限制，需要管理員權限設定
- 定期更新系統以獲得最新的藍牙驅動支援