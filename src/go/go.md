# GO

- [使用Golang 打造Web 應用程式](https://willh.gitbook.io/build-web-application-with-golang-zhtw/)
- [Golang - 100天從新手到大師](https://github.com/rubyhan1314/Golang-100-Days)
- [Go by Example](https://gobyexample-cn.github.io/)
- [xgotop](https://github.com/ozansz/xgotop)
- [入吾 Go 中：走訪 Go 語言內部實作](https://shihyu.github.io/inside-go/)
- [跟煎魚學 Go](https://shihyu.github.io/fish-go)
- [30 篇文帶你用 eBPF 與 Golang 打造 Linux Scheduler](https://shihyu.github.io/ebpf-golang-scheduler)
- [應該是 Profilling 吧？](https://shihyu.github.io/profiling)
- [iT 邦幫忙鐵人賽 60 天整理](https://shihyu.github.io/golang-docker-and-profiling-notes)
- [Go 併發編程實戰課](https://shihyu.github.io/go-concurrency-in-action)
- [深入 Go 語言之旅](https://shihyu.github.io/dive-into-go)
- [語言技術：Go 語言](https://shihyu.github.io/go-gossip)




## Go 標準套件安裝

http://golang.org/dl/

```sh
export GOROOT=$HOME/go
export GOPATH=$HOME/gopath
export PATH=$PATH:$GOROOT/bin:$GOPATH/bin
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
