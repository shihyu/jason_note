# Node.js 與 WebSocket

> Node.js 開發與 WebSocket 即時通訊技術。

## 🚀 Node.js 開發

### 完整指南
- [Node.js 完整開發指南](nodejs-guide.md)

核心內容：
- Node.js 架構與事件循環
- 異步編程模式
- 模組系統與 npm
- Express 框架實戰
- 性能優化技巧

## 📡 WebSocket 技術

### 效能對決
- [WebSocket 效能終極對決完整報告](websocket_perf_comparison_py_go_rust.md)

核心內容：
- Python vs Go vs Rust WebSocket 實現
- 性能基準測試
- 吞吐量與延遲分析
- 資源使用對比
- 技術選型建議

## 💡 Node.js 實踐

### 事件驅動架構
```javascript
const EventEmitter = require('events');

class MyEmitter extends EventEmitter {}
const myEmitter = new MyEmitter();

myEmitter.on('event', () => {
  console.log('事件觸發');
});

myEmitter.emit('event');
```

### Express 快速開始
```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

## 🔌 WebSocket 實踐

### 基本連接
```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  ws.on('message', (message) => {
    console.log('received: %s', message);
    ws.send(`Echo: ${message}`);
  });
});
```

### 廣播訊息
```javascript
wss.clients.forEach((client) => {
  if (client.readyState === WebSocket.OPEN) {
    client.send(data);
  }
});
```

**最後更新**: 2025-12-01
