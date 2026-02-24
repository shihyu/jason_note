# Go Modules 完整指南

本指南整合了 Go Modules 的基礎概念、實務操作與遷移策略，從 `go.mod` / `go.sum` 的基本原理，到從 GOPATH 遷移至 Modules 的完整流程，最後涵蓋進階用法與最佳實踐。

---

## 目錄

- [第一章：模組基礎](#第一章模組基礎)
  - [1.1 什麼是 Go Modules](#11-什麼是-go-modules)
  - [1.2 初始化模組](#12-初始化模組)
  - [1.3 安裝與使用 dependencies](#13-安裝與使用-dependencies)
  - [1.4 go.mod 檔案結構](#14-gomod-檔案結構)
  - [1.5 go.sum 檔案](#15-gosum-檔案)
  - [1.6 Go Modules 指令介紹](#16-go-modules-指令介紹)
- [第二章：GOPATH 到 Modules 的遷移](#第二章gopath-到-modules-的遷移)
  - [2.1 GOPATH 的問題](#21-gopath-的問題)
  - [2.2 Go Modules 初體驗](#22-go-modules-初體驗)
  - [2.3 使用 Go Modules 進行套件相依性管理](#23-使用-go-modules-進行套件相依性管理)
  - [2.4 既有專案遷移至 Go Modules](#24-既有專案遷移至-go-modules)
  - [2.5 CI 環境設定（Travis CI）](#25-ci-環境設定travis-ci)
- [第三章：進階用法與最佳實踐](#第三章進階用法與最佳實踐)
  - [3.1 replace 語法](#31-replace-語法)
  - [3.2 版本指定與 Pseudo-version](#32-版本指定與-pseudo-version)
  - [3.3 indirect 依賴說明](#33-indirect-依賴說明)
  - [3.4 Go Modules 與既有工具鏈的整合](#34-go-modules-與既有工具鏈的整合)
  - [3.5 參考資源](#35-參考資源)

---

## 概覽架構圖

### Go Modules 工作流程

```
                           Go Modules 整體工作流程
 ┌──────────────────────────────────────────────────────────────────────┐
 │                                                                      │
 │  ┌─────────────┐     ┌──────────────┐     ┌──────────────────────┐  │
 │  │  開發者     │     │  go mod init │     │  產生 go.mod         │  │
 │  │  (專案目錄) │────>│  初始化模組  │────>│  (模組名稱+Go版本)  │  │
 │  └─────────────┘     └──────────────┘     └──────────┬───────────┘  │
 │                                                       │              │
 │                                                       v              │
 │  ┌─────────────┐     ┌──────────────┐     ┌──────────────────────┐  │
 │  │ import pkg  │────>│  go get /    │────>│  下載依賴至          │  │
 │  │ 在程式碼中  │     │  go run /    │     │  $GOPATH/pkg/mod/    │  │
 │  │ 引用套件    │     │  go build    │     │  cache               │  │
 │  └─────────────┘     └──────────────┘     └──────────┬───────────┘  │
 │                                                       │              │
 │                                                       v              │
 │                       ┌──────────────┐     ┌──────────────────────┐  │
 │                       │  go.mod      │<───>│  go.sum              │  │
 │                       │  記錄直接    │     │  記錄所有依賴的      │  │
 │                       │  依賴及版本  │     │  hash 校驗值         │  │
 │                       └──────┬───────┘     └──────────────────────┘  │
 │                              │                                       │
 │                              v                                       │
 │                       ┌──────────────┐                               │
 │                       │  go mod tidy │                               │
 │                       │  清理未使用  │                               │
 │                       │  補齊遺漏    │                               │
 │                       └──────────────┘                               │
 └──────────────────────────────────────────────────────────────────────┘
```

### go.mod 與 go.sum 的關係

```
  go.mod (類似 package.json)          go.sum (類似 package-lock.json)
 ┌────────────────────────────┐      ┌────────────────────────────────┐
 │ module myproject           │      │ pkg-A v1.0.0 h1:abc123...     │
 │                            │      │ pkg-A v1.0.0/go.mod h1:def... │
 │ go 1.18                    │      │ pkg-B v2.1.0 h1:ghi456...     │
 │                            │      │ pkg-B v2.1.0/go.mod h1:jkl... │
 │ require (                  │─────>│ pkg-C v0.3.0 h1:mno789...     │
 │   pkg-A v1.0.0             │      │ ...                            │
 │   pkg-B v2.1.0             │      │ (包含所有直接+間接依賴的       │
 │   pkg-C v0.3.0 // indirect │      │  版本與 hash 校驗值)           │
 │ )                          │      └────────────────────────────────┘
 │                            │
 │ replace pkg-A => ../local  │  <── 可選：替換特定套件來源
 └────────────────────────────┘
```

### Go Modules 指令速查

```
 ┌────────────────────────────────────────────────────────────┐
 │                   go mod 指令一覽                           │
 ├──────────────┬─────────────────────────────────────────────┤
 │  init        │  建立 go.mod，初始化模組                    │
 │  tidy        │  增加遺失的依賴，移除未使用的依賴           │
 │  download    │  下載依賴至 $GOPATH/pkg/mod/cache           │
 │  verify      │  驗證本地依賴是否符合 go.sum                │
 │  graph       │  列出模組依賴圖                             │
 │  edit        │  編輯 go.mod（如鎖定版本、replace）         │
 │  vendor      │  將依賴複製到 /vendor 目錄                  │
 │  why         │  解釋某個依賴為何存在                        │
 ├──────────────┼─────────────────────────────────────────────┤
 │  go get      │  安裝/更新依賴（自動更新 go.mod）           │
 │  go run      │  編譯並執行（自動檢查新依賴）               │
 │  go build    │  編譯專案（自動檢查新依賴）                 │
 │  go test     │  執行測試（自動檢查新依賴）                 │
 └──────────────┴─────────────────────────────────────────────┘
```

---

## 第一章：模組基礎

本章介紹 Go Modules 的核心概念，包含 `go.mod` 與 `go.sum` 的作用，以及常用的模組管理指令。

### 1.1 什麼是 Go Modules

**避免重複造輪子** ，所以今天要介紹的就是怎麼使用 Go modules 引用外部的 library。

Go 1.11 之後提供 [go modules](https://blog.golang.org/using-go-modules) 讓我們可以不需要把專案程式碼放在 `$GOPATH/src` 中開發，此外還能管理套件相依性，相當便利。

### 1.2 初始化模組

這邊要使用 `go mod init <project-name>` 進行初始化（類似 `npm init`），完成後會多一個檔案 `go.mod`（就像 Nodejs 中的 `package.json`），因為現在都還沒安裝任何依賴所以 `go.mod` 裡面只有一行 `module go-phishing`



```bash
 go mod init go-phishing
```

### 1.3 安裝與使用 dependencies

```go
go get github.com/sirupsen/logrus
```go

```go
package main

import (
  "github.com/sirupsen/logrus"
)

func main() {
  logrus.SetLevel(logrus.TraceLevel)

  logrus.Trace("trace msg")
  logrus.Debug("debug msg")
  logrus.Info("info msg")
  logrus.Warn("warn msg")
  logrus.Error("error msg")
  logrus.Fatal("fatal msg")
  logrus.Panic("panic msg")
}
```

```bash
go run main.go
```

### 1.4 go.mod 檔案結構

編譯完再看一下 `go.mod` 裡面就有 `logrus` 了，跟 Nodejs 的 `package.json` 長得很像

```text
module go-phishing

go 1.18

require (
	github.com/sirupsen/logrus v1.8.1 // indirect
	golang.org/x/sys v0.0.0-20191026070338-33540a1f6037 // indirect
)
```

`go.mod` 用來紀錄 Go module 的名稱與所使用的 Go 版本，以及相依的 Go modules, 該檔案是 Go module 必備的檔案。

### 1.5 go.sum 檔案

編譯完之後除了 `go.mod` 之外還會多出一個檔案 `go.sum`，因為 `logrus` 也會用到某些 package，裡面記錄的是所有用到的 package 版本，類似 Nodejs 的 `package-lock.json`，如果你有在使用 git 之類的版本控制系統，記得要在 commit 時把它加進去

```sh
github.com/davecgh/go-spew v1.1.1/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
github.com/pmezard/go-difflib v1.0.0/go.mod h1:iKH77koFhYxTK1pcRnkKkqfTogsbg7gZNVY4sRDYZ/4=
github.com/sirupsen/logrus v1.8.1 h1:dJKuHgqk1NNQlqoA6BTlM1Wf9DOH3NBjQyu0h9+AZZE=
github.com/sirupsen/logrus v1.8.1/go.mod h1:yWOB1SBYBC5VeMP7gHvWumXLIWorT60ONWic61uBYv0=
github.com/stretchr/testify v1.2.2/go.mod h1:a8OnRcib4nhh0OaRAV+Yts87kKdq0PP7pXfy6kDkUVs=
golang.org/x/sys v0.0.0-20191026070338-33540a1f6037 h1:YyJpGZS1sBuBCzLAR1VEpK193GlqGZbnPFnPV/5Rsb4=
golang.org/x/sys v0.0.0-20191026070338-33540a1f6037/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
```

### 1.6 Go Modules 指令介紹

```
Usage:go mod <command> [arguments]The commands are:download    // 將依賴全部下載到本機中，位置為 $GOPATH/pkg/mod/cache
edit        // 編輯 go.mod 例如鎖定某個依賴的版本
graph       // 列出專案中哪一個部分使用了某個依賴
init        // 建立 go.mod
tidy        // 增加遺失的依賴，移除未使用的依賴
vendor      // 將既有的 go.mod 依賴全部存在 /vendor 底下
verify      // 驗證本地依賴依然符合 go.sum
why         // 解釋某個依賴為何存在在 go.mod 中，誰使用了它
```

---

## 第二章：GOPATH 到 Modules 的遷移

了解了模組的基礎概念之後，本章將深入介紹如何從傳統的 GOPATH 模式遷移至 Go Modules，並透過完整的實作範例來示範整個流程。

### 2.1 GOPATH 的問題

先前 [Golang - 從 Hello World 認識 GOPATH](https://myapollo.com.tw/zh-tw/golang-hello-world-gopath/) 一文中，我們認識了 GOPATH 的作用，然而 GOPATH 會讓我們的專案程式碼與其他相依的程式碼一起存在 `$GOPATH/src` 資料夾底下，相較於其他程式語言而言，使用上較不直覺，也欠缺相依性管理的功能。

以下對比圖清楚呈現兩種模式的差異：

```
GOPATH 模式 vs Go Modules 模式

┌─ GOPATH 模式 ──────────────────┐    ┌─ Go Modules 模式 ──────────────┐
│                                │    │                                │
│  $GOPATH/                      │    │  任意目錄/                      │
│  └── src/                      │    │  └── myproject/                │
│      ├── myproject/   (你的專案)│    │      ├── go.mod   (依賴管理)   │
│      ├── github.com/  (別人的包)│    │      ├── go.sum   (版本鎖定)   │
│      │   └── fatih/            │    │      ├── main.go              │
│      │       └── color/        │    │      └── greeting/            │
│      └── golang.org/           │    │                                │
│          └── x/                │    │  $GOPATH/pkg/mod/  (快取,自動)  │
│              └── sys/          │    │  └── github.com/fatih/color/  │
│                                │    │                                │
│  ❌ 專案必須放在 $GOPATH/src   │    │  ✅ 專案可放任意目錄            │
│  ❌ 無版本管理                 │    │  ✅ 自動版本管理                │
│  ❌ 所有程式碼混在一起          │    │  ✅ 依賴隔離快取                │
└────────────────────────────────┘    └────────────────────────────────┘
```

### 2.2 Go Modules 初體驗

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
```go

最後將 `greeting.go` 與 `say.go` 填入以下程式碼。 `greeting.go` 是 1 個簡單的 package, 用以列印所傳入的字串；而 `say.go` 則是用以呼叫 `greeting.go` package 所提供的函示。

`greeting.go` 的內容：

```go
package greeting

import "fmt"

func Say(s string) {
    fmt.Println(s)
}
```go

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

### 2.3 使用 Go Modules 進行套件相依性管理

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

```text
module github.com/username/myproject

go 1.13

require (
    github.com/fatih/color v1.8.0
    github.com/mattn/go-colorable v0.1.4 // indirect
    github.com/mattn/go-isatty v0.0.11 // indirect
)
```go

`//indirect` 指的是被相依的套件所使用的 packages:

> The indirect comment indicates a dependency is not used directly by this module, only indirectly by other module dependencies.

另一種常見情況是我們可能會指定 package 到某個 commit id, 這時候就能夠使用 [pseudo-version](https://golang.org/cmd/go/#hdr-Pseudo_versions) ，例如 `v0.0.0-20170915032832-14c0d48ead0c` 就是 1 個指定使用 `20170915032832-14c0d48ead0c` commit 的 pseudo-version.

> [pseudo-version](https://golang.org/cmd/go/#hdr-Pseudo_versions) , which is the go command's version syntax for a specific untagged commit.

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
```go

`say.go` 的內容：

```go
package main

import "github.com/username/myproject/greeting"

func main() {
    greeting.Say("Hello")
    greeting.SayWithColor("World")
}
```

### 2.4 既有專案遷移至 Go Modules

如何在一個新的專案使用 Go Modules？以下以 OSX 為例

```
// 先確認 Go 的版本已經在 1.11 以上
$ brew upgrade go$ mkdir gomod-test // 請確定當前位置在 $GOPATH 以外的地方
$ cd gomod-test
```

其實不一定要在 `$GOPATH` 以外的地方，只是當前 Go Modules 還在實驗階段，如果是在 `$GOPATH` 的專案，預設依然會照舊有的 vendor 機制，除非將環境變數 `GO111MODULE` 該為 `on` 來強制開啟，但既然 Go Modules 一個重要的性質是去除 `$GOPATH` ，就讓我們試試看在其他地方開專案吧！

接著初始化 Go Modules

```
$ go mod init github.com/hieven/gomod-test
```

便會看到專案底下出現 `go.mod` 的檔案，而這也是最重要的檔案，之後會紀錄每一個 dependency 以及版本。現在應該長得像這樣

```
// go.mod
module github.com/hieven/gomod-test
```

最後讓我們做一個簡單的 hello world

```
// main.go
package mainimport "fmt"func main() {
  fmt.Println("hello world")
}
```

此時還沒有任何改變，但接著我們嘗試加入一個 dependency

```go
package mainimport "fmt"
import "github.com/gofrs/uuid"func main() {
  uuid, _ := uuid.NewV4()

  fmt.Println("hello world", uuid)
}
```

接著運行程式 `$ go run main.go` 會發現程式神奇的運作了

```
$ hello world 3f99abff-8404-42ec-b9f6-5fa165e5d447
```

再來檢查 `go.mod` ，會發現已經多了一個 dependency

```
module github.com/hieven/gomod-testrequire (
  github.com/gofrs/uuid v3.1.0+incompatible
)
```

原因是 Go Modules 不僅僅是一個 `go mod xxx` 的工具而已，同時也整合了既有的 `go get`、`go run`、`go build`、`go test` ，每當這些指令運行時，都會去檢查整個 project 底下新的 dependency 並自動更新到 `go.mod` 底下

#### 從既有的套件管理工具遷移

剛好在既有的 project 中分別有用 glide 以及 govendor，所以剛好都試過這兩個的遷移方法，其實非常簡單。只要到 project 底下執行

```
$ go mod init
```

便自動會去讀 `glide.yaml` 或是 `vendor/vendor.json` 並產生一個 `go.mod` 。個人目前還沒有遇到問題

如果有興趣的人可以參考我在 [go-instagram](https://github.com/hieven/go-instagram/pull/22) 中的一個 PR，便是把 glide 轉移成 Go Modules

此外，可以試試看執行

```
$ go mod tidy
```

來移除沒使用的依賴，我自己的私人專案在使用 tidy 之後，成功移除了好幾個呢！

### 2.5 CI 環境設定（Travis CI）

基本上現在的 Travis 也有支援 Go 1.11 了，所以 Go Modules 自然而然就有了。

唯一要特別注意的是， Travis 底下預設把 project 放在 `$GOPATH` 底下，所以要在 env 中把 Go Modules 打開才行

具體設定就是要注意這兩行

```
// .travis.ymlgo:
  - "1.11"env:
  - GO111MODULE=on
```

---

## 第三章：進階用法與最佳實踐

掌握了基礎與遷移流程後，本章將前面兩章中提到的進階主題加以整理，並深入探討 `replace` 語法、版本策略、`indirect` 依賴，以及 Go Modules 與工具鏈的整合方式。

### 3.1 replace 語法

`go.mod` 還提供 `replace` 語法，能夠讓我們取代指定的套件，例如 `replace github.com/fatih/color => ../mycolor` 代表至 `../mycolor` 資料夾中載入 `github.com/fatih/color` package, 例如以下的 `go.mod` :

```text
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

### 3.2 版本指定與 Pseudo-version

Go modules 使用的版本號規則是 [semantic version](https://semver.org/)。當需要指定特定版本時，可以在 package 尾端加上 `@版本號`：

```
$ go get github.com/fatih/color@v1.8.0
```

另一種常見情況是我們可能會指定 package 到某個 commit id, 這時候就能夠使用 [pseudo-version](https://golang.org/cmd/go/#hdr-Pseudo_versions) ，例如 `v0.0.0-20170915032832-14c0d48ead0c` 就是 1 個指定使用 `20170915032832-14c0d48ead0c` commit 的 pseudo-version.

> [pseudo-version](https://golang.org/cmd/go/#hdr-Pseudo_versions) , which is the go command's version syntax for a specific untagged commit.

### 3.3 indirect 依賴說明

`//indirect` 指的是被相依的套件所使用的 packages:

> The indirect comment indicates a dependency is not used directly by this module, only indirectly by other module dependencies.

例如安裝 `github.com/fatih/color` 時，`go.mod` 會出現：

```text
require (
    github.com/fatih/color v1.8.0
    github.com/mattn/go-colorable v0.1.4 // indirect
    github.com/mattn/go-isatty v0.0.11 // indirect
)
```

其中 `go-colorable` 和 `go-isatty` 並非你的程式直接使用，而是 `color` 套件的依賴，因此標記為 `indirect`。

### 3.4 Go Modules 與既有工具鏈的整合

Go Modules 不僅僅是一個 `go mod xxx` 的工具而已，同時也整合了既有的 `go get`、`go run`、`go build`、`go test` ，每當這些指令運行時，都會去檢查整個 project 底下新的 dependency 並自動更新到 `go.mod` 底下。

```
┌───────────────────────────────────────────────────┐
│              Go 工具鏈整合 Modules                 │
│                                                   │
│  go get ──┐                                       │
│  go run ──┤                                       │
│  go build ┼──> 自動檢查依賴 ──> 更新 go.mod/go.sum │
│  go test ─┤                                       │
│  go mod ──┘                                       │
│                                                   │
│  GO111MODULE 環境變數:                             │
│    on  = 強制使用 modules (不論目錄位置)            │
│    off = 強制使用 GOPATH                           │
│    auto = 依據目錄位置自動判斷 (預設)               │
└───────────────────────────────────────────────────┘
```

### 3.5 參考資源

- [Using Go Modules (官方部落格)](https://blog.golang.org/using-go-modules)
- [Go Modules Reference (官方文件)](https://golang.org/ref/mod)
- [Semantic Versioning](https://semver.org/)
- [Pseudo-versions 說明](https://golang.org/cmd/go/#hdr-Pseudo_versions)
- [Golang - 從 Hello World 認識 GOPATH](https://myapollo.com.tw/zh-tw/golang-hello-world-gopath/)
- [從一知半解到略懂 Go modules](https://myapollo.com.tw/zh-tw/golang-go-module-tutorial/)

---

### 結語

以上就是關於 go modules 的一些解說與用法，還有很多細節可以詳閱官方文件，相信大家閱讀之後都可以有不少收獲！

Happy coding!
