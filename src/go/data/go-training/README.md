# go-training
目前市面上各種golang的學習資料實在不少，不過學習過一段時間以後發現有兩個問題。一是每一個文章、站點都是介紹一個方面，缺乏一個整體上的視角。二是學習完了之後不練習的話，基本一週後就忘的差不多了。

所以我把我個人的學習、練習過程以此項目整理發佈了出來。
- 用樹形的方式進行儘量合理地組織，便於整體上把握
- 每一個知識點儘量配置go源代碼，便於動手練習

該項目目前只更新了基礎部分，日後會繼續更新和完善。

![avatar](imgs/golang-small.png)

# 開發環境
- 安裝
- 配置GOROOT、GOPATH
- GoLand使用以及其快捷鍵

# Golang知識樹
- 語言基礎：
    - [關鍵字與預定義標識符](1-basic/keyword/index.md)  
    - [常量的聲明與賦值](1-basic/const/index.md) &nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/const/main.go)
    - [變量的聲明、初始化、生命期](1-basic/variable/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/variable/main.go)
    - [流程控制：if/else、for、switch](1-basic/flow/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/flow/main.go)  
 
- 數據類型
    - [數據類型之整形、布爾、字符串](1-basic/int-bool-string/index.md)
    - [字符串: 使用、內存佈局、深拷貝](1-basic/string/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code]((1-basic/string/main.go)) 
    - [byte數組到字符串、byte數組的零拷貝](1-basic/zerocopy/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code]((1-basic/zerocopy/main.go))
    - [數據類型之數組、切片](1-basic/array/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/array/main.go)
    - [切片內存佈局以及unsafe.Slice之零拷貝創建方式](1-basic/slice/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/slice/main.go)
    - [數據類型之Map](1-basic/map/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/map/main.go)
    - [數據類型之結構體](1-basic/struct/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/struct/main.go)
    - [數據類型之接口](1-basic/interface/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/interface/main.go)
    - [類型轉換](1-basic/convert/index.md) &nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/convert/main.go)
    - [父子struct強制類型轉換](1-basic/forceconvert/index.md) &nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/forceconvert/main.go)
    - [類型斷言](1-basic/assert/index.md) &nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/assert/main.go)
    - [反射](1-basic/reflect/index.md) &nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/reflect/main.go)
- 指針
  - [指針數據類型](1-basic/pointer/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code]((1-basic/pointer/main.go))

- 代碼組織 
    - [函數、匿名函數、閉包](1-basic/function/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/function/main.go)
    - [方法](1-basic/method/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/method/main.go)
    - [包](1-basic/package/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/package/main.go)  
    - [defer、panic和recover](1-basic/defer/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/defer/main.go) 
    - [go module](1-basic/module/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/module/main.go)  

- 文本處理
    - [go template使用](1-basic/template/index.md) &nbsp;&nbsp;&nbsp;&nbsp;[->code](1-basic/template/main.go)

- 併發操作
    - [goroutine](2-concurrecy/goroutine/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](2-concurrecy/goroutine/main.go)
    - [channel](2-concurrecy/channel/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code（無緩存）](2-concurrecy/channel/buffer/main.go)&nbsp;&nbsp;[->code（帶緩存）](2-concurrecy/channel/buffer/main.go)&nbsp;&nbsp;[->code（遍歷）](2-concurrecy/channel/buffer/main.go)
    - [select](2-concurrecy/select/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](2-concurrecy/select/main.go);
    - [sync](2-concurrecy/sync/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code(waitgroup)](2-concurrecy/sync/waitgroup/main.go)&nbsp;&nbsp;[->code(mutex)](2-concurrecy/sync/mutex/main.go)&nbsp;&nbsp;[->code(rwmutex)](2-concurrecy/sync/rwmutex/main.go);
    - context
        - [context源碼淺析](2-concurrecy/context/mycontext/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](2-concurrecy/context/mycontext/main.go)
        - [timeout簡單demo](2-concurrecy/context/timeout/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](2-concurrecy/context/timeout/main.go) 
        - [value簡單demo](2-concurrecy/context/value/index.md)&nbsp;&nbsp;&nbsp;&nbsp;[->code](2-concurrecy/context/value/main.go) 
- 網絡操作
    - [官方net包](3-network/net/index.md) 網絡庫，支持 Socket、HTTP、郵件、RPC、SMTP 等  [->code](3-network/net/server/main.go)
    - [gnet包](3-network/gnet/index.md)
    - [evio]()
    - [netpoll]()
