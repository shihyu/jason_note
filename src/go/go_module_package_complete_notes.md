# Go Module 與 Package 完整筆記

## `go.mod` 檔案長什麼樣

```go
module myapp          // 模組名稱（自行命名）

go 1.21               // Go 版本

require (
  github.com/gin-gonic/gin v1.9.0  // 相依套件
)
```

---

## 常用指令

| 指令 | 用途 | 備註 |
| --- | --- | --- |
| `go mod init <名稱>` | 建立新模組 | 一個專案通常只用一次 |
| `go mod tidy` | 整理相依套件 | 移除沒用到的、補上缺少的 |
| `go get <套件>` | 新增或更新套件 | 例：`go get github.com/gin-gonic/gin` |
| `go mod download` | 下載所有相依到本機快取 | CI 環境常用 |
| `go mod vendor` | 把相依複製進 `vendor/` 資料夾 | 離線環境或公司內網常用 |

---

## `go.mod` vs `go.sum`

| 檔案 | 內容 | 要手動改嗎？ |
| --- | --- | --- |
| `go.mod` | 模組名稱、Go 版本、相依清單 | 可以，但通常交給指令處理 |
| `go.sum` | 套件的雜湊校驗值 | **不要手動改** |

---

## `package` 是什麼

Go 的程式碼以 **package（套件）** 為單位組織，每個 `.go` 檔案第一行都要宣告自己屬於哪個 package。

```go
package main // 可執行程式的入口，一定叫 main
```

```go
package utils // 自訂 package，名稱自行決定
```

### `module` 和 `package` 的關係

```text
module myapp               ← 整個專案的名稱（go.mod 定義）
├── package main           ← main.go
├── package utils          ← utils/helper.go
└── package models         ← models/user.go
```

- **module** = 整個專案或函式庫（一個 `go.mod` 對應一個 module）
- **package** = module 裡的子資料夾，用來分類程式碼

### `import` 怎麼寫

```go
import (
  "fmt"                      // 標準函式庫
  "myapp/utils"              // 自己的 package（模組名 + 路徑）
  "github.com/gin-gonic/gin" // 外部套件
)
```

---

## 專案結構範例

```text
myapp/                        ← module: myapp
├── go.mod
├── go.sum
├── main.go                   ← package main
├── utils/
│   └── helper.go             ← package utils
├── models/
│   └── user.go               ← package models
└── handlers/
    └── api.go                ← package handlers
```

---

## `package` 命名規則

| 規則 | 說明 |
| --- | --- |
| 小寫英文 | `package utils` ✅，`package Utils` ❌ |
| 和資料夾同名 | `handlers/api.go` 對應 `package handlers` |
| 大寫 = 公開 | `func Hello()` 可被其他 package 使用 |
| 小寫 = 私有 | `func hello()` 只有同 package 內可以用 |

---

## 容易誤解的地方

### 1. 模組名稱不一定要 `github.com/...`

- 自己用：`go mod init myapp` 就好
- 要發布讓別人 `go get`：才需要對應真實 URL

```bash
go mod init github.com/你的帳號/專案名
```

### 2. `go mod` 不只是用在 GitHub

任何 Go 專案都建議使用 `go mod`，因為它負責管理相依套件版本，和 GitHub 沒有直接關係。

### 3. 單一 `.go` 檔可以不用 `go mod`

```bash
go run main.go # 沒有外部套件時，直接跑即可
```

但只要用到外部套件，或專案中有多個 package，就建議使用 `go mod`。

### 4. `go.sum` 會自動產生，不要手動編輯

執行 `go mod tidy` 或 `go get` 後，`go.sum` 會自動更新。

### 5. 資料夾名稱不一定等於 package 名稱

技術上可以不同，但強烈建議保持一致，否則 `import` 時很容易搞混。

### 6. `package main` 只能有一個 `main()` 函式入口

