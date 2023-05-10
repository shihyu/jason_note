# Go modules

**避免重複造輪子** ，所以今天要介紹的就是怎麼使用 Go modules 引用外部的 library

### 初始化

這邊要使用 `go mod init <project-name>` 進行初始化（類似 `npm init`），完成後會多一個檔案 `go.mod`（就像 Nodejs 中的 `package.json`），因為現在都還沒安裝任何依賴所以 `go.mod` 裡面只有一行 `module go-phishing`



```go
 go mod init go-phishing
```

### 安裝、使用 dependencies

```go
go get github.com/sirupsen/logrus
```

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

```go
go run main.go
```

編譯完再看一下 `go.mod` 裡面就有 `logrus` 了，跟 Nodejs 的 `package.json` 長得很像

```go
module go-phishing

go 1.18

require (
	github.com/sirupsen/logrus v1.8.1 // indirect
	golang.org/x/sys v0.0.0-20191026070338-33540a1f6037 // indirect
)
```

## `go.sum`

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

## Go Modules 指令介紹

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

## 如何在一個新的專案使用 Go Modules？

以下以 OSX 為例

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

```
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

## 既有的專案如何遷移至 Go Modules？

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

## 如何讓 Travis 能使用 Go Modules？

基本上現在的 Travis 也有支援 Go 1.11 了，所以 Go Modules 自然而然就有了。

唯一要特別注意的是， Travis 底下預設把 project 放在 `$GOPATH` 底下，所以要在 env 中把 Go Modules 打開才行

具體設定就是要注意這兩行

```
// .travis.ymlgo:
  - "1.11"env:
  - GO111MODULE=on
```
