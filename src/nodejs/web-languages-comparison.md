# Web 語言特性比較：JavaScript/TypeScript vs Go

## 📋 目錄
- [JavaScript (Node.js)](#javascript-nodejs)
- [TypeScript](#typescript)
- [Go (Golang)](#go-golang)
- [三者詳細對比](#三者詳細對比)
- [與系統語言簡單對比](#與系統語言簡單對比)

---

## JavaScript (Node.js)

### 🎯 語言特性

#### **1. 動態型別**
```javascript
let data = 42;        // 數字
data = "hello";       // 改成字串，完全合法
data = { name: "John" }; // 改成物件
```
- ✅ 靈活、快速開發
- ❌ 執行時才發現型別錯誤

#### **2. 單執行緒 + Event Loop**
```javascript
console.log('1');
setTimeout(() => console.log('2'), 0);
console.log('3');
// 輸出: 1, 3, 2
```
- 所有 I/O 操作都是非阻塞的
- 透過 callback queue 和 event loop 處理

#### **3. 非同步模型演進**

**Callback (舊)**
```javascript
fs.readFile('file.txt', (err, data) => {
  if (err) throw err;
  console.log(data);
});
```

**Promise (ES6)**
```javascript
fetch('https://api.example.com/data')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));
```

**Async/Await (ES8)**
```javascript
async function getData() {
  try {
    const response = await fetch('https://api.example.com/data');
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}
```

#### **4. 原型鏈繼承**
```javascript
function Animal(name) {
  this.name = name;
}

Animal.prototype.speak = function() {
  console.log(`${this.name} makes a sound`);
};

const dog = new Animal('Dog');
dog.speak(); // Dog makes a sound
```

#### **5. 一等公民函數**
```javascript
// 函數可以當變數
const add = (a, b) => a + b;

// 函數可以當參數
const numbers = [1, 2, 3];
const doubled = numbers.map(n => n * 2);

// 閉包 (Closure)
function makeCounter() {
  let count = 0;
  return () => ++count;
}
const counter = makeCounter();
console.log(counter()); // 1
console.log(counter()); // 2
```

#### **6. 弱型別轉換**
```javascript
console.log(1 + "2");      // "12" (字串)
console.log("5" - 2);      // 3 (數字)
console.log(true + 1);     // 2
console.log([] == false);  // true (!)
```
- ❌ 容易產生難以追蹤的 bug

#### **7. 垃圾回收 (GC)**
- V8 引擎自動管理記憶體
- 開發者無需手動釋放記憶體
- ❌ 可能有 GC pause

---

### 🔧 Node.js 特性

#### **1. 模組系統**

**CommonJS (傳統)**
```javascript
// module.js
module.exports = {
  add: (a, b) => a + b
};

// main.js
const math = require('./module');
console.log(math.add(1, 2));
```

**ES Modules (現代)**
```javascript
// module.mjs
export const add = (a, b) => a + b;

// main.mjs
import { add } from './module.mjs';
console.log(add(1, 2));
```

#### **2. npm 生態系**
- 全球最大的套件管理系統
- 超過 200 萬個套件
- 快速整合第三方功能

#### **3. 單執行緒限制**
```javascript
// CPU 密集任務會阻塞
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

// 這會阻塞整個程式
console.log(fibonacci(40)); // 需要幾秒鐘
```

**解決方案：Worker Threads**
```javascript
const { Worker } = require('worker_threads');

const worker = new Worker('./heavy-task.js');
worker.on('message', result => console.log(result));
```

#### **4. 併發模型**
```javascript
// 可以同時處理 10000+ 連線
const http = require('http');

http.createServer((req, res) => {
  // 非阻塞 I/O
  res.writeHead(200);
  res.end('Hello World');
}).listen(3000);
```

---

## TypeScript

### 🎯 語言特性

#### **1. 靜態型別系統**
```typescript
// 基本型別
let age: number = 25;
let name: string = "John";
let isActive: boolean = true;

// 陣列
let numbers: number[] = [1, 2, 3];
let strings: Array<string> = ["a", "b", "c"];

// 物件型別
interface User {
  id: number;
  name: string;
  email?: string; // 可選屬性
}

const user: User = {
  id: 1,
  name: "John"
};
```

#### **2. 型別推斷**
```typescript
// 自動推斷型別
let count = 0; // 推斷為 number
count = "hello"; // ❌ 錯誤：不能將 string 賦值給 number

// 函數返回值推斷
function add(a: number, b: number) {
  return a + b; // 推斷返回 number
}
```

#### **3. 介面 (Interface)**
```typescript
interface Animal {
  name: string;
  speak(): void;
}

class Dog implements Animal {
  name: string;
  
  constructor(name: string) {
    this.name = name;
  }
  
  speak(): void {
    console.log(`${this.name} barks!`);
  }
}
```

#### **4. 泛型 (Generics)**
```typescript
// 泛型函數
function identity<T>(arg: T): T {
  return arg;
}

let output1 = identity<string>("hello");
let output2 = identity<number>(42);

// 泛型介面
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

const response: ApiResponse<User> = {
  data: { id: 1, name: "John" },
  status: 200,
  message: "Success"
};
```

#### **5. 聯合型別 (Union Types)**
```typescript
// 變數可以是多種型別之一
let value: string | number;
value = "hello"; // ✅
value = 42;      // ✅
value = true;    // ❌ 錯誤

// 實用範例
type Status = "pending" | "success" | "error";

function handleStatus(status: Status) {
  if (status === "success") {
    console.log("Operation succeeded");
  }
}
```

#### **6. 型別守衛 (Type Guards)**
```typescript
function processValue(value: string | number) {
  if (typeof value === "string") {
    // 這裡 TypeScript 知道 value 是 string
    console.log(value.toUpperCase());
  } else {
    // 這裡 TypeScript 知道 value 是 number
    console.log(value.toFixed(2));
  }
}
```

#### **7. Enum 列舉**
```typescript
enum Direction {
  Up = "UP",
  Down = "DOWN",
  Left = "LEFT",
  Right = "RIGHT"
}

function move(direction: Direction) {
  console.log(`Moving ${direction}`);
}

move(Direction.Up);
```

#### **8. 嚴格空值檢查**
```typescript
// 啟用 strictNullChecks
let userName: string;
userName = "John";    // ✅
userName = null;      // ❌ 錯誤

// 明確允許 null
let userEmail: string | null = null; // ✅
```

#### **9. 編譯時檢查**
```typescript
interface Product {
  id: number;
  name: string;
  price: number;
}

function getProduct(id: number): Product {
  // ❌ 編譯時就會報錯：缺少 price 屬性
  return {
    id: id,
    name: "Product"
  };
}
```

---

### 🔧 TypeScript 特有功能

#### **1. 裝飾器 (Decorators)**
```typescript
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  
  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${propertyKey} with`, args);
    return originalMethod.apply(this, args);
  };
}

class Calculator {
  @log
  add(a: number, b: number) {
    return a + b;
  }
}
```

#### **2. 命名空間 (Namespaces)**
```typescript
namespace Validation {
  export interface StringValidator {
    isValid(s: string): boolean;
  }
  
  export class EmailValidator implements StringValidator {
    isValid(s: string): boolean {
      return s.includes("@");
    }
  }
}

let validator = new Validation.EmailValidator();
```

#### **3. 型別別名 (Type Aliases)**
```typescript
type Point = {
  x: number;
  y: number;
};

type ID = string | number;

type Callback = (data: string) => void;
```

#### **4. 條件型別**
```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>;  // true
type B = IsString<number>;  // false
```

---

## Go (Golang)

### 🎯 語言特性

#### **1. 靜態強型別**
```go
package main

import "fmt"

func main() {
    var age int = 25
    var name string = "John"
    
    // 型別推斷
    count := 42  // 自動推斷為 int
    
    // ❌ 錯誤：型別不匹配
    // age = "hello"  // 編譯錯誤
}
```

#### **2. Goroutine - 輕量級執行緒**
```go
package main

import (
    "fmt"
    "time"
)

func sayHello(name string) {
    fmt.Printf("Hello, %s!\n", name)
}

func main() {
    // 啟動 goroutine
    go sayHello("World")
    go sayHello("Go")
    
    // 等待 goroutines 完成
    time.Sleep(time.Second)
}
```

**特性：**
- 一個 goroutine 只佔用約 2KB 記憶體
- 可以輕鬆創建數萬個 goroutines
- 由 Go runtime 排程管理

#### **3. Channel - 通訊機制**
```go
package main

import "fmt"

func sum(numbers []int, resultChan chan int) {
    total := 0
    for _, num := range numbers {
        total += num
    }
    resultChan <- total  // 發送結果到 channel
}

func main() {
    numbers := []int{1, 2, 3, 4, 5}
    resultChan := make(chan int)
    
    go sum(numbers[:len(numbers)/2], resultChan)
    go sum(numbers[len(numbers)/2:], resultChan)
    
    // 接收結果
    result1 := <-resultChan
    result2 := <-resultChan
    
    fmt.Println("Total:", result1+result2)
}
```

**Channel 特性：**
- 用於 goroutines 之間安全通訊
- 避免共享記憶體的競爭條件
- "Don't communicate by sharing memory; share memory by communicating"

#### **4. 結構體 (Struct) 與方法**
```go
package main

import "fmt"

// 定義結構體
type Person struct {
    Name string
    Age  int
}

// 方法
func (p Person) Greet() {
    fmt.Printf("Hello, I'm %s\n", p.Name)
}

// 指標接收者方法（可以修改結構體）
func (p *Person) Birthday() {
    p.Age++
}

func main() {
    person := Person{Name: "John", Age: 25}
    person.Greet()
    person.Birthday()
    fmt.Println(person.Age)  // 26
}
```

#### **5. 介面 (Interface)**
```go
package main

import "fmt"

// 定義介面
type Speaker interface {
    Speak() string
}

// Dog 實現 Speaker
type Dog struct {
    Name string
}

func (d Dog) Speak() string {
    return "Woof!"
}

// Cat 實現 Speaker
type Cat struct {
    Name string
}

func (c Cat) Speak() string {
    return "Meow!"
}

// 多型
func MakeSound(s Speaker) {
    fmt.Println(s.Speak())
}

func main() {
    dog := Dog{Name: "Buddy"}
    cat := Cat{Name: "Whiskers"}
    
    MakeSound(dog)  // Woof!
    MakeSound(cat)  // Meow!
}
```

**Go 介面特性：**
- 隱式實現（不需要明確聲明）
- 只要實現了介面的所有方法就自動滿足介面

#### **6. 錯誤處理**
```go
package main

import (
    "errors"
    "fmt"
)

func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

func main() {
    result, err := divide(10, 2)
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    fmt.Println("Result:", result)
}
```

**特性：**
- 沒有 try-catch
- 錯誤作為返回值顯式處理
- 強制開發者處理錯誤

#### **7. Defer 語句**
```go
package main

import "fmt"

func main() {
    defer fmt.Println("World")  // 最後執行
    fmt.Println("Hello")
    
    // 輸出：
    // Hello
    // World
}

// 實用範例：資源清理
func readFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close()  // 確保文件被關閉
    
    // 讀取文件...
    return nil
}
```

#### **8. 多返回值**
```go
package main

import "fmt"

func swap(a, b int) (int, int) {
    return b, a
}

func divmod(a, b int) (quotient, remainder int) {
    quotient = a / b
    remainder = a % b
    return  // 命名返回值可以直接 return
}

func main() {
    x, y := swap(1, 2)
    fmt.Println(x, y)  // 2 1
    
    q, r := divmod(10, 3)
    fmt.Println(q, r)  // 3 1
}
```

#### **9. 指標**
```go
package main

import "fmt"

func modifyValue(x *int) {
    *x = 100
}

func main() {
    value := 42
    fmt.Println("Before:", value)  // 42
    
    modifyValue(&value)
    fmt.Println("After:", value)   // 100
}
```

**Go 指標特性：**
- 有指標但沒有指標運算
- 更安全、更簡單
- 垃圾回收自動管理

#### **10. Select 語句**
```go
package main

import (
    "fmt"
    "time"
)

func main() {
    ch1 := make(chan string)
    ch2 := make(chan string)
    
    go func() {
        time.Sleep(1 * time.Second)
        ch1 <- "from channel 1"
    }()
    
    go func() {
        time.Sleep(2 * time.Second)
        ch2 <- "from channel 2"
    }()
    
    // Select 等待多個 channel
    for i := 0; i < 2; i++ {
        select {
        case msg1 := <-ch1:
            fmt.Println(msg1)
        case msg2 := <-ch2:
            fmt.Println(msg2)
        }
    }
}
```

#### **11. 內建併發安全**
```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    var counter int
    var mutex sync.Mutex
    var wg sync.WaitGroup
    
    // 啟動 1000 個 goroutines
    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            mutex.Lock()
            counter++
            mutex.Unlock()
        }()
    }
    
    wg.Wait()
    fmt.Println("Counter:", counter)  // 1000
}
```

---

### 🔧 Go 特有功能

#### **1. 編譯速度快**
```bash
# 編譯整個專案通常只需要幾秒
go build .
```

#### **2. 單一可執行檔**
```bash
# 編譯後產生單一二進位檔，包含所有依賴
go build -o myapp
./myapp  # 直接執行，無需安裝任何依賴
```

#### **3. 交叉編譯**
```bash
# 在 Mac 上編譯 Linux 版本
GOOS=linux GOARCH=amd64 go build -o myapp-linux

