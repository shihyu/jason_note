# Node.js 學習指南 - 從 Python/C++/Rust 背景出發

## 安裝 Node.js

### 方法 1：使用 Node Version Manager (NVM) - **推薦**

NVM 讓你能輕鬆切換不同版本的 Node.js（類似 Python 的 pyenv）

#### Linux/macOS
```bash
# 安裝 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
# 或使用 wget
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重新載入設定
source ~/.bashrc

# 安裝最新 LTS 版本
nvm install --lts
nvm use --lts

# 檢查版本
node --version
npm --version
```

#### Windows
```powershell
# 使用 nvm-windows (從 GitHub 下載安裝程式)
# https://github.com/coreybutler/nvm-windows/releases

# 安裝後執行
nvm install lts
nvm use lts
```

### 方法 2：官方安裝包
- 前往 https://nodejs.org/
- 下載 LTS 版本（長期支援版）
- 執行安裝程式

### 方法 3：套件管理器

#### Ubuntu/Debian
```bash
# 使用 NodeSource repository (推薦)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### macOS (Homebrew)
```bash
brew install node
```

#### Windows (Chocolatey)
```powershell
choco install nodejs
```

### 驗證安裝
```bash
node --version  # 應顯示 v20.x.x 或更新
npm --version   # Node Package Manager
npx --version   # npm 套件執行器
```

---

## 語法對照表

### 1. 變數宣告

| Node.js/JavaScript | Python | Rust | C++ |
|-------------------|---------|------|-----|
| `const x = 10;` | `x = 10` | `let x = 10;` | `const int x = 10;` |
| `let y = 20;` | `y = 20` | `let mut y = 20;` | `int y = 20;` |
| `var z = 30;` (避免) | - | - | - |

```javascript
// Node.js 範例
const PI = 3.14159;        // 常數（不可重新賦值）
let counter = 0;           // 變數（可重新賦值）
var oldStyle = "避免使用"; // 舊式宣告（作用域問題）

// 解構賦值（類似 Python 的 tuple unpacking）
const [a, b] = [1, 2];
const {name, age} = {name: "Alice", age: 30};
```

### 2. 函數定義

| 語言 | 基本函數 | Lambda/閉包 |
|-----|----------|------------|
| Node.js | `function add(a, b) { return a + b; }` | `(a, b) => a + b` |
| Python | `def add(a, b): return a + b` | `lambda a, b: a + b` |
| Rust | `fn add(a: i32, b: i32) -> i32 { a + b }` | `\|a, b\| a + b` |
| C++ | `int add(int a, int b) { return a + b; }` | `[](int a, int b) { return a + b; }` |

```javascript
// Node.js 多種函數寫法
// 1. 函數宣告
function greet(name) {
    return `Hello, ${name}!`;
}

// 2. 函數表達式
const greet = function(name) {
    return `Hello, ${name}!`;
};

// 3. 箭頭函數（最常用）
const greet = (name) => `Hello, ${name}!`;

// 4. 方法簡寫（物件內）
const obj = {
    greet(name) {
        return `Hello, ${name}!`;
    }
};

// 預設參數（類似 Python）
const greet = (name = "World") => `Hello, ${name}!`;

// Rest 參數（類似 Python 的 *args）
const sum = (...numbers) => numbers.reduce((a, b) => a + b, 0);

// 解構參數
const printUser = ({name, age}) => console.log(`${name} is ${age}`);
```

### 3. 資料結構

#### 陣列（Array）
```javascript
// Node.js
const arr = [1, 2, 3, 4, 5];

// 常用方法對照
arr.push(6);           // Python: arr.append(6)
arr.pop();             // Python: arr.pop()
arr.shift();           // Python: arr.pop(0)
arr.unshift(0);        // Python: arr.insert(0, 0)
arr.slice(1, 3);       // Python: arr[1:3]
arr.includes(3);       // Python: 3 in arr
arr.length;            // Python: len(arr)

// 函數式操作（類似 Rust 的 Iterator）
const doubled = arr.map(x => x * 2);              // Rust: .map(|x| x * 2)
const evens = arr.filter(x => x % 2 === 0);       // Rust: .filter(|x| x % 2 == 0)
const sum = arr.reduce((acc, x) => acc + x, 0);   // Rust: .fold(0, |acc, x| acc + x)

