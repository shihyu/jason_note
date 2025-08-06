# Go + MySQL 死鎖問題調查指南

## 問題背景

在 Go 應用中遇到 MySQL InnoDB 死鎖時，由於 Go 的特殊架構，問題調查變得困難：

- **單一 PID**：整個程式只有一個 Process ID
- **固定線程數**：預設等於 CPU 核心數量
- **大量 Goroutine**：實際工作單位，但都共享少數線程執行
- **難以追蹤**：無法直接從系統層面定位具體是哪個 goroutine 造成問題

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