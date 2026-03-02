# Go 編譯細節查看指令

```text
┌────────────────────────────────────────────────────────────┐
│  test.go                                                   │
│  Go source code                                            │
└────────────────────────────────────────────────────────────┘
                               |
                               v
┌────────────────────────────────────────────────────────────┐
│  go build  -a -x -work  test.go                            │
│  GOOS=linux  GOARCH=amd64  CGO_ENABLED=0                   │
│  (交叉編譯加: GOARM=7 / GOMIPS=softfloat 等)               │
└────────────────────────────────────────────────────────────┘
                               |
                               v
┌────────────────────────────────────────────────────────────┐
│  mkdir -p $WORK/b001/  $WORK/b002/ ...                     │
│  建立暫存工作目錄  WORK=/tmp/go-buildXXXXXXXX               │
└────────────────────────────────────────────────────────────┘
                               |
               ┌───────────────┴────────────────┐
               |                                |
               v                                v
┌────────────────────────────┐  ┌────────────────────────────┐
│  一般套件                  │  │  含 .s 組語的套件            │
│  compile                  │  │  compile                   │
│    -o $WORK/bXXX/_pkg_.a  │  │    -o $WORK/bXXX/_pkg_.a   │
│    -p <pkgname>           │  │    -p <pkgname>            │
│    -importcfg importcfg   │  │  asm -p <pkgname> *.s      │
│                           │  │    → *.o                   │
│  fmt / time / math/rand   │  │  pack r _pkg_.a *.o        │
│  等標準套件               │  │  runtime / sync/atomic 等  │
└────────────────────────────┘  └────────────────────────────┘
               |                                |
               └───────────────┬────────────────┘
                               |
                               v
┌────────────────────────────────────────────────────────────┐
│  build cache                                               │
│  cp $WORK/bXXX/_pkg_.a  →  ~/.cache/go-build/<hash>-d      │
│  相同輸入條件下次直接復用，跳過重編                          │
└────────────────────────────────────────────────────────────┘
                               |
                               v
┌────────────────────────────────────────────────────────────┐
│  importcfg  (compile 階段相依表)                            │
│  cat > $WORK/b001/importcfg << 'EOF'                       │
│  packagefile fmt     = $WORK/b002/_pkg_.a                  │
│  packagefile time    = $WORK/b038/_pkg_.a                  │
│  packagefile runtime = $WORK/b009/_pkg_.a                  │
│  EOF                                                       │
└────────────────────────────────────────────────────────────┘
                               |
                               v
┌────────────────────────────────────────────────────────────┐
│  compile -p main  ./test.go                                │
│    -o $WORK/b001/_pkg_.a  -pack                            │
│    -importcfg $WORK/b001/importcfg                         │
└────────────────────────────────────────────────────────────┘
                               |
                               v
┌────────────────────────────────────────────────────────────┐
│  importcfg.link  (link 階段相依表)                          │
│  cat > $WORK/b001/importcfg.link << 'EOF'                  │
│  packagefile command-line-arguments=$WORK/b001/_pkg_.a     │
│  packagefile fmt     = $WORK/b002/_pkg_.a                  │
│  packagefile runtime = $WORK/b009/_pkg_.a  ...             │
│  EOF                                                       │
└────────────────────────────────────────────────────────────┘
                               |
                               v
┌────────────────────────────────────────────────────────────┐
│  link                                                      │
│    -o $WORK/b001/exe/a.out                                 │
│    -importcfg $WORK/b001/importcfg.link                    │
│    -buildmode=exe  -extld=gcc                              │
│    $WORK/b001/_pkg_.a                                      │
└────────────────────────────────────────────────────────────┘
                               |
                               v
┌────────────────────────────────────────────────────────────┐
│  buildid -w $WORK/b001/exe/a.out                           │
│  寫入 build ID                                             │
└────────────────────────────────────────────────────────────┘
                               |
                               v
┌────────────────────────────────────────────────────────────┐
│  cp $WORK/b001/exe/a.out → 最終輸出                        │
│                                                            │
│  本機編譯：  cp ... → ./test                               │
│  交叉編譯：  cp ... → qemu-bin/test-linux-386              │
│                       qemu-bin/test-linux-armv7            │
│                       qemu-bin/test-linux-mips             │
│                       qemu-bin/test-linux-ppc64            │
└────────────────────────────────────────────────────────────┘
                               |
                               v  (交叉編譯時)
┌────────────────────────────────────────────────────────────┐
│  qemu user-mode verify                                     │
│  timeout 8s qemu-i386  ./qemu-bin/test-linux-386           │
│  timeout 8s qemu-arm   ./qemu-bin/test-linux-armv7         │
│  timeout 8s qemu-mips  ./qemu-bin/test-linux-mips          │
│  timeout 8s qemu-ppc64 ./qemu-bin/test-linux-ppc64         │
│  → 驗證輸出正常 + exit code = 0                            │
└────────────────────────────────────────────────────────────┘
```

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

