# Go + MySQL 死鎖問題調查指南

## 問題背景

在 Go 應用中遇到 MySQL InnoDB 死鎖時，由於 Go 的特殊架構，問題調查變得困難：

- **單一 PID**：整個程式只有一個 Process ID
- **固定線程數**：預設等於 CPU 核心數量
- **大量 Goroutine**：實際工作單位，但都共享少數線程執行
- **難以追蹤**：無法直接從系統層面定位具體是哪個 goroutine 造成問題

## Go 語言架構特性

### 單一 Process 設計

Go 程式**預設只有一個 process**，不會自動產生多個 process：

```go
func main() {
    // 不管你寫多複雜的程式
    for i := 0; i < 10000; i++ {
        go func() {
            // 開 10000 個 goroutine
            doSomething()
        }()
    }
    // 在作業系統看來，還是只有一個 process
}
```

### 系統層面的觀察

```bash
# 只會看到一個程序
ps aux | grep your-go-app
# PID   USER    COMMAND
# 1234  user    ./your-go-app

# 但這個程序內部有多個線程
ps -T -p 1234
# PID   SPID  COMMAND
# 1234  1234  ./your-go-app
# 1234  1235  ./your-go-app  
# 1234  1236  ./your-go-app
# ... (會有多個線程，SPID 不同但 PID 相同)
```

### 多核心環境下的表現

以 **10核心20線程** 的主機為例：

```go
// Go 會自動偵測到系統有 20 個邏輯處理器
// 預設 GOMAXPROCS = 20
fmt.Println(runtime.GOMAXPROCS(0)) // 輸出: 20
```

**實際運作方式**：
- Go runtime 會建立 **20 個 OS 線程**
- 對應 CPU 的 20 個邏輯處理器（10物理核心 × 2超線程）
- 10000 個 goroutine 會被分配到這 20 個線程上執行

**餐廳比喻**：
- **物理核心** = 10 個廚房區域  
- **邏輯處理器** = 20 個工作台（每個廚房區域有2個工作台）
- **OS 線程** = 20 個廚師（每個工作台配一個廚師）
- **Goroutine** = 成千上萬張訂單
- **Go runtime** = 餐廳經理，分配訂單給20個廚師

### 為什麼採用單一 Process 設計？

**效率考量**：
- **Process 切換成本高** - 需要切換記憶體空間
- **Goroutine 切換成本低** - 只需要切換堆疊  
- **記憶體共享容易** - 同一個 process 內的 goroutine 可以直接共享記憶體

**架構比較**：
```
傳統多進程模式：
Process 1: Thread 1, Thread 2, Thread 3
Process 2: Thread 1, Thread 2, Thread 3  
Process 3: Thread 1, Thread 2, Thread 3
→ 9 個線程，3 個記憶體空間，進程間通訊複雜

Go 模式：
Process 1: 20個線程 + 10000個 Goroutine  
→ 20 個線程，1 個記憶體空間，goroutine 間通訊簡單
```

### 何時會有多個 Process？

**只有主動建立時**：

#### 1. 使用 os/exec 套件
```go
import "os/exec"

func main() {
    // 主動啟動另一個程序
    cmd := exec.Command("ls", "-l")
    cmd.Run() // 這會產生新的 process
}
```

#### 2. 部署時開多個實例
```bash
# 手動啟動多個程序
./my-go-app --port=8080 &  # Process 1234
./my-go-app --port=8081 &  # Process 1235  
./my-go-app --port=8082 &  # Process 1236
```

### 對死鎖調查的影響

**多核心環境下更複雜**：
1. **更多同時進行的操作** - 20個線程同時運行
2. **更高的並行度** - 死鎖發生機會更高
3. **更複雜的交互** - 線程間資源競爭更激烈

**log 記錄會更混亂**：
```
Thread-01: [TraceID-001] Locking user 123
Thread-15: [TraceID-089] Locking user 456  
Thread-03: [TraceID-024] Locking user 123  // <- 可能造成衝突
Thread-08: [TraceID-067] Locking user 456  // <- 可能造成衝突
Thread-12: [TraceID-099] Transfer complete
... (同時會有很多 log 混在一起)
```

## 調查方法

### 1. 從資料庫端找線索

#### 查看死鎖詳情
```sql
SHOW ENGINE INNODB STATUS;
```
可以看到：
- 造成死鎖的 SQL 語句
- 涉及的資料表和索引
- 鎖定的具體資料

#### 開啟完整死鎖記錄
```sql
SET GLOBAL innodb_print_all_deadlocks = ON;
```
所有死鎖都會記錄到 MySQL 錯誤日誌中

### 2. Go 程式中加入追蹤

