# Summary

* [初識Rust](1st-glance/README.md)
* [安裝Rust](install/preface.md)「marvin-min」
  * [Linux](install/install_rust_on_linux.md)
  * [Mac](install/install_rust_on_mac_os.md)
  * [Windows](install/install_rust_on_windows.md)
  * [版本管理工具: rustup](install/rustup.md)
* [編輯器](editors/preface.md)
  * [前期準備](editors/before.md)「wayslog」
  * [vim](editors/vim.md)「wayslog」
  * [emacs](editors/emacs.md)「tiansiyuan」
  * [vscode](editors/vscode.md)「daogangtang」
  * [atom](editors/atom.md)「wayslog」
  * [sublime](editors/sublime.md)
  * [visual studio](editors/visualstudio.md)「marvinguo」
  * [spacemacs](editors/spacemacs.md)「wayslog」
* [Rust快速入門](quickstart/quickstart.md)「Naupio」
  * [Rust旅程](quickstart/rust-travel.md)
  * [變量綁定與原生類型](quickstart/primitive-type.md)
  * [數組、動態數組和字符串](quickstart/vector-string.md)
  * [結構體與枚舉](quickstart/struct-enum.md)
  * [控制流](quickstart/control-flow.md)
  * [函數與方法](quickstart/function-method.md)
  * [特性](quickstart/trait.md)
  * [註釋與文檔](quickstart/comments-document.md)
  * [輸入輸出流](quickstart/io-stream.md)
* [Cargo項目管理器](cargo-projects-manager/cargo-projects-manager.md)「fuyingfuying」
* [基本程序結構](flow/preface.md)「daogangtang」
  * [註釋](flow/comment.md)
  * [條件](flow/condition.md)
  * [循環](flow/repetition.md)
* [類型、運算符和字符串](type/preface.md)「wayslog」
  * [基礎類型](type/types.md)
  * [複合類型](type/compound-types.md)
  * [字符串類](type/string.md)
  * [基礎運算符和字符串格式化](type/operator-and-formatting.md)
* [函數](function/overview.md)「qdao」
  * [函數參數](function/arguement.md)
  * [函數返回值](function/return_value.md)
  * [語句和表達式](function/statement_expression.md)
  * [高階函數](function/higher_order_function.md)
* [模式匹配](match/overview.md)「wayslog」
  * [match關鍵字](match/match.md)
  * [模式 pattern](match/pattern.md)
* [特徵 Trait](trait/overview.md)「JohnSmithX」
  * [trait關鍵字](trait/trait.md)
  * [trait對象](trait/trait-object.md)
* [泛型](generic/generic.md)「stormgbs」
* [可變性、所有權、租借和生命期](ownership-system/preface.md)「stormgbs」
  * [所有權](ownership-system/ownership.md)
  * [引用和借用](ownership-system/borrowing_reference.md)
  * [生命週期](ownership-system/lifetime.md)
* [閉包](closure/overview.md)「qdao」
  * [閉包的語法](closure/syntax.md)
  * [閉包的實現](closure/implementation.md)
  * [閉包作為參數和返回值](closure/as_argument_return_value.md)
* [集合類型 Collections](collections/overview.md)「wayslog」
  * [動態數組 Vec](collections/vec.md)
  * [哈希表 HashMap](collections/hashmap.md)
* [迭代器](iterator/overview.md)「wayslog」
  * [迭代器、適配器、消費者](iterator/iterator.md)
* [模塊和包系統、Prelude](module/preface.md)「daogangtang」
  * [模塊 module 和包 crate](module/module.md)
  * [Prelude](module/prelude.md)
  * [pub restricted](module/pub-restricted.md)
* [Option、Result與錯誤處理](error-handling/option-result.md)「JohnSmithX」
* [輸入與輸出](io/preface.md)
  * [標準輸入輸出](io/io.md) 
  * [print! 宏](io/output.md)
  * [文件輸入輸出](io/file-io.md)「tennix」
* [宏系統](macro/macro.md)「tennix」
* [堆、棧與Box](heap-stack/heap-stack.md)「tennix」
* [幾種智能指針](rcarc/preface.md)「daogangtang」
  * [Rc, Arc](rcarc/rcarc.md)
  * [Mutex, RwLock](rcarc/mutex.md)
  * [Cell, RefCell](rcarc/cell.md)
* [類型系統中的幾個常見 Trait](intoborrow/preface.md) 「daogangtang」
  * [Into/From 及其在 String 和 &str 互轉上的應用](intoborrow/into.md)
  * [AsRef, AsMut](intoborrow/asref.md)
  * [Borrow, BorrowMut, ToOwned](intoborrow/borrow.md)
  * [Deref 與 Deref coercions](intoborrow/deref.md)
  * [Cow 及其在 String 和 &str 上的應用](intoborrow/cow.md)
* [Send 和 Sync](marker/sendsync.md)「daogangtang」
* [併發，並行，多線程編程](concurrency-parallel-thread/preface.md)「anzhihun」
  * [線程](concurrency-parallel-thread/thread.md)
  * [消息傳遞](concurrency-parallel-thread/message-passing.md)
  * [共享內存](concurrency-parallel-thread/share-memory.md)
  * [同步](concurrency-parallel-thread/synchronize.md)
  * [並行](concurrency-parallel-thread/parallel.md)
* [Unsafe、原始指針](unsafe-rawpointer/preface.md)「JohnSmithX」
  * [Unsafe](unsafe-rawpointer/unsafe.md)
  * [原始指針](unsafe-rawpointer/raw-pointer.md)
* [FFI](ffi/preface.md)「42」
  * [rust調用ffi函數](ffi/calling-ffi-function.md)
  * [將rust編譯成庫](ffi/compiling-rust-to-lib.md)
* [運算符重載](operator-overloading/operator.md)「wayslog」
* [屬性和編譯器參數](attr-and-compiler-arg/preface.md)「elton」
  * [屬性](attr-and-compiler-arg/attribute.md)
  * [編譯器參數](attr-and-compiler-arg/rustc-option.md)
* [Cargo參數配置](cargo-detailed-cfg/cargo-detailed-cfg.md)「fuyingfuying」
* [測試與評測](testing/preface.md)「daogangtang」
  * [測試 (testing)](testing/threearchtest.md)
  * [評測 (benchmark)](testing/bench.md)
* [代碼風格](coding-style/style.md)「tiansiyuan」
* [Any與反射](any/any.md)「wayslog」
* [安全](safe/safety.md)「daogangtang」
* [常用數據結構實現](data-structure/preface.md)「Naupio」
  * [棧結構](data-structure/stack.md)
  * [隊列](data-structure/queue.md)
  * [二叉樹](data-structure/binary_tree.md)
  * [優先隊列](data-structure/priority_queue.md)
  * [鏈表](data-structure/linked_list.md)
  * [圖結構](data-structure/graph.md)
* [標準庫介紹](std/overview.md)「wayslog」
  * [系統命令:調用grep](std/process.md)
  * [目錄操作:簡單grep](std/fs-and-path.md)
  * [網絡模塊:W迴音](std/net.md)
* [實戰篇](action/preface.md)「wangyu190810」
  * [實戰：Json處理](action/json_data/readme.md)
  * [實戰：Web 應用開發入門](action/mysite/readme.md)
  * [實戰：使用Postgresql數據庫](action/db/readme.md)
* [附錄-術語表](appendix/glossary.md)「tennix」
