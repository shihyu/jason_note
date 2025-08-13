# Buttplug Python 安裝設置指南

## 📦 安裝步驟

### 1. 安裝 Python 庫
```bash
pip install buttplug
```

### 2. 安裝 Intiface Desktop
- 下載：[https://intiface.com/desktop/](https://intiface.com/desktop/)
- 這是 Buttplug 的圖形界面服務器，負責與硬件設備通信

### 3. 設備準備
- 確保你的設備已充電並開機
- 將設備設置為配對模式（通常是長按電源鍵）

## 🔧 配置 Intiface Desktop

### 1. 啟動 Intiface Desktop
- 打開應用程序
- 點擊 "Start Server" 開始服務器

### 2. 設備配對
- 在 Intiface 中點擊 "Devices" 頁面
- 點擊 "Start Scanning" 掃描設備
- 當你的設備出現在列表中時，點擊連接

### 3. 服務器設置
- 默認端口：12345
- 默認地址：ws://localhost:12345
- 確保 "Server" 標籤顯示 "Running"

## 🚀 快速開始

### 最簡單的範例
```python
import asyncio
from buttplug.client import ButtplugClient, ButtplugClientWebsocketConnector

async def simple_example():
    client = ButtplugClient("測試應用")
    
    try:
        # 連接服務器
        connector = ButtplugClientWebsocketConnector("ws://localhost:12345")
        await client.connect(connector)
        print("已連接到服務器")
        
        # 掃描設備
        await client.start_scanning()
        await asyncio.sleep(5)  # 掃描5秒
        await client.stop_scanning()
        
        # 檢查設備
        if client.devices:
            device = client.devices[0]
            print(f"找到設備: {device.name}")
            
            # 振動測試
            await device.vibrate(0.5)  # 50%強度
            await asyncio.sleep(2)
            await device.stop()  # 停止
            
        else:
            print("未找到設備")
            
    except Exception as e:
        print(f"錯誤: {e}")
    finally:
        await client.disconnect()

# 運行範例
asyncio.run(simple_example())
```

## 🔍 常見問題排解

### Q: 連接失敗 "Connection refused"
**A:** 檢查 Intiface Desktop 是否運行：
- 打開 Intiface Desktop
- 確認 "Server" 狀態為 "Running"
- 檢查端口設置（默認12345）

### Q: 找不到設備
**A:** 設備配對問題：
1. 確保設備已開機且在配對模式
2. 在 Intiface Desktop 中先手動連接設備
3. 檢查設備是否被其他應用程序占用

### Q: 振動命令無效果
**A:** 設備兼容性問題：
1. 確認設備支持振動功能
2. 檢查設備電量是否充足
3. 嘗試在 Intiface Desktop 中手動測試設備

### Q: 權限錯誤（Linux/macOS）
**A:** 
```bash
# Linux: 添加用戶到 dialout 組
sudo usermod -a -G dialout $USER

# 重新登錄或重啟系統
```

## 📱 支持的設備品牌

Buttplug 支持多個主流品牌：

### 🔥 完全支持
- Lovense 系列
- WeVibe 系列  
- Kiiroo 系列
- Magic Motion 系列

### ⚡ 基本支持
- Satisfyer 部分型號
- LELO 部分型號
- Vorze 系列

### 📋 設備功能檢查
```python
async def check_device_features(device):
    print(f"設備名稱: {device.name}")
    
    # 檢查執行器類型
    if hasattr(device, 'actuators'):
        for actuator in device.actuators:
            print(f"執行器類型: {actuator.actuator_type.name}")
            print(f"步進數: {actuator.step_count}")
    
    # 檢查傳感器
    if hasattr(device, 'sensors'):
        for sensor in device.sensors:
            print(f"傳感器類型: {sensor.sensor_type.name}")
```

## 🛡️ 安全使用提醒

### 代碼安全
- 始終使用 `try-except` 捕獲異常
- 程序結束前務必調用 `device.stop()`
- 使用 `asyncio` 避免阻塞

### 硬件安全
- 設定強度上限（建議不超過0.8）
- 避免長時間高強度運行
- 定期檢查設備溫度

### 隱私安全
- 本地運行，不向外部服務器發送數據
- Buttplug 是開源項目，代碼可審查

## 🔧 進階配置

### 自定義服務器地址
```python
# 遠程服務器
connector = ButtplugClientWebsocketConnector("ws://192.168.1.100:12345")

# 不同端口
connector = ButtplugClientWebsocketConnector("ws://localhost:8080")
```

### 多客戶端處理
```python
async def multi_client_example():
    # 可以創建多個客戶端
    client1 = ButtplugClient("應用1")
    client2 = ButtplugClient("應用2")
    
    # 但同一時間只有一個可以控制設備
```

### 自定義事件處理
```python
@client.scanning_finished_handler
async def on_scan_finished():
    print("自定義掃描完成處理")

@client.device_added_handler  
async def on_device_added(device):
    print(f"自定義設備添加處理: {device.name}")
```

## 📚 相關資源

- **官方文檔**: https://buttplug-developer-guide.docs.buttplug.io/
- **Python API 文檔**: https://buttplug-py.docs.buttplug.io/
- **GitHub 倉庫**: https://github.com/buttplugio/buttplug-py
- **社群討論**: https://discord.buttplug.io/

## 🔄 版本兼容性

- **Python**: 3.7+
- **Buttplug Protocol**: v3.0+  
- **Intiface Desktop**: 最新版本

記得定期更新庫以獲得最佳兼容性：
```bash
pip install --upgrade buttplug
```