- 編碼解碼
    - encoding: 常見算法如 JSON、XML、Base64 等
    - json 
        - [encoding/json](4-codec/json/json/index.md)   [->code](4-codec/json/json/main.go)
        - json-iterator
        - tidwall/gjson  
        - easyjson
    - protobuf 
- cgo
  - [入門實例]
    - [最簡單的例子](6-cgo/examples/e01/main.go)
    - [使用golang實現cgo函數並調用](6-cgo/examples/e02/main.go)
  - [跨語言數據類型轉換]
    - [golang訪問C語言中定義的struct、union、enum](6-cgo/examples/e03/main.go)
    - [golang訪問C語言中定義的數組、字符串](6-cgo/examples/e04/main.go)
  - [跨語言函數調用]
    - [golang調用C語言中定義的函數demo](6-cgo/examples/e05/main.go)
    - [golang調用C語言函數性能測試](6-cgo/examples/e06/index.md)
    - [go調用C語言函數內部原理](6-cgo/examples/e07/index.md)
    - [C語言調用go函數內部原理](6-cgo/examples/e08/index.md)
    - [Go跨語言調用核心技術](6-cgo/examples/e09/index.md)
- 性能分析
  - [USDT](5-performance/usdt/index.md)
- 單元測試
  - [基礎單元測試](3-unittest/basic/main_test.go)
  - [testify單元測試](3-unittest/testify/main_test.go)
  - [gomonkey單元測試](3-unittest/gomonkey/main_test.go)
- 標準庫用法
    - bytes: 字節操作
    - context
    - database: 數據庫驅動和接口,包括mysql
    - flag：命令行解析
    - fmt: 格式化操作
    - io：實現 I/O 原始訪問接口及訪問封裝
    - mysql: mysql數據庫操作
    - math: 數學庫
    - os: 操作系統平臺不依賴平臺操作封裝
    - sort: 排序接口
    - strings: 字符串轉換、解析及實用函數
    - time: 時間接口
- golang工具鏈
    - go get命令: 一鍵獲取代碼、編譯並安裝
    - go install命令: 編譯並安裝
    - go module: 依賴管理
    - go fmt命令: 格式化代碼文件
    - go imports: 
    - go build: 編譯
    - go run: 編譯並運行
    - go test: 單元測試
    - go pprof命令: 性能分析
    - 數據競爭
    - 代碼覆蓋率
    
# Golang進階
- 編譯原理
    - [golang之編譯原理]
    - [數組編譯過程理解]
    - [為什麼數組常量下標編譯時報錯，而變量下標運行時panic]
    - [對切片append超過其容量時會發生什麼]
    - [瞭解字符串拼接、轉換的開銷]
    - [golang函數調用和c函數開銷對比]
    - [為什麼make能同時支持map、slice和chan]
    - [for range循環解惑]
    - [GPM之阻塞的系統調用實勘]
    - [Golang協程上的網絡IO]
- 主流第三方庫用法
    - gorm
    - cobra
    - redigo
    - go-cache
    - viper
    - gRPC   
    - 日誌庫 
- 併發
    - goroutine
    - channel
    - select
    - sync包：WaitGroup、互斥鎖、讀寫互斥鎖、Once、併發安全Map           
- 工程化與部署
    - 編碼規範
    - 熱升級   
    - 項目佈局
    - Make file
    - Docker file 
    - 優雅地調試容器
    - CI && CD
# 一個web項目框架

# 經典問題集錦

|--|--|
|--|--|

# 參考學習資料
- [https://golang.org/doc/code.html](https://golang.org/doc/code.html) 
- [https://golang.org/doc/effective_go.html](https://golang.org/doc/effective_go.html) 
- [http://c.biancheng.net/golang/intro/](http://c.biancheng.net/golang/intro/)
- [awesome-go項目中文版](https://github.com/yinggaozhen/awesome-go-cn)  精選了一系列很棒的Go框架、庫和軟件。靈感來自於awesome-python
- [Uber 內部在 github 開源的 的 Go 編程規範](https://github.com/uber-go/guide)
- [Dave Cheney 寫的 《Go語言最佳實戰》 ](https://dave.cheney.net/practical-go/presentations/qcon-china.html)
- [Go語言設計與實現(電子書)](https://draveness.me/golang/)  側重於內部實現分析
- [begoo官方文檔](https://beego.me/)
- [如何優雅地寫出Go代碼](https://draveness.me/golang-101/)


# 硬廣個人技術公眾號
![avatar](imgs/wechat.png)