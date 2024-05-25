# 🏄💨【最安全的編程語言】Rust工程師枕邊資料，大牛文章，開源框架，官方文檔，視頻，推薦書籍，學習乾貨，大牛語錄

<div align=center>

![rust](https://user-images.githubusercontent.com/87457873/132184451-55f1125e-acad-4cc7-9e56-ecbffc0db412.png)
  
## 一個安全、併發、實用的系統語言

<br>
<br>
  
   [🏝<br>&nbsp;&nbsp;&nbsp; &nbsp;環境搭建&nbsp;&nbsp;&nbsp;&nbsp; ](https://github.com/0voice/Understanding_in_Rust#-%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA)  |[📕<br>&nbsp;&nbsp;&nbsp; 入門秘笈&nbsp;&nbsp;&nbsp; ](https://github.com/0voice/Understanding_in_Rust#-%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88-pdf%E6%A1%A3%E4%B8%8B%E8%BD%BD)|  [📖<br>&nbsp;&nbsp;&nbsp; 推薦書籍&nbsp;&nbsp;&nbsp; ](https://github.com/0voice/Understanding_in_Rust/blob/main/README.md#-%E6%8E%A8%E8%8D%90%E4%B9%A6%E7%B1%8D)
:-------: | :-------: | :---------:
 **[📑<br>精選文章](https://github.com/0voice/Understanding_in_Rust#-%E5%A4%A7%E7%89%9B%E6%96%87%E7%AB%A0)**  |  **[📰<br>官方文檔](https://github.com/0voice/Understanding_in_Rust/blob/main/README.md#-%E5%AE%98%E6%96%B9%E6%96%87%E6%A1%A3)**|  **[✈<br> 雜貨鋪](https://github.com/0voice/Understanding_in_Rust/blob/main/README.md#-%E6%9D%82%E8%B4%A7%E9%93%BA)**
**[💽<br>視頻](https://github.com/0voice/Understanding_in_Rust#-%E8%A7%86%E9%A2%91)** | **[🏗<br>開源框架](https://github.com/0voice/Understanding_in_Rust#-%E5%BC%80%E6%BA%90%E6%A1%86%E6%9E%B6)** | **[🐂<br>大牛語錄](https://github.com/0voice/Understanding_in_Rust/blob/main/README.md#-%E5%A4%A7%E7%89%9B%E8%AF%AD%E5%BD%95)**
  
<br>
<br>  

</div>




# 🤔 Why Rust？Why can？

### Jay Oster, PubNub 架構師 :

“除了安全和性能，我們還有：

- 泛型；
- 特徵；
- 代數類型；
- 函數式和命令式範式；
- 可能是世界上最好的依賴管理和構建工具，實際上解決了‘依賴地獄’問題；
- 對內嵌文檔、測試和性能評測的美妙支持；
- 一個大的且正在生長的庫、抽象、工具生態；
- 過程宏；
- 與已有代碼的 FFI 交互性；
- 支持一打平臺（更多的在路上！）；
- 對開發者體驗是正向的、毋庸置疑的滿足。

Rust 是唯一一個下面所有框框都打勾的語言：

- 內存安全
- 類型安全
- 消除數據競爭
- 使用前編譯
- 建立（並且鼓勵）在零抽象之上
- 最小的運行時（無停止世界的垃圾蒐集器，無 JIT 編譯器，無 VM）
- 低內存佔用（程序可以運行在資源受限的環境，比如小的微控制器）
- 裸金屬目標（比如，寫一個 OS 內核或者設備驅動，把 Rust 當一個 ‘高層’彙編器使用）”

### Peter Varo:

“Rust 有一個很香的地方：它像 C 和 C++ 那樣底層，因此也具有底層的這些優勢（比如，控制、大小、速度等）。同時呢，它又像 Haskell 那樣高層，自帶令人吃驚的大量功能傳承。它還是命令式的，所以容易被大多數人上手。然後它又像 Python 一樣靈活，比如，' 鴨子類型（duck-typing）' 的概念出現在編譯時（比如，特徵限定），然後它又沒有陳舊的面向對象模型以及由這個模型導致的各種出名的問題。

最後但很重要的是，還有一連串的東西被包含進來：精簡短小的語法，語言提供的數目不多的特性，標準庫及其一致性，高質量的文檔的集成，包括對初學者和高級用戶都適用的學習材料，這些都是促成因素。”

# 🏝 環境搭建

**安裝及工具：https://www.rust-lang.org/zh-CN/learn/get-started**

# 📕 入門秘笈 [（PDF檔下載）](https://github.com/0voice/Understanding_in_Rust/blob/main/Rust%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88.pdf)

- [Rust簡介](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E7%AE%80%E4%BB%8B.md)<br>
- [Rust的特點](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E7%9A%84%E7%89%B9%E7%82%B9.md)<br>
- [Rust開發環境安裝](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83%E5%AE%89%E8%A3%85.md)<br>
- [Rust第一個程式](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E7%AC%AC%E4%B8%80%E4%B8%AA%E7%A8%8B%E5%BC%8F.md)<br>
- [Rust if語句](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%20if%E8%AF%AD%E5%8F%A5.md)<br>
- [Rust if in a let語句](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%20if%20in%20a%20let%E8%AF%AD%E5%8F%A5.md)<br>
- [Rust loop迴圈](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%20loop%E5%9B%9E%E5%9C%88.md)<br>
- [Rust for迴圈](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%20for%E5%9B%9E%E5%9C%88.md)<br>
- [Rust while迴圈](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%20while%E5%9B%9E%E5%9C%88.md)<br>
- [Rust所有權](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E6%89%80%E6%9C%89%E6%9D%83.md)<br>
- [Rust參照和借用](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E5%8F%82%E7%85%A7%E5%92%8C%E5%80%9F%E7%94%A8.md)<br>
- [Rust切片](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E5%88%87%E7%89%87.md)<br>
- [Rust結構體](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E7%BB%93%E6%9E%84%E4%BD%93.md)<br>
- [Rust結構體更新語法](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E7%BB%93%E6%9E%84%E4%BD%93%E6%9B%B4%E6%96%B0%E8%AF%AD%E6%B3%95.md)<br>
- [Rust結構體方法語法](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E7%BB%93%E6%9E%84%E4%BD%93%E6%96%B9%E6%B3%95%E8%AF%AD%E6%B3%95.md)<br>
- [Rust列舉](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E5%88%97%E4%B8%BE.md)<br>
- [匹配運算子](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/%E5%8C%B9%E9%85%8D%E8%BF%90%E7%AE%97%E5%AD%90.md)<br>
- [Rust if let控制流程](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%20if%20let%E6%8E%A7%E5%88%B6%E6%B5%81%E7%A8%8B.md)<br>
- [Rust模組](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E6%A8%A1%E7%BB%84.md)<br>
- [Rust檔案系統](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E6%A1%A3%E6%A1%88%E7%B3%BB%E7%BB%9F.md)<br>
- [Rust公開函式](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E5%85%AC%E5%BC%80%E5%87%BD%E5%BC%8F.md)<br>
- [Rust use關鍵字參照模組](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%20use%E5%85%B3%E9%94%AE%E5%AD%97%E5%8F%82%E7%85%A7%E6%A8%A1%E7%BB%84.md)<br>
- [Rust向量](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E5%90%91%E9%87%8F.md)<br>
- [Rust字串](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E5%AD%97%E4%B8%B2.md)<br>
- [Rust錯誤處理](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E9%94%99%E8%AF%AF%E5%A4%84%E7%90%86.md)
- [Rust不可恢復的錯誤](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E4%B8%8D%E5%8F%AF%E6%81%A2%E5%A4%8D%E7%9A%84%E9%94%99%E8%AF%AF.md)<br>
- [Rust可恢復的錯誤](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E5%8F%AF%E6%81%A2%E5%A4%8D%E7%9A%84%E9%94%99%E8%AF%AF.md)<br>
- [Rust泛型](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E6%B3%9B%E5%9E%8B.md)<br>
- [Rust Trait](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%20Trait.md)<br>
- [Rust生命週期](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F.md)<br>
- [Rust智慧指標](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%E6%99%BA%E6%85%A7%E6%8C%87%E6%A0%87.md)<br>
- [Rust Box<T>](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%20Box%3CT%3E.md)<br>
- [Rust Deref trait](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%20Deref%20trait.md)<br>
- [Rust Drop trait](https://github.com/0voice/Understanding_in_Rust/blob/main/%E5%85%A5%E9%97%A8%E7%A7%98%E7%AC%88/Rust%20Drop%20trait.md)<br>

# 📖 推薦書籍
  
### 國內書籍
  
- [《深入淺出Rust》](https://jp1lib.org/s/?q=%E3%80%8A%E6%B7%B1%E5%85%A5%E6%B5%85%E5%87%BARust%E3%80%8B)
  
- [《Rust權威指南》](https://book.douban.com/subject/35081743/)
  
- [《Rust 程序設計語言》](https://kaisery.github.io/trpl-zh-cn/)
  
- [《精通Rust(第2版)》](https://jp1lib.org/book/17127064/820864)
  
### 國外書籍
  
**入門書籍**
  
- [《The Rust Programming Language》](https://doc.rust-lang.org/book/)
  
歡迎！本書將教你有關 Rust 編程語言的知識。Rust 是一種系統編程語言，專注於三個目標：安全性、速度和併發性。它在沒有垃圾收集器的情況下實現了這些目標，使其成為其他語言不擅長的許多用例的有用語言：嵌入其他語言、具有特定空間和時間要求的程序以及編寫低級代碼，例如設備驅動程序和操作系統。它通過在不產生運行時開銷的情況下進行大量編譯時安全檢查，同時消除所有數據競爭，從而改進了針對此空間的當前語言。Rust 還旨在實現“零成本抽象”，儘管其中一些抽象感覺像是高級語言的抽象。即便如此，Rust 仍然允許像低級語言一樣進行精確控制。
  
- [《Welcome to Rust-101》](https://www.ralfj.de/projects/rust-101/main.html)
  
這是 Rust-101，一個 Rust 語言的小教程。它旨在成為一門交互式的動手課程：我相信真正學習一門語言的唯一方法是在其中編寫代碼，因此您應該在課程中進行編碼。如果您有任何未在此處回答的問題，請查看下面的“其他資源”。尤其是，IRC 頻道里擠滿了願意幫助你的很棒的人！我在那裡花了很多時間 ;-) 我假設對編程有一定的瞭解，因此不會解釋大多數語言共有的基本概念。相反，我將專注於 Rust 的特殊之處。
  
- [《Rust by Example》](http://rustbyexample.com/)
  
Rust by Example (RBE) 是一組可運行的示例，用於說明各種 Rust 概念和標準庫。
  
- [《Why Rust?》](https://kr1lib.org/book/10990507/3a18af) 
  
儘管自 40 多年前引入 C 以來，系統編程語言已經有了很大的發展，但我們對造成巨大後果的愚蠢錯誤的能力仍然沒有改變，新聞中經常有生動的例子。這份 O'Reilly 報告研究了 Rust，這是一種新的系統編程語言，它將安全性和安全性與性能相結合，與 C 和 C++ 相當。
  
- [《Learning Rust》](https://kr1lib.org/book/11689651/08c0b6) 
  
Rust 是一種高度併發和高性能的語言，專注於安全和速度、內存管理和編寫乾淨的代碼。它還保證線程安全，其目的是提高現有應用程序的性能。它得到了 Mozilla 的支持，以解決併發的關鍵問題。 
  
- [《Beginning Rust - From Novice to Professional》](https://kr1lib.org/book/3490555/7b7c82)
  
學習在 Unix、Linux shell、macOS 和 Windows 命令行上以簡單、循序漸進的方式使用 Rust 進行編程。當您閱讀本書時，您將建立在您在前幾章中獲得的知識的基礎上，並瞭解 Rust 提供了什麼。

開始 Rust 從 Rust 的基礎開始，包括如何命名對象、控制執行流和處理原始類型。您將看到如何進行算術運算、分配內存、使用迭代器以及處理輸入/輸出。一旦掌握了這些核心技能，您將著手處理錯誤並使用 Rust 的面向對象特性立即構建健壯的 Rust 應用程序。

只需要基本的編程知識，最好是 C 或 C++。要理解這本書，知道什麼是整數和浮點數，以及區分標識符和字符串文字就足夠了。
  
- [《Rust Cookbook》](https://kr1lib.org/book/3362654/66eb5a)  
  
本書將幫助您理解 Rust 語言的核心概念，使您能夠通過整合零成本抽象和更好的內存管理等功能來開發高效和高性能的應用程序。深入研究 Rust 中的高級概念，例如錯誤處理、宏、包和並行性。在本書的最後，學習如何創建 HTTP 服務器和 Web 服務，在服務器端編程方面建立強大的基礎知識，並能夠提供使用 Rust 構建高性能和更安全的生產級 Web 應用程序和服務的解決方案。
  
- [《Rust Standard Library Cookbook》](https://kr1lib.org/book/3571952/9b9cdb)  
  
Mozilla 的 Rust 以其驚人的功能和強大的庫而備受關注。本書將帶您瞭解各種秘訣，教您如何利用標準庫來實現高效的解決方案。

本書首先簡要介紹了標準庫和館藏的基本模塊。從這裡開始，食譜將涵蓋通過解析支持文件/目錄處理和交互的包。您將瞭解與高級數據結構、錯誤處理和網絡相關的包。您還將學習使用期貨和實驗性夜間功能。這本書還涵蓋了 Rust 中最相關的外部 crate。
  
- [《Network Programming with Rust》](https://kr1lib.org/book/3571947/48c564)  
  
Rust 足夠低級，可以提供對內存的細粒度控制，同時通過編譯時驗證提供安全性。這使得它特別適合編寫低級網絡應用程序。

本書分為三個主要部分，將帶您踏上構建功能齊全的 Web 服務器的激動人心的旅程。本書首先對 Rust 和基本的網絡概念進行了紮實的介紹。這將為整本書奠定基礎並定下基調。在第二部分中，我們將深入研究如何使用 Rust 開發網絡軟件。從使用套接字的客戶端-服務器網絡到 IPv4/v6、DNS、TCP、UDP，您還將瞭解使用 serde 序列化和反序列化數據。這本書展示瞭如何通過 HTTP 與 REST 服務器進行通信。本書的最後一部分討論了使用 Tokio 堆棧進行異步網絡編程。鑑於安全對於現代系統的重要性，您將看到 Rust 如何支持常見的原語，例如 TLS 和公鑰加密。
  
- [《Rust Programming by Example》](https://kr1lib.org/book/5669466/ef3a67) 
  
從介紹 Rust 開始，您將學習基本方面，例如其語法、數據類型、函數、泛型、控制流等。在此之後，您將直接開始構建您的第一個項目，俄羅斯方塊遊戲。接下來，您將使用 Tokio（可擴展且高效的異步 IO Rust 庫）構建圖形音樂播放器並使用快速、可靠的網絡軟件。

在本書的過程中，您將探索 Rust 編程的各種特性，包括它的 SDL 特性、事件循環、文件 I/O 和著名的 GTK+ 小部件工具包。通過這些項目，您將看到 Rust 在併發方面的表現——包括並行性、可靠性、改進的性能、泛型、宏和線程安全。我們還將介紹 Rust 的一些異步和反應式編程方面。
  
- [《Rust Quick Start Guide》](https://kr1lib.org/book/11689628/cf06fb)
  
熟悉使用流行的新系統編程語言編寫程序，這些語言將低級語言的強大性能與多線程代碼中的線程安全等高級功能結合在一起。
  
- [《Rust in Action [MEAP]》](https://kr1lib.org/book/11235796/a7ef40)  
  
Rust in Action 是一本面向想要探索 Rust 編程語言世界的中級程序員的書。它適用於可能已經用盡網絡上的免費資料但仍想了解更多信息的人。它與 Rust 編程的其他材料不同，因為它還教您有關係統編程的知識。您將能夠更多地瞭解 CPU 的工作原理、計算機如何計時、指針是什麼以及您的網卡和鍵盤如何告訴 CPU 它們已準備好讀取輸入。

從系統編程書籍的角度來看，它實際上也是獨一無二的 - 因為幾乎每個示例都適用於 Windows！如果你是那種喜歡實際例子的學習者，你會喜歡閱讀這本書。
  
- [《A Gentle Introduction to Rust》](https://stevedonovan.github.io/rust-gentle-intro/)  
  
Rust 是一種靜態和強類型的系統編程語言。靜態意味著所有類型在編譯時都是已知的，強烈意味著這些類型旨在使編寫不正確的程序變得更加困難。一個成功的編譯意味著你可以比使用像 C 這樣的牛仔語言更好地保證正確性。系統意味著生成最好的機器代碼，並完全控制內存使用。因此，其用途非常核心：操作系統、設備驅動程序和甚至可能沒有操作系統的嵌入式系統。然而，它實際上也是一種非常令人愉快的語言，可以用來編寫普通的應用程序代碼。

與 C 和 C++ 的最大區別在於 Rust 默認是安全的；檢查所有內存訪問。意外損壞內存是不可能的。
  
- [《Practical Machine Learning with Rust: Creating Intelligent Applications in Rust》](https://kr1lib.org/book/5304256/0ff807)  
  
Rust 中的機器學習已經被社區忽視了很長一段時間。由於宇宙中散佈著許多不同的板條箱，這本書試圖統一所有的信息和用法，並在某種程度上動搖社區採取行動。數據是新的前沿領域，而 Rust 必須成為其中的一部分。

閱讀了使用 Rust 的實用機器學習之後，您將對使用 Rust 創建高計算庫有一個深入的瞭解。掌握了這種神奇語言的知識，您將能夠創建性能更高、內存安全且資源佔用更少的應用程序。
  
- [《Rust Web Development》](https://kr1lib.org/book/11729741/a127f0)  

Rust Web Development 是使用 Rust 構建基於服務器的 Web 應用程序的實踐指南。如果您使用 Java、C# 或 PHP 構建了 Web 服務器，您會立即愛上 Rust 提供的性能和開發體驗。本書向您展示瞭如何使用純 Rust 以及重要的 Rust 庫（例如用於異步運行時的 tokio、用於 Web 服務器和 API 的 warp 以及運行外部 HTTP 請求的 reqwest 等）高效工作。

您可以將這本書交給新聘用的開發人員，並讓他們使用這本書。它包含非常實用的示例和模式，併為未來探索該主題奠定了堅實的基礎。
  
**進階書籍**
 
- [《The Rustonomicon》](https://doc.rust-lang.org/nightly/nomicon/)
  
本書深入探討了編寫正確的不安全 Rust 程序所需的所有可怕細節。由於這個問題的性質，它可能會導致釋放出無法言喻的恐怖，將你的心靈粉碎成十億個無限小的絕望碎片。

如果您希望編寫 Rust 程序的職業生涯長久而快樂，那麼現在您應該回過頭來忘記您曾經看過這本書。這不是必要的。但是，如果您打算編寫不安全的代碼——或者只是想深入瞭解語言的本質——這本書包含了寶貴的信息。  
  
- [《Programming Rust》](https://1lib.limited/book/3400043/791885) 
  
這本實用的書向系統程序員介紹了 Rust，一種新的前沿語言。您將瞭解 Rust 如何提供靜態驗證的內存安全和低級控制的罕見且有價值的組合——想象一下 C++，但沒有懸空指針、空指針取消引用、洩漏或緩衝區溢出。  
  
- [《Rust Essentials - Second Edition》](https://1lib.limited/book/3427870/81d715)  
  
本書首先論證了 Rust 在當今編程語言領域的獨特地位。安裝 Rust 並學習如何使用它的包管理器 Cargo。逐步介紹各種概念：變量、類型、函數和控制結構，以打下基礎。然後探索更多結構化數據，例如字符串、數組和枚舉，並瞭解模式匹配的工作原理。

在這一切中，本書強調了 Rust 編譯器用來生成安全代碼的獨特推理方式。接下來看看 Rust 特定的錯誤處理方式，以及特徵在 Rust 代碼中的整體重要性。在我們探索各種指針類型時，將深入探討內存安全的支柱。接下來，看看宏如何簡化代碼生成，以及如何使用模塊和板條箱組合更大的項目。最後，瞭解我們如何在 Rust 中編寫安全的併發代碼並與 C 程序接口，瞭解 Rust 生態系統，並探索標準庫的使用。  
  
- [《Hands-On Concurrency with Rust》](https://1lib.limited/book/11689707/4154e1)  
  
本書將教你如何在現代機器上管理程序性能，並在 Rust 中構建快速、內存安全和併發的軟件。它從 Rust 的基礎開始，討論機器架構概念。您將瞭解如何系統地衡量和改進 Rust 代碼的性能，以及如何自信地編寫集合。您將瞭解應用於線程的 Sync 和 Send 特性，並使用鎖、原子原語、數據並行等來協調線程執行。

本書將向您展示如何在 C++ 代碼中有效地嵌入 Rust，並探索用於多線程應用程序的各種 crate 的功能。它深入探討了實現。您將瞭解互斥鎖的工作原理並自行構建多個互斥鎖。您將掌握生態系統中存在的完全不同的方法來構建和管理大規模系統。
  
- [《Hands-On Functional Programming in Rust》](https://1lib.limited/book/11689735/4d162e)
  
函數式編程允許開發人員將程序劃分為更小的、可重用的組件，從整體上簡化軟件的創建、測試和維護。結合 Rust 的強大功能，您可以開發滿足現代軟件需求的強大且可擴展的應用程序。本書將幫助您發現可用於以功能方式構建軟件的所有 Rust 功能。

我們首先對針對不同問題和模式的函數式方法和麵向對象方法進行簡要比較。然後我們快速查看控制流的模式、數據以及這些函數式編程獨有的抽象。下一部分介紹如何在 Rust 中創建功能性應用程序；還討論了 Rust 獨有的可變性和所有權。接下來檢查純函數，您將掌握閉包、它們的各種類型和柯里化。我們還通過功能設計原則和使用宏的元編程來實現併發。最後，我們看看調試和優化的最佳實踐。

讀完本書，您將熟悉函數式編程方法，並能夠在日常工作中使用這些技術。  
  
- [《Rust High Performance》](https://1lib.limited/book/11000538/3e9291)
  
有時，很難從 Rust 中獲得最佳性能。這本書教你將你的 Rust 代碼的速度優化到 C/C++ 等語言的水平。您將瞭解並修復常見的陷阱，瞭解如何通過使用元編程來提高生產力，並通過安全輕鬆地併發執行部分代碼來加速代碼。您將掌握這門語言的特性，這將使您脫穎而出，並使用它們來真正提高算法的效率

本書以一個溫和的介紹開始，以幫助您識別 Rust 編程時的瓶頸。我們重點介紹了常見的性能缺陷，以及及早發現和解決這些問題的策略。我們繼續掌握 Rust 的類型系統，這將使我們能夠在編譯時在性能和安全性方面進行令人印象深刻的優化。然後，您將學習如何在 Rust 中有效地管理內存，掌握借用檢查器。我們繼續測量性能，您將看到這如何影響您編寫代碼的方式。繼續前進，您將在 Rust 中執行元編程，以提高代碼的性能和生產力。您最終將學習 Rust 中的並行編程，它通過使用多線程和異步編程實現高效和更快的執行。
  
- [《Zero To Production In Rust》](https://zero2prod.com/) 
  
如果您想學習如何使用 Rust 進行後端開發，這裡就是您的最佳選擇。

Rust 的採用率達到了歷史最高水平：越來越多的公司正在嘗試和招聘。<br>
如果您對使用 Rust 構建 API 感興趣，零到生產是您 Rust 之旅的理想起點。<br>
您將邊做邊學：我們將從頭開始，一步一步地構建一個功能齊全的電子郵件通訊後端 API。<br>

您將學習：

1、導航和利用 Rust 的 crates 生態系統<br>
2、構建您的應用程序以使其模塊化和可擴展<br>
3、編寫測試，從單個單元到成熟的集成測試<br>
4、使用類型系統為您的域建模以強制執行不變量<br>
5、收集日誌、跟蹤和指標以觀察應用程序的狀態<br>
6、為您的 Rust 項目設置一個強大的持續集成和持續部署管道<br>
  
- [《Programming WebAssembly with Rust》](https://1lib.limited/book/5001228/7b21a9)  
  
WebAssembly 不僅僅是一項革命性的新技術。它正在重塑我們為 Web 及其他領域構建應用程序的方式。在 ActiveX 和 Flash 等技術失敗的地方，您現在可以使用您喜歡的任何語言編寫代碼並編譯為 WebAssembly，以便在瀏覽器、移動設備、嵌入式設備等中運行的快速、類型安全的代碼。將 WebAssembly 的便攜、高性能模塊與 Rust 的安全性和強大功能相結合，是一個完美的開發組合。

瞭解 WebAssembly 的堆棧機器架構如何工作，安裝低級 wasm 工具，並發現編寫原始廢棄代碼的黑暗藝術。在此基礎上構建並學習如何通過實現跳棋遊戲的邏輯從 Rust 編譯 WebAssembly 模塊。在 Rust 中創建 wasm 模塊，以多種引人注目的方式與 JavaScript 進行互操作。將您的新技能應用於非網絡主機的世界，並創建從在 Raspberry Pi 上運行的控制照明系統的應用程序到功能齊全的在線多人遊戲引擎，開發人員可以上傳他們自己的競技場綁定 WebAssembly 戰鬥模塊.

立即開始使用 WebAssembly，並改變您對 Web 的看法。  
  
- [《Step Ahead with Rust: Systems Programming in Rust》](https://www.armstrong-publications.com/product/step-ahead-with-rust-super-combo/)  
  
從基本的編程模式到深入瞭解該語言，Step Ahead with Rust 旨在幫助您從編寫程序到使用 Rust 構建軟件。本書將向您展示 Rust 語言最重要的特性，包括貨物、類型系統、迭代器等。讀完本書，您應該會熟悉更多內容，並準備好處理其餘的高級主題。

在您閱讀本書的過程中，我們建議您花時間嘗試一下書頁中所呈現的內容。這本書都是關於 Rust 的實際應用，所以在實踐中應用它是值得期待的。本書涵蓋：貨物、Rust 類型系統、迭代器、宏、所有權、借用和生命週期、不安全模式、併發。A Step Ahead with Rust 讀者應該是一位經驗豐富的開發人員，希望提高他們的 Rust 開發技能。  
  
- [《Creative Projects for Rust Programmers》](https://1lib.limited/book/5639719/c52aca)  
  
瞭解 Rust 編程語言的最新特性、有用的庫和框架的實用指南，將幫助您設計和開發有趣的項目

學習：

1、訪問 TOML、JSON 和 XML 文件以及 SQLite、PostgreSQL 和 Redis 數據庫<br>
2、使用 JSON 有效負載開發 RESTful Web 服務<br>
3、使用 HTML 模板和 JavaScript 創建 Web 應用程序，使用 WebAssembly 創建前端 Web 應用程序或 Web 遊戲<br>
4、構建桌面 2D 遊戲<br>
5、為編程語言開發解釋器和編譯器<br>
6、創建機器語言模擬器<br>
7、使用可加載模塊擴展 Linux 內核<br>
  
# 📑 大牛文章
  
- [理解 Rust 的生命週期](https://github.com/0voice/Understanding_in_Rust/blob/main/%E6%96%87%E7%AB%A0/%E7%90%86%E8%A7%A3%20Rust%20%E7%9A%84%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F.md)
- [高德技術 | 基於Rust的Android Native內存分析方案](https://github.com/0voice/Understanding_in_Rust/blob/main/%E6%96%87%E7%AB%A0/%E5%9F%BA%E4%BA%8ERust%E7%9A%84Android%20Native%E5%86%85%E5%AD%98%E5%88%86%E6%9E%90%E6%96%B9%E6%A1%88.md)
- [Rust 與 C++：深入的語言比較](https://github.com/0voice/Understanding_in_Rust/blob/main/%E6%96%87%E7%AB%A0/Rust%20%E4%B8%8E%20C%2B%2B%EF%BC%9A%E6%B7%B1%E5%85%A5%E7%9A%84%E8%AF%AD%E8%A8%80%E6%AF%94%E8%BE%83.md)
  
# 📰 官方文檔
  
- [標準庫API文檔](https://doc.rust-lang.org/std/)
- [Rust Reference](https://doc.rust-lang.org/reference/index.html): Rust reference 文檔，有中文翻譯版本 [Rust語言規範](https://rustlang-cn.org/office/rust/reference/) 正在翻譯過程中
- [Rust編譯錯誤索引](https://doc.rust-lang.org/error-index.html)：發生編譯錯誤時，可以通過索引找到具體錯誤解釋
- [rustdoc文檔](https://doc.rust-lang.org/rustdoc/): `restdoc`工具的使用文檔
- [Rustonomicon](https://doc.rust-lang.org/reference/): rust的參考文檔。但是目前並不完整，可能有遺漏和錯誤
- [Unstable Book](https://doc.rust-lang.org/unstable-book/): 用於尚不穩定特性的文檔
- [Rustonomicon](https://doc.rust-lang.org/nomicon/): unsafe rust的黑暗藝術，有中文翻譯版本 [Rust高級編程](https://rustlang-cn.org/office/rust/advrust/)
- [The Cargo Book](https://doc.rust-lang.org/cargo/index.html): cargo使用介紹，有中文翻譯版本 [Cargo教程](https://rustlang-cn.org/office/rust/cargo/) 正在進行中
- [Rust Edition Guide](https://doc.rust-lang.org/nightly/edition-guide/introduction.html): Rust 版本指南，傳遞 Rust 不同版本之間大的變更信息
- [Command line apps in Rust](https://rust-lang-nursery.github.io/cli-wg/#command-line-apps-in-rust): 在Rust中編寫命令行程序
  
# ✈ 雜貨鋪
  
- Rust 最大中文社區論壇：https://rustcc.cn/
- 小眾中文社區的翻譯資料/論壇：https://learnku.com/rust
- Rust在線編輯器: https://play.rust-lang.org/
- 2021 年去哪學 Rust：https://loige.co/where-to-go-to-learn-rust-in-2021/
- Rust Cheat Sheet（Rust語法備忘單）：https://cheats.rs/
- Rust 中文書架與資訊：https://budshome.com/ | https://blog.budshome.com/
- 簡要而基礎的 Rust 知識（適合在 Rust Book 階段當作補充材料）：https://learning-rust.github.io/
- 微軟發佈的 Rust 新手教程：https://docs.microsoft.com/en-us/learn/paths/rust-first-steps/
- Rust-leetcodes刷題：https://stevenbai.top/rust-leetcode/
- Rust by Example 通過例子學 Rust：https://doc.rust-lang.org/rust-by-example/index.html
- 電子書下載 ：https://jp1lib.org/s/Rust
- Rust線下全球會議：
  - RustConf: https://rustconf.com/
  - Rust Belt Rust: https://rust-belt-rust.com/
  - RustFest: https://blog.rustfest.eu/
  - Rust Latam: https://rustcon.asia/
  - RustCon Asia: https://rustcon.asia/
  
# 💽 視頻
  
Rust 驗證研討會 2021 | 
:------:|
[Peeking at compiler-internal data (for fun and profit)](https://www.aliyundrive.com/s/4N4EE3URbBT)|
[Ferrite- A Rust EDSL for Message-passing Protocol Verification](https://www.aliyundrive.com/s/hGpvaNzWAHS)|
[Verifying that Rust programs don't crash](https://www.aliyundrive.com/s/TiMG3B7XXyZ)|
[crux-mir- Symbolic testing for Rust](https://www.aliyundrive.com/s/j5LG8Lwdmx8)|
[RustBelt- A Quick Dive Into the Abyss](https://www.aliyundrive.com/s/iv3ohCTjzcs)|
[Rustv- Semi-automatic Verification of Unsafe Rust Programs](https://www.aliyundrive.com/s/bfQjMdJTvow)|  
[Polonius](https://www.aliyundrive.com/s/bNdQLDpKbzN)|
[Towards Automatic Verification of Unsafe Rust with Constrained Horn Solvers](https://www.aliyundrive.com/s/iW2SdR1pFGU)|
[Rust interest in safety- and mission-critical environments](https://www.aliyundrive.com/s/EXnsFymhCib)|  
[Prusti – Deductive Verification for Rust](https://www.aliyundrive.com/s/eph1UzJugSt)|
[Creusot- A prototype tool for verification of Rust software](https://www.aliyundrive.com/s/6aeaQNeGZbX)|
[hacspec_ succinct, executable, verifiable specifications for high-assurance cryptography](https://www.aliyundrive.com/s/DgfNNFRn45G)|  
[Leveraging Compiler Intermediate Representation for Multi- and Cross-Language Verification](https://www.aliyundrive.com/s/oWuWB37ByBH)|
  
<br>
  
Rust Linz 2021 | 
:------:|
[Rust Linz, July 2021 - Stefan Baumgartner - Serverless Rust](https://www.aliyundrive.com/s/7nBT4iWyT5p)|  
[Rust Linz, July 2021 - Rainer Stropek - Traits, not your grandparents' interfaces](https://www.aliyundrive.com/s/1fSbir945Sh)|
[Rust Linz, August 2021 - Rainer Stropek - Rust iterators](https://www.aliyundrive.com/s/G3Yu2U7DaXN)|  
[Rust Linz, May 2021 - Harald Reingruber - Rust for Medical Visualization](https://www.aliyundrive.com/s/5u27AdX5bhq)|  
[Rust Linz, May 2021 - Lisa Passing - Creative Rust](https://www.aliyundrive.com/s/WouXfuZ9VSU)|  
[Rust Linz, June 2021 - Tim McNamara - How to learn Rust](https://www.aliyundrive.com/s/XhSexAWPNKr)|  
[Rust Linz, June 2021 - JT - A new path for your shell](https://www.aliyundrive.com/s/cymDeWwbsr6)|
[Rust Linz x Global Azure, April 2021 - Ryan Levick & Thomas Taylor - Rust, Kubernetes, and the Cloud](https://www.aliyundrive.com/s/Gdd63ojU9Xc)|  
[Rust Linz, April 2021 - Jan-Erik Rediger - Leveraging Rust to build cross-platform libraries](https://www.aliyundrive.com/s/rfPAYT9NWi9)|  
[Rust Linz, April 2021 - Herbert Wolverson - Learning Rust with Game Development - YouTube](https://www.aliyundrive.com/s/AoLEhwsgv9P)|    
  
  

# 🏗 開源框架
  
## 值得新手關注的Rust項目

- [mini redis](https://github.com/tokio-rs/mini-redis) - 不完整的Redis客戶端和服務器實現使用Tokio -僅為學習目的
- [async-graphql](https://github.com/sunli829/async-graphql) - 一個在Rust中實現的GraphQL服務器庫
  
## 應用程序

- [alacritty](https://github.com/alacritty/alacritty) — 跨平臺、GPU 增強的終端模擬器
- [AnderEnder/s3find-rs](https://github.com/AnderEnder/s3find-rs) — 用於遍歷 Amazon S3 層次結構的命令行實用程序，類似於 Amazon S3 的 find
- [andschwa/rust-genetic-algorithm](https://github.com/andschwa/rust-genetic-algorithm) — 一種用於學術基準問題的遺傳算法
- [asm-cli-rust](https://github.com/cch123/asm-cli-rust) — 一個用 Rust 編寫的交互式程序集外殼.
- [ballista](https://github.com/ballista-compute/ballista) — 使用 Rust、Apache Arrow 和 Kubernetes 的分佈式計算平臺的 PoC！
- [cloudflare/boringtun](https://github.com/cloudflare/boringtun) — 用戶空間 WireGuard VPN 實現
- [darrint/device-blocker](https://github.com/darrint/device-blocker) — 通過阻止家庭 Wifi 路由器上的互聯網訪問來限制兒童各種移動設備的屏幕時間.
- [denoland/deno](https://github.com/denoland/deno) — 使用 V8、Rust 和 Tokio 構建的安全 JavaScript/TypeScript 運行時
- [dlecan/generic-dns-update](https://github.com/dlecan/generic-dns-update) — 使用您的 IP 地址更新 DNS 區域文件的工具
- [Factotum](https://github.com/snowplow/factotum) — [A system to programmatically run data pipelines](https://snowplowanalytics.com/blog/2016/04/09/introducing-factotum-data-pipeline-runner/) 
- [fcsonline/drill](https://github.com/fcsonline/drill) — 受 Ansible 語法啟發的 HTTP 負載測試應用程序
- [Fractalide](https://github.com/fractalide/fractalide) — 簡單的 Rust 微服務
- [habitat](https://community.chef.io/tools/chef-habitat) — 一個工具 [Chef](https://www.chef.io/) 構建、部署和管理應用程序.
- [Herd](https://github.com/imjacobclark/Herd) — 一個實驗性的 HTTP 負載測試應用程序
- [intecture/api](https://github.com/intecture/api) — API 驅動的服務器管理和配置工具
- [ivanceras/diwata](https://github.com/ivanceras/diwata) — postgresql 的數據庫管理工具
- [jedisct1/flowgger](https://github.com/awslabs/flowgger) — 快速、簡單和輕量級的數據收集器
- [kbknapp/docli](https://github.com/kbknapp/docli-rs) — 用於管理 DigitalOcean 基礎設施的命令行實用程序 
- [kytan](https://github.com/changlan/kytan) — 高性能點對點 VPN
- [limonite](https://crates.io/crates/limonite) — 靜態博客 / 網站生成器 
- [linkerd/linkerd2-proxy](https://github.com/linkerd/linkerd2-proxy) — Kubernetes 的超輕服務網格.
- [MaidSafe](https://maidsafe.net/) — 一個去中心化的平臺.
- [mdBook](https://crates.io/crates/mdbook) — 從 Markdown 文件創建書籍的命令行實用程序 
- [nicohman/eidolon](https://github.com/nicohman/eidolon) — 適用於 linux 和 macosx 的無 Steam 和 drm 遊戲註冊表和啟動器
- [notty](https://github.com/withoutboats/notty) — 一種新型終端
- [Pijul](https://pijul.org/) — 基於補丁的分佈式版本控制系統
- [rsign](https://crates.io/crates/rsign) — 一個簡單的命令行工具，用於生成 / 簽署 / 驗證旨在與 Minisign 兼容的數字簽名 
- [Rudr](https://github.com/oam-dev/rudr) — Kubernetes 實現 [Open Application Model](https://oam.dev/) 規格
- [rx](https://github.com/cloudhead/rx) — 受 Vi 啟發的現代像素藝術編輯器
- [Sandstorm Collections App](https://github.com/sandstorm-io/collections-app)
- [Servo](https://github.com/servo/servo) — 原型 Web 瀏覽器引擎
- [tiny](https://github.com/osa1/tiny) — 終端 IRC 客戶端
- [trust-dns](https://crates.io/crates/trust-dns) — DNS 服務器
- [updns](https://github.com/wyhaya/updns) — DNS 代理工具
- [Weld](https://github.com/serayuzgur/weld) — 全假 REST API 生成器 
- [wezterm](https://github.com/wez/wezterm) — 一個gpu加速的跨平臺終端模擬器和多路複用器
  
### 音頻和音樂技術

- [enginesound](https://github.com/DasEtwas/enginesound) — 用於按程序生成半逼真引擎聲音的 GUI 和命令行應用程序. 具有深度配置、可變採樣率和頻率分析窗口.
- [indiscipline/zrtstr](https://github.com/indiscipline/zrtstr) — 用於檢查立體聲 wav 文件是否為仿立體聲（即具有相同通道）並將此類文件轉換為單聲道的命令行實用程序.
- [Lyriek](https://github.com/bartwillems/lyriek) — 一個多線程 GTK 3 應用程序，用於獲取當前播放歌曲的歌詞.
- [Phate6660/musinfo](https://github.com/Phate6660/musinfo) — 從 mpd 查詢音樂信息並將其顯示在通知中的程序.
- [Phate6660/rsmpc](https://github.com/Phate6660/rsmpc) — mpc 的實現，但不是直接實現，因為會有一些差異.
- [Phate6660/rsmpc](https://github.com/Phate6660/rsmpc-gui) — 用於 mpd 的 gtk 前端.
- [Polaris](https://github.com/agersant/polaris) — 音樂流媒體應用程序. 
- [Spotify TUI](https://github.com/Rigellute/spotify-tui) — 一個用 Rust 編寫的用於終端的 Spotify 客戶端. 
- [Spotifyd](https://github.com/Spotifyd/spotifyd) — 作為 UNIX 守護程序運行的開源 Spotify 客戶端. 
  
### 加密數字貨幣

- [Bitcoin Satoshi's Vision](https://github.com/brentongunning/rust-sv) — 用於處理比特幣 SV 的 Rust 庫.
- [cardano-cli](https://github.com/input-output-hk/cardano-cli) — 卡爾達諾命令行界面 (CLI)
- [ChainX](https://github.com/chainx-org/ChainX) — Polkadot 上完全去中心化的鏈間加密資產管理.
- [CITA](https://github.com/citahub/cita) — 面向企業用戶的高性能區塊鏈內核.
- [coinbase-pro-rs](https://github.com/inv2004/coinbase-pro-rs) — Rust 中的 Coinbase pro 客戶端，支持同步 / 異步 / websocket 
- [ethaddrgen](https://github.com/Limeth/ethaddrgen) — 用 Rust 製作的自定義以太坊虛地址生成器 
- [Grin](https://github.com/mimblewimble/grin/) — MimbleWimble 協議的演變
- [hdwallet](https://github.com/jjyr/hdwallet) — BIP-32 HD 錢包相關的密鑰推導實用程序.
- [Holochain](https://github.com/holochain/holochain) — 區塊鏈的可擴展 P2P 替代方案，適用於您一直想要構建的所有分佈式應用程序. 舊倉庫的鏈接是 [this](https://github.com/holochain/holochain-rust) 不再維護.[ibc-rs](https://github.com/informalsystems/ibc-rs) - Rust 的實現 [Interblockchain Communication](https://xn--ibc-3h3e109w.org/) 協議
- [infincia/bip39-rs](https://github.com/infincia/bip39-rs) — BIP39 的 Rust 實現.
- [Joystream](https://github.com/Joystream/joystream) — 一個用戶管理的視頻平臺 
- [Diem](https://github.com/diem/diem) — Diem 的使命是建立一個簡單的全球貨幣和金融基礎設施，為數十億人賦能.
- [Lighthouse](https://github.com/sigp/lighthouse) — Rust Ethereum 2.0 客戶端
- [near/nearcore](https://github.com/near/nearcore) — 用於低端移動設備的去中心化智能合約平臺.
- [Nervos CKB](https://github.com/nervosnetwork/ckb) — Nervos CKB 是一個公共的免許可區塊鏈，是 Nervos 網絡的公共知識層.
- [Nimiq](https://github.com/nimiq/core-rs) — Nimiq 節點的 Rust 實現
- [Parity-Bitcoin](https://github.com/paritytech/parity-bitcoin) — Parity 比特幣客戶端
- [Parity-Bridge](https://github.com/paritytech/parity-bridge) — 任何兩個基於以太坊的網絡之間的橋樑
- [Parity-Ethereum](https://github.com/openethereum/openethereum) — 快速、輕便、強大的以太坊客戶端
- [Parity-Zcash](https://github.com/paritytech/parity-zcash) — Zcash 協議的 Rust 實現
- [Phala-Network/phala-blockchain](https://github.com/Phala-Network/phala-blockchain) — 基於 Intel SGX 和 Substrate 的機密智能合約區塊鏈
- [Polkadot](https://github.com/paritytech/polkadot) — 具有集中安全性的異構多鏈技術
- [rbtc](https://github.com/lucawen/rbtc) — 將 BTC 轉換為任何貨幣，反之亦然. 
- [rust-cardano](https://github.com/input-output-hk/rust-cardano) — Cardano 原語、助手和相關應用程序的 Rust 實現
- [Substrate](https://github.com/paritytech/substrate) — 用 Rust 編寫的通用模塊化區塊鏈模板
- [tendermint-rs](https://github.com/informalsystems/tendermint-rs) - Tendermint 區塊鏈數據結構和客戶端的 Rust 實現
- [wagyu](https://github.com/AleoHQ/wagyu) [[wagyu](https://crates.io/crates/wagyu)] — 用於生成加密貨幣錢包的 Rust 庫
- [zcash](https://github.com/zcash/zcash) — Zcash 是 “Zerocash” 協議的實現.
- [YeeCo yeeroot](https://github.com/yeeco/yeeroot) — YeeCo yeeroot 是一個無需許可、安全、高性能和可擴展的公共區塊鏈平臺，由基於 Rust 編寫的 PoW 共識的全分片技術提供支持
  
### 數據庫

- [indradb](https://crates.io/crates/indradb) — 基於 Rust 的圖形數據庫 
- [Materialize](https://github.com/MaterializeInc/materialize) - 由 Timely Dataflow 提供支持的流式 SQL 數據庫：heavy_dollar_sign
- [noria](https://crates.io/crates/noria) — 用於 Web 應用程序後端的動態變化、部分狀態的數據流
- [Lucid](https://github.com/lucid-kv/lucid) — High performance and distributed KV store accessible through a HTTP API.
- [ParityDB](https://github.com/paritytech/parity-db) — 快速可靠的數據庫，針對讀操作進行了優化
- [PumpkinDB](https://github.com/PumpkinDB/PumpkinDB) — 事件溯源數據庫引擎 
- [seppo0010/rsedis](https://github.com/seppo0010/rsedis) — Rust 中的 Redis 重新實現 
- [Skytable](https://github.com/skytable/skytable) — 多模型 NoSQL 數據庫 
- [tikv](https://github.com/tikv/tikv) — Rust 中的分佈式 KV 數據庫 
- [sled](https://crates.io/crates/sled) —（測試版）現代嵌入式數據庫
- [TerminusDB](https://github.com/terminusdb/terminusdb-store) - 開源圖形數據庫和文檔存儲
  
### 模擬器

- [kondrak/rust64](https://github.com/kondrak/rust64) 
- [Ruffle](https://github.com/ruffle-rs/ruffle) — Ruffle 是用 Rust 編程語言編寫的 Adobe Flash Player 模擬器. Ruffle 使用 WebAssembly 面向桌面和 Web.
- [Gekkio/mooneye-gb](https://github.com/Gekkio/mooneye-gb) 
- [mvdnes/rboy](https://github.com/mvdnes/rboy)
- [NivenT/RGB](https://github.com/nivent/RGB) 
- [mohanson/gameboy](https://github.com/mohanson/gameboy) — 全功能跨平臺 GameBoy 模擬器. 永遠的男孩！
- [michelhe/rustboyadvance-ng](https://github.com/michelhe/rustboyadvance-ng) - RustboyAdvance-ng 是一款 Gameboy Advance 模擬器，具有桌面、安卓和 [WebAssembly](https://michelhe.github.io/rustboyadvance-ng/) 支持.
- [iamsix/oxidenes](https://github.com/iamsix/oxidenes)
- [koute/pinky](https://github.com/koute/pinky) 
- [pcwalton/sprocketnes](https://github.com/pcwalton/sprocketnes)
- [Amjad50/plastic](https://github.com/Amjad50/plastic) — plastis 是一個用 Rust 構建的全功能 NES 模擬器.
- [rustation-ng](https://gitlab.com/flio/rustation-ng/) — 使用 Rust 的 Playstation 模擬器
- [pacmancoder/rustzx](https://github.com/pacmancoder/rustzx) 
- [rodrigorc/raze](https://github.com/rodrigorc/raze) — 對於 WebAssembly， [live version here](https://rodrigorc.github.io/raze/) * 虛擬男孩
- [emu-rs/rustual-boy](https://github.com/emu-rs/rustual-boy) 
- [mohanson/i8080](https://github.com/mohanson/i8080) — Rust 的 Intel 8080 cpu 模擬器 
  
### 遊戲

- [lifthrasiir/angolmois-rust](https://github.com/lifthrasiir/angolmois-rust) — 一款支持 BMS 格式的極簡音樂視頻遊戲
- [citybound](https://github.com/citybound/citybound) - 你應得的城市模擬
- [schulke-214/connect-four](https://github.com/schulke-214/connect-four) — 一個簡單的連接四個實現.
- [doukutsu-rs](https://github.com/doukutsu-rs/doukutsu-rs) — 對 Cave Story 引擎的 Rust 重新實現，並進行了一些增強.
- [rsaarelm/magog](https://github.com/rsaarelm/magog) — Rust 中的 roguelike 遊戲
- [schulke-214/rsnake](https://github.com/schulke-214/rsnake) — 用 Rust 編寫的 Snake.
- [soydos](https://github.com/soydos/pusoy_dos2) — Pusoy Dos 的 wasm 實現
- [cristicbz/rust-doom](https://github.com/cristicbz/rust-doom) — Doom 的渲染器，可能會發展成為一款可玩的遊戲 
- [Thinkofname/rust-quake](https://github.com/Thinkofname/rust-quake) — Rust 中的地震地圖渲染器
- [rhex](https://github.com/dpc/rhex) — 六邊形 ascii roguelike
- [garkimasera/rusted-ruins](https://github.com/garkimasera/rusted-ruins) - 具有像素藝術的可擴展開放世界流氓遊戲
- [Veloren](https://gitlab.com/veloren/veloren) — 一個開放世界、開源的多人體素 RPG 遊戲，目前處於 alpha 開發階段
- [swatteau/sokoban-rs](https://github.com/swatteau/sokoban-rs) — 推箱子實現
- [aleshaleksey/TGWM](https://github.com/aleshaleksey/TGWM) — 具有回合制機制的 RPG（正在進行中）
- [ozkriff/zemeroth](https://github.com/ozkriff/zemeroth) — 一款小型 2D 回合制六角策略遊戲
- [Zone of Control](https://github.com/ozkriff/zoc) — 回合制六角策略遊戲 
- [phantomion/snake_game](https://github.com/phantomion/snake_game) - 用 Rust 編寫的簡單終端蛇遊戲.

### 圖形處理

- [Limeth/euclider](https://github.com/Limeth/euclider) — 實時 4D CPU 光線追蹤器
- [RazrFalcon/resvg](https://github.com/RazrFalcon/resvg) — 一個 SVG 渲染庫.
- [ivanceras/svgbob](https://github.com/ivanceras/svgbob) — 將 ASCII 圖轉換為 SVG 圖形 
- [RazrFalcon/svgcleaner](https://github.com/RazrFalcon/svgcleaner) — 整理 SVG 圖形
- [Twinklebear/tray_rust](https://github.com/Twinklebear/tray_rust) — 光線追蹤器
- [turnage/valora](https://crates.io/crates/valora) — 生成美術圖書館 
- [mikigraf/Image-Processing-CLI-in-Rust](https://github.com/mikigraf/Image-Processing-CLI-in-Rust) — 用於處理圖像、生成直方圖的 CLI. 

### 工業自動化

- [locka99/opcua](https://github.com/locka99/opcua) —  [OPC UA](https://opcfoundation.org/about/opc-technologies/opc-ua/) 圖書館.
- [slowtec/tokio-modbus](https://github.com/slowtec/tokio-modbus) - 一種 [tokio](https://tokio.rs/)-based [modbus](https://modbus.org/) 圖書館. 
- [BiancoRoyal/modbus-iiot-rust](https://github.com/BiancoRoyal/modbus-iiot-rust) — 純鏽 [modbus](https://modbus.org/) 沒有或更少依賴的庫.
  
### 可觀察性工具

- [timberio/vector](https://github.com/timberio/vector) — 高性能、日誌、指標和事件路由器.
- [Mnwa/gtsa](https://github.com/Mnwa/gtsa) — 將 gelf 消息（Graylog 的消息）代理到 Sentry 的簡單解決方案
- [OpenTelemetry](https://crates.io/crates/opentelemetry) — OpenTelemetry 提供一組 API、庫、代理和收集器服務，以從您的應用程序中捕獲分佈式跟蹤和指標. 您可以使用 Prometheus、Jaeger 和其他可觀察性工具分析它們.

### 操作系統

- [nebulet/nebulet](https://github.com/nebulet/nebulet) — 實現在 Ring 0 中運行的 WebAssembly“用戶模式” 的微內核.
- [redox-os/redox](https://gitlab.redox-os.org/redox-os/redox) 
- [thepowersgang/rust_os](https://github.com/thepowersgang/rust_os)
- [tock/tock](https://github.com/tock/tock) — 適用於基於 Cortex-M 的微控制器的安全嵌入式操作系統

### 生產能力

- [espanso](https://github.com/federico-terzi/espanso) — 一個用 Rust 編寫的跨平臺文本擴展器 [eureka](https://crates.io/crates/eureka) — 無需離開終端即可輸入和存儲您的想法的 CLI 工具
- [pier-cli/pier](https://github.com/pier-cli/pier) — 用於管理（添加、搜索元數據等）所有單行程序、腳本、工具和 CLI 的中央存儲庫
- [subilo](https://github.com/Bansco/subilo) - 持續部署代理

### 安全工具

- [kpcyrd/authoscope](https://github.com/kpcyrd/authoscope) — 一個可編寫腳本的網絡認證破解器
- [lethe](https://github.com/kostassoid/lethe) — 安全的跨平臺驅動器擦除實用程序 
- [arvancloud/libinjection-rs](https://github.com/arvancloud/libinjection-rs) — Rust 綁定 [libinjection](https://github.com/client9/libinjection)
- [ripasso](https://github.com/cortex/ripasso/) — 密碼管理器，與 pass 兼容的文件系統
- [kpcyrd/rshijack](https://github.com/kpcyrd/rshijack) — 一個 TCP 連接劫持者，對 shijack 進行 Rust 重寫 
- [rustscan/rustscan](https://github.com/RustScan/RustScan) — 使用此端口掃描工具使 Nmap 更快
- [kpcyrd/sniffglue](https://github.com/kpcyrd/sniffglue) — 一個安全的多線程數據包嗅探器
- [kpcyrd/sn0int](https://github.com/kpcyrd/sn0int) — 半自動 OSINT 框架和包管理器   

### 系統工具

- [ajeetdsouza/zoxide](https://github.com/ajeetdsouza/zoxide/) — 一種快速替代 `cd` 的方法，可以學習你的習慣
- [bandwhich](https://github.com/imsnif/bandwhich) — 終端帶寬利用工具
- [brocode/fblog](https://github.com/brocode/fblog) — 小型命令行 JSON 日誌查看器 
- [buster/rrun](https://github.com/buster/rrun) — Linux 的命令啟動器，類似於 gmrun
- [cristianoliveira/funzzy](https://github.com/cristianoliveira/funzzy) — 受啟發的可配置文件系統觀察器 [entr](http://eradman.com/entrproject/) 
- [dalance/procs](https://github.com/dalance/procs) — Rust 編寫的 “ps” 的現代替代品
- [diskonaut](https://github.com/imsnif/diskonaut) — 終端可視化磁盤空間導航器
- [dust](https://github.com/bootandy/dust) — 更直觀的 du 版本
- [ddh](https://github.com/darakian/ddh) — 快速重複文件查找器
- [fselect](https://crates.io/crates/fselect) — 使用類似 SQL 的查詢查找文件 
- [gitui](https://github.com/extrawurst/gitui) - 用 Rust 編寫的 git 快速終端客戶端.
- [k0pernicus/zou](https://github.com/k0pernicus/zou) — 下載加速器
- [Kondo](https://github.com/tbillington/kondo) - 用於刪除軟件項目工件和回收磁盤空間的 CLI 和 GUI 工具
- [lotabout/rargs](https://github.com/lotabout/rargs) [[rargs](https://crates.io/crates/rargs)] — 支持模式匹配的 xargs + awk
- [lotabout/skim](https://github.com/lotabout/skim) — 純鏽的模糊取景器
- [mitnk/cicada](https://github.com/mitnk/cicada) — 一個類似 bash 的 Unix shell
- [mmstick/concurr](https://github.com/mmstick/concurr) — 帶有客戶端 - 服務器架構的 GNU Parallel 的替代方案
- [mmstick/fontfinder](https://github.com/mmstick/fontfinder) — 用於預覽和安裝 Google 字體的 GTK3 應用程序
- [mmstick/parallel](https://github.com/mmstick/parallel) — 重新實現 GNU Parallel
- [mmstick/tv-renamer](https://github.com/mmstick/tv-renamer) — 帶有可選 GTK3 前端的電視劇重命名應用程序. 
- [nushell/nushell](https://github.com/nushell/nushell) — 一個新型Shell. 
- [organize-rt](https://gitlab.com/FixFromDarkness/organize-rt) — 根據正則表達式規則組織文件（默認為文件擴展名）.
- [orhun/kmon](https://github.com/orhun/kmon) — Linux 內核管理器和活動監視器 
- [Peltoche/lsd](https://github.com/Peltoche/lsd) — 一個 ls 有很多漂亮的顏色和很棒的圖標 
- [ogham/exa](https://github.com/ogham/exa) — 'ls' 的替代品 
- [pop-os/debrep](https://github.com/pop-os/debrepbuild) — 用於構建和管理 APT 存儲庫的 APT 存儲庫工具
- [pop-os/popsicle](https://github.com/pop-os/popsicle) — GTK3 和 CLI 實用程序，用於並行刷新多個 USB 設備
- [pueue](https://github.com/nukesor/pueue) — 管理您長時間運行的 shell 命令.
- [Luminarys/synapse](https://github.com/Luminarys/synapse) — 靈活且快速的 BitTorrent 守護進程. 
- [pop-os/system76-power](https://github.com/pop-os/system76-power/) — 帶有 CLI 工具的 Linux 電源管理守護進程（DBus 接口）.
- [mxseev/logram](https://github.com/mxseev/logram) — 將日誌文件的更新推送到 Telegram
- [redox-os/ion](https://github.com/redox-os/ion) — 下一代系統外殼 
- [jamesbirtles/hotkey-rs](https://github.com/jamesbirtles/hotkey-rs) — 在 Rust 中收聽全局熱鍵的庫
- [nivekuil/rip](https://github.com/nivekuil/rip) - 一種安全且符合人體工程學的替代`rm` 
- [sharkdp/bat](https://github.com/sharkdp/bat) — 有翅膀的 cat(1) 克隆體. 
- [sharkdp/fd](https://github.com/sharkdp/fd) — 一種簡單、快速且用戶友好的查找替代方案.
- [sitkevij/hex](https://github.com/sitkevij/hex) — 彩色的 hexdump 終端實用程序.
- [slai11/goto](https://github.com/slai11/goto) — 跳轉到索引目錄的簡單且用戶友好的方式.
- [m4b/bingrep](https://github.com/m4b/bingrep) — 通過來自各種操作系統和體系結構的二進制文件進行 Greps，併為它們著色. 
- [uutils/coreutils](https://github.com/uutils/coreutils) — GNU coreutils 的跨平臺 Rust 重寫
- [watchexec](https://github.com/watchexec/watchexec) — 執行命令以響應文件修改 
- [XAMPPRocky/tokei](https://github.com/XAMPPRocky/tokei) — 計算代碼行數 
- [yake](https://crates.io/crates/yake) — Yake 是一個基於 yaml 文件的任務運行器
- [ytop](https://github.com/cjbassi/ytop) - 一個用 Rust 編寫的 TUI 系統監視器 
- [cocom](https://github.com/LamdaLamdaLamda/cocom) - 純粹用 Rust 編寫的 NTP 客戶端. 

### 文字編輯器

- [amp](https://amp.rs/) — 受 Vi/Vim 的啟發. 
- [gchp/iota](https://github.com/gchp/iota) — 一個簡單的文本編輯器
- [ilai-deutel/kibi](https://github.com/ilai-deutel/kibi) — 具有語法高亮、增量搜索等功能的小型 (≤1024 LOC) 文本編輯器.
- [vamolessa/pepper](https://github.com/vamolessa/pepper) [[pepper](https://crates.io/crates/pepper)] — 一個自以為是的模式編輯器，可簡化從終端進行的代碼編輯
- [mathall/rim](https://github.com/mathall/rim) — 用 Rust 編寫的類似 Vim 的文本編輯器
- [ox](https://github.com/curlpipe/ox) — 在終端中運行的獨立 Rust 文本編輯器！
- [Remacs](https://github.com/remacs/remacs) — 社區驅動的 Emacs 到 Rust 的移植.
- [xi-editor](https://github.com/xi-editor/xi-editor) — 一個現代編輯器，後端是用 Rust 編寫的.
- [xray](https://github.com/atom-archive/xray) — 實驗性的下一代基於電子的文本編輯器. 

### 文本處理

- [cpc](https://github.com/probablykasper/cpc) - 解析和計算數學字符串，支持單位和單位轉換，從 “1+2” 到“1% 的回合（1 光年 / 14!s 到公里 / 小時）”.
- [grex](https://github.com/pemistahl/grex) — 用於從用戶提供的測試用例生成正則表達式的命令行工具和庫
- [dmerejkowsky/ruplacer](https://github.com/dmerejkowsky/ruplacer) — 在源文件中查找和替換文本
- [ripgrep](https://crates.io/crates/ripgrep) — 結合了 Silver Searcher 的可用性和 grep 的原始速度
- [phiresky/ripgrep-all](https://github.com/phiresky/ripgrep-all) — ripgrep，還可以搜索 PDF、電子書、Office 文檔、zip、tar.gz 等.
- [replicadse/complate](https://github.com/replicadse/complate) — 一種終端內文本模板工具，用於標準化消息（如 GIT 提交）. 
- [sd](https://crates.io/crates/sd) — 直觀的查找和替換 CLI
- [lavifb/todo_r](https://github.com/lavifb/todo_r) — 用一個命令查找所有 TODO 筆記！ 
- [whitfin/runiq](https://github.com/whitfin/runiq) — 從未排序的輸入中過濾重複行的有效方法.
- [whitfin/bytelines](https://github.com/whitfin/bytelines) — 將輸入行讀取為字節片以提高效率.
- [vishaltelangre/ff](https://github.com/vishaltelangre/ff) — 按名稱查找文件 (ff)！ 
- [xsv](https://crates.io/crates/xsv) — 一個快速的 CSV 命令行工具（切片、索引、選擇、搜索、採樣等）
- [Lisprez/so_stupid_search](https://github.com/Lisprez/so_stupid_search) — 一個簡單快速的人類字符串搜索工具

### 圖像處理

- [Imager](https://github.com/imager-io/imager) — 自動圖像優化.

### 實用工具

- [aleshaleksey/AZDice](https://github.com/aleshaleksey/AZDice) — 桌面家庭釀酒商的骰子成功分發生成器. 
- [yaa110/cb](https://github.com/yaa110/cb) — 管理剪貼板的命令行界面 
- [brycx/checkpwn](https://github.com/brycx/checkpwn) — 一個 Have I Being Pwned (HIBP) 命令行實用工具，可讓您輕鬆檢查被盜用的帳戶和密碼.
- [vamolessa/copycat](https://github.com/vamolessa/copycat) [[copycat](https://crates.io/crates/copycat)] — 一個簡單的剪貼板 cli 界面，適用於具有文本和 bmp 支持的窗口
- [evansmurithi/cloak](https://github.com/evansmurithi/cloak) — 命令行 OTP（一次性密碼）身份驗證器應用程序. 
- [replydev/cotp](https://github.com/replydev/cotp) - 與外部備份兼容的值得信賴的加密一次性密碼驗證器應用程序. 
- [rustdesk/rustdesk](https://github.com/rustdesk/rustdesk) - 遠程桌面應用程序. 
- [arthrp/consoletimer](https://github.com/arthrp/consoleTimer) — 終端的簡單計時器.
- [tversteeg/emplace](https://github.com/tversteeg/emplace) — 在多臺機器上同步已安裝的包
- [unrelentingtech/freepass](https://github.com/unrelentingtech/freepass) — 高級用戶的免費密碼管理器.
- [yoannfleurydev/gitweb](https://github.com/yoannfleurydev/gitweb) — 在瀏覽器中打開當前遠程存儲庫.
- [mme](https://github.com/GoberInfinity/mme) — 命令行工具來記住您有時忘記的命令. 
- [raftario/licensor](https://github.com/raftario/licensor) — 將許可證寫入標準輸出
- [arthrp/quick-skeleton](https://github.com/arthrp/quick-skeleton) — 項目腳手架工具，類似於 Yeoman 和 Slush. 
- [repoch](https://github.com/lucawen/repoch) — 將紀元轉換為日期時間，將日期時間轉換為紀元 
- [whitfin/s3-concat](https://github.com/whitfin/s3-concat) — 使用靈活模式遠程連接 Amazon S3 文件的命令行工具.
- [whitfin/s3-meta](https://github.com/whitfin/s3-meta) — 用於收集有關 Amazon S3 存儲桶的元數據的命令行工具.
- [whitfin/s3-utils](https://github.com/whitfin/s3-utils) — 一個包含基於 Amazon S3 的實用程序的小工具，可提供額外的便利 API.
- [gorros/s3-edit-rs](https://github.com/gorros/s3-edit-rs) — 直接在 Amazon S3 上編輯文件的命令行工具.
- [fcsonline/tmux-thumbs](https://github.com/fcsonline/tmux-thumbs) — 用 Rust 編寫的 tmux-finger 的閃電般快速版本，像 vimium/vimperator 一樣複製 / 粘貼 tmux.
- [amar-laksh/workstation](https://github.com/amar-laksh/workstation) — 一個命令行工具，可幫助您管理工作站，讓您遠離屏幕、在您不在時鎖定屏幕以及使用 OPENCV 進行其他操作！
- [guoxbin/dtool](https://github.com/guoxbin/dtool) — 一個有用的命令行工具集合，用於協助開發，包括轉換、編解碼器、散列、加密等.
- [nomino](https://github.com/yaa110/nomino) — 開發人員批量重命名實用程序 
- [barberousse](https://github.com/zeapo/barberousse) — AWS Secrets Manager 編輯器 
- [vamolessa/verco](https://github.com/vamolessa/verco) [[verco](https://crates.io/crates/verco)] — 一個簡單的 Git/Hg tui 客戶端，專注於鍵盤快捷鍵
  
### 視頻

- [Phate6660/rsmpv](https://github.com/Phate6660/rsmpv) — MPV 控制器，需要在 MPV 中啟用 IPC.
- [tgotwig/vidmerger](https://github.com/tgotwig/vidmerger) — ffmpeg 的包裝器，可簡化多個視頻的合併
- [xiph/rav1e](https://github.com/xiph/rav1e) — 最快、最安全的 AV1 編碼器.
- [yuvadm/slingr](https://github.com/yuvadm/slingr) — 一個簡單的 CLI，用於通過本地網絡將媒體文件流式傳輸到 UPnP 媒體渲染器
- [yuvadm/streamlib](https://github.com/streamlib/streamlib) — 從命令行播放您最喜歡的實時視頻和音頻流

### 虛擬化技術

- [firecracker-microvm/firecracker](https://github.com/firecracker-microvm/firecracker) — 用於容器工作負載的輕量級虛擬機 [Firecracker Microvm](https://firecracker-microvm.github.io/)
- [oracle/railcar](https://github.com/oracle/railcar) — Rust 中類似 Docker 的容器 OCI 運行時實現
- [tailhook/vagga](https://github.com/tailhook/vagga) — 一個沒有守護進程的容器化工具

### Web

- [Plume-org/Plume](https://github.com/Plume-org/Plume) — ActivityPub 聯合博客應用程序
- [LemmyNet/lemmy](https://github.com/LemmyNet/lemmy) — 聯邦宇宙的鏈接聚合器 / reddit 克隆

### Web Servers

- [mufeedvh/binserve](https://github.com/mufeedvh/binserve) — 極快的靜態 Web 服務器，在單個二進制文件中具有路由、模板和安全性，您可以使用零代碼進行設置 
- [thecoshman/http](https://github.com/thecoshman/http) — 請託管這些東西 — 一個基本的 http 服務器，用於快速簡單地託管文件夾 
- [svenstaro/miniserve](https://github.com/svenstaro/miniserve) — 一個小型的、自包含的跨平臺 CLI 工具，允許您只獲取二進制文件並通過 HTTP 提供一些文件
- [TheWaWaR/simple-http-server](https://github.com/TheWaWaR/simple-http-server) — 簡單的靜態 http 服務器
- [wyhaya/see](https://github.com/wyhaya/see) — 靜態 HTTP 文件服務器
- [ronanyeah/rust-hasura](https://github.com/ronanyeah/rust-hasura) — Rust GraphQL 服務器如何用作遠程模式的演示 [Hasura](https://hasura.io/) 
  
## 開發工具
  
- [clippy](https://crates.io/crates/clippy)
- [clog-tool/clog-cli](https://github.com/clog-tool/clog-cli) — 從 git 元數據生成變更日誌 ([conventional changelog](https://blog.thoughtram.io/announcements/tools/2014/09/18/announcing-clog-a-conventional-changelog-generator-for-the-rest-of-us.html)) 
- [dan-t/rusty-tags](https://github.com/dan-t/rusty-tags) — 為貨物項目及其所有依賴項創建 ctags/etags 
- [datanymizer/datanymizer](https://github.com/datanymizer/datanymizer) - 強大的數據庫匿名器，具有靈活的規則
- [delta](https://crates.io/crates/git-delta) — git 和 diff 輸出的語法高亮器
- [dotenv-linter](https://github.com/dotenv-linter/dotenv-linter) — 用於 `.env` 文件的 Linter[frewsxcv/crate-deps](https://github.com/frewsxcv/crate-deps) — 為 crates.io 上託管的 crate 生成依賴圖的圖像
- [geiger](https://github.com/rust-secure-code/cargo-geiger) — 一個程序，列出與在 Rust crate 及其所有依賴項中使用不安全 Rust 代碼相關的統計信息m/cargo-geiger/cargo-geiger/_build/latest?definitionId=1&branchName=master)
- [git-journal](https://github.com/saschagrunert/git-journal/) — Git 提交消息和變更日誌生成框架 
- [gstats](https://github.com/boonshift/gstats/) — 用於打印當前目錄下所有 git 存儲庫的開發人員方便摘要的命令行工具
- [rust-lang/rustfix](https://github.com/rust-lang/rustfix) — 自動應用 rustc 提出的建議
- [just](https://github.com/casey/just) — 用於特定項目任務的便捷命令運行器
- [mask](https://github.com/jakedeichert/mask) — 由一個簡單的 Markdown 文件定義的 CLI 任務運行器
- [Module Linker](https://github.com/fiatjaf/module-linker) —在 GitHub 的 `mod`、`use` 和 `extern crate` 語句中添加 `<a>` 鏈接到引用的擴展.
- [ptags](https://github.com/dalance/ptags) — git 存儲庫的並行通用 ctags 包裝器 
- [Racer](https://github.com/racer-rust/racer) — Rust 的代碼完成 
- [rustfmt](https://github.com/rust-lang/rustfmt) — Rust 代碼格式化程序
- [Rustup](https://github.com/rust-lang/rustup) — Rust 工具鏈安裝程序 
- [Rust Language Server](https://github.com/rust-lang/rls) — 在後臺運行的服務器，為 IDE、編輯器和其他工具提供有關 Rust 程序的信息
- [Rust Regex Playground](https://2fd.github.io/rust-regex-playground/#method=find&regex=\w%2B&text=abc) — 評估 Rust 正則表達式的 Web 工具
- [Rust Search Extension](https://github.com/huhu/rust-search-extension) — 一個方便的瀏覽器擴展，用於在地址欄（多功能框）中搜索 crate 和文檔. 
- [artifact](https://github.com/vitiral/artifact) — 為開發人員製作的設計文檔工具 
- [semantic-rs](https://github.com/semantic-rs/semantic-rs) — 自動 crate 發佈
- [fw](https://github.com/brocode/fw) — 工作空間生產力助推器 
- [tinyrick](https://github.com/mcandre/tinyrick) 一個基本的任務依賴工具，強調 Rust 功能而不是原始 shell 命令.
- [scriptisto](https://github.com/igor-petruk/scriptisto) 一種與語言無關的 “shebang 解釋器”，它使您能夠用編譯語言編寫一個文件腳本.
 
### 系統編譯

- [Cargo](https://crates.io/) — Rust 包管理器
- [cargo-benchcmp](https://crates.io/crates/cargo-benchcmp) — 比較 Rust 微基準的實用程序 
- [cargo-bitbake](https://crates.io/crates/cargo-bitbake) — 一個貨物擴展，可以利用 meta-rust 中的類生成 BitBake 配方
- [cargo-cache](https://crates.io/crates/cargo-cache) - 檢查 / 管理 / 清理你的貨物緩存（`~/.cargo/`/`${CARGO_HOME}`），打印尺寸等
- [cargo-check](https://crates.io/crates/cargo-check) — `cargo rustc -- -Zno-trans` 的包裝器，如果您只需要正確性檢查，它可以幫助運行更快的編譯
- [cargo-count](https://crates.io/crates/cargo-count) — 列出有關貨物項目的源代碼計數和詳細信息，包括不安全統計數據
- [cargo-deb](https://crates.io/crates/cargo-deb) — 生成二進制 Debian 軟件包
- [cargo-deps](https://crates.io/crates/cargo-deps) — 構建 Rust 項目的依賴圖
- [cargo-do](https://crates.io/crates/cargo-do) — 連續運行多個貨物命令 
- [cargo-ebuild](https://crates.io/crates/cargo-ebuild) — 可以使用樹內 eclasses 生成 ebuild 的貨物擴展
- [cargo-edit](https://crates.io/crates/cargo-edit) — 允許您通過從命令行讀取 / 寫入 Cargo.toml 文件來添加和列出依賴項
- [cargo-generate](https://github.com/cargo-generate/cargo-generate) 通過利用預先存在的 git 存儲庫作為模板來生成 Rust 項目.
- [cargo-get](https://crates.io/crates/cargo-get) - Cargo 插件可以輕鬆地從 Cargo.toml 文件中查詢信息 
- [cargo-graph](https://crates.io/crates/cargo-graph) — 更新了具有附加功能的 `cargo-dot` 分支. 未維護，請參閱`cargo-deps` 
- [cargo-info](https://crates.io/crates/cargo-info) — 從命令行查詢 crates.io 以獲取 crates 詳細信息 
- [cargo-license](https://crates.io/crates/cargo-license) — 一個貨物子命令，用於快速查看所有依賴項的許可證.
- [cargo-make](https://crates.io/crates/cargo-make) — Rust 任務運行器和構建工具. 
- [cargo-modules](https://crates.io/crates/cargo-modules) — 一個貨物插件，用於顯示板條箱模塊的樹狀概覽. 
- [cargo-multi](https://crates.io/crates/cargo-multi) — 在多個板條箱上運行指定的貨物命令
- [cargo-outdated](https://crates.io/crates/cargo-outdated) — 在新版本的 Rust 依賴項可用或過時時顯示
- [cargo-release](https://crates.io/crates/cargo-release) — 用於發佈 git 管理的貨物項目、構建、標記、發佈、文檔和推送的工具 
- [cargo-script](https://crates.io/crates/cargo-script) — 讓人們快速、輕鬆地運行 Rust “腳本”，它可以利用 Cargo 的包生態系統
- [cargo-testify](https://crates.io/crates/cargo-testify) — 監視文件更改、運行測試並通過友好的操作系統通知通知結果
- [cargo-tree](https://github.com/sfackler/cargo-tree) – Cargo 子命令，以樹狀格式可視化 crate 的依賴關係圖
- [cargo-update](https://crates.io/crates/cargo-update) — 用於檢查和應用更新已安裝的可執行文件的貨物子命令 
- [cargo-watch](https://crates.io/crates/cargo-watch) — 貨物在源更改時編譯項目的實用程序
- [liuchong/cargo-x](https://github.com/liuchong/cargo-x) ——一個非常簡單的第三方 cargo 子命令來執行自定義命令
- [dtolnay/cargo-expand](https://github.com/dtolnay/cargo-expand) — 擴展源代碼中的宏
- [Devolutions/CMakeRust](https://github.com/Devolutions/CMakeRust) — 用於將 Rust 庫集成到 CMake 項目中
- [SiegeLord/RustCMake](https://github.com/SiegeLord/RustCMake) — 一個示例項目，展示了 CMake 與 Rust 的使用 
- [icepuma/rust-action](https://github.com/icepuma/rust-action) ——Rust github 動作
- [peaceiris/actions-mdbook](https://github.com/peaceiris/actions-mdbook) — mdBook 的 GitHub 操作
- GitHub 網絡鉤子
- [snare](https://tratt.net/laurie/src/snare/) — GitHub webhooks 運行器守護進程
- 網絡包
- [mxseev/rust-loader](https://github.com/mxseev/rust-loader) — Webpack Rust 加載器 (wasm)

### 調試

- [rust-gdb](https://github.com/rust-lang/rust/blob/master/src/etc/rust-gdb)
- [gdbgui](https://github.com/cs01/gdbgui) — 基於瀏覽器的 gdb 前端，用於調試 C、C++、Rust 和 Go.
- [lldb_batchmode.py](https://github.com/rust-lang/rust/blob/master/src/etc/lldb_batchmode.py) — 允許以類似於 GDB 的批處理模式的方式使用 LLDB.
- [CodeLLDB](https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb) — 一個 LLDB 擴展 [Visual Studio Code](https://code.visualstudio.com/).

### 部署

- [emk/rust-musl-builder](https://github.com/emk/rust-musl-builder) — 用於使用 musl-libc 和 musl-gcc 編譯靜態 Rust 二進制文件的 Docker 映像，以及有用的 C 庫的靜態版本
- [kpcyrd/mini-docker-rust](https://github.com/kpcyrd/mini-docker-rust) — 一個非常小的 Rust docker 鏡像的示例項目 
- [liuchong/docker-rustup](https://github.com/liuchong/docker-rustup) — 多版本（使用 musl 工具）Rust Docker 鏡像
- [messense/rust-musl-cross](https://github.com/messense/rust-musl-cross) — 使用 musl-cross 編譯靜態 Rust 二進制文件的 Docker 鏡像 
- [rust-lang-nursery/docker-rust](https://github.com/rust-lang/docker-rust) — 官方 Rust Docker 鏡像
- [wasm-template-rust](https://github.com/sn99/wasm-template-rust) — Rust 發佈到 gh-pages 的 wasm 模板，無需 npm-deploy 
- [DenisKolodin/rust-app-engine](https://github.com/DenisKolodin/rust-app-engine) — App Engine Rust 樣板
- [emk/heroku-buildpack-rust](https://github.com/emk/heroku-buildpack-rust) — Heroku 上的 Rust 應用程序構建包

### 嵌入式

- [japaric/rust-cross](https://github.com/japaric/rust-cross) ——關於交叉編譯 Rust 程序你需要知道的一切
- [japaric/xargo](https://github.com/japaric/xargo) — 輕鬆地將 Rust 程序交叉編譯到自定義的裸機目標，如 ARM Cortex-M
- [Ogeon/rust-on-raspberry-pi](https://github.com/Ogeon/rust-on-raspberry-pi) — 有關如何為 Raspberry Pi 交叉編譯 Rust 項目的說明. * 阿杜諾
- [avr-rust/ruduino](https://github.com/avr-rust/ruduino) `t Arduino Uno 的可重用組件.

### FFI

也可以看看 [Foreign Function Interface](https://doc.rust-lang.org/book/first-edition/ffi.html), [The Rust FFI Omnibus](http://jakegoulding.com/rust-ffi-omnibus/) （使用其他語言用 Rust 編寫的代碼的示例集合）和 [FFI examples written in Rust](https://github.com/alexcrichton/rust-ffi-examples).

- [rlhunt/cbindgen](https://github.com/eqrion/cbindgen) — 從 Rust 源文件生成 C 頭文件. 在 Gecko 中用於 WebRender 
- [Sean1708/rusty-cheddar](https://github.com/Sean1708/rusty-cheddar) — 從 Rust 源文件生成 C 頭文件
- [rust-lang/rust-bindgen](https://github.com/rust-lang/rust-bindgen) — Rust 綁定生成器
- [dtolnay/cxx](https://github.com/dtolnay/cxx) — Rust 和 C++ 之間的安全互操作
- [rust-cpp](https://crates.io/crates/cpp) - 直接在 Rust 中嵌入 C++ 代碼
- [rusterlium/rustler](https://github.com/rusterlium/rustler) — 用於創建 Erlang NIF 函數的安全 Rust 橋 
- [mgattozzi/curryrs](https://github.com/mgattozzi/curryrs) — 彌合 Haskell 和 Rust 之間的差距
- [mgattozzi/haskellrs](https://github.com/mgattozzi/haskellrs) — Haskell FFI 示例中的 Rust
- [mgattozzi/rushs](https://github.com/mgattozzi/rushs) — Rust FFI 示例中的 Haskell
- [j4rs](https://crates.io/crates/j4rs) — 使用 Rust 中的 Java 
- [bennettanderson/rjni](https://github.com/benanders/rjni) — 使用 Rust 中的 Java
- [drrb/java-rust-example](https://github.com/drrb/java-rust-example) — 使用 Java 中的 Rust
- [jni](https://crates.io/crates/jni) — 使用 Java 中的 Rust
- [jni-sys](https://crates.io/crates/jni-sys) — 對應於 jni.h 的 Rust 定義 
- [rucaja](https://crates.io/crates/rucaja) — 使用 Rust 中的 Java 
- [rawrafox/rust-jdbc](https://github.com/rawrafox/rust-jdbc) — 使用來自 Rust 的 JDBC
- [jcmoyer/rust-lua53](https://github.com/jcmoyer/rust-lua53) — 用於 Rust 的 Lua 5.3 綁定
- [lilyball/rust-lua](https://github.com/lilyball/rust-lua) — Safe Rust bindings to Lua 5.1
- [tickbh/td_rlua](https://github.com/tickbh/td_rlua) — Rust 的零成本高級 lua 5.3 包裝器
- [tomaka/hlua](https://github.com/tomaka/hlua) - 與 Lua 交互的 Rust 庫 
- [anima-engine/mrusty](https://github.com/anima-engine/mrusty) — Rust 的 mruby 安全綁定
- [neon-bindings/neon](https://github.com/neon-bindings/neon) — Rust 綁定，用於編寫安全且快速的原生 Node.js 模塊
- [infinyon/node-bindgen](https://github.com/infinyon/node-bindgen) - 使用 Rust 生成 nodejs 模塊的簡單方法 * 目標 - C
- [SSheldon/rust-objc](https://github.com/SSheldon/rust-objc) — Rust 的 Objective-C 運行時綁定和包裝器
- [vickenty/mi-rust](https://github.com/vickenty/mi-rust) — 添加對 M::I 的支持，以使用 Cargo 構建模塊
- [vickenty/perl-xs](https://github.com/vickenty/perl-xs) — 使用 Rust 創建 Perl XS 模塊 
- [getsentry/milksnake](https://github.com/getsentry/milksnake) — python setuptools 的擴展，它允許您以可想象的最便攜的方式在 Python 輪子中分發動態鏈接庫.
- [dgrunwald/rust-cpython](https://github.com/dgrunwald/rust-cpython) — Python 綁定
- [PyO3/PyO3](https://github.com/PyO3/PyO3) — Python 解釋器的 Rust 綁定 
- [d-unseductable/ruru](https://github.com/d-unseductable/ruru) — 用 Rust 編寫的原生 Ruby 擴展 
- [danielpclark/rutie](https://github.com/danielpclark/rutie) — 用 Rust 編寫的原生 Ruby 擴展，反之亦然 
- [tildeio/helix](https://github.com/tildeio/helix) — 用 Rust 編寫 Ruby 類 
- [rustwasm/wasm-pack](https://github.com/rustwasm/wasm-pack) —   打包 wasm 併發布到 npm！
- [rustwasm/wasm-bindgen](https://github.com/rustwasm/wasm-bindgen) — 一個促進 wasm 模塊和 JS 之間高級交互的項目. 
- [rhysd/wain](https://github.com/rhysd/wain) - wain：在 Safe Rust 中從零開始的 WebAssembly 解釋器，零依賴 
  
### IDEs

也可以看看 [Are we (I)DE yet?](https://areweideyet.com/) 和 [Rust Tools](https://www.rust-lang.org/tools).

- Atom

  - [zargony/atom-language-rust](https://github.com/zargony/atom-language-rust)
  - [rust-lang/atom-ide-rust](https://github.com/rust-lang/atom-ide-rust) — Rust IDE 對 Atom 的支持，由 Rust 語言服務器 (RLS) 提供支持

- Eclipse

  - [Eclipse Corrosion](https://github.com/eclipse/corrosion)
  - [RustDT](https://github.com/RustDT/RustDT) 

- Emacs

  - [rust-mode](https://github.com/rust-lang/rust-mode) — Rust 主要模式
  - [rustic](https://github.com/brotzeit/rustic) - Emacs 的 Rust 開發環境 
  - [flycheck-rust](https://github.com/flycheck/flycheck-rust) — Rust 支持 [Flycheck](https://github.com/flycheck/flycheck)
  - [emacs-racer](https://github.com/racer-rust/emacs-racer) — 自動完成（另見 [company](https://company-mode.github.io/) 和 [auto-complete](https://github.com/auto-complete/auto-complete))

- [gitpod.io](https://gitpod.io/) — 基於 Rust 語言服務器的具有完整 Rust 支持的在線 IDE

- [gnome-builder](https://wiki.gnome.org/Apps/Builder) 自版本 3.22.2 起原生支持 Rust 和 Cargo

- Kakoune

  - [kak-lsp/kak-lsp](https://github.com/kak-lsp/kak-lsp/) — [LSP](https://microsoft.github.io/language-server-protocol/) 客戶. 在 Rust 中實現並支持 rls 開箱即用.

- NetBeans

  - [drrb/rust-netbeans](https://github.com/drrb/rust-netbeans)

- IntelliJ

  - [intellij-rust/intellij-rust](https://github.com/intellij-rust/intellij-rust) 
  - [intellij-rust/intellij-toml](https://github.com/intellij-rust/intellij-toml) — 基本的 Toml 支持

- [Ride](https://github.com/madeso/ride)

- [SolidOak](https://github.com/oakes/SolidOak) — 一個簡單的 Rust IDE，基於 GTK+ 和 [Neovim](https://github.com/neovim/neovim)

- Sublime Text

  - [rust-lang/rust-enhanced](https://github.com/rust-lang/rust-enhanced) — 官方 Rust 包
  - [sublimehq/packages](https://github.com/sublimehq/Packages/tree/master/Rust) — 原生 Sublime 支持（已安裝）

- Vim

  — 無處不在的文本編輯器

  - [rust.vim](https://github.com/rust-lang/rust.vim) — 提供文件檢測、語法高亮、格式化、Syntastic 集成等.
  - [vim-cargo](https://github.com/timonv/vim-cargo) — 命令綁定以從 vim 快速運行貨物.
  - [vim-racer](https://github.com/racer-rust/vim-racer) — 允許 vim 使用 [Racer](https://github.com/racer-rust/racer) 用於 Rust 代碼完成和導航.
  - [autozimu/LanguageClient-neovim](https://github.com/autozimu/LanguageClient-neovim) — [LSP](https://microsoft.github.io/language-server-protocol/) 客戶. 在 Rust 中實現並支持 rls 開箱即用

- 視覺工作室

  - [PistonDevelopers/VisualRust](https://github.com/PistonDevelopers/VisualRust) — Rust 的 Visual Studio 擴展
  - [dgriffen/rls-vs2017](https://github.com/ZoeyR/rls-vs2017) — 對 Visual Studio 2017 預覽版的 Rust 支持

- Visual Studio Code

  - [rust-lang/rls-vscode](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust) — 對 Visual Studio Code 的 Rust 支持
  - [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=matklad.rust-analyzer) — RLS 的替代 Rust 語言服務器
  - [CodeLLDB](https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb) — 一個 LLDB 擴展
  - [crates](https://github.com/serayuzgur/crates) — crates 是 crates.io 依賴項的擴展. 
  
### 圖像識別

- [sfikas/rusteval](https://github.com/sfikas/rusteval) — 用於評估檢索算法輸出的工具 

### 分析

- [bheisler/criterion.rs](https://github.com/bheisler/criterion.rs) — 統計驅動的 Rust 基準測試庫
- [sharkdp/hyperfine](https://github.com/sharkdp/hyperfine) — 命令行基準測試工具 
- [performancecopilot/hornet](https://github.com/performancecopilot/hornet) — Performance Co-Pilot 內存映射值檢測庫 
- [koute/memory-profiler](https://github.com/koute/memory-profiler) — Linux 的內存分析器 
- [ellisonch/rust-stopwatch](https://github.com/ellisonch/rust-stopwatch) — 一個秒錶庫 
- [mrhooray/torch](https://github.com/mrhooray/torch) — 根據 DWARF 調試信息生成 FlameGraphs
- [llogiq/flame](https://github.com/llogiq/flame) 

### Services

- [deps.rs](https://github.com/deps-rs/deps.rs) — 檢測過時或不安全的依賴項
- [docs.rs](https://docs.rs/) — 自動生成 crate 文檔
  
### 靜態分析

- [facebookexperimental/MIRAI](https://github.com/facebookexperimental/mirai) — 一個在 Rust 的中級中間表示 (MIR) 上運行的抽象解釋器
- [static_assertions](https://crates.io/crates/static_assertions) — 編譯時斷言以確保滿足不變量 

### 測試

- [laboratory](https://crates.io/crates/laboratory) — 一個簡單、富有表現力的 Rust 單元測試框架 
- [cucumber-rust](https://crates.io/crates/cucumber-rust) — Rust 的 Cucumber 測試框架的實現.
- [demonstrate](https://crates.io/crates/demonstrate) — 聲明式測試框架 
- [httpmock](https://github.com/alexliesenfeld/httpmock) — HTTP 模擬 
- [mockiato](https://crates.io/crates/mockiato) — 一個嚴格但友好的 Rust 2018 模擬庫
- [mutagen](https://crates.io/crates/mutagen) — 一個源級變異測試框架（僅限每晚）
- [AlKass/polish](https://github.com/AlKass/polish) — 迷你測試 / 測試驅動框架 
- [proptest](https://crates.io/crates/proptest) — 受啟發的屬性測試框架 [Hypothesis](https://hypothesis.works/) Python 框架
- [quickcheck](https://crates.io/crates/quickcheck) — 一個 Rust 實現 [QuickCheck](https://wiki.haskell.org/Introduction_to_QuickCheck1) 
- [mockito](https://crates.io/crates/mockito) — HTTP 模擬 
- [speculate](https://crates.io/crates/speculate) — 一個 RSpec 啟發了 Rust 的最小測試框架
- [rstest](https://crates.io/crates/rstest) — Rust 的基於夾具的測試框架
- [ruspec](https://crates.io/crates/ruspec) — 像 Rspec 測試框架一樣用 Rust 編寫 
- [rust-fuzz/afl.rs](https://github.com/rust-fuzz/afl.rs) — 一個 Rust 模糊器，使用 [AFL](https://lcamtuf.coredump.cx/afl/) 
- [tarpaulin](https://crates.io/crates/cargo-tarpaulin) — 為 Rust 設計的代碼覆蓋率工具 
- [trust](https://github.com/japaric/trust) — Travis CI 和 AppVeyor 模板，用於在 5 種架構上測試您的 Rust crate 併發布其適用於 Linux、macOS 和 Windows 的二進製版本
- [fake-rs](https://github.com/cksac/fake-rs) — 生成假數據的庫 
- [goldenfile](https://github.com/calder/rust-goldenfile) - 一個為 Goldenfile 測試提供簡單 API 的庫.
- [cargo-dinghy](https://crates.io/crates/cargo-dinghy/) - 簡化在智能手機和其他小型處理器設備上運行庫測試和工作臺的貨物擴展.

### 翻譯器

- [immunant/c2rust](https://github.com/immunant/c2rust) — 在 Clang/LLVM 之上構建的 C 到 Rust 翻譯器和交叉檢查器. 
- [jameysharp/corrode](https://github.com/jameysharp/corrode) — 用 Haskell 編寫的 AC 到 Rust 翻譯器.

## 收集系統信息

- [Phate6660/nixinfo](https://github.com/Phate6660/nixinfo) [[crate](https://crates.io/crates/nixinfo)] — 一個用於收集系統信息（如 CPU、發行版、環境、內核等）的 lib crate.
  
# 🐂 大牛語錄
  
### Matthieum:
  
“Rust 使編寫正確且可讀的代碼變得更容易，同時獲得兩者並非巧合。

所有權/借用機制（對生命週期、別名和可變性的嚴格控制）在生成的軟件的數據流中強制執行某種簡單性，您可以在其他編程語言中獲得這種簡單性，但通常不會，因為該語言更寬鬆你得到了一個更復雜的流程。

你是否曾經在 Java 中調試過 ConcurrentModificationException？當您修改正在迭代的容器時會發生這種情況。當您有一系列回調/觀察者時，意外地有導致此異常的循環引用非常容易。在 Rust 中，要解決這種情況，你必須使用 RefCell 或等價物，它應該讓您停下來。”


## 聯繫專欄

#### 關注微信公眾號【後臺服務架構師】——【聯繫我們】，獲取本repo最全PDF學習文檔！

<img width="65%" height="65%" src="https://user-images.githubusercontent.com/87457873/130796999-03af3f54-3719-47b4-8e41-2e762ab1c68b.png"/>
  
  
  
  
  