# 在 Linux 上編譯 Windows 版本
GOOS=windows GOARCH=amd64 go build -o myapp.exe
```

#### **4. 內建工具鏈**
```bash
go fmt      # 格式化程式碼
go test     # 執行測試
go vet      # 檢查程式碼問題
go mod      # 管理依賴
go doc      # 查看文件
```

#### **5. 標準庫豐富**
```go
// HTTP 伺服器
package main

import (
    "fmt"
    "net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, World!")
}

func main() {
    http.HandleFunc("/", handler)
    http.ListenAndServe(":8080", nil)
}
```

---

## 三者詳細對比

### 📊 語言特性比較表

| 特性 | JavaScript | TypeScript | Go |
|------|-----------|-----------|-----|
| **型別系統** | 動態型別 | 靜態型別 | 靜態強型別 |
| **型別檢查** | 執行時 | 編譯時 | 編譯時 |
| **併發模型** | Event Loop + 單執行緒 | Event Loop + 單執行緒 | Goroutines + Channels |
| **記憶體管理** | GC (V8) | GC (V8) | GC (更高效) |
| **編譯** | 無需編譯（JIT） | 編譯成 JS | 編譯成機器碼 |
| **執行速度** | 中等 | 中等 | 快 |
| **開發速度** | 非常快 | 快 | 中等 |
| **學習曲線** | 平緩 | 中等 | 中等 |
| **錯誤處理** | try-catch + Promise | try-catch + Promise | 多返回值 + error |
| **物件導向** | 原型鏈 | 類別 + 介面 | 結構體 + 介面 |

---

### 🔄 併發模型深度對比

#### **JavaScript/TypeScript - Event Loop**

```javascript
// 單執行緒，但可以處理高併發 I/O
async function fetchMultipleUrls(urls) {
  // 所有請求同時發出（非阻塞）
  const promises = urls.map(url => fetch(url));
  const responses = await Promise.all(promises);
  return responses;
}

