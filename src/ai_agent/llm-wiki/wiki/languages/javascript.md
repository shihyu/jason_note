---
title: JavaScript
tags: [javascript, web, frontend, backend]
sources: []
created: 2026-04-07
updated: 2026-04-07
---

# JavaScript

## 語言定位

> JavaScript 是 Web 的母語，從前端互動到後端服務（Node.js）到桌面/行動應用，全能發展。

## 核心特性

- **Event Loop**：非同步編程的核心
- **Prototype-based OOP**：原型鍊而非類別繼承
- **First-class functions**：函式是一等公民
- **Dynamic typing**：彈性但需小心
- **Single thread**：基於事件迴圈的併發

## 語法速查

```javascript
// 變數
let x = 10;        // 區塊範圍，可改值
const y = 20;      // 區塊範圍，不可改值
var z = 30;        // 函式範圍（舊，不推薦）

// 箭頭函式
const add = (a, b) => a + b;

// 解構賦值
const { name, age } = person;
const [first, second] = array;

// Promise + Async/Await
async function fetchData() {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}

// 類別（新語法）
class Point {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }
    
    distance() {
        return Math.sqrt(this.x ** 2 + this.y ** 2);
    }
}

// 模組
export { Point, add };
import { Point } from './point.js';
```

## JavaScript 併發模型

- **Event Loop**：單執行緒，事件驅動
- **Callback**：傳統非同步模式
- **Promise**：鏈式非同步
- **async/await**：Promise 的語法糖
- **Web Workers**：真正的多執行緒

## JS 生態

| 領域 | 常用框架/庫 |
|------|--------------|
| 前端框架 | React, Vue, Svelte, Angular |
| 後端 | Express, Fastify, NestJS |
| 行動 | React Native, Expo |
| 桌面 | Electron, Tauri |
| 建構工具 | Vite, webpack, esbuild |

## 相關概念

- [[concepts/併發模型]]
- [[concepts/錯誤處理]]
- [[concepts/設計模式]]

## 外部資源

- [MDN Web Docs](https://developer.mozilla.org/zh-TW/)
- [JavaScript.info](https://javascript.info/)
