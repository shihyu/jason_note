
# init
在初始化創建一個項目的時候
```go  
go mod init
```

這時候會創建一個go.mod文件，其內容如下。
```go 
module module

go 1.14
```
這時再執行go build 等命令就會下載依賴包，並把依賴信息添加到 go.mod 文件中，同時把依賴版本哈希信息存到 go.sum 文件中
例如當我們在main.go使用了pflag之後，
```go  
go build .
go: finding module for package github.com/spf13/pflag
go: found github.com/spf13/pflag in github.com/spf13/pflag v1.0.5
```

# tidy
當工程運行過一段時間以後，難免會導致go.mod中存在一些已經不用了的依賴。這時候可以通過tidy來清除
```go  
go mod tidy
```