## 9. `build.log` 這份紀錄是怎麼編成執行檔的

這份 `build.log` 對應的是：

```bash
go build -a -x -work test.go > build.log 2>&1
```

最後產生的執行檔是目前目錄下的 `test`。

### 流程拆解

1. 建立暫存工作目錄

一開始會看到：

```text
WORK=/tmp/go-build1624675521
mkdir -p $WORK/b015/
mkdir -p $WORK/b008/
...
```

意思是 Go 先建立一個暫存建置目錄，後面的 `b001`、`b002`、`b009` 這些子目錄就是各套件的中間產物目錄。

2. 先編標準庫與相依套件

例如：

```text
/home/shihyu/go/pkg/tool/linux_amd64/compile -o $WORK/b002/_pkg_.a ... -p fmt ...
/home/shihyu/go/pkg/tool/linux_amd64/compile -o $WORK/b038/_pkg_.a ... -p time ...
/home/shihyu/go/pkg/tool/linux_amd64/compile -o $WORK/b044/_pkg_.a ... -p math/rand ...
```

- `-p fmt`、`-p time`、`-p math/rand` 表示正在編哪個 package
- 輸出檔 `_pkg_.a` 是該 package 的 archive
- 因為有 `-a`，所以連標準庫也會重編

3. 有 assembly 的套件會先 `asm` 再 `pack`

例如 runtime：

```text
/home/shihyu/go/pkg/tool/linux_amd64/asm -p runtime ...
/home/shihyu/go/pkg/tool/linux_amd64/pack r $WORK/b009/_pkg_.a ...
```

流程是先把 `.s` 組語檔組譯成 `.o`，再把 `.go` 編譯結果和 `.o` 一起打包進 `_pkg_.a`。

4. 每個 package 編完會寫入 build cache

例如：

```text
cp $WORK/b002/_pkg_.a /home/shihyu/.cache/go-build/...
```

這表示中間產物被複製到 Go build cache，之後若條件相同可直接重用。

5. 輪到主程式 `test.go`

關鍵段落是：

```text
cat >.../b001/importcfg << 'EOF'
packagefile fmt=/tmp/go-build1624675521/b002/_pkg_.a
packagefile math/rand=/tmp/go-build1624675521/b044/_pkg_.a
packagefile time=/tmp/go-build1624675521/b038/_pkg_.a
packagefile runtime=/tmp/go-build1624675521/b009/_pkg_.a
EOF
/home/shihyu/go/pkg/tool/linux_amd64/compile -o $WORK/b001/_pkg_.a ... -p main ... -pack ./test.go
```

- `importcfg` 先列出 `test.go` 需要的 package 檔案位置
- `-p main` 表示這次編的是主套件
- `./test.go` 被編成 `$WORK/b001/_pkg_.a`

6. 產生 link 階段用的相依清單

接著會看到：

```text
cat >.../b001/importcfg.link << 'EOF'
packagefile command-line-arguments=/tmp/go-build1624675521/b001/_pkg_.a
packagefile fmt=/tmp/go-build1624675521/b002/_pkg_.a
packagefile math/rand=/tmp/go-build1624675521/b044/_pkg_.a
...
EOF
```

- `command-line-arguments` 就是這次命令列直接編譯的主程式，也就是 `test.go`
- `importcfg.link` 比前面的 `importcfg` 更完整，會把 link 階段需要的所有 package 都列出來