整個 module 裡可以有很多個 `package main`，例如 `cmd/` 下放多個工具；但每個可執行程式都只能有一個 `main()` 入口。

```text
myapp/
├── cmd/
│   ├── server/main.go   ← package main（啟動伺服器）
│   └── cli/main.go      ← package main（命令列工具）
└── internal/
    └── db/db.go         ← package db（共用邏輯）
```

---

## 初始化步驟

```bash
mkdir myapp
cd myapp
go mod init myapp       # 建立 go.mod
# 開始寫 main.go...
go get github.com/xxx   # 新增外部套件
go mod tidy             # 整理相依
go build ./...          # 編譯全部
go run main.go          # 執行
```

---

## 實際操作範例（完整流程）

### 範例一：多 Package 專案從零開始

**目標**：建立一個有 `utils`、`models` 兩個 package 的小工具。

```bash
# Step 1：建立目錄並初始化
mkdir -p myapp/utils myapp/models
cd myapp
go mod init myapp
```

**`go.mod` 初始內容**（自動生成）：
```
module myapp

go 1.21
```

---

**`models/user.go`**：
```go
package models

import "fmt"

type User struct {
    ID   int
    Name string
    Age  int
}

// String 讓 fmt.Println 直接輸出好看格式
func (u User) String() string {
    return fmt.Sprintf("User{ID:%d, Name:%s, Age:%d}", u.ID, u.Name, u.Age)
}

// IsAdult 是公開方法（大寫開頭）
func (u User) IsAdult() bool {
    return u.Age >= 18
}

// validate 是私有方法（小寫開頭）
func (u User) validate() bool {
    return u.Name != "" && u.Age > 0
}
```

---

**`utils/helper.go`**：
```go
package utils

import "strings"

// FilterAdults 只保留成年人（公開函式）
func FilterAdults(users []string) []string {
    var result []string
    for _, name := range users {
        name = strings.TrimSpace(name)
        if name != "" {
            result = append(result, name)
        }
    }
    return result
}

// Greet 回傳問候語
func Greet(name string) string {
    return "Hello, " + name + "!"
}
```

---

**`main.go`**：
```go
package main

import (
    "fmt"
    "myapp/models"  // 模組名 + 資料夾路徑
    "myapp/utils"
)

func main() {
    // 使用 models package
    u := models.User{ID: 1, Name: "Alice", Age: 25}
    fmt.Println(u)             // User{ID:1, Name:Alice, Age:25}
    fmt.Println(u.IsAdult())   // true

    // 使用 utils package
    names := []string{"Bob", "Charlie", "  "}
    filtered := utils.FilterAdults(names)
    fmt.Println(filtered)       // [Bob Charlie]

    fmt.Println(utils.Greet("World"))  // Hello, World!
}
```

**執行結果**：
```bash
$ go run main.go
User{ID:1, Name:Alice, Age:25}
true
[Bob Charlie]
Hello, World!
```

---

### 範例二：新增外部套件（以 `uuid` 為例）

```bash
# 安裝外部套件
go get github.com/google/uuid
```

**`go.mod` 變化**（自動更新）：
```
module myapp

go 1.21

require github.com/google/uuid v1.6.0
```

**使用範例**：
```go
package main

import (
    "fmt"
    "github.com/google/uuid"
)

func main() {
    id := uuid.New()
    fmt.Println(id)           // e.g., 550e8400-e29b-41d4-a716-446655440000
    fmt.Println(id.String())  // 同上，字串形式
}
```

```bash
$ go run main.go
3f6a6b3d-1c2e-4e5f-a7b8-9d0e1f2a3b4c
```

---

### 範例三：指定版本、升降版

```bash
# 安裝特定版本
go get github.com/google/uuid@v1.3.0

# 升級到最新版
go get github.com/google/uuid@latest

# 升級到特定版本
go get github.com/google/uuid@v1.6.0

# 移除套件（先從程式碼移除 import，再執行）
go mod tidy
```