// 10000 個請求可以同時處理
const urls = Array(10000).fill('https://api.example.com/data');
fetchMultipleUrls(urls);
```

**優點：**
- ✅ 程式碼簡單，易於理解
- ✅ 避免多執行緒的競爭條件
- ✅ 高 I/O 併發能力

**缺點：**
- ❌ CPU 密集任務會阻塞
- ❌ 無法利用多核心 CPU

---

#### **Go - Goroutines**

```go
package main

import (
    "fmt"
    "sync"
)

func fetchURL(url string, wg *sync.WaitGroup, results chan<- string) {
    defer wg.Done()
    // 模擬網路請求
    result := fmt.Sprintf("Fetched: %s", url)
    results <- result
}

func main() {
    urls := make([]string, 10000)
    results := make(chan string, 10000)
    var wg sync.WaitGroup
    
    // 啟動 10000 個 goroutines
    for _, url := range urls {
        wg.Add(1)
        go fetchURL(url, &wg, results)
    }
    
    wg.Wait()
    close(results)
}
```

**優點：**
- ✅ 真正的平行處理
- ✅ 可以利用多核心 CPU
- ✅ 輕量級（一個 goroutine 只需 2KB）
- ✅ 適合 CPU 密集任務

**缺點：**
- ❌ 需要處理競爭條件（race conditions）
- ❌ Channel 和 goroutine 的管理較複雜

---

### ⚡ 性能對比

#### **Web API 負載測試（10000 併發請求）**

**JavaScript/Node.js:**
```javascript
// 簡單 HTTP 伺服器
const http = require('http');

