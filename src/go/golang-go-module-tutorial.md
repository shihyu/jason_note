## 從一知半解到略懂 Go modules

一直以來沒有好好去詳讀 go modules 的文件，所以都覺得對 go modules 只是一知半解。這次花了些時間看了關於 go modules 的相關文件，並實際寫個小範例體驗，最後整理成本文分享。



### 本文環境

- macOS 10.15
- Go 1.13

### 引言

先前 [Golang - 從 Hello World 認識 GOPATH](https://myapollo.com.tw/zh-tw/golang-hello-world-gopath/) 一文中，我們認識了 GOPATH 的作用，然而 GOPATH 會讓我們的專案程式碼與其他相依的程式碼一起存在 `$GOPATH/src` 資料夾底下，相較於其他程式語言而言，使用上較不直覺，也欠缺相依性管理的功能。

Go 1.11 之後提供 [go modules](https://blog.golang.org/using-go-modules) 讓我們可以不需要把專案程式碼放在 `$GOPATH/src` 中開發，此外還能管理套件相依性，相當便利。

### Go modules 初體驗

首先設置好 GOPATH 之後，先在 `$GOPATH/src` 之外，新增 1 個資料夾存放專案程式：

```
$ export GOPATH=/path/to/goworkspace
$ mkdir myproject
$ cd myproject
```

接著用以下指令新增 Go module:

```
$ go mod init github.com/username/myproject
```

p.s. `github.com/username/myproject` 可以換成任意字串，因為個人希望將 Go module 放置於 GitHub, 因此將模組名稱設定為 `github.com/username/myproject`

上述指令成功後，將會看到資料夾內出現 1 個檔案 `go.mod` :

```
module github.com/username/myproject

go 1.13
```

`go.mod` 用來紀錄 Go module 的名稱與所使用的 Go 版本，以及相依的 Go modules, 該檔案是 Go module 必備的檔案

再來新增 2 個資料夾，以及 2 個 `.go` 檔，建立範例所需要的環境：

```
$ mkdir greeting cli
$ touch greeting/greeting.go cli/say.go
```

進行至此， `myproject` 的資料夾結構應如下所示：

```
.
├── cli
│   └── say.go
├── go.mod
└── greeting
    └── greeting.go
```

最後將 `greeting.go` 與 `say.go` 填入以下程式碼。 `greeting.go` 是 1 個簡單的 package, 用以列印所傳入的字串；而 `say.go` 則是用以呼叫 `greeting.go` package 所提供的函示。

`greeting.go` 的內容：

```go
package greeting

import "fmt"

func Say(s string) {
    fmt.Println(s)
}
```

`say.go` 的內容：

```go
package main

import "github.com/username/myproject/greeting"

func main() {
    greeting.Say("Hello")
}
```

最後，試著編譯一次，正常的話不會有任何錯誤訊息：

```
$ go build ./...
```

至此，我們已經利用 go modules 成功地將 Go 專案移出 `$GOPATH/src` 囉！

p.s. 如果把 `go.mod` 刪除的話，就會發現類似以下的錯誤，這是由於 go 找不到 `go.mod` 因此轉而至 `$GOPATH` 尋找相關的 go package 的緣故：

```
cli/say.go:3:8: cannot find package "github.com/username/myproject/greeting" in any of:
    /usr/local/go/src/github.com/username/myproject/greeting (from $GOROOT)
    $GOPATH/src/github.com/username/myproject/greeting (from $GOPATH)
```

### 使用 go modules 進行套件相依性管理

Go modules 提供的另一個方便的功能則是套件相依性管理，接下來實際透過以下指令安裝套件試試：

```
$ go get github.com/fatih/color
```

安裝成功之後，可以再看一次 `go.mod` ，會發現多了 1 行 `require github.com/fatih/color v1.9.0` :

```
module github.com/username/myproject

go 1.13

require github.com/fatih/color v1.9.0
```

`require github.com/fatih/color v1.9.0` 目前的 Go 專案需要 v1.9.0 版的 `github.com/fatih/color` 。

p.s. go modules 使用的版本號規則是[semantic version](https://semver.org/) , 有興趣的話，可以詳閱該文件

有時候我們可能會需要使用指定版本的 package, 這時候可以在 package 尾端加上 `@版本號` ，例如以下指定使用 v1.8.0 的 `github.com/fatih/color` ：

```
$ go get github.com/fatih/color@v1.8.0
```

安裝完成後，再看一次 `go.mod` 會發現除了 `github.com/fatih/color` 版本變為 v1.8.0 之外，又多了 2 個 `//indirect` 的 go packages:

```go
module github.com/username/myproject

go 1.13

require (
    github.com/fatih/color v1.8.0
    github.com/mattn/go-colorable v0.1.4 // indirect
    github.com/mattn/go-isatty v0.0.11 // indirect
)
```

`//indirect` 指的是被相依的套件所使用的 packages:

> The indirect comment indicates a dependency is not used directly by this module, only indirectly by other module dependencies.

另一種常見情況是我們可能會指定 package 到某個 commit id, 這時候就能夠使用 [pseudo-version](https://golang.org/cmd/go/#hdr-Pseudo_versions) ，例如 `v0.0.0-20170915032832-14c0d48ead0c` 就是 1 個指定使用 `20170915032832-14c0d48ead0c` commit 的 pseudo-version.

> [pseudo-version](https://golang.org/cmd/go/#hdr-Pseudo_versions) , which is the go command’s version syntax for a specific untagged commit.

接著，可以再把 `greeting.go` 與 `say.go` 改為以下形式，使用剛剛所安裝的 package 。

`greeting.go` 的內容:

```go
package greeting

import "fmt"

import "github.com/fatih/color"

func Say(s string) {
    fmt.Println(s)
}

func SayWithColor(s string) {
    color.Red(s)
}
```

`say.go` 的內容：

```go
package main

import "github.com/username/myproject/greeting"

func main() {
    greeting.Say("Hello")
    greeting.SayWithColor("World")
}
```

### `go.mod` 的 replace 語法

`go.mod` 還提供 `replace` 語法，能夠讓我們取代指定的套件，例如 `replace github.com/fatih/color => ../mycolor` 代表至 `../mycolor` 資料夾中載入 `github.com/fatih/color` package, 例如以下的 `go.mod` :

```go
module github.com/username/myproject

go 1.13

require (
    github.com/fatih/color v1.8.0
    github.com/mattn/go-colorable v0.1.4 // indirect
    github.com/mattn/go-isatty v0.0.11 // indirect
)

replace github.com/fatih/color => ../mycolor
```

除了直接編輯 `go.mod` 之外，也可以用以下指令：

```
$ go mod edit -replace github.com/fatih/color=../mycolor
```

`replace` 能夠讓我們輕易地將特定 package 重新定位到特定路徑下，除了能夠方便修改之外，也能夠讓我們更輕鬆地測試 package 不同版本的行為等等，值得注意的是特定路徑下的 package 也必須有 `go.mod` 檔才行

`../mycolor` 是代表在 `go.mod` 檔案的所在目錄的上一層，所以可以先切換至上一層目錄後，再次下載 `https://github.com/fatih/color` 試試：

```
$ cd ../
$ git clone https://github.com/fatih/color mycolor
```

此時的資料夾結構應該會類似以下：

```
.
├── mycolor
│   ├── LICENSE.md
│   ├── README.md
│   ├── color.go
│   ├── color_test.go
│   ├── doc.go
│   ├── go.mod
│   ├── go.sum
│   └── vendor
├── myproject
│   ├── cli
│   ├── go.mod
│   ├── go.sum
│   └── greeting
└── pkg
```

接著回到 `myproject` 試著編譯看看，正常的話就不會出現任何訊息：

```
$ cd myproject
$ go build ./...
```

如此代表成功體驗 replace 的功用了！

### 結語

以上就是關於 go modules 的一些解說與用法，還有很多細節可以詳閱官方文件，相信大家閱讀之後都可以有不少收獲！

Happy coding!

### References

https://blog.golang.org/using-go-modules

https://golang.org/ref/mod

### 出處

https://myapollo.com.tw/zh-tw/golang-go-module-tutorial/