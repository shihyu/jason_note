# Node.js vs JavaScript vs TypeScript 完整比較

## 概述

| 特性 | JavaScript | TypeScript | Node.js |
|------|-----------|------------|---------|
| 類型 | 程式語言 | 程式語言（JS 超集） | 執行環境 |
| 執行環境 | 瀏覽器/Node.js | 編譯為 JS 後執行 | 伺服器端 |
| 類型系統 | 動態類型 | 靜態類型 | 取決於使用的語言 |
| 編譯 | 直譯執行 | 需編譯為 JS | 直接執行 JS |

---

## JavaScript

### 什麼是 JavaScript？
JavaScript 是一種輕量級、直譯式的程式語言，最初設計用於網頁互動，現已成為全端開發的通用語言。

### 特點
```javascript
// 動態類型
let value = 42;        // number
value = "hello";       // string（合法但可能造成問題）
value = { key: "val" }; // object

// 原型繼承
function Animal(name) {
    this.name = name;
}
Animal.prototype.speak = function() {
    console.log(this.name + ' makes a sound.');
};

// 一等公民函數
const greet = (name) => `Hello, ${name}`;
const sayHello = greet;
console.log(sayHello("World"));

// 非同步程式設計
async function fetchData() {
    const response = await fetch('https://api.example.com/data');
    return response.json();
}
```

### 優點
- 學習曲線平緩
- 生態系統龐大
- 靈活性高
- 瀏覽器原生支援

### 缺點
- 動態類型易出錯
- 缺乏編譯期檢查
- 大型專案維護困難
- 隱式類型轉換問題

---

## TypeScript

### 什麼是 TypeScript？
TypeScript 是 Microsoft 開發的 JavaScript 超集，增加了靜態類型系統和其他語言特性。

### 特點
```typescript
// 靜態類型
let value: number = 42;
// value = "hello";  // 編譯錯誤！

// 介面定義
interface User {
    id: number;
    name: string;
    email?: string;  // 可選屬性
    readonly createdAt: Date;  // 唯讀屬性
}

// 泛型
function identity<T>(arg: T): T {
    return arg;
}
const num = identity<number>(42);
const str = identity<string>("hello");

// 類別與裝飾器
class UserService {
    private users: User[] = [];

    addUser(user: User): void {
        this.users.push(user);
    }

    getUser(id: number): User | undefined {
        return this.users.find(u => u.id === id);
    }
}

// 枚舉
enum Status {
    Active = "ACTIVE",
    Inactive = "INACTIVE",
    Pending = "PENDING"
}

// 聯合類型與類型守衛
type Response = Success | Error;

interface Success {
    status: "success";
    data: any;
}

interface Error {
    status: "error";
    message: string;
}

function handleResponse(response: Response) {
    if (response.status === "success") {
        console.log(response.data);
    } else {
        console.error(response.message);
    }
}
```

### 優點
- 編譯期類型檢查，減少執行期錯誤
- 更好的 IDE 支援（自動補全、重構）
- 程式碼可讀性和可維護性更高
- 漸進式採用（可與 JS 共存）
- 先進的語言特性

### 缺點
- 需要編譯步驟
- 學習曲線較陡
- 設定複雜度增加
- 第三方套件可能缺少類型定義

### 配置範例 (tsconfig.json)
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## Node.js

### 什麼是 Node.js？
Node.js 不是程式語言，而是 JavaScript 的執行環境，讓 JS 能在伺服器端執行。

### 特點
```javascript
// 內建模組
const fs = require('fs');
const http = require('http');
const path = require('path');
const crypto = require('crypto');

// 建立 HTTP 伺服器
const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Hello World\n');
});
server.listen(3000);

// 檔案系統操作
const data = fs.readFileSync('config.json', 'utf8');
const config = JSON.parse(data);

// 串流處理
const readStream = fs.createReadStream('large-file.txt');
const writeStream = fs.createWriteStream('output.txt');
readStream.pipe(writeStream);

// 環境變數
const port = process.env.PORT || 3000;
const nodeEnv = process.env.NODE_ENV || 'development';

// 命令列參數
const args = process.argv.slice(2);
console.log('Arguments:', args);
```

### 優點
- 統一前後端語言
- 非阻塞 I/O，高併發處理能力
- npm 生態系統豐富
- 適合微服務和 API 開發
- 活躍的社群支持

### 缺點
- 單執行緒限制（CPU 密集型任務）
- 回呼地獄（可用 async/await 改善）
- 相對年輕，API 變動頻繁
- 錯誤處理需要特別注意

---

## 三者關係圖

```
┌─────────────────────────────────────────┐
│              Node.js (執行環境)           │
│  ┌───────────────────────────────────┐  │
│  │     TypeScript (程式語言超集)       │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │   JavaScript (程式語言)      │  │  │
│  │  │                             │  │  │
│  │  └─────────────────────────────┘  │  │
│  │           編譯為 ↓                  │  │
│  └───────────────────────────────────┘  │
│                  執行 ↓                   │
└─────────────────────────────────────────┘
```

---

## 實際開發場景比較

### 簡單腳本
```javascript
// JavaScript（快速原型）
const fetch = require('node-fetch');
fetch('https://api.github.com/users/octocat')
    .then(res => res.json())
    .then(data => console.log(data.name));
```

### 中型專案
```typescript
// TypeScript（類型安全）
interface GitHubUser {
    login: string;
    name: string;
    public_repos: number;
}

async function getUser(username: string): Promise<GitHubUser> {
    const response = await fetch(`https://api.github.com/users/${username}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json() as Promise<GitHubUser>;
}

getUser('octocat').then(user => {
    console.log(`${user.name} has ${user.public_repos} public repos`);
});
```

### 生產級應用（Node.js + TypeScript）
```typescript
// server.ts
import express, { Request, Response, NextFunction } from 'express';
import { createConnection } from 'typeorm';
import { UserController } from './controllers/UserController';
import { errorHandler } from './middleware/errorHandler';
import { logger } from './utils/logger';

const app = express();

app.use(express.json());

// 路由
app.use('/api/users', UserController);

// 錯誤處理中介軟體
app.use(errorHandler);

// 啟動伺服器
async function bootstrap() {
    try {
        await createConnection();
        logger.info('Database connected');

        const PORT = process.env.PORT || 3000;
        app.listen(PORT, () => {
            logger.info(`Server running on port ${PORT}`);
        });
    } catch (error) {
        logger.error('Failed to start server:', error);
        process.exit(1);
    }
}

bootstrap();
```

---

## 選擇建議

| 場景 | 建議 |
|------|------|
| 小型腳本、快速原型 | JavaScript |
| 中大型專案、團隊協作 | TypeScript |
| 需要編譯期檢查 | TypeScript |
| 伺服器端開發 | Node.js + TypeScript |
| 全端統一語言 | Node.js (前端 JS/TS) |
| 學習階段 | 先 JavaScript，再 TypeScript |

---

## 總結

- **JavaScript**: 基礎程式語言，靈活但缺乏類型安全
- **TypeScript**: JavaScript 的超集，增加類型系統和語言特性
- **Node.js**: JavaScript 的執行環境，讓 JS 能跑在伺服器端

三者相輔相成：
- 學 Node.js 開發 → 必須先會 JavaScript
- 企業級 Node.js 開發 → 強烈建議使用 TypeScript
- TypeScript 編譯後 → 產出 JavaScript
- Node.js → 執行 JavaScript（或編譯後的 TypeScript）
