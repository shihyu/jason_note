## Golang 單步除錯利器 — Delve

[Golang](https://golang.org/) 是一個靜態語言，雖然也有支援 GDB，但[官方也有說](https://golang.org/doc/gdb)，若單純使用內建的 toolchain，推薦使用 [Delve](https://github.com/derekparker/delve) 這個工具，因為 GDB 對於 Go 的 stack 管理、線程或執行時期的環境，並沒有支援的很完善，有時甚至會看到錯誤的狀態。

Delve 也是單步執行工具，和 GDB 很像，但是他更方便安裝，本身也是 go 的 package 之一，安裝方法如下：

Mac 要先安裝編譯用的 toolchain：

```
$ xcode-select --install
$ go get -u github.com/derekparker/delve/cmd/dlv
```

對於 Windows 和 Linux 系統，只需要執行 `go get`即可：

https://github.com/go-delve/delve/tree/master/Documentation/installation

```
$ go install github.com/go-delve/delve/cmd/dlv@v1.7.3
```

記得，所有平臺都要先將 `$GOPATH/bin` 加入系統環境 `PATH`變數，這樣才找得到執行檔。

## 除錯

首先，我們用下面的程式當作範例：

```go
package main

import (
    "fmt"
)

func demo(s string, x int) string {
    ret := fmt.Sprintf("This is a demo, your input is: %s %d", s, x)
    return ret
}

func main() {
    s := "string"
    i := 1111
    fmt.Println(demo(s, i))
}
```



存檔成為 `delve-demo.go`

接著，在 console 使用 `dlv debug <filename>`將 delve 跑起來：

```
$ dlv debug delve-demo.go --check-go-version=false
```

你會看到下面的訊息：

```
$ dlv debug delve-demo.go                                                                                                                                  system
Type 'help' for list of commands.
(dlv) 
```

但其實程式還沒真的跑起來，此時可以先設定中斷點，再來跑程式。

設定中斷點：
使用 `<package>.<function>`或是 `<filename>:<line number>`的格式：

```
# 方法 1
(dlv) break main.main
Breakpoint 1 set at 0x10b0958 for main.main() ./delve-demo.go:12# 方法 2
(dlv) break delve-demo.go:7
Breakpoint 2 set at 0x10b0758 for main.demo() ./delve-demo.go:7
```

接著使用 `c` 或是 `continue`讓程式跑起來，你就會看到 dlv 停在中斷點上：

```
(dlv) b main.main
Breakpoint 1 set at 0x10b0958 for main.main() ./delve-demo.go:12
(dlv) c
> main.main() ./delve-demo.go:12 (hits goroutine(1):1 total:1) (PC: 0x10b0958)
     7: func demo(s string, x int) string {
     8:  ret := fmt.Sprintf("This is a demo, your input is: %s %d", s, x)
     9:  return ret
    10: }
    11:
=>  12: func main() {
    13:  s := "string"
    14:  i := 1111
    15:  fmt.Println(demo(s, i))
    16: }
(dlv)
```

其他使用方式就和 GDB 雷同，下面把比較常用的指令列出來：

單部執行： `n` 或 `next`跳進去函式 (step in)： `s` 或 `step`跳出函式 (step out)： `stepout`看函式引數： `args`
例如：

```
(dlv) args
s = "string"
x = 1111
```

印出參數或表達式： `print <參數>`
例如：

```
(dlv) p x
1111
(dlv) p x+5
1116
(dlv) p x != 5
true
```

印出目前所有的 goroutine：

```
(dlv) goroutines
[4 goroutines]
* Goroutine 1 - User: ./delve-demo.go:9 main.demo (0x10b08e9) (thread 2350822)
  Goroutine 2 - User: /usr/local/Cellar/go/1.10.3/libexec/src/runtime/proc.go:292 runtime.gopark (0x102c209)
  Goroutine 3 - User: /usr/local/Cellar/go/1.10.3/libexec/src/runtime/proc.go:292 runtime.gopark (0x102c209)
  Goroutine 4 - User: /usr/local/Cellar/go/1.10.3/libexec/src/runtime/proc.go:292 runtime.gopark (0x102c209)
```

更多詳細的指令可以參考 [github 說明](https://github.com/derekparker/delve/blob/master/Documentation/cli/README.md)。

## testing 除錯

如果要在跑 go test 的時候除錯也很容易，要跑全部的 test case 只要執行

```
dlv test -- -test.v
# 如同
go test ./...
```

或是隻執行單個測資：

```
dlv test -- -test.run <test function>
# 如同
go test -run <test function>
```

Happy debugging！