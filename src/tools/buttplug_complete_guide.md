# Buttplug Python 簡易指南

## 📦 安裝步驟

### 1. 安裝 Python 庫
```bash
pip install buttplug
```

### 2. 下載 Intiface Desktop
- 下載地址：[https://intiface.com/desktop/](https://intiface.com/desktop/)
- 安裝並啟動
- 點擊 "Start Server" 啟動服務器（默認端口：12345）

### 3. 設備配對
- 確保設備開機並進入配對模式
- 在 Intiface Desktop 的 "Devices" 頁面掃描並連接設備

---

## 🔧 功能說明

### 核心功能
- **統一控制**：一套 API 控制多種品牌設備
- **多種模式**：振動、旋轉、線性運動
- **安全機制**：強度限制、超時保護
- **實時控制**：低延遲設備響應

### 支持的設備類型
- **振動設備**：各種震動棒、跳蛋等
- **旋轉設備**：帶旋轉功能的設備
- **線性設備**：活塞運動類設備
- **感測設備**：可讀取電池、按鈕狀態等

---

## 📋 API 參考表格

### 客戶端連接 API

| 方法 | 描述 | 參數 | 返回值 |
|------|------|------|--------|
| `ButtplugClient(name)` | 創建客戶端 | `name`: 應用名稱 | 客戶端對象 |
| `client.connect(connector)` | 連接服務器 | `connector`: 連接器對象 | 無 |
| `client.disconnect()` | 斷開連接 | 無 | 無 |
| `client.start_scanning()` | 開始掃描設備 | 無 | 無 |
| `client.stop_scanning()` | 停止掃描設備 | 無 | 無 |
| `client.devices` | 獲取設備列表 | 無 | 設備列表 |
| `client.stop_all_devices()` | 停止所有設備 | 無 | 無 |

### 設備控制 API

| 方法 | 描述 | 參數示例 | 功能 |
|------|------|----------|------|
| `device.scalar(commands)` | 通用標量控制 | `[{"Index": 0, "Scalar": 0.5, "ActuatorType": "Vibrate"}]` | 振動控制 |
| `device.linear(commands)` | 線性運動控制 | `[{"Index": 0, "Position": 0.8, "Duration": 1000}]` | 活塞運動 |
| `device.rotate(commands)` | 旋轉控制 | `[{"Index": 0, "Speed": 0.5, "Clockwise": true}]` | 旋轉馬達 |
| `device.stop()` | 停止設備 | 無 | 停止所有動作 |
| `device.sensor_read(index)` | 讀取傳感器 | `index`: 傳感器索引 | 傳感器數據 |
| `device.sensor_subscribe(index)` | 訂閱傳感器 | `index`: 傳感器索引 | 無 |

### 設備屬性 API

| 屬性 | 描述 | 類型 | 示例值 |
|------|------|------|--------|
| `device.name` | 設備名稱 | 字符串 | `"Lovense Edge"` |
| `device.index` | 設備索引 | 整數 | `0` |
| `device.actuators` | 執行器列表 | 列表 | `[actuator1, actuator2]` |
| `device.sensors` | 傳感器列表 | 列表 | `[sensor1, sensor2]` |
| `actuator.actuator_type.name` | 執行器類型 | 字符串 | `"Vibrate"`, `"Rotate"` |
| `actuator.step_count` | 可用步數 | 整數 | `20` |

### 事件處理 API

| 事件處理器 | 觸發時機 | 參數 | 用途 |
|------------|----------|------|------|
| `@client.device_added_handler` | 設備連接時 | `device` | 處理新設備 |
| `@client.device_removed_handler` | 設備斷開時 | `device` | 處理設備斷開 |
| `@client.scanning_finished_handler` | 掃描完成時 | 無 | 掃描結束處理 |
| `@client.sensor_reading_handler` | 傳感器數據 | `device, index, data` | 處理傳感器數據 |

### ActuatorType 類型表

| 類型 | 說明 | 適用設備 | 強度範圍 |
|------|------|----------|----------|
| `"Vibrate"` | 振動控制 | 震動棒、跳蛋 | 0.0 - 1.0 |
| `"Rotate"` | 旋轉控制 | 旋轉類設備 | 0.0 - 1.0 |
| `"Oscillate"` | 震盪控制 | 愛撫機 | 0.0 - 1.0 |
| `"Constrict"` | 收縮控制 | 充氣類設備 | 0.0 - 1.0 |
| `"Inflate"` | 充氣控制 | 充氣類設備 | 0.0 - 1.0 |

### 連接器類型表

| 連接器 | 用途 | 參數示例 | 說明 |
|--------|------|----------|------|
| `ButtplugClientWebsocketConnector` | WebSocket連接 | `"ws://localhost:12345"` | 最常用，連接到 Intiface Desktop |
| `ButtplugEmbeddedConnector` | 嵌入式連接 | 無 | 直接在應用中運行服務器 |

---

## 🐍 Python 範例代碼

### 1. 基礎連接範例

```python
import asyncio
from buttplug.client import ButtplugClient, ButtplugClientWebsocketConnector

async def basic_example():
    # 創建客戶端
    client = ButtplugClient("我的應用")
    
    try:
        # 連接服務器
        connector = ButtplugClientWebsocketConnector("ws://localhost:12345")
        await client.connect(connector)
        print("✅ 已連接")
        
        # 掃描設備
        await client.start_scanning()
        await asyncio.sleep(3)  # 掃描3秒
        await client.stop_scanning()
        
        # 檢查設備
        if client.devices:
            device = client.devices[0]
            print(f"📱 設備: {device.name}")
            
            # 振動測試
            await device.scalar([{
                "Index": 0,
                "Scalar": 0.5,  # 50%強度
                "ActuatorType": "Vibrate"
            }])
            await asyncio.sleep(2)
            
            # 停止
            await device.stop()
        else:
            print("❌ 未找到設備")
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    finally:
        await client.disconnect()

# 運行
asyncio.run(basic_example())
```

### 2. 設備事件處理

```python
import asyncio
from buttplug.client import ButtplugClient, ButtplugClientWebsocketConnector

async def event_example():
    client = ButtplugClient("事件範例")
    
    # 設備連接事件
    @client.device_added_handler
    async def device_connected(device):
        print(f"🔗 設備已連接: {device.name}")
        
        # 自動測試新設備
        await device.scalar([{
            "Index": 0,
            "Scalar": 0.3,
            "ActuatorType": "Vibrate"
        }])
        await asyncio.sleep(1)
        await device.stop()
    
    # 設備斷開事件
    @client.device_removed_handler
    async def device_disconnected(device):
        print(f"🔌 設備已斷開: {device.name}")
    
    try:
        connector = ButtplugClientWebsocketConnector("ws://localhost:12345")
        await client.connect(connector)
        
        # 開始掃描
        await client.start_scanning()
        print("🔍 掃描中，請連接設備...")
        await asyncio.sleep(10)  # 等待10秒
        await client.stop_scanning()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    finally:
        await client.disconnect()

asyncio.run(event_example())
```

### 3. 設備控制類

```python
import asyncio
import math
from buttplug.client import ButtplugClient, ButtplugClientWebsocketConnector

class SimpleController:
    def __init__(self):
        self.client = None
        self.device = None
    
    async def connect(self):
        """連接並找到第一個振動設備"""
        self.client = ButtplugClient("簡單控制器")
        connector = ButtplugClientWebsocketConnector("ws://localhost:12345")
        await self.client.connect(connector)
        
        await self.client.start_scanning()
        await asyncio.sleep(3)
        await self.client.stop_scanning()
        
        # 找到第一個振動設備
        for device in self.client.devices:
            if hasattr(device, 'actuators') and device.actuators:
                for actuator in device.actuators:
                    if actuator.actuator_type.name == 'Vibrate':
                        self.device = device
                        print(f"✅ 使用設備: {device.name}")
                        return True
        
        print("❌ 未找到振動設備")
        return False
    
    async def vibrate(self, intensity: float):
        """設定振動強度 (0.0-1.0)"""
        if not self.device:
            return
        
        await self.device.scalar([{
            "Index": 0,
            "Scalar": min(intensity, 0.8),  # 安全限制
            "ActuatorType": "Vibrate"
        }])
    
    async def stop(self):
        """停止振動"""
        if self.device:
            await self.device.stop()
    
    async def pulse_pattern(self, count=5):
        """脈衝振動模式"""
        for i in range(count):
            await self.vibrate(0.7)
            await asyncio.sleep(0.3)
            await self.stop()
            await asyncio.sleep(0.3)
        print(f"✅ 脈衝模式完成 ({count}次)")
    
    async def wave_pattern(self, duration=10):
        """波浪振動模式"""
        start_time = asyncio.get_event_loop().time()
        step = 0
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            intensity = 0.4 + 0.3 * math.sin(step * 0.3)
            await self.vibrate(intensity)
            step += 1
            await asyncio.sleep(0.1)
        
        await self.stop()
        print(f"✅ 波浪模式完成 ({duration}秒)")
    
    async def escalate_pattern(self):
        """遞增振動模式"""
        intensities = [0.2, 0.4, 0.6, 0.8]
        
        for intensity in intensities:
            print(f"   強度: {int(intensity*100)}%")
            await self.vibrate(intensity)
            await asyncio.sleep(2)
        
        await self.stop()
        print("✅ 遞增模式完成")
    
    async def disconnect(self):
        """斷開連接"""
        if self.device:
            await self.stop()
        if self.client:
            await self.client.disconnect()

# 使用範例
async def main():
    controller = SimpleController()
    
    try:
        if await controller.connect():
            # 測試不同模式
            await controller.pulse_pattern(3)
            await asyncio.sleep(1)
            
            await controller.wave_pattern(5)
            await asyncio.sleep(1)
            
            await controller.escalate_pattern()
    
    finally:
        await controller.disconnect()

asyncio.run(main())
```

### 4. 多設備控制

```python
import asyncio
from buttplug.client import ButtplugClient, ButtplugClientWebsocketConnector

async def multi_device_example():
    client = ButtplugClient("多設備控制")
    
    try:
        connector = ButtplugClientWebsocketConnector("ws://localhost:12345")
        await client.connect(connector)
        
        await client.start_scanning()
        await asyncio.sleep(5)
        await client.stop_scanning()
        
        # 找到所有振動設備
        vibrating_devices = []
        for device in client.devices:
            if hasattr(device, 'actuators') and device.actuators:
                for actuator in device.actuators:
                    if actuator.actuator_type.name == 'Vibrate':
                        vibrating_devices.append(device)
                        break
        
        if len(vibrating_devices) < 2:
            print("❌ 需要至少2個振動設備")
            return
        
        print(f"👥 控制 {len(vibrating_devices)} 個設備")
        
        # 同步振動
        print("🔄 同步振動...")
        for device in vibrating_devices:
            await device.scalar([{
                "Index": 0,
                "Scalar": 0.6,
                "ActuatorType": "Vibrate"
            }])
        
        await asyncio.sleep(3)
        
        # 交替振動
        print("🔄 交替振動...")
        for i in range(6):
            # 停止所有設備
            for device in vibrating_devices:
                await device.stop()
            
            # 啟動當前設備
            current_device = vibrating_devices[i % len(vibrating_devices)]
            await current_device.scalar([{
                "Index": 0,
                "Scalar": 0.7,
                "ActuatorType": "Vibrate"
            }])
            print(f"   啟動: {current_device.name}")
            await asyncio.sleep(1)
        
        # 停止所有設備
        await client.stop_all_devices()
        print("✅ 多設備控制完成")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    finally:
        await client.disconnect()

asyncio.run(multi_device_example())
```

### 5. 設備信息查看

```python
import asyncio
from buttplug.client import ButtplugClient, ButtplugClientWebsocketConnector

async def device_info_example():
    client = ButtplugClient("設備信息")
    
    try:
        connector = ButtplugClientWebsocketConnector("ws://localhost:12345")
        await client.connect(connector)
        
        await client.start_scanning()
        await asyncio.sleep(3)
        await client.stop_scanning()
        
        if not client.devices:
            print("❌ 未找到設備")
            return
        
        print(f"📱 找到 {len(client.devices)} 個設備:")
        print("=" * 50)
        
        for i, device in enumerate(client.devices):
            print(f"\n設備 {i+1}: {device.name}")
            print(f"   索引: {device.index}")
            
            # 執行器信息
            if hasattr(device, 'actuators') and device.actuators:
                print(f"   執行器: {len(device.actuators)} 個")
                for j, actuator in enumerate(device.actuators):
                    print(f"     #{j}: {actuator.actuator_type.name} ({actuator.step_count} 步)")
            
            # 傳感器信息
            if hasattr(device, 'sensors') and device.sensors:
                print(f"   傳感器: {len(device.sensors)} 個")
                for j, sensor in enumerate(device.sensors):
                    print(f"     #{j}: {sensor.sensor_type.name}")
                    
                    # 嘗試讀取傳感器數據
                    try:
                        reading = await device.sensor_read(j)
                        print(f"         讀數: {reading}")
                    except Exception as e:
                        print(f"         讀取失敗: {e}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    finally:
        await client.disconnect()

asyncio.run(device_info_example())
```

### 6. 傳感器監控

```python
import asyncio
from buttplug.client import ButtplugClient, ButtplugClientWebsocketConnector

async def sensor_monitoring_example():
    client = ButtplugClient("傳感器監控")
    
    # 傳感器數據處理
    @client.sensor_reading_handler
    async def sensor_data(device, sensor_index, data):
        print(f"📊 {device.name} 傳感器 {sensor_index}: {data}")
        
        # 根據數據類型處理
        if hasattr(device, 'sensors') and sensor_index < len(device.sensors):
            sensor_type = device.sensors[sensor_index].sensor_type.name
            
            if sensor_type == "Battery" and data < 20:
                print(f"🔋 警告: {device.name} 電量低 ({data}%)")
            elif sensor_type == "Button" and data:
                print(f"🔘 {device.name} 按鈕被按下")
    
    try:
        connector = ButtplugClientWebsocketConnector("ws://localhost:12345")
        await client.connect(connector)
        
        await client.start_scanning()
        await asyncio.sleep(3)
        await client.stop_scanning()
        
        # 訂閱所有設備的傳感器
        for device in client.devices:
            if hasattr(device, 'sensors') and device.sensors:
                print(f"📡 訂閱 {device.name} 的傳感器...")
                for i, sensor in enumerate(device.sensors):
                    try:
                        await device.sensor_subscribe(i)
                        print(f"   ✅ 傳感器 {i}: {sensor.sensor_type.name}")
                    except Exception as e:
                        print(f"   ❌ 訂閱失敗: {e}")
        
        # 監控30秒
        print("🕐 監控30秒...")
        await asyncio.sleep(30)
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    finally:
        await client.disconnect()

asyncio.run(sensor_monitoring_example())
```

---

## 🔧 快速參考

### 常用代碼片段

```python
# 快速連接
client = ButtplugClient("應用名")
connector = ButtplugClientWebsocketConnector("ws://localhost:12345")
await client.connect(connector)

# 掃描設備
await client.start_scanning()
await asyncio.sleep(3)
await client.stop_scanning()

# 振動控制
await device.scalar([{"Index": 0, "Scalar": 0.5, "ActuatorType": "Vibrate"}])

# 停止設備
await device.stop()

# 斷開連接
await client.disconnect()
```

### 安全提醒

- 建議最大強度不超過 0.8
- 使用 try-except 處理異常
- 程序結束前務必調用 disconnect()
- 定期檢查設備電量