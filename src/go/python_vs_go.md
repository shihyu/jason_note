# Python → Go 語法完整對照指南

> 給有 Python 底子的開發者快速上手 Go 語言

---

## 目錄

1. [基本概念差異](#1-基本概念差異)
2. [Hello World](#2-hello-world)
3. [變數宣告](#3-變數宣告)
4. [基本資料型別](#4-基本資料型別)
5. [字串操作](#5-字串操作)
6. [運算子](#6-運算子)
7. [條件判斷](#7-條件判斷)
8. [迴圈](#8-迴圈)
9. [函式](#9-函式)
10. [集合型別：List / Slice](#10-集合型別list--slice)
11. [集合型別：Dict / Map](#11-集合型別dict--map)
12. [集合型別：Tuple / Struct](#12-集合型別tuple--struct)
13. [Set 集合](#13-set-集合)
14. [物件導向：Class / Struct + Method](#14-物件導向class--struct--method)
15. [介面 Interface](#15-介面-interface)
16. [錯誤處理](#16-錯誤處理)
17. [Goroutine 與並發（Go 獨有）](#17-goroutine-與並發go-獨有)
18. [Channel（Go 獨有）](#18-channelgo-獨有)
19. [模組與套件](#19-模組與套件)
20. [常用標準庫對照](#20-常用標準庫對照)
21. [類型斷言與反射](#21-類型斷言與反射)
22. [Defer / Context Manager](#22-defer--context-manager)
23. [指標 Pointer](#23-指標-pointer)
24. [Go 特有概念總整理](#24-go-特有概念總整理)

---

## 1. 基本概念差異

| 特性 | Python | Go |
|------|--------|----|
| 型別系統 | 動態型別 | **靜態型別**（編譯期確定） |
| 編譯方式 | 直譯（Interpreted） | **編譯（Compiled）** |
| 縮排 | 用縮排定義區塊 | 用 `{}` 定義區塊 |
| 行尾 | 不需要分號 | 不需要分號（自動插入） |
| Null 值 | `None` | `nil` |
| 布林值 | `True` / `False` | `true` / `false` |
| 繼承 | 支援繼承 | **無繼承**，用組合（Composition） |
| 並發 | threading / asyncio | **goroutine**（原生、輕量） |
| 未使用變數 | 允許 | **編譯錯誤**（強制使用） |
| 未使用 import | 允許 | **編譯錯誤** |

---

## 2. Hello World

```python
# Python
print("Hello, World!")
```

```go
// Go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```

> ⚠️ Go 每個檔案都必須有 `package` 宣告，程式進入點必須是 `package main` 的 `main()` 函式。

---

## 3. 變數宣告

```python
# Python - 動態型別，直接賦值
x = 10
name = "Alice"
pi = 3.14
is_ok = True
```

```go
// Go - 方法一：完整宣告
var x int = 10
var name string = "Alice"
var pi float64 = 3.14
var is_ok bool = true

// Go - 方法二：型別推斷（最常用）
x := 10
name := "Alice"
pi := 3.14
isOk := true

// Go - 方法三：批次宣告
var (
    x    int    = 10
    name string = "Alice"
)

// 零值（Go 特有）：宣告但不賦值，會有預設零值
var count int    // 0
var msg   string // ""
var flag  bool   // false
var ptr   *int   // nil
```

> 💡 `:=` 是 Go 最常見的短變數宣告，只能在函式內使用。

---

## 4. 基本資料型別

| Python | Go | 說明 |
|--------|----|------|
| `int` | `int`, `int8`, `int16`, `int32`, `int64` | Go 有明確位元寬度 |
| `float` | `float32`, `float64` | |
| `bool` | `bool` | |
| `str` | `string` | Go 字串是 UTF-8 bytes，不可變 |
| `bytes` | `[]byte` | |
| 無 | `rune` | 等同 `int32`，代表一個 Unicode 字元 |
| 無 | `uint`, `uintptr` | 無號整數 |
| `complex` | `complex64`, `complex128` | 複數 |

```go
// Go 型別轉換（必須明確，不會自動轉換）
var i int = 42
var f float64 = float64(i)   // int → float64
var s string = string(rune(65)) // → "A"

// Python 可以直接做，Go 不行：
// i + f  ← 編譯錯誤，型別不符
```

---

## 5. 字串操作

```python
# Python
s = "Hello"
print(len(s))           # 5
print(s[0])             # 'H'
print(s[1:3])           # 'el'
print(s.upper())        # 'HELLO'
print(s + " World")     # 'Hello World'
print(f"Hi {s}")        # f-string
print("l" in s)         # True
```

```go
// Go
import (
    "fmt"
    "strings"
)

s := "Hello"
fmt.Println(len(s))              // 5 (byte 數)
fmt.Println(string(s[0]))        // "H"
fmt.Println(s[1:3])              // "el"
fmt.Println(strings.ToUpper(s))  // "HELLO"
fmt.Println(s + " World")        // "Hello World"
fmt.Printf("Hi %s\n", s)        // Printf 格式化
fmt.Println(strings.Contains(s, "l")) // true

// 多行字串
raw := `這是
多行字串`

// 字串轉數字
import "strconv"
n, err := strconv.Atoi("42")     // string → int
str := strconv.Itoa(42)          // int → string
```

**常用 strings 函式對照：**

| Python | Go (strings 套件) |
|--------|------------------|
| `s.split(",")` | `strings.Split(s, ",")` |
| `",".join(list)` | `strings.Join(slice, ",")` |
| `s.strip()` | `strings.TrimSpace(s)` |
| `s.replace("a","b")` | `strings.ReplaceAll(s, "a", "b")` |
| `s.startswith("Hi")` | `strings.HasPrefix(s, "Hi")` |
| `s.endswith("!")` | `strings.HasSuffix(s, "!")` |
| `s.count("l")` | `strings.Count(s, "l")` |
| `s.index("l")` | `strings.Index(s, "l")` |

---

## 6. 運算子

```python
# Python
10 / 3   # 3.333... (浮點除法)
10 // 3  # 3 (整數除法)
10 % 3   # 1
2 ** 3   # 8 (次方)
and, or, not
```

```go
// Go
10 / 3    // 3 (整數除整數 = 整數)
10.0 / 3  // 3.333...
10 % 3    // 1
// 無 ** 運算子，用 math.Pow(2, 3)
&&, ||, !  // 邏輯運算子（無 and/or/not）
```

---

## 7. 條件判斷

```python
# Python
x = 10
if x > 5:
    print("big")
elif x == 5:
    print("mid")
else:
    print("small")

# 三元運算
result = "yes" if x > 5 else "no"
```

```go
// Go
x := 10
if x > 5 {
    fmt.Println("big")
} else if x == 5 {
    fmt.Println("mid")
} else {
    fmt.Println("small")
}

// Go 無三元運算子

// Go 特有：if 內可初始化變數（作用域限在 if 內）
if val := compute(); val > 10 {
    fmt.Println(val)
}

// switch（Go 不需要 break，預設不 fall-through）
switch x {
case 1:
    fmt.Println("one")
case 2, 3:
    fmt.Println("two or three")
default:
    fmt.Println("other")
}

// switch 無條件（等同 if-else）
switch {
case x < 0:
    fmt.Println("negative")
case x == 0:
    fmt.Println("zero")
default:
    fmt.Println("positive")
}
```

---

## 8. 迴圈

> ⚠️ Go **只有 `for`**，沒有 `while`、`do-while`

```python
# Python for
for i in range(5):
    print(i)

for i in range(1, 10, 2):
    print(i)

# while
while x > 0:
    x -= 1

# enumerate
for i, v in enumerate(["a","b","c"]):
    print(i, v)

# 迭代 dict
for k, v in d.items():
    print(k, v)

# break / continue
for i in range(10):
    if i == 3: continue
    if i == 7: break
```

```go
// Go - 傳統 for
for i := 0; i < 5; i++ {
    fmt.Println(i)
}

// Go - 當 while 用
for x > 0 {
    x--
}

// Go - 無限迴圈
for {
    // ...
    break
}

// Go - range（類似 enumerate）
nums := []int{10, 20, 30}
for i, v := range nums {
    fmt.Println(i, v)
}

// 只要 index
for i := range nums { ... }

// 只要 value（用 _ 忽略 index）
for _, v := range nums { ... }

// 迭代 map
m := map[string]int{"a": 1, "b": 2}
for k, v := range m {
    fmt.Println(k, v)
}

// break / continue（與 Python 相同用法）
// Go 額外支援 label break（跳出多層迴圈）
outer:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if j == 1 {
            break outer
        }
    }
}
```

---

## 9. 函式

```python
# Python
def add(a, b):
    return a + b

# 預設值
def greet(name="World"):
    return f"Hello, {name}"

# 多回傳值（用 tuple）
def min_max(nums):
    return min(nums), max(nums)

lo, hi = min_max([1, 2, 3])

# *args
def sum_all(*args):
    return sum(args)

# **kwargs
def show(**kwargs):
    for k, v in kwargs.items():
        print(k, v)

# lambda
square = lambda x: x * x

# 型別提示（選用）
def add(a: int, b: int) -> int:
    return a + b
```

```go
// Go
func add(a int, b int) int {
    return a + b
}

// 同型別參數可簡寫
func add(a, b int) int {
    return a + b
}

// 多回傳值（Go 原生支援，非常常用）
func minMax(nums []int) (int, int) {
    // ...
    return min, max
}
lo, hi := minMax([]int{1, 2, 3})

// 命名回傳值
func divide(a, b float64) (result float64, err error) {
    if b == 0 {
        err = fmt.Errorf("除以零")
        return  // naked return
    }
    result = a / b
    return
}

// 可變參數（類似 *args）
func sumAll(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}
sumAll(1, 2, 3)
sumAll(nums...)  // 展開 slice

// 匿名函式 / 閉包
square := func(x int) int {
    return x * x
}

// 函式作為參數（First-class function）
func apply(f func(int) int, x int) int {
    return f(x)
}
```

---

## 10. 集合型別：List / Slice

```python
# Python List
lst = [1, 2, 3]
lst.append(4)
lst.extend([5, 6])
lst.pop()
lst.pop(0)
print(len(lst))
print(lst[1:3])
print(1 in lst)
```

```go
// Go Slice
s := []int{1, 2, 3}
s = append(s, 4)
s = append(s, 5, 6)
s = s[:len(s)-1]       // 刪除最後一個
s = s[1:]              // 刪除第一個
fmt.Println(len(s))
fmt.Println(s[1:3])

// 檢查是否包含（Go 無內建，需手動迴圈）
func contains(s []int, val int) bool {
    for _, v := range s {
        if v == val { return true }
    }
    return false
}

// 建立 slice（make）
s := make([]int, 5)       // 長度 5，全為 0
s := make([]int, 0, 10)   // 長度 0，容量 10

// Array（固定長度，與 slice 不同）
arr := [3]int{1, 2, 3}
arr := [...]int{1, 2, 3}  // 自動推斷長度

// 複製 slice
dst := make([]int, len(src))
copy(dst, src)

// 刪除中間元素（index i）
s = append(s[:i], s[i+1:]...)
```

**List Comprehension → Go 沒有，需用迴圈：**

```python
# Python
squares = [x*x for x in range(5)]
evens   = [x for x in range(10) if x%2==0]
```

```go
// Go
squares := make([]int, 5)
for i := range squares {
    squares[i] = i * i
}

var evens []int
for i := 0; i < 10; i++ {
    if i%2 == 0 {
        evens = append(evens, i)
    }
}
```

---

## 11. 集合型別：Dict / Map

```python
# Python Dict
d = {"name": "Alice", "age": 30}
d["city"] = "Taipei"
del d["age"]
print(d.get("name", "unknown"))
print("name" in d)
print(d.keys())
print(d.values())
print(d.items())
```

```go
// Go Map
m := map[string]interface{}{
    "name": "Alice",
    "age":  30,
}
// 或明確型別
m := map[string]string{"name": "Alice"}

m["city"] = "Taipei"
delete(m, "age")

// 取值（安全方式）
val, ok := m["name"]   // ok 是 bool，存在為 true
if !ok {
    val = "unknown"
}

// 檢查 key 是否存在
_, exists := m["name"]

// 迭代
for k, v := range m { ... }

// 建立 map（make）
m := make(map[string]int)

// 計數（類似 Python Counter）
counter := make(map[string]int)
for _, word := range words {
    counter[word]++
}
```

---

## 12. 集合型別：Tuple / Struct

```python
# Python Tuple（不可變）
point = (3, 4)
x, y = point

# namedtuple
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x)
```

```go
// Go Struct（最接近 namedtuple/class）
type Point struct {
    X int
    Y int
}

p := Point{X: 3, Y: 4}
fmt.Println(p.X)

// 匿名 struct
p := struct{ X, Y int }{3, 4}

// 多回傳值可模擬 tuple
func getCoord() (int, int) {
    return 3, 4
}
x, y := getCoord()

// Struct 嵌入（組合，類似繼承）
type Animal struct {
    Name string
}
type Dog struct {
    Animal          // 嵌入
    Breed string
}
d := Dog{Animal: Animal{Name: "Rex"}, Breed: "Lab"}
fmt.Println(d.Name) // 直接存取嵌入欄位
```

---

## 13. Set 集合

```python
# Python
s = {1, 2, 3}
s.add(4)
s.remove(2)
print(1 in s)
a | b  # 聯集
a & b  # 交集
a - b  # 差集
```

```go
// Go 無內建 Set，用 map[T]struct{} 模擬
s := map[int]struct{}{}
s[1] = struct{}{}
s[2] = struct{}{}

// 新增
s[4] = struct{}{}

// 刪除
delete(s, 2)

// 檢查存在
_, ok := s[1]  // ok = true

// 聯集
for k := range b {
    a[k] = struct{}{}
}
```

---

## 14. 物件導向：Class / Struct + Method

```python
# Python Class
class Animal:
    def __init__(self, name: str):
        self.name = name
        self._age = 0  # 慣例私有

    def speak(self) -> str:
        return f"{self.name} makes a sound"

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, val):
        self._age = val

    def __str__(self):
        return f"Animal({self.name})"

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says Woof!"

d = Dog("Rex")
print(d.speak())
```

```go
// Go Struct + Method
type Animal struct {
    Name string
    age  int    // 小寫 = 私有（package 內可見）
}

// 方法（接收者 receiver）
func (a *Animal) Speak() string {
    return a.Name + " makes a sound"
}

// Getter/Setter 慣例
func (a *Animal) Age() int { return a.age }
func (a *Animal) SetAge(v int) { a.age = v }

// Stringer 介面（類似 __str__）
func (a Animal) String() string {
    return fmt.Sprintf("Animal(%s)", a.Name)
}

// 組合（代替繼承）
type Dog struct {
    Animal
}

func (d *Dog) Speak() string {
    return d.Name + " says Woof!"
}

// 建立
d := &Dog{Animal: Animal{Name: "Rex"}}
fmt.Println(d.Speak())
fmt.Println(d.Name)  // 直接存取嵌入欄位
```

> 💡 **值接收者 vs 指標接收者：**
> - `func (a Animal) Method()` → 複製一份，不修改原始值
> - `func (a *Animal) Method()` → 修改原始值（建議預設用指標）

---

## 15. 介面 Interface

```python
# Python - Duck Typing / ABC
from abc import ABC, abstractmethod

class Speaker(ABC):
    @abstractmethod
    def speak(self) -> str: ...

class Dog(Speaker):
    def speak(self): return "Woof"
```

```go
// Go Interface - 隱式實作（不需要明確宣告 implements）
type Speaker interface {
    Speak() string
}

type Dog struct{ Name string }
func (d Dog) Speak() string { return "Woof" }

// Dog 自動滿足 Speaker interface（只要有 Speak() 方法）
var s Speaker = Dog{Name: "Rex"}
fmt.Println(s.Speak())

// 空介面（接受任何型別，類似 Python 的 Any）
var any interface{} = 42
any = "hello"
any = []int{1,2,3}

// Go 1.18+ 可用 any 關鍵字
var x any = 42

// 常用內建介面
// fmt.Stringer:  String() string
// error:         Error() string
// io.Reader:     Read(p []byte) (n int, err error)
// io.Writer:     Write(p []byte) (n int, err error)
```

---

## 16. 錯誤處理

```python
# Python - 例外處理
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unknown: {e}")
else:
    print("Success")
finally:
    print("Always runs")

# 拋出例外
raise ValueError("invalid input")

# 自訂例外
class MyError(Exception):
    pass
```

```go
// Go - 錯誤是回傳值，不是例外
import "errors"

func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

result, err := divide(10, 0)
if err != nil {
    fmt.Println("Error:", err)
} else {
    fmt.Println(result)
}

// fmt.Errorf 格式化錯誤（%w 包裝錯誤）
err = fmt.Errorf("計算失敗: %w", originalErr)

// 自訂錯誤型別
type ValidationError struct {
    Field   string
    Message string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// 解包錯誤（errors.Is / errors.As）
var ve *ValidationError
if errors.As(err, &ve) {
    fmt.Println(ve.Field)
}

// panic / recover（類似 raise / try，但少用）
func safeDivide(a, b int) (result int, err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("panic: %v", r)
        }
    }()
    return a / b, nil
}
```

> ⚠️ Go 的錯誤處理哲學：**錯誤是值，必須明確處理**。`if err != nil` 是最常見的 Go 程式碼。

---

## 17. Goroutine 與並發（Go 獨有）

```python
# Python 多執行緒（有 GIL 限制）
import threading
import time

def worker(n):
    time.sleep(1)
    print(f"Done {n}")

threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
for t in threads: t.start()
for t in threads: t.join()

# asyncio
import asyncio

async def fetch(n):
    await asyncio.sleep(1)
    return n

async def main():
    results = await asyncio.gather(fetch(1), fetch(2))
```

```go
// Go Goroutine（極輕量，可建立百萬個）
import (
    "sync"
    "time"
)

func worker(n int) {
    time.Sleep(time.Second)
    fmt.Println("Done", n)
}

// 啟動 goroutine（加 go 關鍵字）
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(n int) {
        defer wg.Done()
        worker(n)
    }(i)
}
wg.Wait()  // 等待全部完成

// Mutex（互斥鎖）
var mu sync.Mutex
mu.Lock()
// 臨界區...
mu.Unlock()

// RWMutex（讀寫鎖）
var rwmu sync.RWMutex
rwmu.RLock()   // 多個讀取者
rwmu.RUnlock()
```

---

## 18. Channel（Go 獨有）

> Channel 是 goroutine 之間通訊的管道，類似執行緒安全的 queue

```go
// 建立 channel
ch := make(chan int)        // 無緩衝
ch := make(chan int, 10)    // 有緩衝（buffered）

// 發送與接收
ch <- 42        // 發送（blocking if unbuffered）
val := <-ch     // 接收

// 關閉 channel
close(ch)

// 迭代 channel（直到 close）
for v := range ch {
    fmt.Println(v)
}

// select（類似 switch，監聽多個 channel）
select {
case msg := <-ch1:
    fmt.Println("from ch1:", msg)
case msg := <-ch2:
    fmt.Println("from ch2:", msg)
case <-time.After(time.Second):
    fmt.Println("timeout")
default:
    fmt.Println("no message")
}

// 實際範例：producer / consumer
func producer(ch chan<- int) {
    for i := 0; i < 5; i++ {
        ch <- i
    }
    close(ch)
}

func main() {
    ch := make(chan int, 5)
    go producer(ch)
    for v := range ch {
        fmt.Println(v)
    }
}
```

---

## 19. 模組與套件

```python
# Python
# 安裝：pip install requests
import os
import math
from pathlib import Path
from collections import Counter

# 自訂模組：mymodule.py
# import mymodule
```

```go
// Go Module 初始化
// go mod init myproject
// go get github.com/some/package
// go mod tidy

// 引入
import (
    "fmt"
    "math"
    "os"
    "path/filepath"
    "sort"
    "strings"

    "github.com/some/package"  // 第三方
)

// 自訂套件（資料夾名稱 = package 名稱）
// myproject/utils/helper.go
package utils

func Helper() { ... }

// 使用
import "myproject/utils"
utils.Helper()

// 別名
import (
    f "fmt"
    mth "math"
)

// 忽略未使用（用 _）
import _ "github.com/lib/pq"  // 只執行 init()
```

---

## 20. 常用標準庫對照

| 功能 | Python | Go |
|------|--------|----|
| 輸出 | `print()` | `fmt.Println()`, `fmt.Printf()` |
| 格式化字串 | f-string | `fmt.Sprintf()` |
| 數學 | `math` | `math` |
| 隨機 | `random` | `math/rand` |
| 時間 | `datetime`, `time` | `time` |
| 排序 | `sorted()`, `list.sort()` | `sort.Slice()`, `sort.Ints()` |
| 正則 | `re` | `regexp` |
| JSON | `json` | `encoding/json` |
| HTTP Client | `requests` | `net/http` |
| HTTP Server | `flask`, `fastapi` | `net/http` (內建) |
| 檔案 I/O | `open()` | `os`, `bufio`, `io` |
| 路徑 | `pathlib`, `os.path` | `path/filepath` |
| 環境變數 | `os.environ` | `os.Getenv()` |
| 測試 | `unittest`, `pytest` | `testing` (內建) |
| 並發 | `threading`, `asyncio` | `sync`, goroutine |
| 資料庫 | `sqlite3`, `sqlalchemy` | `database/sql` |

```go
// JSON 序列化
import "encoding/json"

type Person struct {
    Name string `json:"name"`
    Age  int    `json:"age,omitempty"`
}

p := Person{Name: "Alice", Age: 30}
data, err := json.Marshal(p)         // → JSON bytes
json.Unmarshal(data, &p)             // JSON → struct

// 排序
nums := []int{3, 1, 4, 1, 5}
sort.Ints(nums)

people := []Person{{Name: "Bob"}, {Name: "Alice"}}
sort.Slice(people, func(i, j int) bool {
    return people[i].Name < people[j].Name
})

// HTTP Server
import "net/http"

http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintln(w, "Hello, Go!")
})
http.ListenAndServe(":8080", nil)
```

---

## 21. 類型斷言與反射

```python
# Python
x = 42
print(type(x))          # <class 'int'>
print(isinstance(x, int))  # True
```

```go
// Go 型別斷言（Type Assertion）
var i interface{} = "hello"

s, ok := i.(string)   // 安全斷言
if ok {
    fmt.Println(s)
}

// Type Switch
func describe(i interface{}) {
    switch v := i.(type) {
    case int:
        fmt.Printf("int: %d\n", v)
    case string:
        fmt.Printf("string: %s\n", v)
    case bool:
        fmt.Printf("bool: %t\n", v)
    default:
        fmt.Printf("unknown: %T\n", v)
    }
}

// 反射（Reflection）
import "reflect"

x := 42
fmt.Println(reflect.TypeOf(x))   // int
fmt.Println(reflect.ValueOf(x))  // 42
```

---

## 22. Defer / Context Manager

```python
# Python - with statement（Context Manager）
with open("file.txt", "r") as f:
    content = f.read()
# 離開 with 自動關閉

# contextlib
from contextlib import contextmanager

@contextmanager
def managed():
    print("enter")
    yield
    print("exit")
```

```go
// Go - defer（函式結束時執行，LIFO 順序）
func readFile(path string) {
    f, err := os.Open(path)
    if err != nil { ... }
    defer f.Close()  // 函式結束時自動執行

    // 繼續使用 f...
}

// 多個 defer（後進先出）
func example() {
    defer fmt.Println("3")
    defer fmt.Println("2")
    defer fmt.Println("1")
    // 輸出：1 2 3
}

// defer + recover（類似 finally）
func safeRun() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Recovered:", r)
        }
    }()
    panic("something went wrong")
}
```

---

## 23. 指標 Pointer

```python
# Python 全部是參考傳遞（reference semantics for objects）
# 無需明確使用指標
lst = [1, 2, 3]
def append_item(l):
    l.append(4)  # 修改原始 list

append_item(lst)  # lst 變成 [1,2,3,4]
```

```go
// Go 有明確指標
x := 42
p := &x          // & 取得位址，p 是 *int
fmt.Println(*p)  // * 解參考，輸出 42
*p = 100         // 修改 x 的值
fmt.Println(x)   // 100

// 值傳遞 vs 指標傳遞
func increment(n int) {
    n++  // 不影響外面
}

func incrementPtr(n *int) {
    *n++  // 影響外面
}

x := 5
increment(x)      // x 還是 5
incrementPtr(&x)  // x 變成 6

// new()
p := new(int)    // 分配 *int，初始值 0
*p = 42

// 結構體通常用指標
a := &Animal{Name: "Rex"}  // 常見
```

---

## 24. Go 特有概念總整理

### Goroutine vs Thread
- Goroutine 初始堆疊只有 **2KB**（Thread 通常 1MB+）
- Go runtime 自動調度，可同時跑 **百萬個** goroutine

### Go 的設計哲學
- **組合優於繼承**（Composition over Inheritance）
- **明確優於隱式**（Explicit over Implicit）
- **錯誤是值**（Errors are values）
- **介面隱式滿足**（Implicit interface satisfaction）

### Go 沒有但 Python 有的：
| Python 特性 | Go 替代方案 |
|------------|------------|
| 繼承 | Embedding（嵌入） |
| List Comprehension | for 迴圈 |
| 裝飾器 Decorator | 高階函式 / middleware |
| try/except | 多回傳值 error |
| None 安全存取 | ok pattern |
| 泛型（3.12+）| Generics（Go 1.18+） |
| GIL | 無 GIL，真正並發 |
| `__magic__` 方法 | Interface 方法 |

### Go 1.18+ 泛型

```go
// Python
def first(lst: list) -> Any:
    return lst[0]

// Go 泛型
func First[T any](s []T) T {
    return s[0]
}

// 使用
First([]int{1,2,3})
First([]string{"a","b"})

// 泛型約束
type Number interface {
    int | float64
}

func Sum[T Number](s []T) T {
    var total T
    for _, v := range s {
        total += v
    }
    return total
}
```

---

## 快速參考：Python → Go 心智模型

```
Python list     →  Go slice ([]T)
Python dict     →  Go map (map[K]V)
Python tuple    →  Go struct / multiple return values
Python class    →  Go struct + methods
Python ABC      →  Go interface
Python None     →  Go nil
Python True     →  Go true
Python lambda   →  Go func literal
Python decorator→  Go higher-order function
Python generator→  Go channel + goroutine
Python except   →  Go error return value
Python __init__ →  Go constructor function (NewXxx)
Python @property→  Go getter/setter methods
Python with     →  Go defer
```

---

*最後更新：2026 | Go 1.22+ | Python 3.12+*
