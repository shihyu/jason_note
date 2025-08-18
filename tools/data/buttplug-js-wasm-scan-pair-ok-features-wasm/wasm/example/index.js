// 測試模組載入
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

async function test_wasm() {
  try {
    addLog("開始基本 WASM 測試...");
    
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
    
    addLog("測試 WASM 模組載入...");
    
    // 測試基本的 WASM 函數
    if (ButtplugWasmClientConnector.wasmInstance) {
      addLog("WASM 實例已存在");
      
      // 測試簡單的 WASM 函數
      try {
        addLog("測試建立嵌入式伺服器...");
        const serverPtr = ButtplugWasmClientConnector.wasmInstance.buttplug_create_embedded_wasm_server(() => {
          addLog("伺服器回調被調用");
        });
        addLog(`伺服器指標: ${serverPtr}`);
        
        if (serverPtr) {
          ButtplugWasmClientConnector.wasmInstance.buttplug_free_embedded_wasm_server(serverPtr);
          addLog("伺服器已釋放");
        }
      } catch (e) {
        addLog(`WASM 函數測試失敗: ${e.message}`);
        return;
      }
    }
    
    addLog("創建 ButtplugClient...");
    globalClient = new ButtplugClient("Test Client");
    addLog("ButtplugClient 創建成功");
    
    addLog("創建 WASM 連接器...");
    const connector = new ButtplugWasmClientConnector();
    addLog("WASM 連接器創建成功");
    
    addLog("連接到客戶端...");
    await globalClient.connect(connector);
    addLog("客戶端連接成功");
    
    addLog("開始掃描設備...");
    isScanning = true;
    await globalClient.startScanning();
    addLog("設備掃描已開始");
    
    // 監聽設備事件
    globalClient.addListener('deviceadded', (device) => {
      addLog(`找到設備: ${device.name || 'Unknown'} (${device.index})`);
      connectedDevices.push(device);
      updateDeviceList();
    });
    
    // 自動停止掃描（5秒後）
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
    }, 5000);
    
    addLog("測試完成！");
  } catch (error) {
    isScanning = false;
    addLog(`錯誤: ${error.message}`);
    addLog(`錯誤堆棧: ${error.stack}`);
    console.error("WASM 測試錯誤:", error);
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
      if (device.vibrateAttributes && device.vibrateAttributes.length > 0) {
        const vibrateArray = new Array(device.vibrateAttributes.length).fill(intensity);
        await device.vibrate(vibrateArray);
      }
    }
  } catch (error) {
    addLog(`振動強度調整錯誤: ${error.message}`);
  }
}

// 開始振動
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
      if (device.vibrateAttributes && device.vibrateAttributes.length > 0) {
        const vibrateArray = new Array(device.vibrateAttributes.length).fill(intensity);
        await device.vibrate(vibrateArray);
        addLog(`設備 ${device.name} 開始振動，強度: ${Math.round(intensity * 100)}%`);
      }
    }
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
      if (device.vibrateAttributes && device.vibrateAttributes.length > 0) {
        await device.stop();
        addLog(`設備 ${device.name} 停止振動`);
      }
    }
  } catch (error) {
    addLog(`停止振動錯誤: ${error.message}`);
  }
}

onload = () => {
  addLog("頁面已載入");
  
  // 掃描按鈕
  document.getElementById('b').onclick = () => {
    addLog("Scan 按鈕被點擊");
    test_wasm();
  };
  
  // 振動滑桿
  const slider = document.getElementById('vibrateSlider');
  const valueDisplay = document.getElementById('vibrateValue');
  
  slider.oninput = () => {
    const intensity = slider.value / 100;
    valueDisplay.textContent = slider.value + '%';
    
    // 即時調整振動強度
    if (isVibrating) {
      setVibrationIntensity(intensity);
    }
  };
  
  // 振動控制按鈕
  document.getElementById('vibrateBtn').onclick = startVibration;
  document.getElementById('stopBtn').onclick = stopVibration;
};
