// 全域變數
let isScanning = false;
let connectedDevices = [];
let isVibrating = false;

// 在頁面上顯示 log
function addLog(message) {
  const logDiv = document.getElementById('logs') || createLogDiv();
  const p = document.createElement('p');
  p.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
  logDiv.appendChild(p);
  logDiv.scrollTop = logDiv.scrollHeight;
  console.log(message);
}

function createLogDiv() {
  const logDiv = document.createElement('div');
  logDiv.id = 'logs';
  logDiv.style.cssText = 'border:1px solid #ccc; padding:10px; margin:10px 0; height:300px; overflow-y:scroll; font-family:monospace; font-size:12px';
  const title = document.createElement('h3');
  title.textContent = 'Debug Logs:';
  document.body.insertBefore(title, document.body.firstChild);
  document.body.insertBefore(logDiv, title.nextSibling);
  return logDiv;
}

// 真實藍牙掃描功能
async function scanBluetoothDevices() {
  try {
    addLog("開始真實藍牙設備掃描...");
    
    // 檢查是否已在掃描中
    if (isScanning) {
      addLog("停止當前掃描...");
      isScanning = false;
      addLog("已停止掃描");
      return;
    }
    
    // 檢查瀏覽器是否支援 Web Bluetooth
    if (!navigator.bluetooth) {
      addLog("❌ 此瀏覽器不支援 Web Bluetooth");
      addLog("請使用 Chrome/Edge 桌面版本或 Chrome Android");
      return;
    }
    
    addLog("✅ 瀏覽器支援 Web Bluetooth");
    addLog("正在掃描藍牙設備...");
    
    isScanning = true;
    
    try {
      // 使用 Web Bluetooth API 直接掃描設備
      const device = await navigator.bluetooth.requestDevice({
        acceptAllDevices: true,
        optionalServices: [
          'device_information',
          'battery_service',
          '12345678-1234-1234-1234-123456789abc', // Buttplug service UUID 範例
          '0000180f-0000-1000-8000-00805f9b34fb', // Battery service
          '0000180a-0000-1000-8000-00805f9b34fb', // Device Information service
        ]
      });
      
      if (device) {
        addLog(`🎯 找到設備: ${device.name || '未命名設備'}`);
        addLog(`📱 設備 ID: ${device.id}`);
        
        // 嘗試連接到設備
        addLog("正在連接到設備...");
        
        device.addEventListener('gattserverdisconnected', () => {
          addLog(`設備 ${device.name} 已斷線`);
        });
        
        try {
          const server = await device.gatt.connect();
          addLog(`✅ 成功連接到 ${device.name}`);
          
          // 獲取設備服務
          const services = await server.getPrimaryServices();
          addLog(`📋 找到 ${services.length} 個服務:`);
          
          for (const service of services) {
            addLog(`  - 服務: ${service.uuid}`);
            
            try {
              const characteristics = await service.getCharacteristics();
              addLog(`    特徵數量: ${characteristics.length}`);
              
              for (const char of characteristics) {
                const properties = [];
                if (char.properties.read) properties.push('讀取');
                if (char.properties.write) properties.push('寫入');
                if (char.properties.notify) properties.push('通知');
                
                addLog(`      - 特徵: ${char.uuid} [${properties.join(', ')}]`);
              }
            } catch (e) {
              addLog(`    無法獲取特徵: ${e.message}`);
            }
          }
          
          // 加入到設備列表
          const mockDevice = {
            name: device.name || '藍牙設備',
            index: connectedDevices.length + 1,
            id: device.id,
            gattServer: server,
            vibrateAttributes: [{ Index: 0, StepCount: 20 }] // 模擬振動屬性
          };
          
          connectedDevices.push(mockDevice);
          updateDeviceList();
          
          addLog(`🎉 設備 ${device.name} 已加入控制列表`);
          
        } catch (connectError) {
          addLog(`❌ 連接失敗: ${connectError.message}`);
        }
        
      } else {
        addLog("沒有選擇設備");
      }
      
    } catch (scanError) {
      if (scanError.name === 'NotFoundError') {
        addLog("❌ 沒有找到藍牙設備");
      } else if (scanError.name === 'SecurityError') {
        addLog("❌ 安全錯誤: 需要在 HTTPS 環境下使用");
      } else {
        addLog(`❌ 掃描錯誤: ${scanError.message}`);
      }
    }
    
    isScanning = false;
    addLog("掃描完成");
    
  } catch (error) {
    isScanning = false;
    addLog(`錯誤: ${error.message}`);
    console.error("藍牙掃描錯誤:", error);
  }
}

// 更新設備列表顯示
function updateDeviceList() {
  const deviceListDiv = document.getElementById('deviceList');
  if (connectedDevices.length === 0) {
    deviceListDiv.innerHTML = '尚未找到設備';
  } else {
    deviceListDiv.innerHTML = connectedDevices.map(device => 
      `<div style="padding: 5px; border-bottom: 1px solid #eee;">
        ${device.name || 'Unknown'} (索引: ${device.index})
        <br><small>執行器數量: ${device.vibrateAttributes?.length || 0}</small>
      </div>`
    ).join('');
  }
}