// 鏈式操作
const result = arr
    .filter(x => x > 2)
    .map(x => x * 2)
    .reduce((a, b) => a + b, 0);
```

#### 物件（Object）
```javascript
// Node.js 物件（類似 Python dict / Rust HashMap）
const person = {
    name: "Alice",
    age: 30,
    "special-key": "value",  // 特殊鍵名
    greet() {
        return `Hello, I'm ${this.name}`;
    }
};

// 存取
person.name;            // 點記法
person["special-key"];  // 括號記法（類似 Python dict）

// 物件操作
Object.keys(person);    // Python: person.keys()
Object.values(person);  // Python: person.values()
Object.entries(person); // Python: person.items()

// 展開運算子（類似 Python 的 **dict）
const newPerson = {...person, city: "Taipei"};

// 可選鏈（Optional Chaining）- 類似 Rust 的 ?
const city = person?.address?.city;  // 安全存取
```

### 4. 控制流程

```javascript
// if-else（與 C/Rust 類似）
if (condition) {
    // ...
} else if (otherCondition) {
    // ...
} else {
    // ...
}

// 三元運算子
const result = condition ? valueIfTrue : valueIfFalse;

// switch（類似 Rust 的 match，但較弱）
switch (value) {
    case 1:
        console.log("one");
        break;
    case 2:
    case 3:
        console.log("two or three");
        break;
    default:
        console.log("other");
}

// for 迴圈
for (let i = 0; i < 10; i++) { }              // C-style
for (const item of array) { }                 // Python: for item in array
for (const key in object) { }                 // Python: for key in object
array.forEach((item, index) => { });          // 函數式

// while
while (condition) { }
do { } while (condition);

// 迴圈控制
break;      // 跳出迴圈
continue;   // 跳過本次迭代
```

### 5. 類別與繼承

```javascript
// ES6 Class（類似 Python class）
class Animal {
    constructor(name) {
        this.name = name;  // 類似 Python 的 self.name
    }
    
    speak() {
        console.log(`${this.name} makes a sound`);
    }
    
    // Getter/Setter
    get age() {
        return this._age;
    }
    
    set age(value) {
        this._age = value;
    }
    
    // 靜態方法（類似 Python @staticmethod）
    static createDog(name) {
        return new Dog(name);
    }
}

// 繼承
class Dog extends Animal {
    constructor(name, breed) {
        super(name);  // 呼叫父類建構子
        this.breed = breed;
    }
    
    speak() {
        super.speak();
        console.log("Woof!");
    }
}

const dog = new Dog("Max", "Golden Retriever");
```

---

## 非同步程式設計（Node.js 核心）

### 1. Callback（回呼函數）- 舊式
```javascript
// Node.js 傳統回呼模式（error-first）
fs.readFile('file.txt', 'utf8', (err, data) => {
    if (err) {
        console.error(err);
        return;
    }
    console.log(data);
});

// 回呼地獄（Callback Hell）
getData((err, data) => {
    if (err) return handleError(err);
    processData(data, (err, result) => {
        if (err) return handleError(err);
        saveData(result, (err) => {
            if (err) return handleError(err);
            console.log('Done!');
        });
    });
});
```

### 2. Promise - 中間演進
```javascript
// Promise 基礎
const promise = new Promise((resolve, reject) => {
    setTimeout(() => {
        if (Math.random() > 0.5) {
            resolve('Success!');
        } else {
            reject(new Error('Failed'));
        }
    }, 1000);
});

// Promise 鏈
promise
    .then(result => console.log(result))
    .catch(error => console.error(error))
    .finally(() => console.log('Cleanup'));

