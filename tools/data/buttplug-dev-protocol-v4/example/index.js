// 全域變數
let isScanning = false;
let connectedDevices = [];
let isVibrating = false;
let globalClient = null;

// 異步載入 Buttplug 模組
async function loadButtplugModule() {
  try {
    addLog("正在載入 Buttplug 模組...");
    const { ButtplugClient } = await import("buttplug");
    addLog("✅ Buttplug 模組載入成功");
    return { ButtplugClient };
  } catch (error) {
    addLog(`❌ Buttplug 模組載入失敗: ${error.message}`);
    return null;
  }
}

// 在頁面上顯示 log
function addLog(message) {
  const logDiv = document.getElementById('logs') || createLogDiv();
  const p = document.createElement('p');
  p.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
  logDiv.appendChild(p);
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

// 使用 Buttplug 進行真實設備掃描和控制
async function scanBluetoothDevices() {
  try {
    addLog("開始 Buttplug 設備掃描...");
    
    // 檢查是否已在掃描中
    if (isScanning) {
      addLog("停止當前掃描...");
      if (globalClient) {
        try {
          await globalClient.stopScanning();
          await globalClient.disconnect();
        } catch (e) {
          addLog(`停止掃描時出錯: ${e.message}`);
        }
        globalClient = null;
      }
      isScanning = false;
      addLog("已停止掃描");
      return;
    }
    
    // 載入 Buttplug 模組
    const buttplugModule = await loadButtplugModule();
    if (!buttplugModule) {
      return;
    }
    
    addLog("創建 Buttplug 客戶端...");
    globalClient = new buttplugModule.ButtplugClient("ERICA Client");
    
    // 監聽設備事件
    globalClient.addListener('deviceadded', (device) => {
      addLog(`🎯 找到設備: ${device.name || 'Unknown'} (索引: ${device.index})`);
      addLog(`   執行器數量: ${device.vibrateAttributes?.length || 0}`);
      
      // 加入到設備列表
      const buttplugDevice = {
        name: device.name || '未知設備',
        index: device.index,
        buttplugDevice: device, // 保存原始 Buttplug 設備物件
        vibrateAttributes: device.vibrateAttributes || []
      };
      
      connectedDevices.push(buttplugDevice);
      updateDeviceList();
      
      addLog(`🎉 設備 ${device.name} 已加入控制列表`);
    });
    
    addLog("開始掃描設備...");
    isScanning = true;
    await globalClient.startScanning();
    
    // 自動停止掃描（10秒後）
    setTimeout(async () => {
      if (isScanning && globalClient) {
        addLog("自動停止掃描...");
        try {
          await globalClient.stopScanning();
          isScanning = false;
          addLog("掃描已停止");
        } catch (e) {
          addLog(`停止掃描出錯: ${e.message}`);
        }
      }
    }, 10000);
    
    addLog("掃描中... (10秒後自動停止)");
    
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

// ERICA 設備專用協議測試函數
async function testERICAProtocols() {
  if (connectedDevices.length === 0) {
    addLog("沒有連接的設備");
    return;
  }
  
  const device = connectedDevices[0]; // 假設是 ERICA
  if (!device.gattServer || !device.gattServer.connected) {
    addLog("設備未連接");
    return;
  }
  
  addLog("🧪 開始 ERICA 設備協議測試...");
  
  // 找到寫入特徵
  const targetService = '0000ffe0-0000-1000-8000-00805f9b34fb';
  const targetChar = '0000ffe1-0000-1000-8000-00805f9b34fb';
  
  try {
    const service = await device.gattServer.getPrimaryService(targetService);
    const characteristic = await service.getCharacteristic(targetChar);
    
    const testProtocols = [
      { name: "單字節強度 (0-255)", data: [69] }, // 約27%強度
      { name: "雙字節命令+強度", data: [0x01, 69] },
      { name: "振動器協議 0xAA", data: [0xAA, 69] },
      { name: "振動器協議 0x55", data: [0x55, 69] },
      { name: "Lovense風格", data: [0x43, 0x01, 14] },
      { name: "百分比協議", data: [27] },
      { name: "反向協議", data: [69, 0x01] },
      { name: "三字節協議", data: [0xFF, 0x01, 69] },
      { name: "ASCII V協議", data: Array.from(new TextEncoder().encode("V27")) },
      { name: "魔法字節協議", data: [0xF0, 0xF0, 69] },
    ];
    
    for (let i = 0; i < testProtocols.length; i++) {
      const protocol = testProtocols[i];
      addLog(`🔬 測試協議 ${i+1}: ${protocol.name}`);
      
      try {
        await characteristic.writeValue(new Uint8Array(protocol.data));
        addLog(`✅ 發送成功: [${protocol.data.join(', ')}]`);
        addLog(`⏱️ 測試 3 秒... 請檢查設備是否振動`);
        
        // 等待 3 秒讓用戶感受振動
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // 發送停止命令
        await characteristic.writeValue(new Uint8Array([0]));
        addLog(`⏹️ 發送停止命令`);
        
        // 等待 1 秒間隔
        await new Promise(resolve => setTimeout(resolve, 1000));
        
      } catch (error) {
        addLog(`❌ 協議 ${i+1} 錯誤: ${error.message}`);
      }
    }
    
    addLog("🏁 協議測試完成！如果某個協議有效果，請記住編號。");
    
  } catch (error) {
    addLog(`協議測試失敗: ${error.message}`);
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
          // 檢查設備是否有可寫入的特徵
          if (!device.hasWriteCharacteristic) {
            addLog(`⚠️ 設備 ${device.name} 沒有可寫入的特徵，嘗試通用振動協議`);
          }
          
          let vibrateCommandSent = false;
          
          // 使用保存的服務信息
          const services = device.services || await device.gattServer.getPrimaryServices();
          
          for (const service of services) {
            try {
              const characteristics = await service.getCharacteristics();
              
              for (const char of characteristics) {
                if (char.properties.write || char.properties.writeWithoutResponse) {
                  try {
                    // 針對 ERICA 設備的特定協議測試
                    const protocols = [
                      // 協議 1: 單字節強度值 (0-255) - 原有的
                      new Uint8Array([Math.round(intensity * 255)]),
                      // 協議 2: 雙字節，第一字節是命令，第二字節是強度
                      new Uint8Array([0x01, Math.round(intensity * 255)]),
                      // 協議 3: 常見的振動器協議 (0xAA + 強度)
                      new Uint8Array([0xAA, Math.round(intensity * 255)]),
                      // 協議 4: 另一種常見協議 (0x55 + 強度)
                      new Uint8Array([0x55, Math.round(intensity * 255)]),
                      // 協議 5: Lovense 風格協議
                      new Uint8Array([0x43, 0x01, Math.round(intensity * 20)]), // 'C' + command + level
                      // 協議 6: 百分比協議 (0-100)
                      new Uint8Array([Math.round(intensity * 100)]),
                      // 協議 7: 雙字節反向 (強度 + 命令)
                      new Uint8Array([Math.round(intensity * 255), 0x01]),
                      // 協議 8: 三字節協議 (頭 + 命令 + 強度)
                      new Uint8Array([0xFF, 0x01, Math.round(intensity * 255)]),
                      // 協議 9: ASCII 'V' + 數字字符串
                      new TextEncoder().encode(`V${Math.round(intensity * 100)}`),
                      // 協議 10: 魔法字節 + 強度
                      new Uint8Array([0xF0, 0xF0, Math.round(intensity * 255)]),
                    ];
                    
                    for (let i = 0; i < protocols.length; i++) {
                      const protocol = protocols[i];
                      try {
                        await char.writeValue(protocol);
                        addLog(`✅ 協議 ${i+1}: 向設備 ${device.name} 發送 [${Array.from(protocol).join(', ')}]`);
                        vibrateCommandSent = true;
                        
                        // 只使用第一個成功的協議，不再嘗試其他的
                        break;
                      } catch (writeError) {
                        addLog(`❌ 協議 ${i+1} 失敗: ${writeError.message}`);
                      }
                    }
                    
                    if (vibrateCommandSent) break;
                  } catch (charError) {
                    addLog(`特徵寫入錯誤: ${charError.message}`);
                  }
                }
              }
              if (vibrateCommandSent) break;
            } catch (e) {
              // 忽略無法訪問的特徵
            }
          }
          
          if (!vibrateCommandSent) {
            addLog(`❌ 無法向設備 ${device.name} 發送振動命令 - 沒有找到可用的寫入特徵`);
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
          let stopCommandSent = false;
          
          // 使用保存的服務信息
          const services = device.services || await device.gattServer.getPrimaryServices();
          
          for (const service of services) {
            try {
              const characteristics = await service.getCharacteristics();
              
              for (const char of characteristics) {
                if (char.properties.write || char.properties.writeWithoutResponse) {
                  try {
                    // 嘗試多種停止協議
                    const stopProtocols = [
                      new Uint8Array([0]), // 協議 1: 零值
                      new Uint8Array([0x00, 0x00]), // 協議 2: 雙零
                      new Uint8Array([0x01, 0x00]), // 協議 3: 命令+零強度
                      new Uint8Array([0xFF, 0x00]), // 協議 4: 開關+零強度
                      new Uint8Array([0x56, 0x00]), // 協議 5: 'V' + 零
                    ];
                    
                    for (const protocol of stopProtocols) {
                      try {
                        await char.writeValue(protocol);
                        addLog(`✅ 設備 ${device.name} 停止振動 [${Array.from(protocol).join(', ')}]`);
                        stopCommandSent = true;
                        break;
                      } catch (writeError) {
                        // 嘗試下一個協議
                      }
                    }
                    
                    if (stopCommandSent) break;
                  } catch (charError) {
                    // 忽略無法訪問的特徵
                  }
                }
              }
              if (stopCommandSent) break;
            } catch (e) {
              // 忽略無法訪問的特徵
            }
          }
          
          if (!stopCommandSent) {
            addLog(`❌ 無法向設備 ${device.name} 發送停止命令`);
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

// 確保頁面和模組都載入完成後設定事件
function initializeApp() {
  addLog("開始初始化應用程序");
  
  // 等待一小段時間確保 DOM 完全載入
  setTimeout(() => {
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
  
  // 創建協議測試按鈕
  const testBtn = document.createElement('button');
  testBtn.textContent = '測試 ERICA 協議';
  testBtn.style.cssText = 'margin: 10px; padding: 10px; background: #ff6b6b; color: white; border: none; border-radius: 5px; cursor: pointer;';
  testBtn.onclick = testERICAProtocols;
  
  // 插入到振動控制區域
  const existingVibrateBtn = document.getElementById('vibrateBtn');
  if (existingVibrateBtn && existingVibrateBtn.parentNode) {
    existingVibrateBtn.parentNode.insertBefore(testBtn, existingVibrateBtn);
    addLog("✅ 協議測試按鈕已添加");
  }
  
    addLog("🎉 所有事件綁定完成，ready!");
  }, 100); // 等待 100ms 確保 DOM 完全載入
}

// 多種方式確保初始化執行
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeApp);
} else {
  initializeApp();
}

// 也監聽 window.onload 作為備選
window.addEventListener('load', () => {
  // 如果還沒有初始化（沒有看到初始化日誌），則強制初始化
  const logs = document.getElementById('logs');
  if (!logs || logs.children.length === 0) {
    addLog("備選初始化觸發");
    initializeApp();
  }
});