7. linker 產生暫存執行檔

真正把可執行檔連出來的是：

```text
/home/shihyu/go/pkg/tool/linux_amd64/link -o $WORK/b001/exe/a.out -importcfg $WORK/b001/importcfg.link -buildmode=exe ... -extld=gcc $WORK/b001/_pkg_.a
```

- `link` 讀入主套件 `$WORK/b001/_pkg_.a`
- 再依照 `importcfg.link` 把 `fmt`、`time`、`runtime` 等 package 一起連結
- `-buildmode=exe` 表示輸出型態是一般 Linux 可執行檔
- `-extld=gcc` 表示需要外部 linker 時會交給 `gcc`

8. 把暫存執行檔複製成最終輸出

最後兩行最重要：

```text
/home/shihyu/go/pkg/tool/linux_amd64/buildid -w $WORK/b001/exe/a.out # internal
cp $WORK/b001/exe/a.out test
```

- `buildid -w` 會把 build id 寫回執行檔
- `cp ... test` 才是把暫存中的 `a.out` 複製成目前目錄下真正的輸出檔 `test`

### 一句話總結

這份 `build.log` 的流程就是：

`編標準庫/相依套件 -> 產生各自的 _pkg_.a -> 編 test.go 成 main package -> 生成 importcfg.link -> link 成 $WORK/b001/exe/a.out -> 複製成 ./test`

## 10. 只看編譯出來的 `test`，怎麼判斷有沒有用到 Linux system API

先分清楚兩件事：

- Linux kernel syscall
- 系統 C 函式庫，例如 `glibc`

這兩個不是同一件事。

### 1. 看執行時實際打了哪些 Linux syscall

最準的是：

```bash
strace -f ./test
```

會直接看到實際發生的 syscall，例如：

```text
write(1, ...)
futex(...)
clone(...)
mmap(...)
clock_nanosleep(...)
```

如果看到了這些，就代表程式執行時確實有呼叫 Linux kernel API。

### 2. 看有沒有依賴系統 C 函式庫

```bash
ldd ./test
readelf -d ./test | rg 'NEEDED|INTERP'
```

判讀方式：

- 有 `libc.so.6`、`libpthread.so.0` 之類，代表有動態依賴系統函式庫
- 如果像這次的 `test` 一樣是靜態連結，`ldd` 會顯示不是動態可執行檔

注意：

- 沒有動態依賴 `glibc`，不代表沒有 syscall
- Go 純靜態程式一樣可能直接對 Linux kernel 發 syscall

### 3. 看 binary 內可能會用到哪些 syscall 或 runtime 路徑

```bash
go tool nm ./test | rg 'syscall|runtime\.|futex|clone|write|epoll'
objdump -d ./test | rg '\bsyscall\b'
strings ./test | rg 'epoll|futex|clone|nanosleep|clock_gettime'
```

這些只能幫你判斷「可能會用到」，不能保證執行時一定走到。

### 4. 只看 `build.log` 能知道多少

`build.log` 比較適合看：

- 有沒有走 `cgo`
- 有沒有出現 `gcc` / `_cgo_*.go` / C 編譯步驟
- 最後是怎麼 link 成執行檔

但它不能準確告訴你執行時到底打了哪些 Linux syscall。

### 一句話總結

- 想看「執行時真的有沒有呼叫 Linux kernel API」：`strace -f ./test`
- 想看「有沒有依賴 glibc 之類系統函式庫」：`ldd ./test`、`readelf -d ./test`
- 想看「binary 內可能有哪些 syscall 痕跡」：`go tool nm`、`objdump`、`strings`

## 11. 這次 `test` 實際跑出來的 Linux syscall

直接執行：

```bash
strace -f ./test
```

這次實際看到的代表性輸出包含：

```text
execve("./test", ["./test"], ...) = 0
mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = ...
clone(child_stack=..., flags=CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD|...) = ...
futex(..., FUTEX_WAIT_PRIVATE, ...)
futex(..., FUTEX_WAKE_PRIVATE, ...)
write(1, "烏龜跑了 1 步...\n", 22) = 22
epoll_create1(EPOLL_CLOEXEC) = 3
epoll_ctl(3, EPOLL_CTL_ADD, 4, ...) = 0
epoll_pwait(3, [], 128, 4999, NULL, 0) = 0
nanosleep({tv_sec=0, tv_nsec=20000}, NULL) = 0
exit_group(0) = ?
```

