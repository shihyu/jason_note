# Node.js I/O 並發範例

> 三種常見的 Node.js 並發模式：異步並發、Worker Threads、文件 I/O

---

## 目錄

1. [基礎異步 I/O 並發（單線程）](#1-基礎異步-io-並發單線程)
2. [Worker Threads 多線程版本](#2-worker-threads-多線程版本)
3. [文件 I/O 並發讀取](#3-文件-io-並發讀取)
4. [單線程 vs 多線程對比](#單線程-vs-多線程對比)
5. [你的代碼分析](#你的代碼分析)

---

## 1. 基礎異步 I/O 並發（單線程）

**檔案：`simple-io-concurrent.js`**

```javascript
// simple-io-concurrent.js
const fs = require('fs').promises;

async function task(id, delay) {
  const start = Date.now();
  console.log(`[${id}] 開始 | PID: ${process.pid} | 主線程`);

  // 模擬異步 I/O
  await new Promise(r => setTimeout(r, delay));

  const elapsed = Date.now() - start;
  console.log(`[${id}] 完成 | 耗時: ${elapsed}ms`);
  return { id, elapsed };
}

async function main() {
  console.log(`主進程 PID: ${process.pid}\n`);

  const start = Date.now();

  // 並發執行 5 個任務
  const results = await Promise.all([
    task('任務A', 1000),
    task('任務B', 500),
    task('任務C', 800),
    task('任務D', 300),
    task('任務E', 1200)
  ]);

  const total = Date.now() - start;
  console.log(`\n全部完成 | 總耗時: ${total}ms`);
  console.log('結果:', results);
}

main();
```

**執行：**
```bash
node simple-io-concurrent.js
```

**輸出示例：**
```
主進程 PID: 12345

[任務A] 開始 | PID: 12345 | 主線程
[任務B] 開始 | PID: 12345 | 主線程
[任務C] 開始 | PID: 12345 | 主線程
[任務D] 開始 | PID: 12345 | 主線程
[任務E] 開始 | PID: 12345 | 主線程
[任務D] 完成 | 耗時: 302ms
[任務B] 完成 | 耗時: 503ms
[任務C] 完成 | 耗時: 802ms
[任務A] 完成 | 耗時: 1001ms
[任務E] 完成 | 耗時: 1202ms

全部完成 | 總耗時: 1205ms
結果: [
  { id: '任務A', elapsed: 1001 },
  { id: '任務B', elapsed: 503 },
  { id: '任務C', elapsed: 802 },
  { id: '任務D', elapsed: 302 },
  { id: '任務E', elapsed: 1202 }
]
```

**特點：**
- 單線程，所有任務共享同一個 PID
- 使用 `Promise.all` 實現並發
- 適合 I/O 密集型任務
- 總耗時約等於最慢任務（1200ms），而非累加（4000ms）

---

## 2. Worker Threads 多線程版本

**檔案：`worker-threads-example.js`**

```javascript
// worker-threads-example.js
const { Worker, isMainThread, parentPort, threadId, workerData } = require('worker_threads');

if (isMainThread) {
  // === 主線程 ===
  console.log(`主進程 PID: ${process.pid} | TID: ${threadId}\n`);

  const start = Date.now();
  const workers = [];

  // 創建 5 個 worker
  for (let i = 1; i <= 5; i++) {
    const worker = new Worker(__filename, {
      workerData: { taskId: i, delay: Math.random() * 1000 + 500 }
    });

    workers.push(new Promise((resolve, reject) => {
      worker.on('message', msg => {
        console.log(`Task ${msg.taskId} 完成 | 耗時: ${msg.elapsed}ms`);
        resolve(msg);
      });
      worker.on('error', reject);
      worker.on('exit', code => {
        if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
      });
    }));
  }

  // 等待所有 worker 完成
  Promise.all(workers).then(results => {
    const total = Date.now() - start;
    console.log(`\n全部完成 | 總耗時: ${total}ms`);
    console.log(`處理: ${results.length} 個任務`);
  });

} else {
  // === Worker 線程 ===
  const { taskId, delay } = workerData;
  const start = Date.now();

  console.log(`[Task ${taskId}] 開始 | PID: ${process.pid} | Worker TID: ${threadId}`);

  // 模擬工作
  setTimeout(() => {
    const elapsed = Date.now() - start;
    parentPort.postMessage({ taskId: `Task ${taskId}`, elapsed });
  }, delay);
}
```

**執行：**
```bash
node worker-threads-example.js
```

**輸出示例：**
```
主進程 PID: 12345 | TID: 0

[Task 1] 開始 | PID: 12345 | Worker TID: 1
[Task 2] 開始 | PID: 12345 | Worker TID: 2
[Task 3] 開始 | PID: 12345 | Worker TID: 3
[Task 4] 開始 | PID: 12345 | Worker TID: 4
[Task 5] 開始 | PID: 12345 | Worker TID: 5
Task 2 完成 | 耗時: 523ms
Task 4 完成 | 耗時: 678ms
Task 1 完成 | 耗時: 891ms
Task 5 完成 | 耗時: 1034ms
Task 3 完成 | 耗時: 1256ms

全部完成 | 總耗時: 1258ms
處理: 5 個任務
```

**特點：**
- 多線程，每個 Worker 有獨立的 TID
- 相同 PID（同一進程）
- 適合 CPU 密集型任務
- 更高的內存開銷

---

## 3. 文件 I/O 並發讀取

**檔案：`file-io-concurrent.js`**

```javascript
// file-io-concurrent.js
const fs = require('fs').promises;
const path = require('path');

async function readFile(filename, id) {
  console.log(`[${id}] 開始讀取 ${filename} | PID: ${process.pid}`);

  try {
    const content = await fs.readFile(filename, 'utf-8');
    console.log(`[${id}] ${filename} | 大小: ${content.length} bytes`);
    return { filename, size: content.length };
  } catch (e) {
    console.log(`[${id}] ${filename} | 錯誤: ${e.message}`);
    return { filename, error: e.message };
  }
}

async function main() {
  console.log(`PID: ${process.pid}\n`);

  // 準備測試文件（創建幾個測試文件）
  const testDir = path.join(__dirname, 'tmp');
  await fs.mkdir(testDir, { recursive: true });

  const testFiles = ['test1.txt', 'test2.txt', 'test3.txt'].map(f => path.join(testDir, f));
  for (const f of testFiles) {
    await fs.writeFile(f, `內容 ${path.basename(f)} `.repeat(1000));
  }

  const start = Date.now();

  // 並發讀取
  const results = await Promise.all(
    testFiles.map((f, i) => readFile(f, i + 1))
  );

  console.log(`\n總耗時: ${Date.now() - start}ms`);
  console.log('結果:', results);

  // 清理
  for (const f of testFiles) {
    await fs.unlink(f);
  }
  await fs.rmdir(testDir);
}

main();
```

**執行：**
```bash
node file-io-concurrent.js
```

**輸出示例：**
```
PID: 12345

[1] 開始讀取 test1.txt | PID: 12345
[2] 開始讀取 test2.txt | PID: 12345
[3] 開始讀取 test3.txt | PID: 12345
[1] test1.txt | 大小: 11000 bytes
[2] test2.txt | 大小: 11000 bytes
[3] test3.txt | 大小: 11000 bytes

總耗時: 8ms
結果: [
  { filename: 'test1.txt', size: 11000 },
  { filename: 'test2.txt', size: 11000 },
  { filename: 'test3.txt', size: 11000 }
]
```

---

## 單線程 vs 多線程對比

| 特性 | 單線程異步 | Worker Threads |
|------|-----------|----------------|
| **模組** | `Promise.all` + `async/await` | `worker_threads` |
| **PID** | 全部相同 | 全部相同 |
| **TID** | 無（只有主線程） | 每個 Worker 不同 |
| **CPU 利用** | 單核心 | 多核心 |
| **內存** | 低（共享內存） | 高（每個線程獨立） |
| **適用場景** | I/O 密集 | CPU 密集 |
| **複雜度** | 低 | 較高 |
| **例子** | 網絡請求、文件讀寫 | 圖像處理、加密運算 |

---

## 你的代碼分析

### 你的 `batch-query-blocks.js` 是什麼模式？

```javascript
// 單線程異步並發
await Promise.all(workers.map(w => w.run()));
```

**判斷依據：**

```javascript
// 沒有使用多線程模組
const { Worker } = require('worker_threads');  // 不存在
const cluster = require('cluster');             // 不存在

// 使用異步並發
class Worker {
  async run() {
    const resp = await axios.get(...);  // 異步 I/O
  }
}
```

### 並發原理圖

```
+-------------------------------------+
|     主線程 (PID: 12345)              |
|  +--------------------------------+ |
|  |   事件循環 (Event Loop)         | |
|  |                                 | |
|  |  Worker1 -> axios (異步)        | |
|  |  Worker2 -> axios (異步)        | |
|  |  Worker3 -> axios (異步)        | |
|  |  Worker4 -> axios (異步)        | |
|  |     ...                         | |
|  |  Worker8 -> axios (異步)        | |
|  |                                 | |
|  |  (所有在同一個線程執行)         | |
|  +--------------------------------+ |
+-------------------------------------+
```

### 為什麼能並發？

```javascript
// 這是 I/O 密集型任務（網絡請求）
async query(address) {
  const resp = await axios.get(...);  // <- 異步等待
  // CPU 在等待網絡回應時，可以處理其他請求
}

// Promise.all 讓 8 個 Worker "同時"發起請求
await Promise.all(workers.map(w => w.run()));
// 雖然是單線程，但 I/O 等待期間不阻塞
```

### 結論

你的代碼是 **單線程異步並發**，非常適合 I/O 密集型任務（API 請求）！

**優點：**
- 設計正確：瓶頸是網絡延遲，不是 CPU
- 資源效率高：單線程異步已經能充分利用並發
- 複雜度低：不需要多線程的額外開銷

**如果改成多線程：**
- 沒必要：網絡請求不受益於多核心
- 增加複雜度：線程間通信、錯誤處理
- 更高內存：每個線程獨立內存空間

---

## 快速測試

```bash
# 進入範例目錄
cd nodejs-io-concurrent-examples

# 查看可用指令
make

# 執行測試
make build
make test

# 執行所有範例
make run

# 執行單一範例
make run-simple
make run-worker
make run-file

# 清理
make clean
```

---

## 參考資源

- [Node.js 官方文檔 - Worker Threads](https://nodejs.org/api/worker_threads.html)
- [Node.js 官方文檔 - Event Loop](https://nodejs.org/en/docs/guides/event-loop-timers-and-nexttick/)
- [Promise.all() - MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all)

---

**最後更新：** 2025-11-16
