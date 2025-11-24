# Go、C、C++、Rust 核心語言特性全面比較

## 目錄
1. [併發機制比較](#一併發機制比較)
2. [垃圾回收與記憶體管理](#二垃圾回收與記憶體管理)
3. [介面與多型](#三介面與多型)
4. [錯誤處理](#四錯誤處理)
5. [反射機制](#五反射機制)
6. [包管理與編譯](#六包管理與編譯)
7. [泛型系統](#七泛型系統)
8. [總結比較](#八總結比較)

---

## 一、併發機制比較

### 1.1 Goroutine (Go)

#### 設計哲學與實現
* **設計哲學：** Go 將併發性 (concurrency) 作為其語言的核心功能之一。
* **實現方式：** Goroutine 是有棧協程 (stackful coroutines)，由 Go 運行時 (runtime) 排程器管理，而非作業系統執行緒。

#### 優勢
* **輕量高效：** 啟動棧空間極小 (幾 KB)，可以在單一程式中輕鬆管理數百萬個併發任務，適合高併發的網路服務和微服務。
* **使用簡便：** 內建於語言中，使用 `go func()` 即可建立，開發者體驗佳。
* **隱藏底層細節：** 開發者不需要手動管理異步操作的細節，由 Go 運行時自動處理。

#### 限制
* 依賴垃圾回收 (GC) 和 Go 運行時，記憶體管理不如 C++/Rust 精細。

---

### 1.2 Coroutines (C++20)

#### 設計哲學與實現
* **設計哲學：** 為程式設計師提供低階控制和極致彈性。
* **實現方式：** 支援無棧協程 (stackless coroutines) 和有棧協程的實現 (透過函式庫如 Boost.Asio)，允許高度優化和客製化的排程器。

#### 優勢
* **極致效能：** 允許開發者精確控制記憶體配置和執行流程，實現接近裸機的性能。
* **零成本抽象：** 在許多情況下，C++ Coroutines 可以編譯成高效的機器碼，避免不必要的開銷。
* **高度靈活：** 開發者可以自行選擇或編寫排程器，實現特定用途的最佳化。

#### 限制
* 複雜度高，學習曲線陡峭，需要手動管理許多細節 (如記憶體配置、排程器整合)。

---

### 1.3 Async/Await (Rust)

#### 設計哲學與實現
* **設計哲學：** 強調記憶體安全性和正確性，並提供高性能。
* **實現方式：** 採用無棧協程 (stackless coroutines)，編譯時將異步狀態機嵌入 `Future` trait 中。

#### 優勢
* **記憶體安全：** 利用所有權 (ownership) 系統在編譯時保證執行緒安全，大大減少併發 bug。
* **無垃圾回收：** 性能穩定且可預測，無 GC 停頓問題。
* **靈活選擇運行時：** `async/await` 語法是語言特性，但運行時 (如 Tokio) 由函式庫提供，允許開發者選擇最適合的運行時。

#### 限制
* 學習曲線較陡峭，且有「函數著色」(function coloring) 問題 (同步函數無法直接呼叫異步函數，反之亦然)，需要使用特定的 async 運行時來執行。

---

### 1.4 併發實現範例

#### Go 原生實現
```go
package main

import (
    "fmt"
    "time"
)

func worker(id int) {
    fmt.Printf("Worker %d starting\n", id)
    time.Sleep(time.Second)
    fmt.Printf("Worker %d done\n", id)
}

func main() {
    for i := 1; i <= 5; i++ {
        go worker(i)
    }
    time.Sleep(2 * time.Second)
}
```

#### C 實現 (使用 POSIX Threads)
```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

void* worker(void* arg) {
    int id = *(int*)arg;
    printf("Worker %d starting\n", id);
    sleep(1);
    printf("Worker %d done\n", id);
    free(arg);
    return NULL;
}

int main() {
    pthread_t threads[5];
    
    for (int i = 1; i <= 5; i++) {
        int* id = malloc(sizeof(int));
        *id = i;
        pthread_create(&threads[i-1], NULL, worker, id);
    }
    
    for (int i = 0; i < 5; i++) {
        pthread_join(threads[i], NULL);
    }
    
    return 0;
}
```

#### C++ 實現 (使用 std::thread)
```cpp
#include <iostream>
#include <thread>
#include <vector>
#include <chrono>

void worker(int id) {
    std::cout << "Worker " << id << " starting\n";
    std::this_thread::sleep_for(std::chrono::seconds(1));
    std::cout << "Worker " << id << " done\n";
}

int main() {
    std::vector<std::thread> threads;
    
    for (int i = 1; i <= 5; i++) {
        threads.emplace_back(worker, i);
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    return 0;
}
```

#### C++20 Coroutines 實現
```cpp
#include <cppcoro/task.hpp>
#include <cppcoro/sync_wait.hpp>
#include <cppcoro/when_all.hpp>
#include <iostream>
#include <chrono>

cppcoro::task<> worker(int id) {
    std::cout << "Worker " << id << " starting\n";
    co_await std::suspend_for(std::chrono::seconds(1));
    std::cout << "Worker " << id << " done\n";
}

cppcoro::task<> main_task() {
    std::vector<cppcoro::task<>> tasks;
    for (int i = 1; i <= 5; i++) {
        tasks.push_back(worker(i));
    }
    co_await cppcoro::when_all(std::move(tasks));
}

int main() {
    cppcoro::sync_wait(main_task());
    return 0;
}
```

#### Rust 實現 (使用 Tokio)
```rust
use tokio::time::{sleep, Duration};

async fn worker(id: i32) {
    println!("Worker {} starting", id);
    sleep(Duration::from_secs(1)).await;
    println!("Worker {} done", id);
}

#[tokio::main]
async fn main() {
    let mut handles = vec![];
    
    for i in 1..=5 {
        handles.push(tokio::spawn(worker(i)));
    }
    
    for handle in handles {
        handle.await.unwrap();
    }
}
```

---

### 1.5 Channel 通訊模式實現

#### Go 原生實現
```go
package main

import "fmt"

func producer(ch chan int) {
    for i := 0; i < 5; i++ {
        ch <- i
    }
    close(ch)
}

func main() {
    ch := make(chan int)
    go producer(ch)
    
    for val := range ch {
        fmt.Println("Received:", val)
    }
}
```

#### C 實現 (使用條件變數)
```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_SIZE 10

typedef struct {
    int buffer[BUFFER_SIZE];
    int count;
    int in;
    int out;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} Channel;

void channel_init(Channel* ch) {
    ch->count = 0;
    ch->in = 0;
    ch->out = 0;
    pthread_mutex_init(&ch->mutex, NULL);
    pthread_cond_init(&ch->not_empty, NULL);
    pthread_cond_init(&ch->not_full, NULL);
}

void channel_send(Channel* ch, int value) {
    pthread_mutex_lock(&ch->mutex);
    while (ch->count == BUFFER_SIZE) {
        pthread_cond_wait(&ch->not_full, &ch->mutex);
    }
    ch->buffer[ch->in] = value;
    ch->in = (ch->in + 1) % BUFFER_SIZE;
    ch->count++;
    pthread_cond_signal(&ch->not_empty);
    pthread_mutex_unlock(&ch->mutex);
}

int channel_recv(Channel* ch) {
    pthread_mutex_lock(&ch->mutex);
    while (ch->count == 0) {
        pthread_cond_wait(&ch->not_empty, &ch->mutex);
    }
    int value = ch->buffer[ch->out];
    ch->out = (ch->out + 1) % BUFFER_SIZE;
    ch->count--;
    pthread_cond_signal(&ch->not_full);
    pthread_mutex_unlock(&ch->mutex);
    return value;
}

void* producer(void* arg) {
    Channel* ch = (Channel*)arg;
    for (int i = 0; i < 5; i++) {
        channel_send(ch, i);
    }
    return NULL;
}

int main() {
    Channel ch;
    channel_init(&ch);
    
    pthread_t prod_thread;
    pthread_create(&prod_thread, NULL, producer, &ch);
    
    for (int i = 0; i < 5; i++) {
        int val = channel_recv(&ch);
        printf("Received: %d\n", val);
    }
    
    pthread_join(prod_thread, NULL);
    return 0;
}
```

#### C++ 實現 (使用 std::queue)
```cpp
#include <iostream>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>

template<typename T>
class Channel {
private:
    std::queue<T> queue_;
    std::mutex mutex_;
    std::condition_variable cond_;
    bool closed_ = false;

public:
    void send(T value) {
        std::lock_guard<std::mutex> lock(mutex_);
        queue_.push(value);
        cond_.notify_one();
    }
    
    bool recv(T& value) {
        std::unique_lock<std::mutex> lock(mutex_);
        cond_.wait(lock, [this] { return !queue_.empty() || closed_; });
        
        if (queue_.empty()) return false;
        
        value = queue_.front();
        queue_.pop();
        return true;
    }
    
    void close() {
        std::lock_guard<std::mutex> lock(mutex_);
        closed_ = true;
        cond_.notify_all();
    }
};

void producer(Channel<int>& ch) {
    for (int i = 0; i < 5; i++) {
        ch.send(i);
    }
    ch.close();
}

int main() {
    Channel<int> ch;
    std::thread prod(producer, std::ref(ch));
    
    int val;
    while (ch.recv(val)) {
        std::cout << "Received: " << val << std::endl;
    }
    
    prod.join();
    return 0;
}
```

#### Rust 實現 (使用 tokio::sync::mpsc)
```rust
use tokio::sync::mpsc;

async fn producer(tx: mpsc::Sender<i32>) {
    for i in 0..5 {
        tx.send(i).await.unwrap();
    }
}

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel(10);
    
    tokio::spawn(producer(tx));
    
    while let Some(val) = rx.recv().await {
        println!("Received: {}", val);
    }
}
```

---

### 1.6 併發性能比較

#### 基準測試場景：建立 100萬個輕量級併發任務

| 語言/實現方式 | 記憶體使用 | 啟動時間 | 上下文切換開銷 | GC 影響 |
|------------|----------|---------|--------------|---------|
| **Go Goroutine** | ~2GB (每個 2KB) | 極快 | 低 (用戶態調度) | 有 (STW 暫停) |
| **C pthread** | ~2TB (每個 2MB) | 慢 | 高 (內核態) | 無 |
| **C++ std::thread** | ~2TB (每個 2MB) | 慢 | 高 (內核態) | 無 |
| **C++20 Coroutines** | ~100MB | 極快 | 極低 (無棧) | 無 |
| **Rust async/await** | ~100MB | 極快 | 極低 (無棧) | 無 |

#### 關鍵發現

1. **記憶體效率**
   - Go Goroutine 比傳統執行緒輕量 1000 倍
   - C++/Rust 無棧協程比 Go 更節省記憶體 (20 倍優勢)

2. **原始性能**
   - C++ Coroutines：手動記憶體管理，零成本抽象，最快
   - Rust async/await：接近 C++ 性能，但有編譯時安全保證
   - Go Goroutine：因 GC 和運行時開銷略慢，但開發效率高

3. **延遲可預測性**
   - Rust/C++：無 GC 暫停，延遲穩定
   - Go：GC 暫停可能造成毫秒級延遲抖動

4. **開發複雜度**
   - Go：最簡單，內建語言支援
   - Rust：中等，需理解所有權系統
   - C++：最複雜，需手動管理所有細節
   - C：最原始，完全手動控制

---

## 二、垃圾回收與記憶體管理

### 2.1 Go 的垃圾回收

#### 設計與特性
* **設計哲學：** 自動記憶體管理，降低開發負擔
* **實現方式：** 併發三色標記清除 (Concurrent Mark-Sweep)，STW 時間極短

#### 優勢
* 開發效率極高，無需手動管理記憶體
* 減少記憶體洩漏和懸空指標等常見錯誤
* 適合快速迭代開發

#### 限制
* GC 暫停影響延遲敏感應用
* 記憶體佔用較高（需保留堆空間）
* 性能不可預測

#### Go 實現範例
```go
package main

type Buffer struct {
    data []byte
}

func NewBuffer(size int) *Buffer {
    return &Buffer{
        data: make([]byte, size),
    }
}

func main() {
    buf := NewBuffer(1024)
    // 無需手動釋放，GC 自動回收
    
    buffers := make([]*Buffer, 0)
    buffers = append(buffers, NewBuffer(512))
    // GC 會在適當時機回收
}
```

---

### 2.2 C 的手動記憶體管理

#### 實現範例
```c
#include <stdlib.h>
#include <string.h>

typedef struct {
    char* data;
    size_t length;
} Buffer;

Buffer* create_buffer(size_t size) {
    Buffer* buf = malloc(sizeof(Buffer));
    if (!buf) return NULL;
    
    buf->data = malloc(size);
    if (!buf->data) {
        free(buf);
        return NULL;
    }
    
    buf->length = size;
    return buf;
}

void destroy_buffer(Buffer* buf) {
    if (buf) {
        free(buf->data);
        free(buf);
    }
}

int main() {
    Buffer* buf = create_buffer(1024);
    // 使用 buffer...
    destroy_buffer(buf);  // 必須手動釋放
    return 0;
}
```

#### 特點
* 完全手動控制，性能最優
* 容易出現記憶體洩漏、雙重釋放、懸空指標
* 開發成本高

---

### 2.3 C++ 的 RAII (智能指標)

#### 實現範例
```cpp
#include <memory>
#include <vector>
#include <string>

class Buffer {
private:
    std::unique_ptr<char[]> data_;
    size_t length_;

public:
    Buffer(size_t size) : data_(std::make_unique<char[]>(size)), length_(size) {}
    
    // 自動析構，無需手動 delete
    ~Buffer() = default;
    
    // 禁止複製，只允許移動
    Buffer(const Buffer&) = delete;
    Buffer(Buffer&&) = default;
};

int main() {
    auto buf = std::make_unique<Buffer>(1024);
    // 離開作用域自動釋放
    
    std::vector<std::unique_ptr<Buffer>> buffers;
    buffers.push_back(std::make_unique<Buffer>(512));
    // vector 清理時自動釋放所有 buffer
    
    return 0;
}
```

#### 特點
* 確定性析構，零開銷
* 需要理解所有權語義
* 仍可能出錯（循環引用、裸指標）

---

### 2.4 Rust 的所有權系統

#### 實現範例
```rust
struct Buffer {
    data: Vec<u8>,
}

impl Buffer {
    fn new(size: usize) -> Self {
        Buffer {
            data: vec![0; size],
        }
    }
}

fn main() {
    let buf = Buffer::new(1024);
    // 離開作用域自動釋放，編譯器保證安全
    
    let buf2 = buf;  // 所有權轉移
    // println!("{}", buf.data.len());  // 編譯錯誤！buf 已被移動
    
    let mut buffers = Vec::new();
    buffers.push(Buffer::new(512));
    // Vec drop 時自動清理
}
```

#### 特點
* 編譯時保證記憶體安全
* 無 GC 開銷，性能可預測
* 學習曲線陡峭

---

### 2.5 記憶體管理比較表

| 特性 | C | C++ | Rust | Go |
|------|---|-----|------|-----|
| **記憶體安全** | ❌ 手動保證 | ⚠️ 部分保證 | ✅ 編譯時保證 | ✅ 運行時保證 |
| **性能開銷** | 0% | 0% | 0% | 5-15% (GC) |
| **延遲可預測性** | ✅ 完全可控 | ✅ 完全可控 | ✅ 完全可控 | ⚠️ GC 暫停 |
| **開發效率** | ❌ 低 | ⚠️ 中等 | ⚠️ 中等 | ✅ 高 |
| **記憶體洩漏風險** | 高 | 低 | 極低 | 極低 |

---

## 三、介面與多型

### 3.1 Go 的隱式介面

#### 實現範例
```go
package main

import "fmt"

// 定義介面
type Speaker interface {
    Speak() string
}

// Dog 實現介面（隱式）
type Dog struct {
    Name string
}

func (d Dog) Speak() string {
    return "Woof!"
}

// Cat 實現介面（隱式）
type Cat struct {
    Name string
}

func (c Cat) Speak() string {
    return "Meow!"
}

func MakeSound(s Speaker) {
    fmt.Println(s.Speak())
}

func main() {
    dog := Dog{Name: "Buddy"}
    cat := Cat{Name: "Whiskers"}
    
    MakeSound(dog)  // 自動符合介面
    MakeSound(cat)
}
```

#### 特點
* 鴨子型別 (Duck Typing)，無需顯式聲明
* 解耦設計，類型與介面獨立演化
* 運行時動態分派（虛函數表）

---

### 3.2 C 的函數指標模擬

#### 實現範例
```c
#include <stdio.h>
#include <stdlib.h>

// 定義介面（函數指標結構）
typedef struct {
    const char* (*speak)(void* self);
} Speaker;

typedef struct {
    Speaker speaker;  // 內嵌介面
    const char* name;
} Dog;

typedef struct {
    Speaker speaker;
    const char* name;
} Cat;

const char* dog_speak(void* self) {
    return "Woof!";
}

const char* cat_speak(void* self) {
    return "Meow!";
}

void make_sound(Speaker* s, void* instance) {
    printf("%s\n", s->speak(instance));
}

int main() {
    Dog dog = {{dog_speak}, "Buddy"};
    Cat cat = {{cat_speak}, "Whiskers"};
    
    make_sound(&dog.speaker, &dog);
    make_sound(&cat.speaker, &cat);
    
    return 0;
}
```

#### 特點
* 完全手動實現
* 無類型安全
* 性能開銷最小

---

### 3.3 C++ 的虛函數多型

#### 實現範例
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>

// 抽象基類（介面）
class Speaker {
public:
    virtual ~Speaker() = default;
    virtual std::string speak() const = 0;  // 純虛函數
};

class Dog : public Speaker {
private:
    std::string name_;
public:
    Dog(std::string name) : name_(std::move(name)) {}
    
    std::string speak() const override {
        return "Woof!";
    }
};

class Cat : public Speaker {
private:
    std::string name_;
public:
    Cat(std::string name) : name_(std::move(name)) {}
    
    std::string speak() const override {
        return "Meow!";
    }
};

void make_sound(const Speaker& s) {
    std::cout << s.speak() << std::endl;
}

int main() {
    Dog dog("Buddy");
    Cat cat("Whiskers");
    
    make_sound(dog);
    make_sound(cat);
    
    // 多型容器
    std::vector<std::unique_ptr<Speaker>> animals;
    animals.push_back(std::make_unique<Dog>("Rex"));
    animals.push_back(std::make_unique<Cat>("Mittens"));
    
    for (const auto& animal : animals) {
        std::cout << animal->speak() << std::endl;
    }
    
    return 0;
}
```

#### 特點
* 顯式繼承，強類型檢查
* 虛函數表（vtable）開銷
* 編譯時和運行時多型兩種選擇

---

### 3.4 C++ 模板（編譯時多型）

#### 實現範例
```cpp
#include <iostream>
#include <string>

// 無需基類
class Dog {
public:
    std::string speak() const { return "Woof!"; }
};

class Cat {
public:
    std::string speak() const { return "Meow!"; }
};

// 模板函數，編譯時生成特化版本
template<typename T>
void make_sound(const T& animal) {
    std::cout << animal.speak() << std::endl;
}

int main() {
    Dog dog;
    Cat cat;
    
    make_sound(dog);  // 零開銷
    make_sound(cat);
    
    return 0;
}
```

#### 特點
* 零運行時開銷
* 編譯時類型檢查
* 代碼膨脹問題

---

### 3.5 Rust 的 Trait

#### 實現範例
```rust
// 定義 trait（類似介面）
trait Speaker {
    fn speak(&self) -> &str;
}

struct Dog {
    name: String,
}

impl Speaker for Dog {
    fn speak(&self) -> &str {
        "Woof!"
    }
}

struct Cat {
    name: String,
}

impl Speaker for Cat {
    fn speak(&self) -> &str {
        "Meow!"
    }
}

// 靜態分派（編譯時）
fn make_sound<T: Speaker>(animal: &T) {
    println!("{}", animal.speak());
}

// 動態分派（運行時）
fn make_sound_dyn(animal: &dyn Speaker) {
    println!("{}", animal.speak());
}

fn main() {
    let dog = Dog { name: "Buddy".to_string() };
    let cat = Cat { name: "Whiskers".to_string() };
    
    make_sound(&dog);  // 靜態分派，零開銷
    make_sound(&cat);
    
    // 動態分派
    let animals: Vec<Box<dyn Speaker>> = vec![
        Box::new(Dog { name: "Rex".to_string() }),
        Box::new(Cat { name: "Mittens".to_string() }),
    ];
    
    for animal in &animals {
        make_sound_dyn(animal.as_ref());
    }
}
```

#### 特點
* 兼具靜態和動態分派
* 編譯時安全保證
* 零成本抽象

---

### 3.6 介面性能比較

| 特性 | C | C++ Virtual | C++ Template | Go Interface | Rust Trait (靜態) | Rust Trait (動態) |
|------|---|-------------|--------------|--------------|------------------|------------------|
| **分派方式** | 手動 | 動態 | 靜態 | 動態 | 靜態 | 動態 |
| **運行時開銷** | 最低 | 中等 | 零 | 中等 | 零 | 中等 |
| **類型安全** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **靈活性** | 低 | 高 | 低 | 極高 | 高 | 高 |
| **解耦能力** | 低 | 中 | 低 | 極高 | 高 | 高 |

---

## 四、錯誤處理

### 4.1 Go 的多返回值錯誤處理

#### 實現範例
```go
package main

import (
    "errors"
    "fmt"
    "strconv"
)

func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

func parseAndDivide(aStr, bStr string) (float64, error) {
    a, err := strconv.ParseFloat(aStr, 64)
    if err != nil {
        return 0, fmt.Errorf("invalid first number: %w", err)
    }
    
    b, err := strconv.ParseFloat(bStr, 64)
    if err != nil {
        return 0, fmt.Errorf("invalid second number: %w", err)
    }
    
    result, err := divide(a, b)
    if err != nil {
        return 0, fmt.Errorf("division failed: %w", err)
    }
    
    return result, nil
}

func main() {
    result, err := parseAndDivide("10", "2")
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    fmt.Println("Result:", result)
}
```

#### 特點
* 顯式錯誤處理，強制檢查
* 錯誤是值，可以組合和包裝
* 代碼冗長（`if err != nil` 模式）

---

### 4.2 C 的錯誤碼

#### 實現範例
```c
#include <stdio.h>
#include <errno.h>
#include <string.h>

typedef enum {
    SUCCESS = 0,
    ERR_DIVISION_BY_ZERO = -1,
    ERR_INVALID_INPUT = -2
} ErrorCode;

ErrorCode divide(double a, double b, double* result) {
    if (b == 0) {
        return ERR_DIVISION_BY_ZERO;
    }
    *result = a / b;
    return SUCCESS;
}

int main() {
    double result;
    ErrorCode err = divide(10.0, 2.0, &result);
    
    if (err != SUCCESS) {
        fprintf(stderr, "Error: %d\n", err);
        return 1;
    }
    
    printf("Result: %f\n", result);
    return 0;
}
```

#### 特點
* 輕量，性能最優
* 容易忽略錯誤
* 缺乏上下文信息

---

### 4.3 C++ 的異常處理

#### 實現範例
```cpp
#include <iostream>
#include <stdexcept>
#include <string>

class DivisionByZeroError : public std::runtime_error {
public:
    DivisionByZeroError() : std::runtime_error("Division by zero") {}
};

double divide(double a, double b) {
    if (b == 0) {
        throw DivisionByZeroError();
    }
    return a / b;
}

double parseAndDivide(const std::string& aStr, const std::string& bStr) {
    try {
        double a = std::stod(aStr);
        double b = std::stod(bStr);
        return divide(a, b);
    } catch (const std::invalid_argument& e) {
        throw std::runtime_error("Invalid number format");
    } catch (const std::out_of_range& e) {
        throw std::runtime_error("Number out of range");
    }
}

int main() {
    try {
        double result = parseAndDivide("10", "2");
        std::cout << "Result: " << result << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
```

#### 特點
* 自動堆棧展開
* 性能開銷（異常表）
* 可能跳過清理代碼（需 RAII）

---

### 4.4 C++ 的 std::expected (C++23)

#### 實現範例
```cpp
#include <expected>
#include <string>
#include <iostream>

enum class DivideError {
    DivisionByZero
};

std::expected<double, DivideError> divide(double a, double b) {
    if (b == 0) {
        return std::unexpected(DivideError::DivisionByZero);
    }
    return a / b;
}

int main() {
    auto result = divide(10.0, 2.0);
    
    if (result) {
        std::cout << "Result: " << *result << std::endl;
    } else {
        std::cerr << "Error: Division by zero" << std::endl;
    }
    
    return 0;
}
```

#### 特點
* 零開銷錯誤處理
* 類型安全
* 需要 C++23

---

### 4.5 Rust 的 Result<T, E>

#### 實現範例
```rust
use std::num::ParseFloatError;

#[derive(Debug)]
enum DivideError {
    DivisionByZero,
    ParseError(ParseFloatError),
}

fn divide(a: f64, b: f64) -> Result<f64, DivideError> {
    if b == 0.0 {
        return Err(DivideError::DivisionByZero);
    }
    Ok(a / b)
}

fn parse_and_divide(a_str: &str, b_str: &str) -> Result<f64, DivideError> {
    let a = a_str.parse::<f64>()
        .map_err(DivideError::ParseError)?;  // ? 運算符自動傳播錯誤
    
    let b = b_str.parse::<f64>()
        .map_err(DivideError::ParseError)?;
    
    divide(a, b)
}

fn main() {
    match parse_and_divide("10", "2") {
        Ok(result) => println!("Result: {}", result),
        Err(e) => eprintln!("Error: {:?}", e),
    }
}
```

#### 特點
* 強制錯誤處理（編譯器檢查）
* `?` 運算符簡化傳播
* 零成本抽象

---

### 4.6 錯誤處理比較表

| 特性 | C 錯誤碼 | C++ 異常 | C++ expected | Go error | Rust Result |
|------|---------|---------|--------------|----------|-------------|
| **性能開銷** | 零 | 高（異常路徑） | 零 | 極低 | 零 |
| **強制檢查** | ❌ | ❌ | ⚠️ | ✅ | ✅ |
| **上下文信息** | ❌ | ✅ | ⚠️ | ✅ | ✅ |
| **可組合性** | ❌ | ⚠️ | ✅ | ✅ | ✅ |
| **可恢復性** | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 五、反射機制

### 5.1 Go 的運行時反射

#### 實現範例
```go
package main

import (
    "fmt"
    "reflect"
)

type Person struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}

func inspectType(v interface{}) {
    t := reflect.TypeOf(v)
    val := reflect.ValueOf(v)
    
    fmt.Printf("Type: %s\n", t.Name())
    fmt.Printf("Kind: %s\n", t.Kind())
    
    if t.Kind() == reflect.Struct {
        for i := 0; i < t.NumField(); i++ {
            field := t.Field(i)
            value := val.Field(i)
            fmt.Printf("  Field: %s, Type: %s, Value: %v, Tag: %s\n",
                field.Name, field.Type, value, field.Tag.Get("json"))
        }
    }
}

func main() {
    p := Person{Name: "Alice", Age: 30}
    inspectType(p)
}
```

#### 特點
* 完整的運行時類型信息
* 支持標籤 (tags) 元數據
* 性能開銷較大

---

### 5.2 C 的有限反射（手動實現）

#### 實現範例
```c
#include <stdio.h>
#include <string.h>

typedef enum {
    TYPE_INT,
    TYPE_STRING,
    TYPE_STRUCT
} FieldType;

typedef struct {
    const char* name;
    FieldType type;
    size_t offset;
} FieldInfo;

typedef struct {
    char name[50];
    int age;
} Person;

FieldInfo person_fields[] = {
    {"name", TYPE_STRING, offsetof(Person, name)},
    {"age", TYPE_INT, offsetof(Person, age)},
};

void inspect_person(Person* p) {
    printf("Person:\n");
    for (int i = 0; i < 2; i++) {
        printf("  %s: ", person_fields[i].name);
        
        void* field_ptr = (char*)p + person_fields[i].offset;
        
        if (person_fields[i].type == TYPE_INT) {
            printf("%d\n", *(int*)field_ptr);
        } else if (person_fields[i].type == TYPE_STRING) {
            printf("%s\n", (char*)field_ptr);
        }
    }
}

int main() {
    Person p = {"Alice", 30};
    inspect_person(&p);
    return 0;
}
```

#### 特點
* 完全手動，無運行時支持
* 零開銷
* 維護困難

---

### 5.3 C++ 的編譯時反射（部分支持）

#### 實現範例
```cpp
#include <iostream>
#include <string>
#include <type_traits>

// C++20 無完整反射，使用模板元編程模擬
template<typename T>
struct TypeInfo {
    static constexpr const char* name() {
        return typeid(T).name();  // 編譯器相關
    }
};

// 手動定義結構體元信息
struct Person {
    std::string name;
    int age;
};

// Magic Get 庫（實驗性）或等待 C++26 反射提案
#include <boost/pfr.hpp>  // 需要 Boost.PFR

void inspect_person(const Person& p) {
    boost::pfr::for_each_field(p, [](const auto& field, std::size_t idx) {
        std::cout << "Field " << idx << ": " << field << std::endl;
    });
}

int main() {
    Person p{"Alice", 30};
    inspect_person(p);
    return 0;
}
```

#### 特點
* 需要第三方庫或 C++26
* 編譯時反射性能最優
* 功能受限

---

### 5.4 Rust 的過程宏（編譯時反射）

#### 實現範例
```rust
use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]  // 自動生成序列化代碼
struct Person {
    name: String,
    age: u32,
}

fn main() {
    let p = Person {
        name: "Alice".to_string(),
        age: 30,
    };
    
    // 序列化為 JSON（編譯時生成）
    let json = serde_json::to_string(&p).unwrap();
    println!("{}", json);
    
    // 反序列化
    let p2: Person = serde_json::from_str(&json).unwrap();
    println!("{:?}", p2);
}
```

#### 特點
* 編譯時代碼生成
* 零運行時開銷
* 類型安全

---

### 5.5 反射能力比較表

| 特性 | C | C++ | Go | Rust |
|------|---|-----|-----|------|
| **運行時反射** | ❌ | ❌ | ✅ | ❌ |
| **編譯時反射** | ❌ | ⚠️ (C++26) | ❌ | ✅ (宏) |
| **性能開銷** | N/A | 零 | 中等 | 零 |
| **易用性** | ❌ | ❌ | ✅ | ✅ |
| **類型安全** | ❌ | ⚠️ | ✅ | ✅ |

---

## 六、包管理與編譯

### 6.1 Go Modules

#### 使用範例
```bash
# 初始化模組
go mod init github.com/user/project

# 添加依賴（自動管理）
go get github.com/gin-gonic/gin@v1.9.0

# 編譯（單一二進制）
go build -o myapp

# 跨平台編譯
GOOS=linux GOARCH=amd64 go build
```

#### 特點
* 內建包管理器
* 語義化版本控制
* 快速編譯
* 單一二進制輸出

---

### 6.2 C 的傳統構建

#### 使用範例
```bash
# 手動管理依賴
# 使用 Makefile
gcc -o myapp main.c utils.c -lpthread -lm

# 或使用 CMake
cmake -B build
cmake --build build
```

#### 特點
* 無標準包管理器
* 依賴地獄
* 編譯最快
* 需要手動處理依賴

---

### 6.3 C++ 的現代工具鏈

#### 使用範例
```bash
# Conan 包管理
conan install . --build=missing

# CMake 構建
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build

# 或使用 vcpkg
vcpkg install boost
```

#### 特點
* 多種包管理器（Conan, vcpkg, CPM）
* 複雜的構建配置
* 編譯時間長
* 強大的構建系統（CMake）

---

### 6.4 Rust Cargo

#### 使用範例
```bash
# 創建項目
cargo new myapp

# 添加依賴（自動下載）
cargo add tokio --features full

# 編譯優化版本
cargo build --release

# 跨平台編譯
rustup target add x86_64-pc-windows-gnu
cargo build --target x86_64-pc-windows-gnu

# 運行測試
cargo test

# 生成文檔
cargo doc --open
```

#### 特點
* 官方包管理器
* 快速增量編譯
* 一體化工具鏈
* 內建測試和文檔生成

---

### 6.5 工具鏈比較表

| 特性 | C | C++ | Go | Rust |
|------|---|-----|-----|------|
| **包管理** | ❌ | ⚠️ 多種方案 | ✅ 內建 | ✅ 內建 |
| **編譯速度** | 極快 | 慢 | 快 | 中等 |
| **依賴管理** | 手動 | 複雜 | 自動 | 自動 |
| **跨平台編譯** | 困難 | 困難 | 簡單 | 簡單 |
| **增量編譯** | ⚠️ | ⚠️ | ✅ | ✅ |
| **內建測試** | ❌ | ❌ | ✅ | ✅ |

---

## 七、泛型系統

### 7.1 Go 1.18+ 泛型

#### 實現範例
```go
package main

import "fmt"

// 泛型函數
func Max[T comparable](a, b T) T {
    if a > b {
        return a
    }
    return b
}

// 泛型類型
type Stack[T any] struct {
    items []T
}

func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item, true
}

func main() {
    fmt.Println(Max(10, 20))
    fmt.Println(Max("apple", "banana"))
    
    stack := Stack[int]{}
    stack.Push(1)
    stack.Push(2)
    val, _ := stack.Pop()
    fmt.Println(val)
}
```

#### 特點
* 語法簡潔
* 運行時實現（部分單態化）
* 功能相對受限
* 約束系統較簡單

---

### 7.2 C 的宏模擬

#### 實現範例
```c
#include <stdio.h>
#include <stdlib.h>

#define DEFINE_STACK(TYPE)                          \
    typedef struct {                                \
        TYPE* items;                                \
        size_t size;                                \
        size_t capacity;                            \
    } Stack_##TYPE;                                 \
                                                    \
    void Stack_##TYPE##_push(Stack_##TYPE* s, TYPE item) { \
        if (s->size >= s->capacity) {               \
            s->capacity = s->capacity == 0 ? 4 : s->capacity * 2; \
            s->items = realloc(s->items, s->capacity * sizeof(TYPE)); \
        }                                           \
        s->items[s->size++] = item;                 \
    }

DEFINE_STACK(int)
DEFINE_STACK(double)

int main() {
    Stack_int s = {NULL, 0, 0};
    Stack_int_push(&s, 42);
    printf("%d\n", s.items[0]);
    free(s.items);
    return 0;
}
```

#### 特點
* 純文本替換
* 無類型安全
* 編譯錯誤難讀
* 調試困難

---

### 7.3 C++ 模板

#### 實現範例
```cpp
#include <iostream>
#include <vector>
#include <concepts>  // C++20

// 概念約束
template<typename T>
concept Comparable = requires(T a, T b) {
    { a > b } -> std::convertible_to<bool>;
};

template<Comparable T>
T max_value(T a, T b) {
    return a > b ? a : b;
}

// 泛型類
template<typename T>
class Stack {
private:
    std::vector<T> items_;

public:
    void push(T item) {
        items_.push_back(std::move(item));
    }
    
    bool pop(T& item) {
        if (items_.empty()) return false;
        item = std::move(items_.back());
        items_.pop_back();
        return true;
    }
};

int main() {
    std::cout << max_value(10, 20) << std::endl;
    std::cout << max_value(3.14, 2.71) << std::endl;
    
    Stack<int> stack;
    stack.push(42);
    
    int val;
    stack.pop(val);
    std::cout << val << std::endl;
    
    return 0;
}
```

#### 特點
* 圖靈完備（模板元編程）
* 編譯時完全展開
* 代碼膨脹
* 強大的概念約束（C++20）

---

### 7.4 Rust 泛型

#### 實現範例
```rust
use std::cmp::PartialOrd;

// 泛型函數
fn max<T: PartialOrd>(a: T, b: T) -> T {
    if a > b { a } else { b }
}

// 泛型結構體
struct Stack<T> {
    items: Vec<T>,
}

impl<T> Stack<T> {
    fn new() -> Self {
        Stack { items: Vec::new() }
    }
    
    fn push(&mut self, item: T) {
        self.items.push(item);
    }
    
    fn pop(&mut self) -> Option<T> {
        self.items.pop()
    }
}

fn main() {
    println!("{}", max(10, 20));
    println!("{}", max(3.14, 2.71));
    
    let mut stack = Stack::new();
    stack.push(42);
    
    if let Some(val) = stack.pop() {
        println!("{}", val);
    }
}
```

#### 特點
* 零成本抽象
* 單態化（Monomorphization）
* 編譯時類型檢查
* 強大的 trait 約束系統

---

### 7.5 泛型能力比較表

| 特性 | C 宏 | C++ 模板 | Go 泛型 | Rust 泛型 |
|------|------|---------|---------|----------|
| **類型安全** | ❌ | ✅ | ✅ | ✅ |
| **運行時開銷** | 零 | 零 | 小 | 零 |
| **編譯時間** | 快 | 慢 | 中等 | 慢 |
| **表達能力** | 弱 | 極強 | 中等 | 強 |
| **錯誤訊息** | 極差 | 差 | 良好 | 優秀 |
| **約束系統** | ❌ | ✅ (concepts) | ⚠️ | ✅ (traits) |

---

## 八、總結比較

### 8.1 核心特性綜合比較表

| 核心特性 | C | C++ | Go | Rust |
|---------|---|-----|-----|------|
| **記憶體管理** | 手動 | RAII/智能指標 | GC | 所有權系統 |
| **併發模型** | pthread | thread/coroutine | goroutine | async/await |
| **錯誤處理** | 錯誤碼 | 異常/expected | 多返回值 | Result<T,E> |
| **多型** | 函數指標 | 虛函數/模板 | 隱式介面 | Trait |
| **泛型** | 宏 | 模板 | 有限泛型 | 完整泛型 |
| **反射** | ❌ | ❌ | ✅ | 宏 |
| **包管理** | ❌ | 多種方案 | go mod | cargo |
| **編譯速度** | 極快 | 慢 | 快 | 中等 |
| **運行時性能** | 極快 | 極快 | 快 | 極快 |
| **記憶體安全** | ❌ | ⚠️ | ✅ (運行時) | ✅ (編譯時) |
| **學習曲線** | 中等 | 陡峭 | 平緩 | 陡峭 |
| **生態系統** | 成熟 | 極其豐富 | 快速成長 | 快速成長 |

---

### 8.2 性能特性比較

| 性能指標 | C | C++ | Go | Rust |
|---------|---|-----|-----|------|
| **執行速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **記憶體效率** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **編譯速度** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **並發性能** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **啟動速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **延遲可預測** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

### 8.3 開發體驗比較

| 開發體驗 | C | C++ | Go | Rust |
|---------|---|-----|-----|------|
| **易學性** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **開發速度** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **工具鏈** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **錯誤訊息** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **IDE 支援** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **除錯體驗** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

### 8.4 適用場景建議

#### C 最適合
* 嵌入式系統開發
* 作業系統核心開發
* 硬體驅動程式
* 極致性能要求的關鍵路徑
* 需要與硬體直接交互的場景
* 記憶體受限的環境

**優勢：** 最小開銷、完全控制、廣泛支援
**劣勢：** 開發效率低、容易出錯、缺乏現代特性

---

#### C++ 最適合
* 遊戲引擎開發
* 高性能計算 (HPC)
* 圖形渲染引擎
* 實時系統
* 需要極致性能優化的應用
* 大型複雜系統（配合 OOP）

**優勢：** 極致性能、豐富生態、靈活性高
**劣勢：** 複雜度高、編譯慢、容易寫出不安全代碼

---

#### Go 最適合
* 微服務架構
* 雲原生應用
* 網路服務和 API
* 分散式系統
* DevOps 工具
* 命令列工具
* 高併發的 I/O 密集型應用

**優勢：** 開發效率極高、併發模型優秀、部署簡單
**劣勢：** GC 延遲、泛型支援有限、性能不如 C++/Rust

---

#### Rust 最適合
* 系統編程
* WebAssembly 應用
* 區塊鏈開發
* 安全關鍵應用
* 嵌入式系統（替代 C）
* 高性能網路服務
* CLI 工具（需要速度和安全）

**優勢：** 記憶體安全、性能卓越、現代工具鏈
**劣勢：** 學習曲線陡峭、編譯慢、生態相對年輕

---

### 8.5 選擇決策樹

```
需要極致性能？
├─ 是 → 需要記憶體安全保證？
│       ├─ 是 → Rust
│       └─ 否 → C/C++
└─ 否 → 需要高併發？
        ├─ 是 → 需要 GC 可接受？
        │       ├─ 是 → Go
        │       └─ 否 → Rust
        └─ 否 → 開發速度優先？
                ├─ 是 → Go
                └─ 否 → 視需求選擇
```

---

### 8.6 結論

**並非「無法超越」，而是不同語言在設計時的取捨不同：**

1. **Go** 優先考慮開發效率和併發簡潔性，犧牲了部分性能和記憶體控制
2. **C** 提供最大控制權和最小開銷，但需要開發者承擔所有責任
3. **C++** 在性能和靈活性之間取得平衡，但複雜度極高
4. **Rust** 在性能、安全和現代性之間找到新的平衡點，但學習成本高

**選擇建議：**
* **快速開發、高併發：** Go
* **極致性能、複雜系統：** C++
* **安全關鍵、系統級：** Rust
* **嵌入式、OS 開發：** C

最終選擇應基於：
- 專案需求（性能、安全、開發速度）
- 團隊能力（學習成本、維護成本）
- 生態系統（函式庫、工具、社群支援）
- 長期維護考量（可讀性、可維護性）

---

## 附錄：學習資源

### Go
- 官方文檔：https://go.dev/doc/
- Go by Example：https://gobyexample.com/
- Effective Go：https://go.dev/doc/effective_go

### C
- C Programming Language (K&R)
- Modern C (Jens Gustedt)
- POSIX 標準文檔

### C++
- cppreference.com
- C++ Core Guidelines
- Effective Modern C++ (Scott Meyers)

### Rust
- The Rust Programming Language Book
- Rust by Example
- Rustlings 練習

---

**文檔版本：** 1.0  
**最後更新：** 2024-11  
**作者：** Claude  
**授權：** CC BY-SA 4.0
