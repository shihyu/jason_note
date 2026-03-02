# Go 編譯細節查看指令

以目前目錄的 `test.go` 為例。

## 範例程式碼

`test.go` 內容如下：

```go
package main

import (
    "fmt"
    "math/rand"
    "time"
)

func random(min, max int) int {
    rand.Seed(time.Now().Unix())
    return rand.Intn(max-min) + min
}

func tortoise(totalStep int) {
    for step := 1; step <= totalStep; step++ {
        fmt.Printf("烏龜跑了 %d 步...\n", step)
    }
}

func hare(totalStep int) {
    flags := [...]bool{true, false}
    step := 0
    for step < totalStep {
        isHareSleep := flags[random(1, 10)%2]
        if isHareSleep {
            fmt.Println("兔子睡著了zzzz")
        } else {
            step += 2
            fmt.Printf("兔子跑了 %d 步...\n", step)
        }
    }
}

func main() {
    totalStep := 10

    go tortoise(totalStep)
    go hare(totalStep)

    time.Sleep(5 * time.Second)
}
```

## 1. 看完整編譯流程

```bash
go build -a -x -work test.go
```

- `-x`：印出實際執行的 compile / asm / link 指令
- `-a`：強制重編，避免 build cache 導致輸出過少
- `-work`：保留暫存目錄，輸出會顯示 `WORK=/tmp/go-build...`

常見重點輸出：

```text
/home/shihyu/go/pkg/tool/linux_amd64/compile ... ./test.go
/home/shihyu/go/pkg/tool/linux_amd64/link ...
cp $WORK/b001/exe/a.out test
```

## 2. 只想執行並顯示建置流程

```bash
go run -a -x test.go
```

適合快速看 `run` 時背後做了哪些編譯與連結步驟。

## 3. 看 inline / escape analysis

```bash
go build -gcflags='all=-m -m' test.go
```

可看到：

- 哪些函式被 inline
- 哪些變數逃逸到 heap
- 編譯器最佳化判斷

## 4. 看組語

```bash
go build -a -gcflags='all=-S' test.go 2> build.s
```

- `-S`：輸出 assembly
- 建議把 stderr 轉到檔案，不然終端會很亂

查看：

```bash
less build.s
```

## 5. 看暫存工作目錄內容

先執行：

```bash
go build -a -x -work test.go
```

再進去 `WORK` 目錄，例如：

```bash
less /tmp/go-build438143439/b001/importcfg
less /tmp/go-build438143439/b001/importcfg.link
```

可看到：

- 套件依賴
- link 階段匯入設定
- 中間產物位置

## 6. 常用組合

### 看流程 + 最佳化資訊

```bash
go build -a -x -work -gcflags='all=-m -m' test.go
```

### 看流程 + 組語

```bash
go build -a -x -work -gcflags='all=-S' test.go 2> build.s
```

## 7. 使用範例

### 範例 1：直接看 `test.go` 的完整編譯流程

```bash
go build -a -x -work test.go
```

預期會看到類似：

```text
WORK=/tmp/go-build438143439
/home/shihyu/go/pkg/tool/linux_amd64/compile ... ./test.go
/home/shihyu/go/pkg/tool/linux_amd64/link ...
cp $WORK/b001/exe/a.out test
```

用途：

- 確認 Go 實際呼叫了哪些 compiler / linker
- 確認最後輸出的執行檔名稱

### 範例 2：把編譯流程存成 log

```bash
go build -a -x -work test.go > build.log 2>&1
less build.log
```

用途：

- 方便搜尋 `compile`
- 方便搜尋 `link`
- 適合保留建置紀錄

### 範例 3：只看 escape analysis

```bash
go build -gcflags='all=-m -m' test.go 2> escape.log
less escape.log
```

可搜尋：

```bash
rg "escapes to heap|can inline|inlining call" escape.log
```

用途：

- 檢查變數是否逃逸到 heap
- 檢查函式是否被 inline

### 範例 4：輸出組語後查 `main.main`

```bash
go build -a -gcflags='all=-S' test.go 2> build.s
rg "main.main|main.hare|main.tortoise" build.s
```

用途：

- 快速定位 `main.main`
- 檢查 `hare` / `tortoise` 對應的 assembly

### 範例 5：取得 `WORK` 目錄後查看 link 設定

```bash
go build -a -x -work test.go 2>&1 | tee build.log
rg '^WORK=' build.log
```

假設找到：

```text
WORK=/tmp/go-build438143439
```

再查看：

```bash
less /tmp/go-build438143439/b001/importcfg
less /tmp/go-build438143439/b001/importcfg.link
```

用途：

- 看 `test.go` 編譯時吃了哪些套件
- 看 link 階段的 packagefile 對應

### 範例 6：邊執行邊看建置流程

```bash
go run -a -x test.go
```

用途：

- 不只編譯，還會直接執行程式
- 適合快速驗證單檔案程式

## 8. 注意事項

- 沒加 `-a` 時，可能只看到 `WORK=...`，因為 Go 直接用 cache
- `-S`、`-m` 大多走 stderr，重導向時要注意
- 單檔案模式會輸出成預設執行檔，例如這裡是 `./test`
