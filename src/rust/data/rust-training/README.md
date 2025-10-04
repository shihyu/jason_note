
## 語言基礎
### 開發環境
- [安裝](1-basic/install/index.md)
- [使用cargo創建項目](1-basic/cargo/index.md)

### 內存管理
- 變量
  - [變量可變性與隱藏](2-memory/variable/index.md)
  - [整型、浮點、字符串](2-memory/variable/scalar.md)
  - [數組、元組](2-memory/variable/compound.md)
  - [結構體](2-memory/struct/index.md)
- 所有權與生命週期
  - [所有權移動、借用、部分借用](2-memory/ownership/index.md)
  - [克隆](2-memory/ownership/clone.md)
  - [借用檢查器](2-memory/ownership/borrowchecker.md)
  - [函數參數生命週期標註](2-memory/ownership/func-lifetime.md)
  - [結構體生命週期標註](2-memory/ownership/struct-lifetime.md)
- 集合數據結構(都存儲在堆上)
  - [vector](2-memory/collection/vector.md)
  - [string](2-memory/collection/string.md)
  - [哈希表](2-memory/collection/hashmap.md)
- 智能指針
  -  [指向堆上的數據](2-memory/smart-pointer/reference.md)
  
### 同步執行流
- 基礎執行流
  - [函數](3-exec-sync/function/index.md)
  - [循環](3-exec-sync/loop/index.md)
  - [match](3-exec-sync/match/index.md)
  - [if let](3-exec-sync/if-let/index.md)
- 包和crate
  - [使用外部crate的簡單例子](3-exec-sync/crate/demo.md)
  - [使用lib.rs中定義的函數的例子](3-exec-sync/crate/lib-rs.md)
- 泛型與trait
  - [trait](3-exec-sync/generic/trait.md)
  - [泛型](3-exec-sync/generic/generic.md)
- 閉包
  - [閉包](3-exec-sync/closure/index.md)
- 迭代器
  - [實現自定義迭代器](3-exec-sync/iterator/index.md)
- 併發編程
  - [創建線程傳遞數據並等待](3-exec-sync/thread/demo.md)
  - [使用多線程實現生產者與消費者](3-exec-sync/thread/consumer.md)
  - [多線程之間訪問共享變量](3-exec-sync/thread/mutex.md)
- 宏
  - [聲明宏的定義與使用，以及try、?錯誤處理](3-exec-sync/macro/index.md)
- Rust和Go跨語言互調
  - [Go調用Rust生成的動態鏈接庫-入門demo](3-exec-sync/ffi/go2rust_demo/index.md)
  - [Rust調用Go生成的動態鏈接庫-入門demo](3-exec-sync/ffi/rust2go_demo/index.md)
  - [在rust中使用c語言 - libc crate](3-exec-sync/ffi/crate_libc/index.md)
  - [在rust中自動構建編譯C代碼 - cc crate](3-exec-sync/ffi/crate_cc/index.md)
  - [解析rust代碼為抽象語法樹 - syn crate](3-exec-sync/ffi/crate_syn/index.md)
  - [生成rust代碼 - quote crate](3-exec-sync/ffi/crate_quote/index.md)
  - [基於rust代碼生成C代碼 - cbindgen crate](3-exec-sync/ffi/crate_cbindgen/index.md)

### 異步執行流
- [future與executor工作原理]
  - [future實現](3-exec-async/internal/timer.md)
  - [excutor實現](3-exec-async/internal/executor.md)
- [使用async/await實現異步](3-exec-async/async/async.md)
- [固定](3-exec-async/pin/pin.md)
  - [不固定的話存在的問題](3-exec-async/pin/swap_problem.md)
  - [固定到棧上](3-exec-async/pin/pin_to_stack.md)
  - [固定到堆上](3-exec-async/pin/pin_to_heap.md)
- 多future同時運行
  - [join!](3-exec-async/concurrency/join.md)
  - [select!](3-exec-async/concurrency/select.md)
- [多線程與異步](3-exec-async/async/multi-thread.md)
- tokio工作原理

### 網絡編程
- [單線程簡單HTTP服務器](4-network/basic/simple-http-server.md)
- [基於線程池的HTTP服務器](4-network/basic/multi-thread-server.md)
- [基於異步的HTTP服務器](4-network/basic/async-http-server.md)

## 參考資料
- [《Rust程序設計語言》](https://www.rustwiki.org.cn/zh-CN/book/title-page.html)
- [《Rust中的異步編程》](https://huangjj27.github.io/async-book/index.html)