http.createServer((req, res) => {
  res.writeHead(200);
  res.end('Hello World');
}).listen(3000);
```
- **吞吐量**: ~30,000 req/s
- **記憶體**: ~50MB
- **CPU**: 單核使用率 100%

**Go:**
```go
package main

import (
    "fmt"
    "net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello World")
}

func main() {
    http.HandleFunc("/", handler)
    http.ListenAndServe(":8080", nil)
}
```
- **吞吐量**: ~100,000 req/s
- **記憶體**: ~20MB
- **CPU**: 多核平均分配

---

### 💻 開發體驗對比

#### **JavaScript - 快速原型開發**
```javascript
// 快速建立 REST API
const express = require('express');
const app = express();

app.get('/api/users', async (req, res) => {
  const users = await db.query('SELECT * FROM users');
  res.json(users);
});

app.listen(3000);
```

**優點：**
- 快速迭代
- 豐富的 npm 套件
- 前後端共用語言

---

#### **TypeScript - 大型專案開發**
```typescript
// 型別安全的 API
interface User {
  id: number;
  name: string;
  email: string;
}

interface ApiResponse<T> {
  data: T;
  error?: string;
}

async function getUser(id: number): Promise<ApiResponse<User>> {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}

// 編譯時就能發現錯誤
const user = await getUser(1);
console.log(user.data.name);  // 型別安全
```

**優點：**
- 編譯時錯誤檢查
- IDE 自動補全
- 重構更安全
- 適合團隊協作

---

#### **Go - 高性能服務開發**
```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
)

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