// Promise 組合
Promise.all([promise1, promise2, promise3])       // 全部完成
Promise.race([promise1, promise2, promise3])      // 第一個完成
Promise.allSettled([promise1, promise2])          // 全部結束（不管成功失敗）
```

### 3. Async/Await - 現代寫法（類似 Python/Rust async）
```javascript
// 基本 async/await
async function fetchData() {
    try {
        const response = await fetch('https://api.example.com/data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}

// 並行執行
async function fetchMultiple() {
    // 錯誤：順序執行（慢）
    const data1 = await fetch('/api/1');
    const data2 = await fetch('/api/2');
    
    // 正確：並行執行（快）
    const [data1, data2] = await Promise.all([
        fetch('/api/1'),
        fetch('/api/2')
    ]);
    
    return {data1, data2};
}

// 非同步迭代
async function* generateNumbers() {
    for (let i = 0; i < 5; i++) {
        await new Promise(resolve => setTimeout(resolve, 100));
        yield i;
    }
}

// 使用非同步迭代器
for await (const num of generateNumbers()) {
    console.log(num);
}
```

---

## Event Loop（事件循環）

### 執行順序
```javascript
console.log('1: 同步程式碼');

setTimeout(() => console.log('2: Timer (宏任務)'), 0);

Promise.resolve().then(() => console.log('3: Promise (微任務)'));

process.nextTick(() => console.log('4: nextTick (最優先)'));

console.log('5: 同步程式碼');

// 輸出順序：1, 5, 4, 3, 2
```

### Event Loop 階段
1. **同步程式碼** - 立即執行
2. **process.nextTick** - Node.js 特有，最高優先級
3. **微任務（Microtasks）** - Promise callbacks, queueMicrotask
4. **宏任務（Macrotasks）** - setTimeout, setInterval, I/O

---

## 模組系統

### CommonJS（Node.js 傳統）
```javascript
// math.js - 匯出
function add(a, b) {
    return a + b;
}

module.exports = {
    add,
    subtract: (a, b) => a - b,
    PI: 3.14159
};

// main.js - 匯入
const math = require('./math');
const { add, PI } = require('./math');  // 解構匯入

console.log(math.add(2, 3));
console.log(PI);
```

### ES6 Modules（現代標準）
```javascript
// math.mjs - 匯出
export function add(a, b) {
    return a + b;
}

export const PI = 3.14159;

export default class Calculator {
    // ...
}

// main.mjs - 匯入
import Calculator, { add, PI } from './math.mjs';
import * as math from './math.mjs';  // 匯入全部

// 動態匯入
const module = await import('./math.mjs');
```

---

## 錯誤處理

```javascript
// 自定義錯誤類別
class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

// try-catch（類似其他語言）
try {
    throw new ValidationError('Invalid input');
} catch (error) {
    if (error instanceof ValidationError) {
        console.error('Validation failed:', error.message);
    } else {
        throw error;  // 重新拋出
    }
} finally {
    console.log('Cleanup');
}

// 非同步錯誤處理
async function riskyOperation() {
    try {
        const result = await someAsyncFunction();
        return result;
    } catch (error) {
        console.error('Async error:', error);
        throw error;
    }
}

// Promise 錯誤處理
promise
    .then(result => {
        if (!result.valid) {
            throw new Error('Invalid result');
        }
        return result;
    })
    .catch(error => {
        console.error('Promise rejected:', error);
    });

// 全域錯誤處理
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
```

---

## 重要內建模組

### File System (fs)
```javascript
const fs = require('fs').promises;  // 使用 Promise 版本

// 讀寫檔案
async function fileOperations() {
    // 讀檔
    const data = await fs.readFile('file.txt', 'utf8');
    
    // 寫檔
    await fs.writeFile('output.txt', data);
    
    // 檢查檔案存在
    try {
        await fs.access('file.txt');
        console.log('File exists');
    } catch {
        console.log('File does not exist');
    }
    
    // 讀取目錄
    const files = await fs.readdir('.');
    
    // 檔案資訊
    const stats = await fs.stat('file.txt');
    console.log(stats.size, stats.isDirectory());
}
```

### Path
```javascript
const path = require('path');

// 路徑操作
path.join('/users', 'john', 'documents', 'file.txt');
path.resolve('file.txt');  // 絕對路徑
path.dirname('/users/john/file.txt');  // '/users/john'
path.basename('/users/john/file.txt'); // 'file.txt'
path.extname('file.txt');  // '.txt'
```

### HTTP/HTTPS
```javascript
const http = require('http');

// 建立簡單伺服器
const server = http.createServer((req, res) => {
    if (req.url === '/' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end('Hello World\n');
    } else {
        res.writeHead(404);
        res.end('Not Found\n');
    }
});

server.listen(3000, () => {
    console.log('Server running at http://localhost:3000/');
});
```

### Process
```javascript
// 命令列參數
console.log(process.argv);  // ['node', 'script.js', ...args]

// 環境變數
console.log(process.env.NODE_ENV);

// 退出程式
process.exit(0);  // 0 = 成功, 非 0 = 錯誤

// 當前目錄
console.log(process.cwd());

// 記憶體使用
console.log(process.memoryUsage());

// 事件
process.on('exit', (code) => {
    console.log(`About to exit with code: ${code}`);
});
```

---

## JavaScript 特殊概念

### 1. 型別轉換（Type Coercion）
```javascript
// 自動型別轉換（與 Python/Rust 差異很大）
console.log(5 + "3");     // "53" (字串連接)
console.log(5 - "3");     // 2 (轉為數字)
console.log("5" * "3");   // 15 (轉為數字)
console.log(5 == "5");    // true (寬鬆相等)
console.log(5 === "5");   // false (嚴格相等，推薦)

// Truthy/Falsy
// Falsy: false, 0, "", null, undefined, NaN
// Truthy: 其他所有值（包括 [], {}）

if ([]) console.log("Empty array is truthy!");  // 會執行！
```

### 2. this 綁定
```javascript
// this 的值取決於如何呼叫函數
const obj = {
    value: 42,
    getValue() {
        return this.value;
    },
    getValueArrow: () => this.value,  // 箭頭函數的 this 不同！
    getValueLater() {
        setTimeout(() => {
            console.log(this.value);  // 箭頭函數保留 this
        }, 1000);
        
        setTimeout(function() {
            console.log(this.value);  // undefined（this 丟失）
        }, 1000);
    }
};

// 綁定 this
const getValue = obj.getValue.bind(obj);
```

### 3. 閉包（Closure）
```javascript
// 函數記住外部變數
function makeCounter() {
    let count = 0;
    return {
        increment: () => ++count,
        decrement: () => --count,
        getCount: () => count
    };
}

const counter = makeCounter();
console.log(counter.increment()); // 1
console.log(counter.increment()); // 2

// 常見陷阱
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100);  // 印出 3, 3, 3
}

// 修正方法
for (let i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100);  // 印出 0, 1, 2
}
```

### 4. 原型鏈（Prototype Chain）
```javascript
// JavaScript 的繼承機制
function Person(name) {
    this.name = name;
}