#### 關鍵操作加入詳細 Log
```go
func transferMoney(fromID, toID int, amount float64) {
    traceID := generateTraceID() // 產生唯一追蹤ID
    
    log.Printf("[%s] START transfer from=%d to=%d amount=%.2f", traceID, fromID, toID, amount)
    
    tx, err := db.Begin()
    if err != nil {
        log.Printf("[%s] ERROR begin transaction: %v", traceID, err)
        return err
    }
    
    log.Printf("[%s] LOCK user %d", traceID, fromID)
    _, err = tx.Exec("SELECT * FROM users WHERE id = ? FOR UPDATE", fromID)
    if err != nil {
        log.Printf("[%s] ERROR lock user %d: %v", traceID, fromID, err)
        return err
    }
    
    // ... 其他操作也都加 log
}
```

#### 記錄 Goroutine 資訊
```go
import "runtime"

func getGoroutineID() uint64 {
    // 取得當前 goroutine ID
    return goid.Get()
}

// 在每個資料庫操作前記錄
log.Printf("Goroutine %d executing SQL: %s", getGoroutineID(), sqlQuery)
```

### 3. 使用分散式追蹤

#### 建立追蹤上下文
```go
import "github.com/google/uuid"

type Context struct {
    TraceID string
    UserID  int
}

func (c *Context) logSQL(sql string, args ...interface{}) {
    log.Printf("TraceID=%s UserID=%d SQL=%s Args=%v", 
               c.TraceID, c.UserID, sql, args)
}

// 使用範例
ctx := &Context{
    TraceID: uuid.New().String(),
    UserID:  123,
}
```

### 4. 業務流程監控

#### 記錄完整業務上下文
```go
func processOrder(orderID int) {
    log.Printf("=== Processing Order %d START ===", orderID)
    defer log.Printf("=== Processing Order %d END ===", orderID)
    
    log.Printf("Order %d: checking inventory", orderID)
    // ... SQL操作
    
    log.Printf("Order %d: updating stock", orderID) 
    // ... SQL操作
    
    log.Printf("Order %d: creating payment", orderID)
    // ... SQL操作
}
```

### 5. 程式碼靜態分析

#### 檢查鎖定順序
- 搜尋所有 `FOR UPDATE`、`BEGIN TRANSACTION` 語句
- 檢查不同函數是否以不同順序存取相同資料表
- 建立鎖定依賴圖，視覺化潛在死鎖路徑

### 6. 壓力測試重現

#### 建立死鎖重現測試
```go
func TestDeadlock(t *testing.T) {
    var wg sync.WaitGroup
    
    // 同時執行多個會衝突的操作
    for i := 0; i < 100; i++ {
        wg.Add(2)
        go func() {
            defer wg.Done()
            transferMoney(1, 2, 100) // A->B
        }()
        go func() {
            defer wg.Done() 
            transferMoney(2, 1, 50)  // B->A
        }()
    }
    wg.Wait()
}
```

**可能需要的配置調整**：
```go
// 如果死鎖問題嚴重，可以考慮限制並行度
runtime.GOMAXPROCS(10) // 只用10個線程而不是20個

// 或者調整資料庫連接池
db.SetMaxOpenConns(10) // 限制最大連接數
db.SetMaxIdleConns(5)  // 限制閒置連接數
```

**監控策略**：
```go
// 需要更詳細的 goroutine 和線程資訊
func logWithRuntimeInfo() {
    log.Printf("PID: %d, GOMAXPROCS: %d, NumGoroutine: %d, NumCPU: %d", 
               os.Getpid(),
               runtime.GOMAXPROCS(0), 
               runtime.NumGoroutine(),
               runtime.NumCPU())
}
```

## 建議調查順序

### 第一步：資料庫層面分析
1. 檢查 `SHOW ENGINE INNODB STATUS` 輸出
2. 開啟 `innodb_print_all_deadlocks` 記錄完整死鎖資訊
3. 分析死鎖涉及的具體 SQL 語句和資料表

### 第二步：程式碼對應
1. 在程式碼中搜尋死鎖相關的 SQL 語句
2. 找到執行這些 SQL 的函數和業務流程
3. 檢查是否存在不同順序的資源存取

### 第三步：加入追蹤
1. 在可疑程式碼區域加入詳細日誌
2. 加入 TraceID 或 Goroutine ID 追蹤
3. 記錄業務操作的完整流程

### 第四步：重現測試  
1. 在測試環境嘗試重現死鎖
2. 透過壓力測試驗證修復效果
3. 建立監控機制持續觀察

## 關鍵重點

- **建立業務操作到 SQL 的對應關係**：這是在 goroutine 海中找到問題源頭的關鍵
- **詳細記錄執行順序**：死鎖通常與資源存取順序有關
- **保留足夠上下文資訊**：TraceID、UserID、OrderID 等業務標識符
- **結合資料庫和應用日誌**：兩邊的資訊互相印證才能完整還原問題

雖然 Go 的 goroutine 架構讓問題追蹤變複雜，但透過適當的日誌記錄和分析方法，還是可以有效定位和解決死鎖問題。