func getUser(w http.ResponseWriter, r *http.Request) {
    user := User{ID: 1, Name: "John", Email: "john@example.com"}
    json.NewEncoder(w).Encode(user)
}

func main() {
    http.HandleFunc("/api/users", getUser)
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

**優點：**
- 高性能
- 編譯型，部署簡單（單一二進位檔）
- 內建併發支援
- 適合微服務

---

### 🎯 最佳使用場景

#### **JavaScript/Node.js 適合：**
- ✅ 快速原型開發
- ✅ 前端開發（React, Vue, Angular）
- ✅ 即時應用（WebSocket、聊天室）
- ✅ 小型 API 服務
- ✅ 伺服器端渲染（SSR）
- ✅ Serverless Functions

**範例專案：**
- Express.js API
- Next.js 全端應用
- Socket.io 即時通訊
- 自動化腳本

---

#### **TypeScript 適合：**
- ✅ 大型企業應用
- ✅ 長期維護的專案
- ✅ 團隊協作開發
- ✅ 需要重構的舊專案
- ✅ 複雜的前端應用

**範例專案：**
- Angular 企業應用
- NestJS 後端框架
- React + TypeScript 大型 SPA
- 微服務架構

---

#### **Go 適合：**
- ✅ 高併發服務
- ✅ 微服務架構
- ✅ 雲原生應用
- ✅ DevOps 工具
- ✅ 分散式系統
- ✅ CLI 工具

**範例專案：**
- Kubernetes
- Docker
- Prometheus
- gRPC 服務
- 高性能 API Gateway

---

### 📈 生態系統對比

| 特性 | JavaScript/TypeScript | Go |
|------|---------------------|-----|
| **套件數量** | 2,000,000+ (npm) | 100,000+ |
| **套件品質** | 參差不齊 | 較高品質 |
| **標準庫** | 較小，依賴第三方 | 豐富且完整 |
| **框架** | Express, Nest, Koa, Fastify | Gin, Echo, Fiber |
| **ORM** | Prisma, TypeORM, Sequelize | GORM, sqlx |
| **測試** | Jest, Mocha, Vitest | 內建 testing 套件 |
| **文件** | 豐富但分散 | 官方文件完善 |

---

### 🔐 型別安全對比

#### **JavaScript - 執行時錯誤**
```javascript
function calculateTotal(price, quantity) {
  return price * quantity;
}

console.log(calculateTotal(100, 2));      // 200 ✅
console.log(calculateTotal("100", "2"));  // "10010" ❌ (字串相乘)
console.log(calculateTotal(100));         // NaN ❌ (undefined * 100)
```

---

#### **TypeScript - 編譯時檢查**
```typescript
function calculateTotal(price: number, quantity: number): number {
  return price * quantity;
}

console.log(calculateTotal(100, 2));      // 200 ✅
// console.log(calculateTotal("100", "2"));  // ❌ 編譯錯誤
// console.log(calculateTotal(100));         // ❌ 編譯錯誤
```

---

#### **Go - 嚴格型別**
```go
func calculateTotal(price float64, quantity int) float64 {
    return price * float64(quantity)
}

fmt.Println(calculateTotal(100.0, 2))   // 200 ✅
// fmt.Println(calculateTotal("100", "2"))  // ❌ 編譯錯誤
// fmt.Println(calculateTotal(100))         // ❌ 編譯錯誤
```

---

### 🛠️ 錯誤處理比較

#### **JavaScript - try-catch**
```javascript
async function fetchData(url) {
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

---

#### **TypeScript - 型別安全的錯誤處理**
```typescript
type Result<T, E> = 
  | { ok: true; value: T }
  | { ok: false; error: E };

async function fetchData(url: string): Promise<Result<Data, Error>> {
  try {
    const response = await fetch(url);
    const data = await response.json();
    return { ok: true, value: data };
  } catch (error) {
    return { ok: false, error: error as Error };
  }
}

// 使用
const result = await fetchData('/api/data');
if (result.ok) {
  console.log(result.value);  // 型別安全
} else {
  console.error(result.error);
}
```

---

#### **Go - 顯式錯誤處理**
```go
func fetchData(url string) (*Data, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    var data Data
    err = json.NewDecoder(resp.Body).Decode(&data)
    if err != nil {
        return nil, err
    }
    
    return &data, nil
}

// 使用
data, err := fetchData("https://api.example.com")
if err != nil {
    log.Fatal(err)
}
fmt.Println(data)
```

**Go 錯誤處理優點：**
- 強制處理錯誤（不能忽略）
- 錯誤路徑清晰
- 無隱藏的異常

---

### 🚀 部署與維運對比

#### **JavaScript/TypeScript**
```bash
# 需要 Node.js 運行環境
npm install
npm start

# Docker 部署
FROM node:18
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "start"]
```

**部署大小：** ~100MB+（包含 node_modules）

---

#### **Go**
```bash
# 編譯成單一可執行檔
go build -o app

