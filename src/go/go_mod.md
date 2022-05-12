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