**查看目前所有相依版本**：
```bash
$ go list -m all
myapp
github.com/google/uuid v1.6.0
```

---

### 範例四：`replace` 指令（本地開發替換）

當你正在同時開發兩個 module（例如開發一個函式庫並在另一個專案測試它），可以用 `replace` 讓 Go 直接讀本機版本，不從網路抓。

**目錄結構**：
```
~/projects/
├── mylib/        ← 你正在開發的函式庫
│   ├── go.mod    (module github.com/you/mylib)
│   └── lib.go
└── myapp/        ← 使用該函式庫的專案
    ├── go.mod
    └── main.go
```

**`mylib/go.mod`**：
```
module github.com/you/mylib

go 1.21
```

**`mylib/lib.go`**：
```go
package mylib

func Hello() string {
    return "Hello from local mylib!"
}
```

**`myapp/go.mod`**（加入 replace）：
```
module myapp

go 1.21

require github.com/you/mylib v0.0.0

replace github.com/you/mylib => ../mylib   ← 指向本機路徑
```

**`myapp/main.go`**：
```go
package main

import (
    "fmt"
    "github.com/you/mylib"
)

func main() {
    fmt.Println(mylib.Hello())  // Hello from local mylib!
}
```

```bash
$ cd myapp && go run main.go
Hello from local mylib!
```

> **注意**：`replace` 只影響當前 module，不會傳遞給依賴你的人。要發布前記得移除 replace。

---

### 範例五：`internal` package（受保護的內部套件）

`internal/` 資料夾內的 package 只有**同一個 module** 可以 import，外部套件無法引用。

```
myapp/
├── go.mod                    (module myapp)
├── main.go
├── internal/
│   └── auth/
│       └── token.go          ← package auth（受保護）
└── api/
    └── handler.go            ← 可以 import internal/auth
```

**`internal/auth/token.go`**：
```go
package auth

import "crypto/rand"
import "encoding/hex"

// GenerateToken 產生隨機 token（只限內部使用）
func GenerateToken() string {
    b := make([]byte, 16)
    rand.Read(b)
    return hex.EncodeToString(b)
}
```

**`api/handler.go`**（同一 module，可以 import）：
```go
package api

import (
    "fmt"
    "myapp/internal/auth"  // ✅ 同 module，可以用
)

func HandleLogin() {
    token := auth.GenerateToken()
    fmt.Println("Token:", token)
}
```

**外部 module 嘗試 import 會報錯**：
```
# otherpkg/main.go
import "myapp/internal/auth"
# Error: use of internal package myapp/internal/auth not allowed
```

---

### 範例六：多個可執行檔（`cmd/` 模式）

```
myapp/
├── go.mod
├── cmd/
│   ├── server/
│   │   └── main.go    ← 啟動 HTTP server
│   └── migrate/
│       └── main.go    ← 執行資料庫遷移
└── internal/
    └── db/
        └── db.go
```

**`cmd/server/main.go`**：
```go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    fmt.Println("Starting server on :8080")
    http.ListenAndServe(":8080", nil)
}
```

**`cmd/migrate/main.go`**：
```go
package main

import "fmt"

func main() {
    fmt.Println("Running database migration...")
}
```

**分別編譯與執行**：
```bash
# 執行特定 cmd
go run ./cmd/server
go run ./cmd/migrate

# 編譯全部
go build ./cmd/...

# 個別編譯
go build -o bin/server ./cmd/server
go build -o bin/migrate ./cmd/migrate
```

---

### 範例七：`go work`（多 Module 工作區，Go 1.18+）

當你在同一個機器上同時修改多個相互依賴的 module，`go.work` 比 `replace` 更方便，不需要修改 `go.mod`。

```bash
# 在上層目錄初始化 workspace
cd ~/projects
go work init ./mylib ./myapp
```

**`go.work`（自動生成）**：
```
go 1.21

use (
    ./mylib
    ./myapp
)
```

