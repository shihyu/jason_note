# 輸入與輸出

輸入與輸出可以說是一個實用程序的最基本要求，沒有輸入輸出的程序是沒有什麼卵用的。雖然輸入輸出被函數式編程語言鄙稱為副作用，但正是這個副作用才賦予了程序實用性，君不見某著名函數式語言之父稱他主導設計的函數式語言"[is useless](https://www.youtube.com/watch?v=iSmkqocn0oQ)"。這章我們就來談談輸入輸出副作用。

## 讀寫 Trait

輸入最基本的功能是讀(Read)，輸出最基本的功能是寫(Write)。標準庫裡面把怎麼讀和怎麼寫抽象出來歸到了 `Read` 和 `Write` 兩個接口裡面，實現了 `Read` 接口的叫 reader，而實現了 `Write` 的叫 writer。Rust裡面的 Trait 比其它語言裡面的接口更好的一個地方是 Trait 可以帶默認實現，比如用戶定義的 reader 只需要實現 `read` 一個方法就可以調用 `Read` trait 裡面的任意其它方法，而 writer 也只需要實現 `write` 和 `flush` 兩個方法。

Read 和 Write 這兩個 Trait 都有定義了好多方法，具體可以參考標準庫 API 文檔中的[Read](http://doc.rust-lang.org/stable/std/io/trait.Read.html) 和 [Write](http://doc.rust-lang.org/stable/std/io/trait.Write.html)

Read 由於每調用一次 `read` 方法都會調用一次系統API與內核交互，效率比較低，如果給 reader 增加一個 buffer，在調用時 `read` 方法時多讀一些數據放在 buffer 裡面，下次調用 `read` 方法時就有可能只需要從 buffer 裡面取數據而不用調用系統API了，從而減少了系統調用次數提高了讀取效率，這就是所謂的 `BufRead` Trait。一個普通的 reader 通過 `io::BufReader::new(reader)` 或者 `io::BufReader::with_capacity(bufSize, reader)` 就可以得到一個 BufReader 了，顯然這兩個創建 BufReader 的函數一個是使用默認大小的 buffer 一個可以指定 buffer 大小。BufReader 比較常用的兩個方法是按行讀： `read_line(&mut self, buf: &mut String) -> Result<usize>` 和 `lines(&mut self) -> Lines<Self>`，從函數簽名上就可以大概猜出函數的用法所以就不囉嗦了，需要注意的是後者返回的是一個迭代器。詳細說明直接看 API 文檔中的[BufRead](http://doc.rust-lang.org/stable/std/io/trait.BufRead.html)

同樣有 `BufWriter` 只不過由於其除了底層加了 buffer 之外並沒有增加新的寫方法，所以並沒有專門的 `BufWrite` Trait，可以通過 `io::BufWriter::new(writer)` 或 `io::BufWriter::with_capacity(bufSize, writer)` 創建 `BufWriter`。

輸入與輸出接口有了，我們接下來看看實際應用中最常用的兩類 reader 和 writer：標準輸入/輸出，文件輸入/輸出