# 直接執行，無需額外依賴
./app

# Docker 部署（多階段構建）
FROM golang:1.21 AS builder
COPY . .
RUN go build -o app

FROM alpine:latest
COPY --from=builder /app .
CMD ["./app"]
```

**部署大小：** ~10MB（單一二進位檔）

**Go 部署優勢：**
- ✅ 無需安裝運行環境
- ✅ 容器化體積小
- ✅ 冷啟動快
- ✅ 交叉編譯方便

---

### 📊 記憶體與性能總結

| 場景 | JavaScript/TS | Go | 結論 |
|------|--------------|-----|------|
| **簡單 HTTP 服務** | 50MB / 30k req/s | 20MB / 100k req/s | Go 快 3x |
| **WebSocket 連線** | 1000 連線 / 100MB | 10000 連線 / 50MB | Go 更高效 |
| **CPU 密集計算** | 慢（單執行緒） | 快（多核心） | Go 完勝 |
| **I/O 密集任務** | 快 | 快 | 相當 |
| **啟動時間** | 快（即時） | 快（編譯） | 相當 |
| **記憶體佔用** | 中等 | 低 | Go 更省 |

---

## 與系統語言簡單對比

### C/C++
- **特點：** 手動記憶體管理、極致性能、接近硬體
- **vs Web 語言：** 開發慢、難度高、但性能最強
- **適用：** 作業系統、遊戲引擎、嵌入式系統

### Rust
- **特點：** 所有權系統、記憶體安全、無 GC
- **vs Web 語言：** 學習曲線陡峭、編譯慢、但安全且快速
- **適用：** 系統編程、WebAssembly、高性能微服務

### 關鍵差異
```
系統語言 (C/C++/Rust):
├─ CPU 運算為主
├─ 手動/所有權記憶體管理
├─ 編譯成機器碼
└─ 極致性能