### 這些 syscall 大致對應什麼

- `execve`：啟動 `./test`
- `mmap`：Go runtime 配置記憶體
- `clone`：建立 runtime thread
- `futex`：goroutine / thread 同步
- `write`：`fmt.Printf`、`fmt.Println` 輸出到 stdout
- `epoll_*`：Go runtime 的 netpoll / 事件等待機制
- `nanosleep`：`time.Sleep` 以及 runtime 內部等待
- `exit_group`：程式結束

### 這次案例的結論

- `test` 確實有呼叫 Linux kernel API
- 這些呼叫主要來自 Go runtime 與標準庫
- 即使 `test` 是靜態連結，也一樣會直接使用 Linux syscall

## 12. 交叉編譯 `x86` / `ARM` / `MIPS` / `PowerPC` 並用 qemu 驗證

先安裝 qemu user mode：

```bash
sudo apt-get update
sudo apt-get install -y qemu-user
```

### 編譯四種 Linux 架構執行檔

這裡用 `CGO_ENABLED=0` 產出靜態執行檔，避免還要準備對應架構的動態函式庫。

```bash
mkdir -p qemu-bin

CGO_ENABLED=0 GOOS=linux GOARCH=386 \
go build -o qemu-bin/test-linux-386 ./test.go

CGO_ENABLED=0 GOOS=linux GOARCH=arm GOARM=7 \
go build -o qemu-bin/test-linux-armv7 ./test.go

CGO_ENABLED=0 GOOS=linux GOARCH=mips GOMIPS=softfloat \
go build -o qemu-bin/test-linux-mips ./test.go

CGO_ENABLED=0 GOOS=linux GOARCH=ppc64 \
go build -o qemu-bin/test-linux-ppc64 ./test.go
```

### 確認產物架構

```bash
file qemu-bin/test-linux-386 qemu-bin/test-linux-armv7 qemu-bin/test-linux-mips qemu-bin/test-linux-ppc64
```

這次實際結果：

```text
qemu-bin/test-linux-386:   ELF 32-bit LSB executable, Intel 80386, ... statically linked
qemu-bin/test-linux-armv7: ELF 32-bit LSB executable, ARM, EABI5 ... statically linked
qemu-bin/test-linux-mips:  ELF 32-bit MSB executable, MIPS, MIPS32 ... statically linked
qemu-bin/test-linux-ppc64: ELF 64-bit MSB executable, 64-bit PowerPC ... statically linked
```

### 用 qemu 執行驗證

```bash
timeout 8s qemu-i386 ./qemu-bin/test-linux-386
timeout 8s qemu-arm  ./qemu-bin/test-linux-armv7
timeout 8s qemu-mips ./qemu-bin/test-linux-mips
timeout 8s qemu-ppc64 ./qemu-bin/test-linux-ppc64
```

如果能正常看到程式輸出，例如：

```text
烏龜跑了 1 步...
兔子睡著了zzzz
兔子跑了 2 步...
```

而且行程最後正常結束，就代表：

- binary 架構正確
- qemu 對應模擬器可正常載入該執行檔
- 該架構下的 Go runtime 可正常啟動與執行

### 這次驗證結果

- `qemu-i386 ./qemu-bin/test-linux-386`：可執行，exit code `0`
- `qemu-arm ./qemu-bin/test-linux-armv7`：可執行，exit code `0`
- `qemu-mips ./qemu-bin/test-linux-mips`：可執行，exit code `0`
- `qemu-ppc64 ./qemu-bin/test-linux-ppc64`：可執行，exit code `0`

### 補充

這支 `test.go` 的 `random()` 每次呼叫都重新 `Seed(time.Now().Unix())`，同一秒內可能一直拿到相同亂數，所以會看到大量重複的：

```text
兔子睡著了zzzz
```

這不影響 qemu 驗證結果，只是程式本身的亂數寫法會讓輸出非常多。
