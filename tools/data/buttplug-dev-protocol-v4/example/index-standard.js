// 標準 Buttplug 實現 - 參考工作程式
try {
  const wasmModule = await import("@wasm");
  console.log("WASM 模組載入成功:", wasmModule);
  var ButtplugWasmClientConnector = wasmModule.ButtplugWasmClientConnector;
} catch (error) {
  console.error("WASM 模組載入失敗:", error);
}

try {
  const buttplugModule = await import("@buttplug");
  console.log("Buttplug 模組載入成功:", buttplugModule);
  var ButtplugClient = buttplugModule.ButtplugClient;
} catch (error) {
  console.error("Buttplug 模組載入失敗:", error);
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

// 全域變數來追蹤狀態
let globalClient = null;
let isScanning = false;
let connectedDevices = [];
let isVibrating = false;

async function test_buttplug_standard() {
  try {
    addLog("開始標準 Buttplug 測試...");
    
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
      connectedDevices = [];
      updateDeviceList();
      addLog("已停止掃描");
      return;
    }
    
    addLog("創建 ButtplugClient...");
    globalClient = new ButtplugClient("ERICA Standard Client");
    addLog("ButtplugClient 創建成功");
    
    addLog("創建 WASM 連接器...");
    const connector = new ButtplugWasmClientConnector();
    addLog("WASM 連接器創建成功");
    
    addLog("連接到客戶端...");
    await globalClient.connect(connector);
    addLog("客戶端連接成功");
    
    // 監聽設備事件 - 參考工作程式
    globalClient.addListener('deviceadded', (device) => {
      addLog(`✅ 找到設備: ${device.name || 'Unknown'} (${device.index})`);
      addLog(`設備執行器數量: ${device.vibrateAttributes?.length || 0}`);
      connectedDevices.push(device);
      updateDeviceList();
      
      // 如果是 ERICA，進行連接測試
      if (device.name === 'ERICA') {
        addLog("🎯 檢測到 ERICA 設備，準備測試振動功能");
        setTimeout(() => {
          testStandardVibration(device);
        }, 1000);
      }
    });
    
    globalClient.addListener('deviceremoved', (device) => {
      addLog(`❌ 設備移除: ${device.name || 'Unknown'}`);
      connectedDevices = connectedDevices.filter(d => d.index !== device.index);
      updateDeviceList();
    });
    
    addLog("開始掃描設備...");
    isScanning = true;
    await globalClient.startScanning();
    addLog("設備掃描已開始 - 使用標準 Buttplug 協議");
    
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
    
    addLog("✅ 標準 Buttplug 測試完成！");
  } catch (error) {
    isScanning = false;
    addLog(`❌ 錯誤: ${error.message}`);
    addLog(`錯誤堆棧: ${error.stack}`);
    console.error("Buttplug 標準測試錯誤:", error);
  }
}

// 測試標準的設備振動功能
async function testStandardVibration(device) {
  if (!device || !device.vibrateAttributes || device.vibrateAttributes.length === 0) {
    addLog("設備不支援振動功能");
    return;
  }
  
  try {
    addLog(`🧪 測試 ${device.name} 標準振動功能...`);
    
    // 測試序列：低、中、高強度
    const testSequence = [
      { name: "低強度", intensity: 0.2 },
      { name: "中強度", intensity: 0.5 }, 
      { name: "高強度", intensity: 0.8 }
    ];
    
    for (const test of testSequence) {
      addLog(`🎮 ${test.name} (${Math.round(test.intensity * 100)}%)`);
      
      // 使用標準 Buttplug API
      const vibrateArray = new Array(device.vibrateAttributes.length).fill(test.intensity);
      await device.vibrate(vibrateArray);
      
      addLog(`✅ ${test.name} 振動命令發送成功`);
      
      // 等待 2 秒
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 停止振動
      await device.stop();
      addLog(`⏹️ ${test.name} 停止`);
      
      // 間隔 1 秒
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    addLog("🏁 標準振動測試完成！");
    
  } catch (error) {
    addLog(`❌ 標準振動測試失敗: ${error.message}`);
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
        <strong>${device.name || 'Unknown'}</strong> (索引: ${device.index})
        <br><small>執行器數量: ${device.vibrateAttributes?.length || 0}</small>
        <br><small>設備類型: ${device.displayName || 'Unknown'}</small>
        ${device.name === 'ERICA' ? '<br><span style="color: green;">✅ ERICA 設備 (支援標準協議)</span>' : ''}
      </div>`
    ).join('');
  }
}

// 手動振動控制
async function startStandardVibration() {
  const slider = document.getElementById('vibrateSlider');
  const intensity = slider.value / 100;
  
  if (connectedDevices.length === 0) {
    addLog("沒有連接的設備");
    return;
  }
  
  try {
    isVibrating = true;
    for (const device of connectedDevices) {
      if (device.vibrateAttributes && device.vibrateAttributes.length > 0) {
        const vibrateArray = new Array(device.vibrateAttributes.length).fill(intensity);
        await device.vibrate(vibrateArray);
        addLog(`🎮 設備 ${device.name} 開始振動，強度: ${Math.round(intensity * 100)}% (標準API)`);
      }
    }
  } catch (error) {
    addLog(`❌ 標準振動控制錯誤: ${error.message}`);
    isVibrating = false;
  }
}

async function stopStandardVibration() {
  if (connectedDevices.length === 0) {
    addLog("沒有連接的設備");
    return;
  }
  
  try {
    isVibrating = false;
    for (const device of connectedDevices) {
      if (device.vibrateAttributes && device.vibrateAttributes.length > 0) {
        await device.stop();
        addLog(`⏹️ 設備 ${device.name} 停止振動 (標準API)`);
      }
    }
  } catch (error) {
    addLog(`❌ 停止振動錯誤: ${error.message}`);
  }
}

// 設定振動強度（即時更新）
async function setStandardVibrationIntensity(intensity) {
  if (connectedDevices.length === 0 || !isVibrating) {
    return;
  }
  
  try {
    for (const device of connectedDevices) {
      if (device.vibrateAttributes && device.vibrateAttributes.length > 0) {
        const vibrateArray = new Array(device.vibrateAttributes.length).fill(intensity);
        await device.vibrate(vibrateArray);
      }
    }
  } catch (error) {
    addLog(`❌ 標準振動強度調整錯誤: ${error.message}`);
  }
}

onload = () => {
  addLog("頁面已載入 - 標準 Buttplug 版本");
  
  // 掃描按鈕
  document.getElementById('b').onclick = () => {
    addLog("🔍 Scan 按鈕被點擊 (標準模式)");
    test_buttplug_standard();
  };
  
  // 振動滑桿
  const slider = document.getElementById('vibrateSlider');
  const valueDisplay = document.getElementById('vibrateValue');
  
  slider.oninput = () => {
    const intensity = slider.value / 100;
    valueDisplay.textContent = slider.value + '%';
    
    // 即時調整振動強度
    if (isVibrating) {
      setStandardVibrationIntensity(intensity);
    }
  };
  
  // 振動控制按鈕
  document.getElementById('vibrateBtn').onclick = startStandardVibration;
  document.getElementById('stopBtn').onclick = stopStandardVibration;
  
  addLog("🎉 標準 Buttplug 控制器準備就緒");
};