Web 語言 (JS/TS/Go):
├─ I/O 併發為主
├─ GC 自動記憶體管理
├─ 快速開發
└─ 平衡性能與生產力
```

---

## 🎓 選擇建議

### 選擇 JavaScript
- 快速原型開發
- 前端 + 後端統一技術棧
- 團隊熟悉 JS 生態
- Serverless 應用

### 選擇 TypeScript
- 大型企業專案
- 長期維護需求
- 需要重構的舊專案
- 團隊協作開發

### 選擇 Go
- 高併發服務
- 微服務架構
- 雲原生應用
- DevOps 工具
- 需要極致性能

### 選擇系統語言 (C/C++/Rust)
- 作業系統開發
- 遊戲引擎
- 嵌入式系統
- WebAssembly
- 對性能極度敏感的場景

---

## 📚 總結

### Web 語言核心差異

| 維度 | JavaScript | TypeScript | Go |
|------|-----------|-----------|-----|
| **核心優勢** | 快速開發 | 型別安全 | 高併發 |
| **最大缺點** | 執行時錯誤多 | 需要編譯 | 學習曲線 |
| **最佳場景** | 原型/小專案 | 大型專案 | 高性能服務 |
| **團隊規模** | 小型 | 中大型 | 中大型 |

### 併發模型本質

- **JS/TS：** 單執行緒 + Event Loop = I/O 併發強，CPU 併發弱
- **Go：** Goroutines + Channels = I/O 與 CPU 併發都強
- **系統語言：** 手動管理多執行緒 = 最大靈活性與複雜度

### 最終建議

1. **小型專案/快速迭代** → JavaScript
2. **中大型專案/長期維護** → TypeScript
3. **高併發/微服務/DevOps** → Go
4. **系統編程/極致性能** → C/C++/Rust

記住：**沒有最好的語言，只有最適合的語言**。選擇取決於：
- 專案需求（I/O vs CPU）
- 團隊技能
- 開發速度要求
- 性能要求
- 維護成本