現在 `myapp` 會自動使用本機 `mylib`，**不需要修改任何 `go.mod`**。

```bash
# 加入更多 module 到 workspace
go work use ./another-module

# 開發完成後，可以完全忽略 go.work（CI 環境不需要它）
GOWORK=off go build ./...
```

---

## 常見錯誤與解法

### 錯誤 1：`no required module provides package`

```
no required module provides package github.com/foo/bar
```

**原因**：用到了沒有 `go get` 的套件。
**解法**：
```bash
go get github.com/foo/bar
# 或
go mod tidy  # 自動補上 import 的套件
```

---

### 錯誤 2：`imported and not used`

```
./main.go:5:2: "fmt" imported and not used
```

**原因**：import 了但沒用到。
**解法**：刪除該 import，或用空白識別符（只想要 side effect）：
```go
import _ "github.com/lib/pq"  // 只執行 init()，不使用其他符號
```

---

### 錯誤 3：`package xxx is not in GOROOT`

```
package utils: package utils is not in GOROOT (/usr/local/go/src/utils)
```

**原因**：直接寫了 `"utils"` 而不是 `"myapp/utils"`。
**解法**：import 自己的 package 要加上 module 名：
```go
import "myapp/utils"   // ✅
import "utils"         // ❌
```

---

### 錯誤 4：`ambiguous import`

```
ambiguous import: found package github.com/foo/bar in multiple modules
```

**原因**：`go.work` 或 `replace` 造成同一套件有多個來源。
**解法**：檢查 `go.work` 和 `go.mod` 的 `replace` 設定，確保每個 package 只有一個來源。

---

### 錯誤 5：`cannot find module providing package`（Go Proxy 問題）

```bash
# 設定 proxy（中國大陸常見問題）
go env -w GOPROXY=https://goproxy.cn,direct

# 關閉 proxy（私有 repo）
go env -w GONOSUMCHECK=your.private.domain
go env -w GOFLAGS=-mod=mod
```

---

## `go mod tidy` 實際展示

```bash
$ cat go.mod
module myapp

go 1.21

require (
    github.com/google/uuid v1.6.0
    github.com/some/unused v1.0.0   ← 程式碼已不用但還在這
)

$ go mod tidy
# 自動移除 unused，補上 missing

$ cat go.mod
module myapp

go 1.21

require github.com/google/uuid v1.6.0
# some/unused 已被移除
```

---

## 版本語義（SemVer）

Go module 遵守 [Semantic Versioning](https://semver.org/)：

| 版本 | 意義 | 範例 |
| --- | --- | --- |
| `v1.2.3` | 正式版 | `go get pkg@v1.2.3` |
| `v1.2.3-alpha` | 預覽版 | `go get pkg@v1.2.3-alpha` |
| `@latest` | 最新正式版 | `go get pkg@latest` |
| `@main` | main 分支最新 commit | `go get pkg@main` |

> **Major version 規則**：v2 以上的 module，import 路徑要加 `/v2`：
> ```go
> import "github.com/foo/bar/v2"  // v2+
> import "github.com/foo/bar"      // v0 / v1
> ```

---

## 完整指令速查

```bash
# 初始化
go mod init <模組名>

# 新增套件
go get <套件>@<版本>           # 指定版本
go get <套件>@latest           # 最新版
go get <套件>@main             # main 分支

# 整理
go mod tidy                    # 移除未用、補上缺少

# 查詢
go list -m all                 # 列出所有相依版本
go mod graph                   # 顯示相依樹
go mod why <套件>              # 解釋為什麼需要這個套件

# 下載
go mod download                # 預先下載所有相依

# 離線/vendor
go mod vendor                  # 複製相依到 vendor/
go build -mod=vendor ./...     # 使用 vendor/ 建置

# Workspace
go work init ./a ./b           # 初始化工作區
go work use ./c                # 加入 module
go work sync                   # 同步 go.work.sum
```