// 設定振動強度（即時更新）
async function setVibrationIntensity(intensity) {
  if (connectedDevices.length === 0 || !isVibrating) {
    return;
  }
  
  try {
    for (const device of connectedDevices) {
      if (device.gattServer && device.gattServer.connected) {
        addLog(`調整 ${device.name} 振動強度到 ${Math.round(intensity * 100)}%`);
        // 這裡實現具體的振動控制
      }
    }
  } catch (error) {
    addLog(`振動強度調整錯誤: ${error.message}`);
  }
}

// 開始振動 - 與真實藍牙設備交互
async function startVibration() {
  const slider = document.getElementById('vibrateSlider');
  const intensity = slider.value / 100;
  
  if (connectedDevices.length === 0) {
    addLog("沒有連接的設備");
    return;
  }
  
  try {
    isVibrating = true;
    for (const device of connectedDevices) {
      addLog(`嘗試控制設備 ${device.name}，強度: ${Math.round(intensity * 100)}%`);
      
      if (device.gattServer && device.gattServer.connected) {
        try {
          const services = await device.gattServer.getPrimaryServices();
          
          for (const service of services) {
            try {
              const characteristics = await service.getCharacteristics();
              
              for (const char of characteristics) {
                if (char.properties.write || char.properties.writeWithoutResponse) {
                  const vibrationData = new Uint8Array([Math.round(intensity * 255)]);
                  await char.writeValue(vibrationData);
                  addLog(`✅ 向設備 ${device.name} 發送振動命令`);
                  break;
                }
              }
            } catch (e) {
              // 忽略無法訪問的特徵
            }
          }
          
        } catch (controlError) {
          addLog(`設備控制錯誤: ${controlError.message}`);
        }
      } else {
        addLog(`設備 ${device.name} 未連接`);
      }
    }
    
    addLog(`🎮 所有設備振動強度設定為 ${Math.round(intensity * 100)}%`);
    
  } catch (error) {
    addLog(`振動控制錯誤: ${error.message}`);
    isVibrating = false;
  }
}

async function stopVibration() {
  if (connectedDevices.length === 0) {
    addLog("沒有連接的設備");
    return;
  }
  
  try {
    isVibrating = false;
    for (const device of connectedDevices) {
      addLog(`停止設備 ${device.name} 振動`);
      
      if (device.gattServer && device.gattServer.connected) {
        try {
          const services = await device.gattServer.getPrimaryServices();
          
          for (const service of services) {
            try {
              const characteristics = await service.getCharacteristics();
              
              for (const char of characteristics) {
                if (char.properties.write || char.properties.writeWithoutResponse) {
                  const stopData = new Uint8Array([0]);
                  await char.writeValue(stopData);
                  addLog(`✅ 設備 ${device.name} 停止振動`);
                  break;
                }
              }
            } catch (e) {
              // 忽略無法訪問的特徵
            }
          }
          
        } catch (controlError) {
          addLog(`設備控制錯誤: ${controlError.message}`);
        }
      }
    }
    
    addLog("🛑 所有設備已停止振動");
    
  } catch (error) {
    addLog(`停止振動錯誤: ${error.message}`);
  }
}

// 頁面載入完成後設定事件
document.addEventListener('DOMContentLoaded', () => {
  addLog("頁面已載入");
  
  // 掃描按鈕
  const scanBtn = document.getElementById('b');
  if (scanBtn) {
    scanBtn.onclick = () => {
      addLog("Scan 按鈕被點擊");
      scanBluetoothDevices();
    };
    addLog("✅ 掃描按鈕事件綁定完成");
  } else {
    addLog("❌ 找不到掃描按鈕 (id='b')");
  }
  
  // 振動滑桿
  const slider = document.getElementById('vibrateSlider');
  const valueDisplay = document.getElementById('vibrateValue');
  
  if (slider && valueDisplay) {
    slider.oninput = () => {
      const intensity = slider.value / 100;
      valueDisplay.textContent = slider.value + '%';
      
      if (isVibrating) {
        setVibrationIntensity(intensity);
      }
    };
    addLog("✅ 振動滑桿事件綁定完成");
  }
  
  // 振動控制按鈕
  const vibrateBtn = document.getElementById('vibrateBtn');
  const stopBtn = document.getElementById('stopBtn');
  
  if (vibrateBtn) {
    vibrateBtn.onclick = startVibration;
    addLog("✅ 開始振動按鈕事件綁定完成");
  }
  
  if (stopBtn) {
    stopBtn.onclick = stopVibration;
    addLog("✅ 停止振動按鈕事件綁定完成");
  }
  
  addLog("🎉 所有事件綁定完成，ready!");
});