Person.prototype.greet = function() {
    return `Hello, I'm ${this.name}`;
};

const alice = new Person("Alice");
console.log(alice.greet());  // "Hello, I'm Alice"

// 原型鏈查找
console.log(alice.hasOwnProperty('name'));  // true
console.log(alice.hasOwnProperty('greet')); // false (在原型上)
```

---

## NPM（Node Package Manager）

### 基本指令
```bash
# 初始化專案（建立 package.json）
npm init -y

# 安裝套件
npm install express              # 生產依賴
npm install --save-dev eslint    # 開發依賴
npm install -g typescript        # 全域安裝

# 簡寫
npm i express
npm i -D eslint
npm i -g typescript

# 更新套件
npm update
npm update express

# 移除套件
npm uninstall express

# 列出套件
npm list
npm list --depth=0  # 只顯示第一層

# 執行腳本
npm run test
npm start  # 特殊腳本，不需要 run

# 安裝所有依賴（根據 package.json）
npm install

# 檢查過時套件
npm outdated

# 審計安全性問題
npm audit
npm audit fix
```

### package.json 範例
```json
{
  "name": "my-project",
  "version": "1.0.0",
  "description": "My Node.js project",
  "main": "index.js",
  "type": "module",  // 使用 ES6 模組
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest",
    "lint": "eslint ."
  },
  "dependencies": {
    "express": "^4.18.0",
    "mongoose": "^7.0.0"
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "jest": "^29.0.0",
    "nodemon": "^3.0.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=8.0.0"
  }
}
```

---

## TypeScript 整合（類似 Rust 的型別系統）

如果你喜歡 Rust 的型別安全，可以使用 TypeScript：

```typescript
// 型別定義
interface User {
    id: number;
    name: string;
    email?: string;  // 可選屬性
}

