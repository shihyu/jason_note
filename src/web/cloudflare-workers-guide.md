# Cloudflare Workers 完整指南：Python & Go

> 基於 Wrangler 4.69.0 實測驗證（2026-03）

---

## 目錄

1. [語言選擇比較](#語言選擇比較)
2. [共用環境安裝](#共用環境安裝)
3. [帳號申請與登入](#帳號申請與登入)
4. [Python Workers](#python-workers)
   - [建立專案](#python-建立專案)
   - [編寫程式碼](#python-編寫程式碼)
   - [本地測試](#python-本地測試)
   - [部署](#python-部署)
   - [常見錯誤](#python-常見錯誤)
5. [Go Workers（TinyGo）](#go-workers-tinygo)
   - [架構說明](#go-架構說明)
   - [安裝 TinyGo](#安裝-tinygo)
   - [建立專案](#go-建立專案)
   - [編寫程式碼](#go-編寫程式碼)
   - [本地測試](#go-本地測試)
   - [部署](#go-部署)
   - [常見錯誤](#go-常見錯誤)
6. [免費方案限制](#免費方案限制)
7. [其他替代方案](#其他替代方案)
8. [參考資源](#參考資源)

---

## 語言選擇比較

| 項目 | Python | Go（TinyGo） |
|------|--------|-------------|
| 官方支援等級 | Beta（官方） | 透過 WASM 橋接 |
| 入門難度 | 低，語法直覺 | 中，需了解 WASM 記憶體模型 |
| 執行機制 | Pyodide（WASM） | TinyGo → WASM → JS 橋接 |
| WASM 大小 | 自動管理 | 25 KB（基礎）～ 470 KB（含 json） |
| 第三方套件 | 官方支援清單（FastAPI 等） | 受限（無 GC、無排程器） |
| goroutine | 不適用 | ❌ 不支援 |
| 適合情境 | API、資料處理、AI 整合 | 純運算、高效能邏輯 |

---

## 共用環境安裝

Python 和 Go Workers 都需要 Node.js + wrangler。

### 必要工具

| 工具 | 版本 | 用途 |
|------|------|------|
| Node.js | v18+ | 執行 wrangler CLI |
| npm | v9+ | 套件管理 |
| wrangler | v4.x | Cloudflare CLI（透過 npx，不需全域安裝） |

### 確認環境

```bash
node --version          # 應顯示 v18 以上
npm --version           # 應顯示 v9 以上
npx wrangler --version  # 應顯示 4.x.x
```

實測輸出：
```
v24.4.1
11.4.2
4.69.0
```

### 安裝 Node.js（如未安裝）

```bash
# Ubuntu / Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 驗證
node --version && npm --version
```

---

## 帳號申請與登入

| 操作 | 需要帳號 |
|------|----------|
| 本地測試（`npx wrangler dev`） | ❌ 不需要 |
| 部署（`npx wrangler deploy`） | ✅ 需要 |

### Step 1：申請免費帳號

前往 `dash.cloudflare.com` 註冊，**不需要綁定信用卡**。

### Step 2：登入 wrangler

```bash
npx wrangler login
```

執行後會自動開啟瀏覽器，授權後回到終端機即完成登入。

---

## Python Workers

### Python 建立專案

#### ⚠️ 舊語法 vs 新語法

| 版本 | 語法 | 狀態 |
|------|------|------|
| wrangler 3.x（舊） | `npx wrangler init my-python-worker --lang=python` | ❌ 已移除 |
| wrangler 4.x（新） | 手動建立 + `wrangler.toml` 設定 | ✅ 正確方式 |

#### Step 1：建立目錄結構

```bash
mkdir -p my-python-worker/src
cd my-python-worker
```

最終結構：

```
my-python-worker/
├── wrangler.toml       ← 設定檔（必要）
├── requirements.txt    ← 第三方套件（選用）
└── src/
    └── entry.py        ← 主程式
```

#### Step 2：建立 wrangler.toml

```toml
name = "my-python-worker"
main = "src/entry.py"
compatibility_date = "2024-12-01"
compatibility_flags = ["python_workers"]
```

> `compatibility_flags = ["python_workers"]` 是啟用 Python 支援的必要設定，缺少這行會導致執行失敗。

#### Step 3：建立主程式 src/entry.py

```python
from js import Response


async def on_fetch(request, env):
    return Response.new("Hello from Python on Cloudflare Workers!")
```

**說明**：
- `from js import Response`：`js` 是 Workers 執行環境的內建模組，本機 IDE 顯示 import 錯誤屬正常，可忽略
- `on_fetch(request, env)`：所有請求的入口函式，名稱固定不可更改
- 函式必須是 `async`

---

### Python 編寫程式碼

#### 基本：Hello World

```python
from js import Response


async def on_fetch(request, env):
    return Response.new("Hello from Python on Cloudflare Workers!")
```

#### 讀取請求資訊

```python
from js import Response


async def on_fetch(request, env):
    body = f"URL: {request.url}\nMethod: {request.method}"
    return Response.new(body)
```

實測輸出：
```
URL: http://localhost:8787/
Method: GET
```

#### 回傳 JSON

```python
from js import Response, Headers
import json


async def on_fetch(request, env):
    data = {
        "message": "Hello from Python!",
        "method": request.method,
        "url": request.url,
    }
    headers = Headers.new({"Content-Type": "application/json"}.items())
    return Response.new(json.dumps(data), headers=headers)
```

實測輸出：
```json
{"message": "Hello from Python!", "method": "GET", "url": "http://localhost:8787/"}
```

> 注意：回傳 JSON 時 headers 需用 `Headers.new()` 建立，不能直接傳 dict。

#### 路由處理

```python
from js import Response
from urllib.parse import urlparse


async def on_fetch(request, env):
    path = urlparse(request.url).path

    if path == "/":
        return Response.new("首頁")
    elif path == "/hello":
        return Response.new("Hello!")
    else:
        return Response.new("404 Not Found", status=404)
```

實測輸出：
```bash
curl http://localhost:8787/        # → 首頁
curl http://localhost:8787/hello   # → Hello!
curl http://localhost:8787/other   # → 404 Not Found（HTTP 404）
```

#### 使用第三方套件

建立 `requirements.txt`：
```
fastapi
```

```python
from js import Response
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI on Workers!"}


async def on_fetch(request, env):
    # 整合 FastAPI 路由
    ...
```

> 僅支援 Cloudflare 驗證過的套件清單，包含 FastAPI、httpx 等。

#### Workers AI 整合

```python
from js import Response
import json


async def on_fetch(request, env):
    result = await env.AI.run(
        "@cf/meta/llama-3.1-8b-instruct",
        {"messages": [{"role": "user", "content": "Hello!"}]},
    )
    return Response.new(
        json.dumps(result),
        headers={"Content-Type": "application/json"},
    )
```

---

### Python 本地測試

```bash
cd my-python-worker
npx wrangler dev
```

啟動輸出：
```
⛅️ wrangler 4.69.0
───────────────────
⎔ Starting local server...
[wrangler:info] Ready on http://localhost:8787
```

測試指令：
```bash
curl http://localhost:8787/
curl -X POST http://localhost:8787/ -d '{"key": "value"}'
curl -H "Content-Type: application/json" http://localhost:8787/
```

---

### Python 部署

```bash
npx wrangler deploy
```

實測輸出：
```
⛅️ wrangler 4.69.0
───────────────────
Total Upload: 0.13 KiB / gzip: 0.13 KiB
Worker Startup Time: 839 ms
Uploaded my-python-worker (9.44 sec)
Deployed my-python-worker triggers (2.98 sec)
  https://my-python-worker.yaoshihyu.workers.dev
Current Version ID: 5bb974f1-411e-4702-9aab-e84d7c4b10cb
```

驗證：
```bash
curl https://my-python-worker.yaoshihyu.workers.dev
# → Hello from Python on Cloudflare Workers!
```

---

### Python 常見錯誤

#### 錯誤 1：`Unknown arguments: lang`
```
✘ [ERROR] Unknown arguments: lang, git
```
**原因**：使用舊版語法 `--lang=python`，wrangler 4.x 已移除。
**解決**：改用手動建立專案結構。

#### 錯誤 2：IDE 顯示 `Import "js" could not be resolved`
```
✘ Import "js" could not be resolved [reportMissingImports]
```
**原因**：`js` 模組只存在於 Workers 執行環境，不在本機。
**解決**：正常現象，直接忽略，不影響部署和執行。

#### 錯誤 3：忘記加 `compatibility_flags`

**現象**：wrangler dev 啟動後請求沒有回應。
**解決**：確認 `wrangler.toml` 包含：
```toml
compatibility_flags = ["python_workers"]
```

#### 錯誤 4：JSON 回應用 dict 傳 headers 導致 Worker 掛起

**現象**：請求超時，wrangler 報 "Worker hung"。
**錯誤寫法**：
```python
return Response.new(json.dumps(data), headers={"Content-Type": "application/json"})
```
**正確寫法**：
```python
headers = Headers.new({"Content-Type": "application/json"}.items())
return Response.new(json.dumps(data), headers=headers)
```

---

## Go Workers（TinyGo）

### Go 架構說明

Cloudflare Workers **不直接支援 Go**，需透過 WebAssembly（WASM）橋接：

```
Go 原始碼（main.go）
    ↓  tinygo build -target wasm-unknown
worker.wasm（WebAssembly，~25 KB 起）
    ↓  JavaScript 橋接讀取 WASM 記憶體
worker.js（Workers 入口）
    ↓  Cloudflare Edge 執行
```

#### 為何選 TinyGo 而非標準 Go？

| 項目 | 標準 Go WASM | TinyGo WASM |
|------|-------------|-------------|
| 編譯指令 | `GOOS=js GOARCH=wasm` | `tinygo build -target wasm-unknown` |
| 輸出大小 | ~1.5 MB | ~25 KB（基礎） |
| 需要 wasm_exec.js | ✅（且與 Workers 不相容） | ❌ 不需要 |
| Workers 實測 | ❌ 無法執行 | ✅ 正常運作 |

> 標準 Go WASM 的 `wasm_exec.js` 依賴 `node:fs`、`node:crypto` 等 Node.js API，在 Workers 環境會導致 `Maximum call stack size exceeded` 錯誤。

---

### 安裝 TinyGo

```bash
# 下載（Linux amd64）
curl -fsSL "https://github.com/tinygo-org/tinygo/releases/download/v0.34.0/tinygo0.34.0.linux-amd64.tar.gz" \
  -o /tmp/tinygo.tar.gz

# 解壓縮
sudo tar -xzf /tmp/tinygo.tar.gz -C /usr/local/

# 加入 PATH（加到 ~/.bashrc 或 ~/.zshrc）
export PATH=$PATH:/usr/local/tinygo/bin

# 驗證
tinygo version
```

實測輸出：
```
tinygo version 0.34.0 linux/amd64 (using go version go1.21.6 and LLVM version 18.1.2)
```

---

### Go 建立專案

#### Step 1：建立目錄結構

```bash
mkdir -p my-go-worker
cd my-go-worker
go mod init my-go-worker
```

最終結構：

```
my-go-worker/
├── go.mod          ← Go 模組設定
├── main.go         ← Go 主程式
├── worker.js       ← Workers 入口（JavaScript 橋接）
├── worker.wasm     ← 編譯產物（建議加入 .gitignore）
└── wrangler.toml   ← Cloudflare 設定
```

#### Step 2：建立 wrangler.toml

```toml
name = "my-go-worker"
main = "worker.js"
compatibility_date = "2024-12-01"
```

---

### Go 編寫程式碼

#### TinyGo wasm-unknown 功能限制

| 功能 | 可用 |
|------|------|
| 基本型別（int, string, []byte） | ✅ |
| encoding/json | ✅ |
| 標準字串操作 | ✅ |
| goroutine | ❌（scheduler = none） |
| 垃圾回收 | ❌（gc = leaking） |
| syscall/js | ❌ |
| net/http | ❌ |

#### JS ↔ Go 資料交換模式

```
JS → writeString(str) → alloc() 取得 WASM 記憶體位址 → 寫入字串
JS → 呼叫 handle(methodPtr, methodLen, pathPtr, pathLen)
Go → 處理邏輯 → 寫入 responseData 全域變數
JS → responsePtr() + responseLen() → 讀取回應
JS → new Response(body) → 回傳給 Cloudflare
```

#### 基本範例：Hello World

**main.go**：
```go
//go:build tinygo.wasm

package main

import "unsafe"

var responseData []byte

//export handle
func handle() {
    responseData = []byte("Hello from Go (TinyGo) on Cloudflare Workers!")
}

//export responsePtr
func responsePtr() uintptr {
    if len(responseData) == 0 {
        return 0
    }
    return uintptr(unsafe.Pointer(&responseData[0]))
}

//export responseLen
func responseLen() int32 {
    return int32(len(responseData))
}

func main() {}
```

**worker.js**：
```js
import wasmModule from "./worker.wasm";

// wasmModule 已是 WebAssembly.Module，instantiate 直接回傳 Instance
const instance = await WebAssembly.instantiate(wasmModule, {});
const { handle, responsePtr, responseLen, memory } = instance.exports;

export default {
  async fetch(request) {
    handle();
    const ptr = responsePtr();
    const len = responseLen();
    const body = new TextDecoder().decode(new Uint8Array(memory.buffer, ptr, len));
    return new Response(body);
  },
};
```

#### 進階範例：路由 + JSON（實測版）

**main.go**：
```go
//go:build tinygo.wasm

package main

import (
    "encoding/json"
    "unsafe"
)

var responseData []byte
var responseStatus int32 = 200

//export handle
func handle(methodPtr uintptr, methodLen int32, pathPtr uintptr, pathLen int32) {
    method := readString(methodPtr, methodLen)
    path := readString(pathPtr, pathLen)

    switch path {
    case "/":
        responseData = []byte("Hello from Go (TinyGo) on Cloudflare Workers!")
        responseStatus = 200
    case "/json":
        data := map[string]string{
            "message": "Hello from Go!",
            "method":  method,
        }
        b, _ := json.Marshal(data)
        responseData = b
        responseStatus = 200
    case "/hello":
        responseData = []byte("Hello!")
        responseStatus = 200
    default:
        responseData = []byte("404 Not Found")
        responseStatus = 404
    }
}

func readString(ptr uintptr, length int32) string {
    buf := make([]byte, length)
    copy(buf, (*[1 << 30]byte)(unsafe.Pointer(ptr))[:length:length])
    return string(buf)
}

//export responsePtr
func responsePtr() uintptr {
    if len(responseData) == 0 {
        return 0
    }
    return uintptr(unsafe.Pointer(&responseData[0]))
}

//export responseLen
func responseLen() int32 {
    return int32(len(responseData))
}

//export getStatus
func getStatus() int32 {
    return responseStatus
}

//export alloc
func alloc(size int32) uintptr {
    buf := make([]byte, size)
    return uintptr(unsafe.Pointer(&buf[0]))
}

func main() {}
```

**worker.js**：
```js
import wasmModule from "./worker.wasm";

const instance = await WebAssembly.instantiate(wasmModule, {});
const { handle, responsePtr, responseLen, getStatus, alloc, memory } = instance.exports;

function writeString(str) {
  const encoded = new TextEncoder().encode(str);
  const ptr = alloc(encoded.length);
  new Uint8Array(memory.buffer, ptr, encoded.length).set(encoded);
  return [ptr, encoded.length];
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const [methodPtr, methodLen] = writeString(request.method);
    const [pathPtr, pathLen] = writeString(url.pathname);

    handle(methodPtr, methodLen, pathPtr, pathLen);

    const ptr = responsePtr();
    const len = responseLen();
    const status = getStatus();
    const body = new TextDecoder().decode(new Uint8Array(memory.buffer, ptr, len));

    const headers = url.pathname === "/json"
      ? { "Content-Type": "application/json" }
      : { "Content-Type": "text/plain" };

    return new Response(body, { status, headers });
  },
};
```

---

### Go 本地測試

#### Step 1：編譯 Go → WASM

```bash
tinygo build -o worker.wasm -target wasm-unknown ./...
```

```bash
ls -lh worker.wasm
# -rwxr-xr-x 1 user user  25K worker.wasm（僅基礎）
# -rwxr-xr-x 1 user user 469K worker.wasm（含 encoding/json）
```

#### Step 2：啟動本地伺服器

```bash
npx wrangler dev
```

輸出：
```
⛅️ wrangler 4.69.0
───────────────────
⎔ Starting local server...
[wrangler:info] Ready on http://localhost:8787
```

#### Step 3：測試各端點

```bash
curl http://localhost:8787/
# → Hello from Go (TinyGo) on Cloudflare Workers!

curl http://localhost:8787/json
# → {"message":"Hello from Go!","method":"GET"}

curl http://localhost:8787/hello
# → Hello!

curl -w "\nHTTP Status: %{http_code}" http://localhost:8787/other
# → 404 Not Found
# → HTTP Status: 404
```

---

### Go 部署

```bash
npx wrangler deploy
```

實測輸出：
```
⛅️ wrangler 4.69.0
───────────────────
Total Upload: 470.15 KiB / gzip: 182.92 KiB
Uploaded my-go-worker (5.81 sec)
Deployed my-go-worker triggers (9.36 sec)
  https://my-go-worker.yaoshihyu.workers.dev
Current Version ID: 42f758f8-fb93-42e6-bbea-3069dd097ef6
```

驗證：
```bash
curl https://my-go-worker.yaoshihyu.workers.dev/
# → Hello from Go (TinyGo) on Cloudflare Workers!

curl https://my-go-worker.yaoshihyu.workers.dev/json
# → {"message":"Hello from Go!","method":"GET"}

curl -w "\nHTTP: %{http_code}" https://my-go-worker.yaoshihyu.workers.dev/other
# → 404 Not Found
# → HTTP: 404
```

---

### Go 常見錯誤

#### 錯誤 1：使用標準 Go WASM

**現象**：
```
Uncaught RangeError: Maximum call stack size exceeded
```
或
```
ReferenceError: handleRequest is not defined
```
**原因**：`GOOS=js GOARCH=wasm` 的 `wasm_exec.js` 依賴 Node.js API，在 Workers 不相容。
**解決**：改用 TinyGo + `wasm-unknown` target。

#### 錯誤 2：`Cannot read properties of undefined (reading 'exports')`

**原因**：在 Workers 中 import WASM 後，`WebAssembly.instantiate(module)` 直接回傳 `Instance`，不是 `{ instance, module }`。

```js
// ❌ 錯誤
const { instance } = await WebAssembly.instantiate(wasmModule, {});

// ✅ 正確
const instance = await WebAssembly.instantiate(wasmModule, {});
```

#### 錯誤 3：build constraint 不符

```
build constraints exclude all Go files in ...
```
**原因**：`//go:build tinygo.wasm` 限制只在 TinyGo 編譯，用 `go build` 會跳過。
**解決**：
```bash
# ❌ 錯誤
go build ./...

# ✅ 正確
tinygo build -o worker.wasm -target wasm-unknown ./...
```

#### 錯誤 4：`//export` 格式錯誤

```go
// ❌ 有空格，不生效
// export handle
func handle() {}

// ❌ 有空行，不生效
//export handle

func handle() {}

// ✅ 正確
//export handle
func handle() {}
```

---

## 免費方案限制

| 項目 | 限制 |
|------|------|
| 每天請求數 | 100,000 次 |
| CPU 時間 | 10ms / 請求（付費 30ms） |
| Workers 數量 | 100 個 |
| 記憶體 | 128 MB |
| Worker 大小 | 1 MB（未壓縮） |
| 費用 | **免費** |

> Go Worker（含 encoding/json）上傳大小約 470 KB，gzip 後 183 KB，符合免費方案限制。

---

## 其他替代方案

### 管理 Cloudflare 資源（python-cloudflare SDK）

不需要 Workers，直接管理 DNS、清除快取等：

```bash
pip install cloudflare
```

```python
import cloudflare

client = cloudflare.Cloudflare(api_token="your_api_token")
records = client.dns.records.list(zone_id="your_zone_id")
```

### 暴露既有服務（Cloudflare Tunnel）

本機已跑 Django / Flask / Go HTTP Server，不需要公開 IP：

```bash
# 安裝
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

# 將本地 8000 port 對外公開
./cloudflared tunnel --url http://localhost:8000
```

---

## 參考資源

### Python
- [Cloudflare Workers Python 官方文件](https://developers.cloudflare.com/workers/languages/python/)
- [支援的 Python 套件清單](https://developers.cloudflare.com/workers/languages/python/packages/)

### Go / TinyGo
- [TinyGo 官方文件](https://tinygo.org/docs/)
- [TinyGo WASM 支援說明](https://tinygo.org/docs/guides/webassembly/)
- [Cloudflare Workers WASM 文件](https://developers.cloudflare.com/workers/runtime-apis/webassembly/)

### 通用
- [Wrangler CLI 文件](https://developers.cloudflare.com/workers/wrangler/)
- [Cloudflare Workers 免費方案說明](https://developers.cloudflare.com/workers/platform/pricing/)
