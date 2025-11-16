# Node.js 完整指南

## 什麼是 Node.js？

Node.js 是一個基於 Chrome V8 引擎的 JavaScript 執行環境，讓 JavaScript 能夠在伺服器端執行。它使用事件驅動、非阻塞 I/O 模型，非常適合建構可擴展的網路應用程式。

## 核心特性

### 1. 單執行緒事件迴圈 (Event Loop)
```javascript
// 非阻塞 I/O 範例
const fs = require('fs');

console.log('開始讀取檔案');
fs.readFile('data.txt', 'utf8', (err, data) => {
    if (err) throw err;
    console.log('檔案內容:', data);
});
console.log('繼續執行其他任務'); // 不會被阻塞
```

### 2. npm 套件管理系統
```bash
# 初始化專案
npm init -y

# 安裝套件
npm install express
npm install -D nodemon  # 開發依賴

# 全域安裝
npm install -g typescript
```

### 3. 模組系統

#### CommonJS (Node.js 傳統)
```javascript
// math.js
module.exports = {
    add: (a, b) => a + b,
    subtract: (a, b) => a - b
};

// app.js
const math = require('./math');
console.log(math.add(2, 3));
```

#### ES Modules (現代標準)
```javascript
// math.mjs
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;

// app.mjs
import { add, subtract } from './math.mjs';
console.log(add(2, 3));
```

## 常用框架與工具

### Web 框架
- **Express.js** - 極簡彈性的 Web 框架
- **NestJS** - 企業級 TypeScript 框架
- **Fastify** - 高效能 Web 框架
- **Koa.js** - Express 團隊開發的下一代框架

### 資料庫連接
- **Mongoose** - MongoDB ODM
- **Sequelize** - SQL ORM
- **Prisma** - 現代 ORM 工具
- **TypeORM** - TypeScript ORM

### 開發工具
- **nodemon** - 自動重啟開發伺服器
- **pm2** - 生產環境程序管理器
- **jest** - 測試框架
- **webpack/esbuild** - 打包工具

## 學習資源

### 官方文件
- [Node.js 官方文件](https://nodejs.org/docs/)
- [Node.js API 參考](https://nodejs.org/api/)
- [npm 文件](https://docs.npmjs.com/)

### 線上課程
- [The Odin Project - Node.js](https://www.theodinproject.com/paths/full-stack-javascript/courses/nodejs)
- [freeCodeCamp - Node.js](https://www.freecodecamp.org/learn/back-end-development-and-apis/)
- [Node.js 官方學習指南](https://nodejs.dev/learn)

### 書籍推薦
- 《Node.js 設計模式》
- 《Node.js 實戰》
- 《深入淺出 Node.js》

### GitHub 專案學習
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [Awesome Node.js](https://github.com/sindresorhus/awesome-nodejs)
- [Node.js 官方程式碼](https://github.com/nodejs/node)

### 中文資源
- [Node.js 中文網](https://nodejs.org/zh-cn/)
- [Express 中文文件](https://expressjs.com/zh-tw/)
- [NestJS 中文文件](https://docs.nestjs.cn/)

## 典型應用場景

1. **RESTful API 伺服器**
2. **即時通訊應用 (WebSocket)**
3. **微服務架構**
4. **命令列工具 (CLI)**
5. **串流處理**
6. **物聯網 (IoT) 應用**

## 效能考量

- 適合 I/O 密集型任務
- 不適合 CPU 密集型計算（可用 Worker Threads 改善）
- 記憶體使用需要注意（避免記憶體洩漏）
- 使用 cluster 模組實現多核心利用