// 函數型別
function greet(user: User): string {
    return `Hello, ${user.name}!`;
}

// 泛型（類似 Rust）
function identity<T>(value: T): T {
    return value;
}

// 聯合型別
type Status = "pending" | "approved" | "rejected";

// 型別守衛
function isUser(obj: any): obj is User {
    return obj && typeof obj.id === 'number';
}

// Async 函數型別
async function fetchUser(id: number): Promise<User> {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
}
```

---

## 常用框架與工具

### Web 框架
- **Express.js** - 最流行的輕量級框架
- **Koa.js** - Express 的現代化版本
- **Fastify** - 高效能框架
- **NestJS** - 企業級框架（類似 Spring）

### 工具
- **nodemon** - 自動重啟（開發用）
- **pm2** - Process Manager（生產環境）
- **npm/yarn/pnpm** - 套件管理器
- **ESLint** - 程式碼檢查
- **Prettier** - 程式碼格式化

---

## 學習資源

### 官方文件
- Node.js 官方文件：https://nodejs.org/docs
- MDN JavaScript：https://developer.mozilla.org/zh-TW/docs/Web/JavaScript
- NPM 官方：https://docs.npmjs.com/

### 推薦書籍
- 《You Don't Know JS》系列
- 《Node.js Design Patterns》
- 《JavaScript: The Good Parts》

### 線上教學
- Node.js 官方教學：https://nodejs.dev/learn
- The Odin Project：https://www.theodinproject.com/
- freeCodeCamp：https://www.freecodecamp.org/

### 實作專案建議
1. CLI 工具（類似 Python script）
2. REST API 伺服器
3. WebSocket 即時聊天
4. 檔案處理工具
5. Web Scraper

---

## 從 Python/Rust 背景的提醒

### 與 Python 的差異
1. **非同步是預設**：Node.js 的 I/O 操作預設非阻塞
2. **單執行緒**：用事件循環處理並發，不是多執行緒
3. **原型繼承**：不是傳統的 class-based OOP
4. **弱型別**：需要更多防禦性程式設計
5. **this 綁定**：比 self 複雜很多

### 與 Rust 的差異
1. **沒有所有權系統**：需要手動管理記憶體洩漏
2. **執行時錯誤**：沒有編譯時保證
3. **可變性**：預設可變，用 const 來限制
4. **null/undefined**：兩種空值概念
5. **型別安全**：使用 TypeScript 獲得部分型別保證

### 最佳實踐
1. **永遠使用 `===` 而非 `==`**
2. **優先使用 const，其次 let，避免 var**
3. **使用 async/await 而非 callback**
4. **啟用 strict mode：`'use strict';`**
5. **處理所有錯誤情況**
6. **使用 ESLint 和 Prettier**
7. **考慮使用 TypeScript**
8. **理解事件循環**
9. **避免阻塞事件循環**
10. **適當使用 npm scripts**

---

## 快速開始範例

### Hello World API Server
```javascript
// server.js
import express from 'express';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Routes
app.get('/', (req, res) => {
    res.json({ message: 'Hello World!' });
});

app.get('/users/:id', async (req, res) => {
    try {
        const { id } = req.params;
        // 模擬資料庫查詢
        const user = await getUserById(id);
        res.json(user);
    } catch (error) {
        res.status(404).json({ error: 'User not found' });
    }
});

// 啟動伺服器
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});

// 模擬非同步函數
async function getUserById(id) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (id === '1') {
                resolve({ id: 1, name: 'Alice' });
            } else {
                reject(new Error('Not found'));
            }
        }, 100);
    });
}
```

執行：
```bash
npm init -y
npm install express
node server.js
```

---

祝你學習順利！有 Python/C++/Rust 背景學 Node.js 會很快上手的。重點是理解事件驅動模型和非同步程式設計。