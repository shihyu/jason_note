
# 🌞🌞🌞 最新整理， C++ 學習資料，含C++ 11 / 14 / 17 / 20 / 23 新特性、入門教程、推薦書籍、優質文章、學習筆記、教學影片等
<br>

<div align=center>
	
<img width="70%" height="70%" src="https://user-images.githubusercontent.com/87457873/134297801-d13053cc-0a5d-4efd-9f02-9343b513fc33.png"/>
	
## 🚀 直達  [（# C++11）](#cpp_11) [（# C++14）](#cpp_14) [（# C++17）](#cpp_17) [（# C++20）](#cpp_20) [（# C++23）](#cpp_23)

<br>

</div>

# 🔥🔥🔥 [【重磅推薦收藏：C++ 參考手冊】](https://c-cpp.com/cpp) - 11~20你想要查的，他都有

# 🌋 C++ 發展歷程

* C++ 編程語言的歷史可以追溯到 **1979 年**，當時 Bjarne Stroustrup 為博士學位元元論文進行了一些開發。在 Stroustrup 可以使用的所有語言中，有一種被稱為 Simula 的語言，顧名思義，它可能是一種主要為仿真而設計的語言。Simula 67 語言是 Stroustrup 使用的變體，被認為是支援面向物件編程範例的主要語言。Stroustrup 發現這種範例對包裝開發很有幫助。但是，Simula 語言對於實踐和實際使用而言太慢了。
隨後不久，Bjarne Stroustrup 希望通過支援面向物件範例來增強 C。他深入研究了 Smalltalk 的 OO 實現，以獲取有關實現的想法。但是他不願意為此放棄性能，因此他開始從事 “C with Classes (帶有類的 C）” 的工作，希望 C++ 程式碼運行時應具有與 C 程式碼相似（或更好）的性能。

* **1983 年**，語言的名稱從 “帶有類的 C” 更改為 C++。C 語言中的 ++ 運算子是用於遞增變數的運算子，它使您可以深入瞭解 Stroustrup 如何看待該語言。在此期間添加了許多新功能，其中最引人注目的是虛擬函式，函式多載，帶有＆符號的參照，const 關鍵字和使用兩個正斜槓的單行註釋。

* **1985 年**，Stroustrup 出版了名為*“C++ 編程語言” 的書籍*。同年，C++ 被實現為商業產品。該語言尚未正式標準化，因此使該書成為非常重要的參考。該語言在 1989 年再次進行了更新，以包括受保護的成員和靜態成員，以及從多個類的繼承。

* **1990 年**，發行了*《帶註釋的 C++ 參考手冊*》。同年，Borland 的 Turbo C++ 編譯器將作為商業產品發佈。Turbo C++ 添加了許多其他庫，這些庫會對 C++ 的開發產生相當大的影響。儘管 Turbo C++ 的最後一個穩定版本是 2006 年，但該編譯器仍被廣泛使用。

* **1998 年**，C++ 標準委員會發布了第一個 C++ ISO / IEC 14882：1998 國際標準，其非正式名稱為 C++ 98。據說*《帶註釋的 C++ 參考手冊*》對標準的制定產生了很大的影響。還包括標準樣板庫，該樣板庫於 1979 年開始概念開發。2003 年，該委員會對 1998 年標準所報告的多個問題做出了回應，並對其進行了相應的修訂。更改的語言稱為 C++ 03。

* **2005 年**，C++ 標準委員會發布了一份技術報告（稱為 TR1），詳細介紹了他們計劃添加到最新 C++ 標準中的各種功能。新標準被非正式地稱為 C++ 0x，因為它有望在第一個十年結束之前的某個時間發佈。具有諷刺意味的是，新標準要到 2011 年年中才會發布。直到那時為止，已經發布了幾份技術報告，並且一些編譯器開始為新功能添加實驗性支援。

* **2011 年中**，新的 C++ 標準（稱為 C++ 11）完成。Boost 庫專案對新標準產生了重大影響，其中一些新模組直接來自相應的 Boost 庫。一些新功能包括正則表達式支援，全面的隨機化庫，新的 C++ 時間庫，原子支援，標準執行緒庫 ，一種新的 for 迴圈語法，提供的功能類似於某些其他語言中的 foreach 迴圈，auto 關鍵字，新的容器類，對聯合和陣列初始化列表以及可變參數樣板的更好支援。

* **2014 年**，C++ 14（也稱為 C++ 1y）作為 C++11 的一個小擴展發佈，主要功能是錯誤修復和小的改進，國際標準投票程式草案於 2014 年 8 月中完成，加強 lambda 函式，constexpr 和型別推導特性。

* **2017 年**，發佈 C17 標準，C17 提供了很多東西。增強了核心語言和庫。

* **2020 年**，發佈 C++20 標準，推出了很多重量級功能，其中比較重要的有：

  - Concepts：概念改變了我們思考和編程樣板的方式。它們是樣板參數的語義類別。它們使您可以直接在型別系統中表達您的意圖。如果出了什麼問題，您會收到清晰的錯誤消息。
  - Ranges library：新的 ranges 庫使它可以直接在容器上執行演演算法，用管道符號組成演演算法，並將其應用於無限數據流。
  - Coroutines：由於協程，C++ 中的非同步編程成為主流。協程是協作任務，事件迴圈，無限數據流或管道的基礎。
  - Modules：模組克服了頭檔案的限制。頭檔案和原始檔的分離變得和預處理器一樣過時了。最後，我們有更快的構建時間和更輕鬆的構建軟體包的方法。
  - Concurrency：Atomic Smart Pointers,Joining & Cancellable Threads,The C20 Synchronization Library，增強了 C++ 併發編程能力；
</br>

---


# 🚪 入門教程 
### [C++ 入門教程（41課時） - 阿里雲大學](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md)
* [C++ 教程](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%95%99%E7%A8%8B)
* [C++ 簡介](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E7%AE%80%E4%BB%8B)
* [C++ 環境設置](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E7%8E%AF%E5%A2%83%E8%AE%BE%E7%BD%AE)
* [C++ 基本語法](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%9F%BA%E6%9C%AC%E8%AF%AD%E6%B3%95)
* [C++ 註釋](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%B3%A8%E9%87%8A)
* [C++ 數據型別](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%95%B0%E6%8D%AE%E7%B1%BB%E5%9E%8B)
* [C++ 變數型別](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%8F%98%E9%87%8F%E7%B1%BB%E5%9E%8B)
* [C++ 變數作用域](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%8F%98%E9%87%8F%E4%BD%9C%E7%94%A8%E5%9F%9F)
* [C++ 常數](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%B8%B8%E9%87%8F)
* [C++ 修飾符型別](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E4%BF%AE%E9%A5%B0%E7%AC%A6%E7%B1%BB%E5%9E%8B)
* [C++ 存儲類](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%AD%98%E5%82%A8%E7%B1%BB)
* [C++ 運算子](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E8%BF%90%E7%AE%97%E7%AC%A6)
* [C++ 迴圈](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%BE%AA%E7%8E%AF)
* [C++ 判斷](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%88%A4%E6%96%AD)
* [C++ 函式](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%87%BD%E6%95%B0)
* [C++ 數字](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%95%B0%E5%AD%97)
* [C++ 陣列](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%95%B0%E7%BB%84)
* [C++ 字串](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%AD%97%E7%AC%A6%E4%B8%B2)
* [C++ 指標](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%8C%87%E9%92%88)
* [C++ 參照](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%BC%95%E7%94%A8)
* [C++ 日期 & 時間](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%97%A5%E6%9C%9F--%E6%97%B6%E9%97%B4)
* [C++ 基本的輸入輸出](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%9F%BA%E6%9C%AC%E7%9A%84%E8%BE%93%E5%85%A5%E8%BE%93%E5%87%BA)
* [C++ 數據結構](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84)
* [C++ 類 & 物件](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E7%B1%BB--%E5%AF%B9%E8%B1%A1)
* [C++ 繼承](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E7%BB%A7%E6%89%BF)
* [C++ 多載運算子和多載函式](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E9%87%8D%E8%BD%BD%E8%BF%90%E7%AE%97%E7%AC%A6%E5%92%8C%E9%87%8D%E8%BD%BD%E5%87%BD%E6%95%B0)
* [C++ 多型](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%A4%9A%E6%80%81)
* [C++ 數據抽象](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%95%B0%E6%8D%AE%E6%8A%BD%E8%B1%A1)
* [C++ 數據封裝](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%95%B0%E6%8D%AE%E5%B0%81%E8%A3%85)
* [C++ 介面（抽象類）](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%8E%A5%E5%8F%A3%E6%8A%BD%E8%B1%A1%E7%B1%BB)
* [C++ 檔案和流](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%96%87%E4%BB%B6%E5%92%8C%E6%B5%81)
* [C++ 異常處理](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%BC%82%E5%B8%B8%E5%A4%84%E7%90%86)
* [C++ 動態記憶體](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%8A%A8%E6%80%81%E5%86%85%E5%AD%98)
* [C++ 命名空間](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4)
* [C++ 樣板](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%A8%A1%E6%9D%BF)
* [C++ 預處理器](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E9%A2%84%E5%A4%84%E7%90%86%E5%99%A8)
* [C++ 信號處理](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E4%BF%A1%E5%8F%B7%E5%A4%84%E7%90%86)
* [C++ 多執行緒](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E5%A4%9A%E7%BA%BF%E7%A8%8B)
* [C++ Web 編程](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-web-%E7%BC%96%E7%A8%8B)
* [C++ STL 教程](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-stl-%E6%95%99%E7%A8%8B)
* [C++ 標準庫](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%20%E5%85%A5%E9%97%A8%E6%95%99%E7%A8%8B%EF%BC%8841%E8%AF%BE%E6%97%B6%EF%BC%89%20-%20%E9%98%BF%E9%87%8C%E4%BA%91%E5%A4%A7%E5%AD%A6.md#c-%E6%A0%87%E5%87%86%E5%BA%93)

### [C++ 學習筆記](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0.md)

* [一、基礎知識](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0.md#%E4%B8%80%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86)
  * 1、goto 語句(不建議使用)
  * 2、一維陣列
  * 3、二維陣列
  * 4、函式中的值傳遞
  * 5、函式的聲明
  * 6、函式的分檔案編寫
  * 7、指標
    * 7.1 指標的基本概念
    * 7.2 指標變數的定義和使用
    * 7.3 指標所佔記憶體空間
    * 7.4 空指標和野指標
    * 7.5 const修飾指標
    * 7.6 指標和陣列
    * 7.7 指標和函式
    * 7.8 指標、陣列、函式
  * 8、結構
    * 8.1 結構基本概念
    * 8.2 結構定義和使用
    * 8.3 結構陣列
    * 8.4 結構指標
    * 8.5 結構嵌套結構
    * 8.6 結構做函式參數
    * 8.7 結構中 const使用場景
* [二、核心編程](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0.md#%E4%BA%8C%E6%A0%B8%E5%BF%83%E7%BC%96%E7%A8%8B)
  * 1、記憶體分區模型
    * 1.1 程式運行前
    * 1.2 程式運行後
    * 1.3 new操作符
  * 2、參照
    * 2.1 參照的基本使用
    * 2.2 參照注意事項
    * 2.3 參照做函式參數
    * 2.4 參照做函式回傳值
    * 2.5 參照的本質
    * 2.6 常數參照
  * 3、函式
    * 3.1 函式預設參數
    * 3.2 函式佔位元元參數
    * 3.3 函式多載

# 📚 書籍推薦

* [《深入理解C++11：C++11新特性解析與應用》](https://www.aliyundrive.com/s/LKc1X2mL9G9)
* [《C++入門經典（第10版）》](https://book.douban.com/subject/30247747/)
* [《C++ Primer Plus 第6版 中文版(非同步圖書出品)》](https://www.epubit.com/bookDetails?id=UB7209840d845c9)
* [《清華電腦圖書譯叢：精通C++（第9版）》](https://item.jd.com/12432130.html)
* [《C++高級編程(第4版)》](http://www.tup.tsinghua.edu.cn/booksCenter/book_07894801.html)
* [《C++遊戲編程入門（第4版）(非同步圖書出品)》](https://item.jd.com/13265350.html)
* [《STL源碼剖析》](https://book.douban.com/subject/1110934/)
* [《C++程式設計:原理與實踐(基礎篇)(原書第2版)》](https://book.douban.com/subject/27023080/)
* [《Accelerated C++中文版》](https://book.douban.com/subject/2280545//)
* [《C++編程思想(兩卷合訂本)》](https://book.douban.com/subject/6558198/)
* [《中文版Effective STL:50條有效使用STL的經驗》](https://book.douban.com/subject/1792179/)
* [《C++編程剖析:問題、方案和設計準則》](https://book.douban.com/subject/5367371/)
* [《C++ Templates中文版》](https://book.douban.com/subject/1144020/)
* [《C++設計新思維》](https://book.douban.com/subject/1103566/)
* [《C++樣板元編程》](https://book.douban.com/subject/4136223/)
* [《C++併發編程實戰》](https://book.douban.com/subject/26386925/)
* [《C++程式設計語言(第1-3部分)(原書第4版)》](https://book.douban.com/subject/26857943/)
* [《C++標準庫(第2版)》](https://book.douban.com/subject/26419721/)
* [《Essential C++》](https://book.douban.com/subject/24868427/)
* [《C++ 語言的設計與演化》](https://book.douban.com/subject/1096216/)
* [《深度探索C++ 物件模型》](https://book.douban.com/subject/1091086/)
* [《泛型編程與STL》](https://book.douban.com/subject/1241423/)

# 📰 文章推薦
* [每個c++開發人員都應該使用的10個c++11特性](https://github.com/0voice/cpp_new_features/blob/main/%E6%AF%8F%E4%B8%AAc%2B%2B%E5%BC%80%E5%8F%91%E4%BA%BA%E5%91%98%E9%83%BD%E5%BA%94%E8%AF%A5%E4%BD%BF%E7%94%A8%E7%9A%8410%E4%B8%AAc%2B%2B%2011%E7%89%B9%E6%80%A7.md)
* [在c++專案中你必須真正使用的15個c++11特性](https://github.com/0voice/cpp_new_features/blob/main/%E5%9C%A8c%2B%2B%E9%A1%B9%E7%9B%AE%E4%B8%AD%E4%BD%A0%E5%BF%85%E9%A1%BB%E7%9C%9F%E6%AD%A3%E4%BD%BF%E7%94%A8%E7%9A%8415%E4%B8%AAc%2B%2B%E7%89%B9%E6%80%A7.md)
* [如何在 C++11 中使用 Lambda 表達式](https://github.com/0voice/cpp_new_features/blob/main/%E5%A6%82%E4%BD%95%E5%9C%A8%20C%2B%2B11%20%E4%B8%AD%E4%BD%BF%E7%94%A8%20Lambda%20%E8%A1%A8%E8%BE%BE%E5%BC%8F.md)
* [深入理解C++11](https://github.com/0voice/cpp_new_features/blob/main/%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3C%2B%2B11.md)
* [吐血整理：C++11新特性](https://github.com/0voice/cpp_new_features/blob/main/%E5%90%90%E8%A1%80%E6%95%B4%E7%90%86%EF%BC%9AC%2B%2B11%E6%96%B0%E7%89%B9%E6%80%A7.md)
* [C++11新特性之auto和decltype知識點](https://github.com/0voice/cpp_new_features/blob/main/%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%9AC++%2011%E6%96%B0%E7%89%B9%E6%80%A7.md#c11%E6%96%B0%E7%89%B9%E6%80%A7%E4%B9%8Bauto%E5%92%8Cdecltype%E7%9F%A5%E8%AF%86%E7%82%B9)
* [C++11新特性之左值參照、右值參照、移動語意、完美轉送](https://github.com/0voice/cpp_new_features/blob/main/%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%9AC++%2011%E6%96%B0%E7%89%B9%E6%80%A7.md#c11%E6%96%B0%E7%89%B9%E6%80%A7%E4%B9%8B%E5%B7%A6%E5%80%BC%E5%BC%95%E7%94%A8%E5%8F%B3%E5%80%BC%E5%BC%95%E7%94%A8%E7%A7%BB%E5%8A%A8%E8%AF%AD%E4%B9%89%E5%AE%8C%E7%BE%8E%E8%BD%AC%E5%8F%91)
* [C++11新特性之列表初始化](https://github.com/0voice/cpp_new_features/blob/main/%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%9AC++%2011%E6%96%B0%E7%89%B9%E6%80%A7.md#c11%E6%96%B0%E7%89%B9%E6%80%A7%E4%B9%8B%E5%88%97%E8%A1%A8%E5%88%9D%E5%A7%8B%E5%8C%96)
* [C++11新特性std::function和lambda表達式](https://github.com/0voice/cpp_new_features/blob/main/%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%9AC++%2011%E6%96%B0%E7%89%B9%E6%80%A7.md#c11%E6%96%B0%E7%89%B9%E6%80%A7stdfunction%E5%92%8Clambda%E8%A1%A8%E8%BE%BE%E5%BC%8F)
* [C++11新特性之樣板改進](https://github.com/0voice/cpp_new_features/blob/main/%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%9AC++%2011%E6%96%B0%E7%89%B9%E6%80%A7.md#c11%E6%96%B0%E7%89%B9%E6%80%A7%E4%B9%8B%E6%A8%A1%E6%9D%BF%E6%94%B9%E8%BF%9B)
* [C++11新特性之執行緒相關知識點](https://github.com/0voice/cpp_new_features/blob/main/%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%9AC++%2011%E6%96%B0%E7%89%B9%E6%80%A7.md#c11%E6%96%B0%E7%89%B9%E6%80%A7%E4%B9%8B%E7%BA%BF%E7%A8%8B%E7%9B%B8%E5%85%B3%E7%9F%A5%E8%AF%86%E7%82%B9)
* [C++11新特性之非同步操作-async](https://github.com/0voice/cpp_new_features/blob/main/%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%9AC++%2011%E6%96%B0%E7%89%B9%E6%80%A7.md#c11-%E7%9A%84%E5%BC%82%E6%AD%A5%E6%93%8D%E4%BD%9C-async)
* [C++11新特性之智慧指標](https://github.com/0voice/cpp_new_features/blob/main/%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%EF%BC%9AC++%2011%E6%96%B0%E7%89%B9%E6%80%A7.md#c11%E6%96%B0%E7%89%B9%E6%80%A7%E4%B9%8B%E6%99%BA%E8%83%BD%E6%8C%87%E9%92%88)
* [C++11常用新特性（一）](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B11%E5%B8%B8%E7%94%A8%E6%96%B0%E7%89%B9%E6%80%A7%EF%BC%88%E4%B8%80%EF%BC%89.md)
* [C++11常用新特性（二）](https://github.com/0voice/cpp_new_features/blob/main/C++11%E5%B8%B8%E7%94%A8%E6%96%B0%E7%89%B9%E6%80%A7%EF%BC%88%E4%BA%8C%EF%BC%89.md)
* [C++14新特性淺談](https://github.com/0voice/cpp_new_features/blob/main/%E3%80%8CNotes%E3%80%8DC%2B%2B14%E6%96%B0%E7%89%B9%E6%80%A7%E6%B5%85%E8%B0%88.md)
* [C++14新特性的所有知識點全在這兒啦](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B14%E6%96%B0%E7%89%B9%E6%80%A7%E7%9A%84%E6%89%80%E6%9C%89%E7%9F%A5%E8%AF%86%E7%82%B9%E5%85%A8%E5%9C%A8%E8%BF%99%E5%84%BF%E5%95%A6%EF%BC%81.md)
* [總結歸納：C++17新特性](https://github.com/0voice/cpp_new_features/blob/main/%E6%80%BB%E7%BB%93%E5%BD%92%E7%BA%B3%EF%BC%9AC%2B%2B17%E6%96%B0%E7%89%B9%E6%80%A7.md)
* [C++ 20語言特性](https://github.com/0voice/cpp_new_features/blob/main/C%2B%2B%2020%E8%AF%AD%E8%A8%80%E7%89%B9%E6%80%A7.md)


# ▶ 教學影片

#### [【GeekBand】侯捷 - C++面向物件高級編程](https://www.aliyundrive.com/s/HapPXxjQ1U7)

* [P1 C++編程簡介](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P2 頭檔案與類的聲明](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P3 建構函式](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P4 參數傳遞與回傳值](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P5 操作符多載與臨時物件](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P6 複習Complex類的實現過程](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P7 三大函式：複製建構，複製複製，解構](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P8 堆，棧與記憶體管理](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P9 複習String類的實現過程](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P10 擴展補充：類樣板，函式樣板，及其他](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P11 組合與繼承](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P13 委託相關設計](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P14 1 導讀](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P15 2 conversion function](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P16 3 non explicit one argument constructor](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P17 4 pointer like classes](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P18 5 function like classes](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P19 6 namespace經驗談](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P20 7 class template](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P21 8 Funtion Template](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P22 9 Member Template](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P23 10 specialization](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P24 11 樣板偏特化](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P25 12 樣板樣板參數](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P26 13 關於C++標準庫](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P27 14 三個主題](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P28 15 Reference](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P29 16 複合&繼承關係下的建構和解構](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P30 17 關於vptr和vtbl](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P31 18 關於this](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P32 19 0 關於Dynamic Binding](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P33 19 1 關於Dynamic Binding](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P34 20 關於New,Delete](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P35 21 Operator new，operator delete](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P36 22  示例](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P37 23  多載new,delete$示例](https://www.aliyundrive.com/s/HapPXxjQ1U7)
* [P38 24 Basic String使用newextra擴充申請量](https://www.aliyundrive.com/s/HapPXxjQ1U7)


# 🌰 乾貨鋪
* [C++ Standard Library](http://en.wikipedia.org/wiki/C%2B%2B_Standard_Library) - 一系列類和函式的集合，使用核心語言編寫，也是C++ISO自身標準的一部分
* [Standard Template Library](https://en.wikipedia.org/wiki/Standard_Template_Library) - 標準樣板庫
* [C POSIX library](https://en.wikipedia.org/wiki/C_POSIX_library) - POSIX系統的C標準庫規範
* [ISO C++ Standards Committee](https://github.com/cplusplus) - C++標準委員會
* [C++ FAQ](https://isocpp.org/faq) − C++ 常見問題
* [Free Country](https://www.thefreecountry.com/sourcecode/cpp.shtml?spm=5176.10731542.0.0.4fc35bde2jHhz4) − Free Country 提供了免費的 C++ 原始碼和 C++ 庫，這些原始碼和庫涵蓋了壓縮、存檔、遊戲編程、標準樣板庫和 GUI 編程等 C++ 編程領域。
* [C and C++ Users Group](http://www.hal9k.com/cug/?spm=5176.10731542.0.0.4fc35bde2jHhz4) − C 和 C++ 的用戶團體提供了免費的涵蓋各種編程領域 C++ 專案的原始碼，包括 AI、動畫、編譯器、資料庫、除錯、加密、遊戲、圖形、GUI、語言工具、系統編程等
* [LearnCpp](https://www.learncpp.com/) - 免費學習c++編程
* [CodeCogs](https://www.codecogs.com/) - CodeCogs是一項協作的開放源碼庫，C/C++的數值方面的組件
* [codeproject](https://www.codeproject.com/) - codeproject提供的C/C++資原始碼專案
* [thoughtco](https://www.thoughtco.com/c-and-c-plus-programming-4133470) - 遊戲有關的C++原始碼
* [Free C/C++ Libraries](https://www.programmerworld.net/resources/c_library.htm) - 免費C++原始碼和其它有用的工具
* [The C++ Standard Library](http://www.josuttis.com/libbook/examples.html) - 這是一個收集了數C/C++網站連結列表的網頁
* [cplusplus](http://www.cplusplus.com/) - C++學習網站
* [C++ Source Codes](https://people.sc.fsu.edu/~jburkardt/cpp_src/cpp_src.html) - 這是一個全面的關於C++的345個原始碼清單

# 🗜 框架
* [Apache C++ Standard Library](http://stdcxx.apache.org/) : 是一系列演演算法，容器，疊代器和其他基本組件的集合
* [ASL](http://stlab.adobe.com/) : Adobe原始碼庫提供了同行的評審和可移植的C++原始碼庫。
* [Boost](https://github.com/boostorg) : 大量通用C++庫的集合。
* [BDE](https://github.com/bloomberg/bde) : 來自於彭博資訊實驗室的開發環境。
* [Cinder](https://libcinder.org/) : 提供專業品質創造性編碼的開源開發社區。
* [Bxxomfort](http://ryan.gulix.cl/fossil.cgi/cxxomfort/index) : 輕量級的，只包含頭檔案的庫，將C++ 11的一些新特性移植到C++03中。
* [Dlib](http://dlib.net/) : 使用契約式編程和現代C++科技設計的通用的跨平臺的C++庫。
* [EASTL](https://github.com/paulhodge/EASTL) : EA-STL公共部分
* [ffead-cpp](https://github.com/sumeetchhetri/ffead-cpp) : 企業應用程式開發框架
* [Folly](https://github.com/facebook/folly) : 由Facebook開發和使用的開源C++庫。
* [JUCE](https://github.com/WeAreROLI/JUCE) : 包羅萬象的C++類庫，用於開發跨平臺軟體
* [libphenom](https://github.com/facebookarchive/libphenom) : 用於構建高性能和高度可擴展性系統的事件框架。
* [LibSourcey](https://github.com/sourcey/libsourcey) : 用於實時的影片流和高性能網路應用程式的C++11 evented IO
* [Loki](http://loki-lib.sourceforge.net/) : C++庫的設計，包括常見的設計模式和習語的實現。
* [MiLi](https://code.google.com/p/mili/) : 只含頭檔案的小型C++庫
* [openFrameworks](https://openframeworks.cc/) : 開發C++工具包，用於創意性編碼。
* [Qt](https://www.qt.io/developers/) : 跨平臺的應用程式和用戶界面框架
* [Reason](http://code.google.com/p/reason/) : 跨平臺的框架，使開發者能夠更容易地使用Java，.Net和Python，同時也滿足了他們對C++性能和優勢的需求。
* [ROOT](https://root.cern.ch/) : 具備所有功能的一系列面向物件的框架，能夠非常高效地處理和分析大量的數據，為歐洲原子能研究機構所用。
* [STLport](http://www.stlport.org/) : 是STL具有代表性的版本
* [STXXL](http://stxxl.sourceforge.net/) : 用於額外的大型數據集的標準樣板庫。
* [Ultimate++](https://www.ultimatepp.org/) : C++跨平臺快速應用程式開發框架
* [Windows Template Library](https://sourceforge.net/projects/wtl/) : 用於開發Windows應用程式和UI組件的C++庫
* [Yomm11](https://github.com/jll63/yomm11) : C++11的開放multi-methods.

<br>

### 非同步事件迴圈
* [Boost.Asio](https://think-async.com/Asio/) : 用於網路和底層I/O編程的跨平臺的C++庫。
* [libev](http://libev.schmorp.de/) : 功能齊全，高性能的時間迴圈，輕微地仿效libevent，但是不再像libevent一樣有侷限性，也修復了它的一些bug。
* [libevent](http://libevent.org/) : 事件通知庫
* [libuv](https://github.com/joyent/libuv) : 跨平臺非同步I/O。
* [libco](https://github.com/Tencent/libco) : 協程，微信支援8億用戶同時在線的底層IO庫。功能強大
* [libgo](https://github.com/yyzybb537/libgo) : golang風格的併發框架，C++11實現協程庫


<br>

### 網路庫
* [ACE](https://github.com/cflowe/ACE) : C++面向物件網路變成工具包
* [Casablanca](https://archive.codeplex.com/?p=casablanca) : C++ REST SDK
* [cpp-netlib](https://cpp-netlib.org/) : 高級網路編程的開源庫集合
* [libCurl](https://curl.haxx.se/libcurl/) : 多協議檔案傳輸庫
* [Mongoose](https://github.com/cesanta/mongoose) : 非常輕量級的網路伺服器
* [Muduo](https://github.com/chenshuo/muduo) : 用於Linux多執行緒伺服器的C++非阻塞網路庫
* [net_skeleton](https://github.com/cesanta/fossa) : C/C++的TCP 用戶端/伺服器庫
* [POCO](https://github.com/pocoproject/poco) : 用於構建網路和基於互聯網應用程式的C++類庫，可以運行在桌面，伺服器，移動和嵌入式系統。
* [RakNet](https://github.com/facebookarchive/RakNet) : 為遊戲開發人員提供的跨平臺的開源C++網路引擎。
* [Tufao](https://github.com/vinipsmaker/tufao) : 用於Qt之上的C++構建的非同步Web框架。
* [WebSocket++](https://github.com/zaphoyd/websocketpp) : 基於C++/Boost Aiso的websocket 用戶端/伺服器庫
* [ZeroMQ](http://zeromq.org/) : 高速，模組化的非同步通信庫


<br>

### TCP/IP協議棧
* [f-stack](https://github.com/f-stack/f-stack) : 騰訊開源的協議棧，基於DPDK的高性能用戶態協議棧。
* [NtyTcp](https://github.com/wangbojing/NtyTcp) : 單執行緒的協議棧的，基於netmap,DPDK,rawSocket的實現。
* [LWIP](http://savannah.nongnu.org/projects/lwip/) : 針對 RAM 平臺的精簡版的 TCP/IP 協議棧實現。
* [mTCP](https://github.com/mtcp-stack/mtcp) : 針對多核系統的高可擴展性的用戶空間 TCP/IP 協議棧。
* [4.4BSD](https://www.freebsd.org/zh_CN/copyright/license.html) : * nix的協議棧是源於4.4BSD的。

<br>

### WEB應用框架

* [Nginx](http://nginx.org/) : 一個高性能的HTTP和反向代理web伺服器，同時也提供了IMAP/POP3/SMTP服務。
* [Lighttpd](http://www.lighttpd.net/) : 一款開源 Web 伺服器軟體，安全快速,符合行業標準,適配性強並且針對高配置環境進行了最佳化。
* [Libmicrohttpd](http://www.gnu.org/software/libmicrohttpd/) : GNU軟體下的簡單c庫的Web伺服器。API簡單，快速。
* [shttpd](http://shttpd.sourceforge.net/) : 基於Mongoose的Web伺服器框架。
* [CivetWeb](https://github.com/bel2125/civetweb) : 提供易於使用，強大的，C/C++嵌入式Web伺服器，帶有可選的CGI，SSL和Lua支援。
* [CppCMS](http://cppcms.com/wikipp/en/page/main) : 免費高性能的Web開發框架（不是 CMS）.
* [Crow](https://github.com/ipkn/crow) : 一個C++微型web框架（靈感來自於Python Flask）
* [Kore](https://kore.io/) : 使用C語言開發的用於web應用程式的超快速和靈活的web伺服器/框架。
* [libOnion](https://www.coralbits.com/libonion/) : 輕量級的庫，幫助你使用C編程語言創建web伺服器。
* [QDjango](https://github.com/jlaine/qdjango/) : 使用C++編寫的，基於Qt庫的web框架，試圖效仿Django API，因此得此名。
* [Wt](https://www.webtoolkit.eu/wt) : 開發Web應用的C++庫。

<br>

### 標準庫，演演算法與函式
* [C++ Standard Library](http://en.wikipedia.org/wiki/C%2B%2B_Standard_Library) : 是一系列類和函式的集合，使用核心語言編寫，也是C++ISO自身標準的一部分。
* [Standard Template Library](https://en.wikipedia.org/wiki/Standard_Template_Library) : 標準樣板庫, STL
* [ISO C++ Standards Committee](https://github.com/cplusplus) : C++標準委員會

<br>

### 音頻庫
* [FMOD](https://www.fmod.com/) : 易於使用的跨平臺的音頻引擎和音頻內容的遊戲創作工具。
* [Maximilian](https://github.com/micknoise/Maximilian) : C++音頻和音樂數字信號處理庫
* [OpenAL](http://www.openal.org/) : 開源音頻庫—跨平臺的音頻API
* [Opus](http://opus-codec.org/) : 一個完全開放的，免版稅的，高度通用的音頻編解碼器
* [Speex](https://www.speex.org/) : 免費編解碼器，為Opus所廢棄
* [Tonic](https://github.com/TonicAudio/Tonic) : C++易用和高效的音頻合成
* [Vorbis](http://xiph.org/vorbis/) : Ogg Vorbis是一種完全開放的，非專有的，免版稅的通用壓縮音頻格式。

<br>

### 生態學
* [lisequence](http://molpopgen.github.io/libsequence/) : 用於表示和分析群體遺傳學數據的C++庫。
* [SeqAn](http://www.seqan.de/) : 專注於生物數據序列分析的演演算法和數據結構。
* [Vcflib](https://github.com/vcflib/vcflib) : 用於解析和處理VCF檔案的C++庫
* [Wham](https://github.com/zeeev/wham) : 直接把聯想測試應用到BAM檔案的基因結構變異。

<br>

### 壓縮
* [bzip2](http://www.bzip.org/) : 一個完全免費，免費專利和高質量的數據壓縮
* [doboz](https://bitbucket.org/attila_afra/doboz/src) : 能夠快速解壓縮的壓縮庫
* [PhysicsFS](https://icculus.org/physfs/) : 對各種歸檔提供抽象訪問的庫，主要用於影片遊戲，設計靈感部分來自於Quake3的檔案子系統。
* [KArchive](https://projects.kde.org/projects/frameworks/karchive) : 用於創建，讀寫和操作檔案檔案（例如zip和 tar）的庫，它通過QIODevice的一系列子類，使用gzip格式，提供了透明的壓縮和解壓縮的數據。
* [LZ4](https://code.google.com/p/lz4/) : 非常快速的壓縮演演算法
* [LZHAM](https://code.google.com/p/lzham/) : 無損壓縮資料庫，壓縮比率跟LZMA接近，但是解壓縮速度卻要快得多。
* [LZMA](http://www.7-zip.org/sdk.html) : 7z格式預設和通用的壓縮方法。
* [LZMAT](http://www.matcode.com/lzmat.htm) : 及其快速的實時無損數據壓縮庫
* [Minizip](https://code.google.com/p/miniz/) : Zlib最新bug修復，支援PKWARE磁碟跨越，AES加密和IO緩衝。
* [Snappy](https://code.google.com/p/snappy/) : 快速壓縮和解壓縮
* [ZLib](http://zlib.net/) : 非常緊湊的數據流壓縮庫
* [ZZIPlib](http://zziplib.sourceforge.net/) : 提供ZIP歸檔的讀權限。


<br>

### 併發性
* [Boost.Compute](https://github.com/boostorg/compute) : 用於OpenCL的C++GPU計算庫
* [Bolt](https://github.com/HSA-Libraries/Bolt) :  針對GPU進行最佳化的C++樣板庫
* [C++React](https://github.com/schlangster/cpp.react) : 用於C++11的反應性編程庫
* [Intel TBB](https://www.threadingbuildingblocks.org/) : Intel執行緒構件塊
* [Libclsph](https://github.com/libclsph/libclsph) : 基於OpenCL的GPU加速SPH流體仿真庫
* [OpenCL](https://www.khronos.org/opencl/) : 並行編程的異構系統的開放標準
* [OpenMP](https://www.openmp.org/) : OpenMP API
* [Thrust](http://thrust.github.io/) : 類似於C++標準樣板庫的並行演演算法庫
* [HPX](https://github.com/STEllAR-GROUP/hpx/) : 用於任何規模的並行和分佈式應用程式的通用C++運行時系統
* [VexCL](https://github.com/ddemidov/vexcl) : 用於OpenCL/CUDA 的C++向量表達式樣板庫。


<br>

### 密碼學
* [Bcrypt](http://bcrypt.sourceforge.net/) : 一個跨平臺的檔案加密工具，加密檔案可以移植到所有可支援的作業系統和處理器中。
* [BeeCrypt](https://github.com/klchang/beecrypt) : 快速的加密圖形庫，功能強大，介面方便。
* [Botan](https://botan.randombit.net/) : C++加密庫
* [Crypto++](https://www.cryptopp.com/) : 一個有關加密方案的免費的C++庫
* [GnuPG](https://www.gnupg.org/) : OpenPGP標準的完整實現
* [GnuTLS](https://www.gnutls.org/) : 實現了SSL，TLS和DTLS協議的安全通信庫
* [Libgcrypt](https://gnupg.org/related_software/libgcrypt/) : 基於GnuPG的加密圖形庫。
* [Libmcrypt](https://github.com/winlibs/libmcrypt) : 執行緒安全，提供統一的API。
* [LibreSSL](http://www.libressl.org/) : 免費的SSL/TLS協議，屬於2014 OpenSSL的一個分支
* [LibTomCrypt](https://github.com/libtom/libtomcrypt) : 一個非常全面的，模組化的，可移植的加密工具
* [libsodium](https://github.com/jedisct1/libsodium) : 基於NaCI的加密庫，固執己見，容易使用
* [Nettle](http://www.lysator.liu.se/~nisse/nettle/) : 底層的加密庫
* [OpenSSL](https://www.openssl.org/) : 一個強大的，商用的，功能齊全的，開放原始碼的加密庫。

<br>

### 資料庫
* [hiberlite](https://github.com/paulftw/hiberlite) : 用於Sqlite3的C++物件關係映射
* [LevelDB](https://github.com/google/leveldb) : 快速鍵值存儲庫
* [LMDB](https://symas.com/lmdb/technical/) : 符合資料庫四大基本元素的嵌入鍵值存儲
* [MySQL++](https://tangentsoft.com/mysqlpp/home) : 封裝了MySql的C API的C++ 包裝器
* [RocksDB](https://github.com/facebook/rocksdb) : 來自Facebook的嵌入鍵值的快速存儲
* [SQLite](https://www.sqlite.org/index.html) : 一個完全嵌入式的，功能齊全的關係資料庫，只有幾百KB，可以正確包含到你的專案中。
* [MongoDB](https://www.mongodb.com/) : 一個基於分佈式檔案存儲的資料庫

<br>

### 除錯
* [Boost.Test](https://www.boost.org/doc/libs/master/libs/test/doc/html/index.html) : Boost測試庫
* [Catch](https://github.com/catchorg/Catch2) : 一個很時尚的，C++原生的框架，只包含頭檔案，用於單元測試，測試驅動開發和行為驅動開發。
* [CppUnit](https://www.freedesktop.org/wiki/Software/cppunit/) : 由JUnit移植過來的C++測試框架
* [GoogleTest](http://code.google.com/p/googletest/) : 谷歌C++測試框架
* [ig-debugheap](https://github.com/deplinenoise/ig-debugheap) : 用於跟蹤記憶體錯誤的多平臺除錯堆
* [MemTrack](http://www.almostinfinite.com/memtrack.html) : 用於C++跟蹤記憶體分配
* [MicroProfile](https://bitbucket.org/jonasmeyer/microprofile/src/default/) : 跨平臺的網路試圖分析器
* [UnitTest++](http://unittest-cpp.sourceforge.net/) : 輕量級的C++單元測試框架


<br>

### 容器
* [C++ B-Tree](https://code.google.com/p/cpp-btree/) : 基於B樹數據結構，實現命令記憶體容器的樣板庫
* [Hashmaps](https://github.com/goossaert/hashmap) : C++中開放尋址哈希表演演算法的實現

<br>

### 遊戲引擎
* [Cocos2d-x](https://cocos2d-x.org/) : 一個跨平臺框架，用於構建2D遊戲，互動圖書，演示和其他圖形應用程式。
* [Grit](http://gritengine.com/) : 社區專案，用於構建一個免費的遊戲引擎，實現開放的世界3D遊戲。
* [lrrlicht](http://irrlicht.sourceforge.net/) : C++語言編寫的開源高性能的實時#D引擎
* [PolyCode](http://polycode.org/) : C++實現的用於創建遊戲的開源框架（與Lua綁定）。


<br>

### 圖形庫
* [bgfx](https://github.com/bkaradzic/bgfx) : 跨平臺的渲染庫
* [Cairo](http://www.cairographics.org/) : 支援多種輸出設備的2D圖形庫
* [Horde3D](https://github.com/horde3d/Horde3D) : 一個小型的3D渲染和動畫引擎
* [magnum](https://github.com/mosra/magnum) : C++11和OpenGL 2D/3D 圖形引擎
* [Ogre 3D](https://www.ogre3d.org/) : 用C++編寫的一個面向場景，實時，靈活的3D渲染引擎（並非遊戲引擎）
* [OpenSceneGraph](http://www.openscenegraph.org/) : 具有高性能的開源3D圖形工具包
* [Panda3D](https://www.panda3d.org/) : 用於3D渲染和遊戲開發的框架，用Python和C++編寫。
* [Skia](https://github.com/google/skia) : 用於繪製文字，圖形和圖像的完整的2D圖形庫
* [urho3d](https://github.com/urho3d/Urho3D) : 跨平臺的渲染和遊戲引擎。

<br>

### 圖像處理
* [Boost.GIL](https://www.boost.org/doc/libs/1_56_0/libs/gil/doc/index.html) : 通用圖像庫
* [CImg](https://sourceforge.net/projects/cimg/) : 用於圖像處理的小型開源C++工具包
* [FreeImage](http://freeimage.sourceforge.net/) : 開源庫，支援現在多媒體應用所需的通用圖片格式和其他格式。
* [GDCM](http://gdcm.sourceforge.net/wiki/index.php/Main_Page) : Grassroots DICOM 庫
* [ITK](https://itk.org/) : 跨平臺的開源圖像分析系統
* [Magick++](http://www.imagemagick.org/script/api.php) : ImageMagick程式的C++介面
* [OpenCV](https://opencv.org/) : 開源電腦視覺類庫
* [tesseract-ocr](https://code.google.com/p/tesseract-ocr/) : OCR引擎
* [VIGRA](https://github.com/ukoethe/vigra) : 用於圖像分析通用C++電腦視覺庫
* [VTK](https://vtk.org/) : 用於3D電腦圖形學，圖像處理和可視化的開源免費軟體系統。


<br>

### 國際化
* [gettext](http://www.gnu.org/software/gettext/) :  GNU gettext
* [IBM ICU](http://site.icu-project.org/) : 提供Unicode 和全球化支援的C、C++ 和Java庫
* [libiconv](http://www.gnu.org/software/libiconv/) : 用於不同字符編碼之間的編碼轉換庫


<br>

### Json庫
* [frozen](https://github.com/cesanta/frozen) : C/C++的Jason解析生成器
* [Jansson](https://github.com/akheron/jansson) : 進行編解碼和處理Jason數據的C語言庫
* [jbson](https://github.com/chrismanning/jbson) : C++14中構建和迭代BSON data,和Json 文件的庫
* [JeayeSON](https://github.com/jeaye/jeayeson) : 非常健全的C++ JSON庫，只包含頭檔案
* [JSON++](https://github.com/hjiang/jsonxx) : C++ JSON 解析器
* [json-parser](https://github.com/udp/json-parser) : 用可移植的ANSI C編寫的JSON解析器，佔用記憶體非常少
* [json11](https://github.com/dropbox/json11) : 一個迷你的C++11 JSON庫
* [jute](https://github.com/amir-s/jute) : 非常簡單的C++ JSON解析器
* [ibjson](https://github.com/vincenthz/libjson) : C語言中的JSON解析和印出庫，很容易和任何模型集成
* [libjson](https://sourceforge.net/projects/libjson/) : 輕量級的JSON庫
* [PicoJSON](https://github.com/kazuho/picojson) : C++中JSON解析序列化，只包含頭檔案
* [Qt-Json](https://github.com/qt-json/qt-json) : 用於JSON數據和 QVariant層次間的相互解析的簡單類
* [QJson](https://github.com/flavio/qjson) : 將JSON數據映射到QVariant物件的基於Qt的庫
* [RepidJSON](https://github.com/Tencent/rapidjson) : 用於C++的快速JSON 解析生成器，包含SAX和DOM兩種風格的API


<br>

### 日誌
* [Boost.Log](http://www.boost.org/doc/libs/1_56_0/libs/log/doc/html/index.html) : 設計非常模組化，並且具有擴展性
* [easyloggingpp](https://github.com/zuhd-org/easyloggingpp) : C++日誌庫，只包含單一的頭檔案。
* [Log4cpp](http://log4cpp.sourceforge.net/) : 一系列C++類庫，靈活添加日誌到檔案，系統日誌，IDSA和其他地方。
* [templog](http://www.templog.org/) : 輕量級C++庫，可以添加日誌到你的C++應用程式中


<br>

### 機器學習，人工智能

* [btsk](https://github.com/aigamedev/btsk) : 遊戲行為樹啟動器工具
* [Evolving Objects](http://eodev.sourceforge.net/) : 基於樣板的，ANSI C++演化計算庫，能夠幫助你非常快速地編寫出自己的隨機最佳化演演算法。
* [Caffe](https://github.com/BVLC/caffe) : 快速的神經網路框架
* [CCV](https://github.com/liuliu/ccv) : 以C語言為核心的現代電腦視覺庫
* [mlpack](http://www.mlpack.org/) :  可擴展的C++機器學習庫
* [OpenCV](https://github.com/opencv/opencv) : 開源電腦視覺庫
* [Recommender](https://github.com/GHamrouni/Recommender) : 使用協同過濾進行產品推薦/建議的C語言庫。
* [SHOGUN](https://github.com/shogun-toolbox/shogun) : Shogun 機器學習工具
* [sofia-ml](https://code.google.com/p/sofia-ml/) : 用於機器學習的快速增量演演算法套件



<br>

### 數學庫

* [Armadillo](http://arma.sourceforge.net/) : 高質量的C++線性代數庫，速度和易用性做到了很好的平衡。語法和MatlAB很相似
* [blaze](https://code.google.com/p/blaze-lib/) : 高性能的C++數學庫，用於密集和稀疏演演算法。
* [ceres-solver](http://ceres-solver.org/) : 來自谷歌的C++庫，用於建模和解決大型複雜非線性最小平方問題。
* [CGal](http://www.cgal.org/) : 高效，可靠的集合演演算法集合
* [CML](https://github.com/demianmnave/CML/wiki/The-Configurable-Math-Library) : 用於遊戲和圖形的免費C++數學庫
* [Eigen](http://eigen.tuxfamily.org/index.php?title=Main_Page) : 高級C++樣板頭檔案庫，包括線性代數，矩陣，向量操作，數值解決和其他相關的演演算法。
* [GMTL](http://ggt.sourceforge.net/) : 數學圖形樣板庫是一組廣泛實現基本圖形的工具。
* [GMP](https://gmplib.org/) : 用於個高精度計算的C/C++庫，處理有符號整數，有理數和浮點數。


<br>

### 多媒體庫

* [GStreamer](https://gstreamer.freedesktop.org/) : 構建媒體處理組件圖形的庫
* [LIVE555 Streaming Media](http://www.live555.com/liveMedia/) : 使用開放標準協議(RTP/RTCP, RTSP, SIP) 的多媒體流庫
* [libVLC](https://wiki.videolan.org/LibVLC) : libVLC (VLC SDK)媒體框架
* [QtAV](https://github.com/wang-bin/QtAV) : 基於Qt和FFmpeg的多媒體播放框架，能夠幫助你輕而易舉地編寫出一個播放器
* [SDL](http://www.libsdl.org/) : 簡單直控媒體層
* [SFML](http://www.sfml-dev.org/) : 快速，簡單的多媒體庫


<br>

### 物理學
* [Box2D](https://code.google.com/p/box2d/) : 2D的遊戲物理引擎。
* [Bullet](https://github.com/bulletphysics/bullet3) : 3D的遊戲物理引擎。
* [Chipmunk](https://github.com/slembcke/Chipmunk2D) : 快速，輕量級的2D遊戲物理庫
* [LiquidFun](https://github.com/google/liquidfun) : 2D的遊戲物理引擎
* [ODE](http://www.ode.org/) : 開放動力學引擎-開源，高性能庫，模擬剛體動力學。
* [ofxBox2D](https://github.com/vanderlin/ofxBox2d) : Box2D開源框架包裝器。
* [Simbody](https://github.com/simbody/simbody) : 高性能C++多體動力學/物理庫，模擬關節生物力學和機械系統，像車輛，機器人和人體骨骼。

<br>

### 機器人學
* [MOOS-Ivp](http://moos-ivp.org/) : 一組開源C++模組，提供機器人平臺的自主權，尤其是自主的海洋車輛。
* [MRPT](https://www.mrpt.org/) : 移動機器人編程工具包
* [PCL](https://github.com/PointCloudLibrary/pcl) : 點雲庫是一個獨立的，大規模的開放專案，用於2D/3D圖像和點雲處理。
* [Robotics Library](http://www.roboticslibrary.org/) : 一個獨立的C++庫，包括機器人動力學，運動規劃和控制。
* [RobWork](http://www.robwork.dk/apidoc/nightly/rw/) : 一組C++庫的集合，用於機器人系統的仿真和控制。
* [ROS](http://wiki.ros.org/) : 機器人作業系統，提供了一些庫和工具幫助軟體開發人員創建機器人應用程式。

<br>


<br>

### 腳本
* [ChaiScript](https://github.com/ChaiScript/ChaiScript/) : 用於C++的易於使用的嵌入式腳本語言。
* [Lua](http://www.lua.org/) : 用於配置檔案和基本應用程式腳本的小型快速腳本引擎。
* [luacxx](https://github.com/dafrito/luacxx) : 用於創建Lua綁定的C++ 11 API
* [SWIG](http://www.swig.org/) : 一個可以讓你的C++程式碼連結到JavaScript，Perl，PHP，Python，Tcl和Ruby的包裝器/介面生成器
* [V7](https://github.com/cesanta/v7) : 嵌入式的JavaScript 引擎。
* [V8](http://code.google.com/p/v8/) : 谷歌的快速JavaScript引擎，可以被嵌入到任何C++應用程式中。

<br>

### 序列化
* [Cap'n Proto](https://capnproto.org/) : 快速數據交換格式和RPC系統。
* [cereal](https://github.com/USCiLab/cereal) : C++11 序列化庫
* [FlatBuffers](https://github.com/google/flatbuffers) : 記憶體高效的序列化庫
* [MessagePack](https://github.com/msgpack/msgpack-c) : C/C++的高效二進制序列化庫，例如 JSON
* [ProtoBuf](http://code.google.com/p/protobuf/) : 協議緩衝，谷歌的數據交換格式。
* [SimpleBinaryEncoding](https://github.com/real-logic/simple-binary-encoding) : 用於低延遲應用程式的對二進制格式的應用程式資訊的編碼和解碼。
* [Thrift](https://thrift.apache.org/) : 高效的跨語言IPC/RPC，用於C++，Java，Python，PHP，C#和其它多種語言中，最初由Facebook開發。


<br>

### 影片庫
* [libvpx](http://www.webmproject.org/code/) : VP8/VP9編碼解碼SDK
* [FFMpeg](https://www.ffmpeg.org/) : 一個完整的，跨平臺的解決方案，用於記錄，轉換影片和音頻流。
* [libde265](https://github.com/strukturag/libde265) : 開放的h.265影片編解碼器的實現。
* [OpenH264](https://github.com/cisco/openh264) : 開源H.364 編解碼器。
* [Theora](https://www.theora.org/) : 免費開源的影片壓縮格式。



<br>

### XML庫

* [LibXml++](http://libxmlplusplus.sourceforge.net/) : C++的xml解析器
* [PugiXML](https://pugixml.org/) : 用於C++的，支援XPath的輕量級，簡單快速的XML解析器。
* [RapidXML](http://rapidxml.sourceforge.net/) : 試圖創建最快速的XML解析器，同時保持易用性，可移植性和合理的W3C兼容性。
* [TinyXML](https://sourceforge.net/projects/tinyxml/) : 簡單小型的C++XML解析器，可以很容易地集成到其它專案中。
* [TinyXML2](https://github.com/leethomason/tinyxml2) : 簡單快速的C++CML解析器，可以很容易集成到其它專案中。
* [TinyXML++](https://code.google.com/p/ticpp/) : TinyXML的一個全新的介面，使用了C++的許多許多優勢，樣板，異常和更好的異常處理。
* [Xerces-C++](http://xerces.apache.org/xerces-c/) : 用可移植的C++的子集編寫的XML驗證解析器。


---

<div id="cpp_11" align=center>
	
<img width="30%" height="30%" src="https://user-images.githubusercontent.com/87457873/134301566-dfe24e96-44a5-48b7-9294-f72c49010c2f.jpg"/>

</div>

# 🖥 部分程式碼案例

### <h3 id="cpp_11_keywords">關鍵字</h3>

#### <h5 id="cpp_11_new_keywords">新增關鍵字</h5>

* [thread_local](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_new_keywords_README.md#thread_local)
* [static_assert](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_new_keywords_README.md#static_assert)
* [nullptr](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_new_keywords_README.md#nullptr)
* [noexcept](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_new_keywords_README.md#noexcept)
* [decltype](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_new_keywords_README.md#decltype)
* [constexpr](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_new_keywords_README.md#constexpr)
* [char16_t](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_new_keywords_README.md#char16_t)
* [char32_t](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_new_keywords_README.md#char16_t)
* [alignof](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_new_keywords_README.md#alignof)
* [alignas](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_new_keywords_README.md#alignof)


#### <h5 id="cpp_11_meaning_changed__OR__new_meaning_added">含義變化或者新增含義關鍵字（meaning changed or new meaning added）</h5>

* [auto](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_meaning_keywords_README.md#auto)
* [class](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_meaning_keywords_README.md#clazz)
* [default](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_meaning_keywords_README.md#default)
* [delete](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_meaning_keywords_README.md#delete)
* [export](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_meaning_keywords_README.md#export)
* [extern](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_meaning_keywords_README.md#extern)
* [inline](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_meaning_keywords_README.md#inline)
* [mutable](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_meaning_keywords_README.md#mutable)
* [sizeof](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_meaning_keywords_README.md#sizeof)
* [struct](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_meaning_keywords_README.md#struct)
* [using](https://github.com/0voice/cpp_new_features/blob/main/cpp_11/001_meaning_keywords_README.md#using)

### <h3 id="cpp_11_RTTI">型別支援（基本型別、RTTI、型別特性）</h3>

#### <h5 id="cpp_11_RTTI_Primary_type_categories">Defined in header &lt;type_traits&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_void.cpp">is_void</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_integral.cpp">is_integral</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_floating_point.cpp">is_floating_point</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_array.cpp">is_array</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_enum.cpp">is_enum</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_union.cpp">is_union</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_class.cpp">is_class</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_function.cpp">is_function</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_pointer.cpp">is_pointer</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_lvalue_reference.cpp">is_lvalue_reference</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_rvalue_reference.cpp">is_rvalue_reference</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_member_object_pointer.cpp">is_member_object_pointer</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_member_function_pointer.cpp">is_member_function_pointer</a>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_fundamental.cpp">is_fundamental</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_arithmetic.cpp">is_arithmetic</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_scalar.cpp">is_scalar</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_object.cpp">is_object</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_compound.cpp">is_compound</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_reference.cpp">is_reference</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_member_pointer.cpp">is_member_pointer</a>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_const.cpp">is_const</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_volatile.cpp">is_volatile</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_trivial.cpp">is_trivial</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_trivially_copyable.cpp">is_trivially_copyable</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_standard_layout.cpp">is_standard_layout</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_literal_type.cpp">is_literal_type</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_empty.cpp">is_empty</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_polymorphic.cpp">is_polymorphic</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_abstract.cpp">is_abstract</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_signed.cpp">is_signed</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_unsigned.cpp">is_unsigned</a>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_constructible.cpp">is_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_trivially_constructible.cpp">is_trivially_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_nothrow_constructible.cpp">is_nothrow_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_default_constructible.cpp">is_default_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_trivially_default_constructible.cpp">is_trivially_default_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_nothrow_default_constructible.cpp">is_nothrow_default_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_copy_constructible.cpp">is_copy_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_trivially_copy_constructible.cpp">is_trivially_copy_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_nothrow_copy_constructible.cpp">is_nothrow_copy_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_move_constructible.cpp">is_move_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_trivially_move_constructible.cpp">is_trivially_move_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_nothrow_move_constructible.cpp">is_nothrow_move_constructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_assignable.cpp">is_assignable</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_trivially_assignable.cpp">is_trivially_assignable</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_nothrow_assignable.cpp">is_nothrow_assignable</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_copy_assignable.cpp">is_copy_assignable</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_trivially_copy_assignable.cpp">is_trivially_copy_assignable</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_nothrow_copy_assignable.cpp">is_nothrow_copy_assignable</a>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_is_move_assignable.cpp">is_move_assignable</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_trivially_move_assignable.cpp">is_trivially_move_assignable</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_nothrow_move_assignable.cpp">is_nothrow_move_assignable</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_destructible.cpp">is_destructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_trivially_destructible.cpp">is_trivially_destructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_is_nothrow_destructible.cpp">is_nothrow_destructible</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_rtti_std_has_virtual_destructor.cpp">has_virtual_destructor</a>


### <h3 id="cpp_11_stl">STL容器</h3>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_array.cpp">std::array</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_forward_list.cpp">std::forward_list</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_begin.cpp">std::begin</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_end.cpp">std::end</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_move.cpp">std::move</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_container_init.cpp">容器初始化</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_emplace.cpp">emplace</a>

#### <h5 id="cpp_11_unordered_containers">無序容器</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_unordered_map.cpp">std::unordered_map</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_unordered_multimap.cpp">std::unordered_multimap</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_unordered_set.cpp">std::unordered_set</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_unordered_multiset.cpp">std::unordered_multiset</a>

#### <h5 id="cpp_11_tuple">元組std::tuple</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_make_tuple.cpp">std::make_tuple</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_get.cpp">std::get</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_tie.cpp">std::tie</a>

#### <h5 id="cpp_11_hash">hash</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_hash_std_string.cpp">std::hash&lt;std::string&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_hash_std_u16string.cpp">std::hash&lt;std::u16string&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_hash_std_u32string.cpp">std::hash&lt;std::u32string&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_hash_std_wstring.cpp">std::hash&lt;std::wstring&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_hash_std_error_code.cpp">std::hash&lt;std::error_code&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_hash_std_bitset.cpp">std::hash&lt;std::bitset&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_hash_std_type_index.cpp">std::hash&lt;std::type_index&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_hash_std_vector_bool.cpp">std::hash&lt;std::vector&lt;bool&gt;&gt;</a>
<!-- 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_hash_std_thread_id.cpp">std::hash&lt;std&#58;&#58;thread&#58;&#58;id&gt;</a>
 -->

### <h3 id="cpp_11_smart_pointer">智慧指標</h3>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_shared_ptr.cpp">std::shared_ptr</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_weak_ptr.cpp">std::weak_ptr</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_unique_ptr.cpp">std::unique_ptr</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_auto_ptr.cpp">auto_ptr(棄用)</a>

### <h3 id="cpp_11_regex">正則表達式</h3>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_shared_ptr.cpp">basic_regex</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_weak_ptr.cpp">sub_match</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_unique_ptr.cpp">match_results</a>

### <h3 id="cpp_11_function">函式</h3>

#### <h5 id="cpp_11_function_nonstatic">非靜態成員函式</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_shared_ptr.cpp">cv限定函式</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_weak_ptr.cpp">參照限定</a>

#### <h5 id="cpp_11_function_template">函式物件樣板</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_unique_ptr.cpp">std::function</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_unique_ptr.cpp">std::bind</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_unique_ptr.cpp">std::bad_function_call</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_stl_std_unique_ptr.cpp">mem_fn</a>

### <h3 id="cpp_11_class">類</h3>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_class_type_alias.cpp">型別別名</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_class_member_init.cpp">類成員初始化</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_class_functor.cpp">仿函式(functor)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_class_delegating_constructors.cpp">委託建構函式</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_class_inheritance_constructor.cpp">繼承建構函式</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_class_move_constructor.cpp">移動建構函式</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_class_move_assignment_operator.cpp">移動賦值運算子</a>

### <h3 id="cpp_11_template">樣板</h3>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_template_angle_bracket.cpp">尖括號“>”</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_template_aliases.cpp">別名樣板</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_template_external_template.cpp">外部樣板</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_template_variable_parameter_template.cpp">可變參數樣板</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_template_default_template_parameters.cpp">預設樣板參數</a>


### <h3 id="cpp_11_template">原子操作</h3>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_bool.cpp">std::atomic&lt;bool&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_char.cpp">std::atomic&lt;char&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_signed_char.cpp">std::atomic&lt;signed char&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_unsigned_char.cpp">std::atomic&lt;unsigned char&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_short.cpp">std::atomic&lt;short&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_unsigned_short.cpp">std::atomic&lt;unsigned short&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_int.cpp">std::atomic&lt;int&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_unsigned_int.cpp">std::atomic&lt;unsigned int&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_long.cpp">std::atomic&lt;long&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_unsigned_long.cpp">std::atomic&lt;unsigned long&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_long_long.cpp">std::atomic&lt;long long&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_unsigned_long_long.cpp">std::atomic&lt;unsigned long long&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_char8_t.cpp">std::atomic&lt;char8_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_char16_t.cpp">std::atomic&lt;char16_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_char32_t.cpp">std::atomic&lt;char32_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_wchar_t.cpp">std::atomic&lt;wchar_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int8_t.cpp">std::atomic&lt;std::int8_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint8_t.cpp">std::atomic&lt;std::uint8_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int16_t.cpp">std::atomic&lt;std::int16_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint16_t.cpp">std::atomic&lt;std::uint16_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int32_t.cpp">std::atomic&lt;std::int32_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint32_t.cpp">std::atomic&lt;std::uint32_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int64_t.cpp">std::atomic&lt;std::int64_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint64_t.cpp">std::atomic&lt;std::uint64_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int_least8_t.cpp">std::atomic&lt;std::int_least8_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint_least8_t.cpp">std::atomic&lt;std::uint_least8_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int_least16_t.cpp">std::atomic&lt;std::int_least16_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint_least16_t.cpp">std::atomic&lt;std::uint_least16_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int_least32_t.cpp">std::atomic&lt;std::int_least32_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint_least32_t.cpp">std::atomic&lt;std::uint_least32_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int_least64_t.cpp">std::atomic&lt;std::int_least64_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint_least64_t.cpp">std::atomic&lt;std::uint_least64_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int_fast8_t.cpp">std::atomic&lt;std::int_fast8_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint_fast8_t.cpp">std::atomic&lt;std::uint_fast8_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int_fast16_t.cpp">std::atomic&lt;std::int_fast16_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint_fast16_t.cpp">std::atomic&lt;std::uint_fast16_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int_fast32_t.cpp">std::atomic&lt;std::int_fast32_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint_fast32_t.cpp">std::atomic&lt;std::uint_fast32_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_int_fast64_t.cpp">std::atomic&lt;std::int_fast64_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uint_fast64_t.cpp">std::atomic&lt;std::uint_fast64_t&gt;</a>
<!--
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_intptr_t.cpp">std::atomic&lt;std::intptr_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uintptr_t.cpp">std::atomic&lt;std::uintptr_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_size_t.cpp">std::atomic&lt;std::size_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_ptrdiff_t.cpp">std::atomic&lt;std::ptrdiff_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_intmax_t.cpp">std::atomic&lt;std::intmax_t&gt;</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_atomic_std_uintmax_t.cpp">std::atomic&lt;std::uintmax_t&gt;</a>
-->


### <h3 id="cpp_11_template">執行緒</h3>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_thread_std_thread.cpp">std::thread</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_thread_std_mutex.cpp">std::mutex</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_thread_std_lock.cpp">std::lock</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_thread_std_call_once.cpp">std::call_once</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_thread_std_atomic.cpp">std::atomic</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_thread_std_cond_ition_variable.cpp">std::cond_ition_variable</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_thread_async.cpp">std::async</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_thread_volatile.cpp">volatile</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_thread_std_future.cpp">std::future</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_std_thread_std_thread_local.cpp">std::thread_local</a>


### <h3 id="cpp_11_exception">異常</h3>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_exception_std_exception_ptr.cpp">std::exception_ptr</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_exception_std_make_exception_ptr.cpp">std::make_exception_ptr</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_exception_std_current_exception.cpp">std::current_exception</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_exception_std_rethrow_exception.cpp">std::rethrow_exception</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_exception_std_nested_exception.cpp">std::nested_exception</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_exception_std_throw_with_nested.cpp">std::throw_with_nested</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_exception_std_rethrow_if_nested.cpp">std::rethrow_if_nested</a>
<!--
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_exception_std_noexcept.cpp">std::noexcept</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_exception_std_terminate_handler.cpp">std::terminate_handler</a>
-->
### <h3 id="cpp_11_error">錯誤</h3>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_error_std_error_category.cpp">std::error_category</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_error_std_generic_category.cpp">std::generic_category</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_error_std_error_condition.cpp">std::error_condition</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_error_std_errc.cpp">std::errc</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_error_std_error_code.cpp">std::error_code</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/003_error_std_system_error.cpp">std::system_error</a>


### <h3 id="cpp_11_keywords">新語法</h3>

#### <h5 id="cpp_11_new_pretreatment">預處理</h5>

* <p>語法：__pragma(字串字面量)</p>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_pragma.cpp">_Pragma運算子</a>

#### <h5 id="cpp_11_cplusplus_macro">C++巨集(cplusplus macro)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_cpluscplus.h">_cplusplus巨集</a>

#### <h5 id="cpp_11_for">基於範圍的for語句</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_for_loop.cpp">for迴圈 for(x:range)</a>

####  <h5 id="cpp_11_alignment_support">對齊支援(alignment support)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_alignof.cpp">alignof</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_alignas.cpp">alignas</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_alignment_of.cpp">std::alignment_of</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_aligned_storage.cpp">std::aligned_storage</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_max_align_t.cpp">std::max_align_t</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_align.cpp">std::align</a>

####  <h5 id="cpp_11_explicit_conversion_operators">顯式轉換操作符(explicit conversion operators)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_explicit.cpp">explicit關鍵字</a>

####  <h5 id="cpp_11_static_assert">靜態斷言(static assert)</h5>

* <p>語法：static_assert(常數表達式，"提示字串")</p>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_static_assert.cpp">static assert</a>

####  <h5 id="cpp_11_numeric_limits">數字限制(numeric limits)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_numeric_limits.cpp">數字限制</a>

####  <h5 id="cpp_11_raw_string">原始字串(raw string)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_raw_string.cpp">原始字串</a>

####  <h5 id="cpp_11_trailing_return_type_syntax">追蹤返回型別語法(trailing return type syntax)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_trailing_return_type_syntax.cpp">追蹤返回型別語法</a>

####  <h5 id="cpp_11_extended_friend_syntax">擴展的friend語法(extended friend syntax)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_extended_friend_syntax.cpp">擴展的friend語法</a>

####  <h5 id="cpp_11_extended_integer_types">擴展的整型(extended integer types)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_extended_integer_types.cpp">擴展的整型</a>

####  <h5 id="cpp_11_unrestricted_union">非受限聯合(unrestricted union)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_unrestricted_union.cpp">非受限聯合</a>

####  <h5 id="cpp_11_lnline_namespace">內聯名字空間(lnline namespace)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_lnline.cpp">內聯名字空間</a>

####  <h5 id="cpp_11_user_defined_literals">用戶定義的字面量(user-defined literals)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_user_defined_literals.cpp">用戶定義的字面量</a>

####  <h5 id="cpp_11_enum_class">強型別列舉(scoped and strongly typed enums)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_scoped_and_strongly_typed_enums.cpp">強型別列舉</a>

####  <h5 id="cpp_11_random_device">隨機裝置(random device)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_random_device.cpp">random device</a>

####  <h5 id="cpp_11_stdref_std_cref">std::ref和std::cref</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_stdref_stdcref.cpp">std::ref和std::cref</a>

####  <h5 id="cpp_11_constexpr">常數表達式(constexpr)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_constexpr.cpp">constexpr</a>

####  <h5 id="cpp_11_lamda">lamda表達式</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_lamda.cpp">lamda表達式</a>

####  <h5 id="cpp_11_nullptr">指標空值(nullptr)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_nullptr.cpp">nullptr</a>

####  <h5 id="cpp_11_preventing_narrowing">防止型別收窄(Preventing narrowing)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_preventing_narrowing.cpp">防止型別收窄</a>

####  <h5 id="cpp_11_initializer_lists">初始化列表(initializer lists)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_initializer_lists01.cpp">初始化列表——Initializer List</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_initializer_lists02.cpp">initializer_list<T>(作入參)</a>

####  <h5 id="cpp_11_Uniform_initialization_syntax_and_semantics">統一的初始化語法和語義(Uniform initialization syntax and semantics)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_Uniform_initialization_syntax_and_semantics.cpp">統一的初始化語法和語義</a>

####  <h5 id="cpp_11_POD">POD(plain old data)</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_POD.cpp">POD</a>
							
####  <h5 id="cpp_11_POD">long long整型</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_long_long.cpp">long long</a>
	
####  <h5 id="cpp_11_move_semantics">移動語意(move semantics)</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_move_semantics.cpp">move semantics</a>
	
####  <h5 id="cpp_11_rvalue_reference">右值參照(rvalue reference)</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_rvalue_reference.cpp">rvalue reference</a>

####  <h5 id="cpp_11_c99">c99特性(c99)</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_c99.cpp">c99特性</a>

####  <h5 id="cpp_11_SFINAE">一般化的SFINAE規則(generalized SFINAE rules)</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_11/002_grammar_SFINAE.cpp">generalized SFINAE rules</a>
	
-----	
	
<div  id="cpp_14" align=center>
	
<img width="30%" height="30%" src="https://user-images.githubusercontent.com/87457873/134302218-7e6d1586-7210-4121-8aa0-244ddb37572a.jpg"/>

</div>		
	

### <h3 id="cpp_14_RTTI">型別支援（基本型別、RTTI、型別特性）</h3>
	
### <h5 id="cpp_headfile_type_traits">Defined in header&lt;type_traits&gt;</h5>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_type_traits_is_null_pointer.cpp">檢查型別是否為 std::nullptr_t</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_type_traits_is_final.cpp">is_final(檢查型別是否為 final 類型別)</a>

### <h5 id="cpp_headfile_utility">Defined in header&lt;utility&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_utility_exchange.cpp">exchange(將實際參數替換為一個新值，並返回其先前值)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_utility_integer_sequence.cpp">integer_sequence(實現編譯時整數數列)</a>

### <h5 id="cpp_headfile_initializer_list">Defined in header&lt;initializer_list&gt;</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_initializer_list_rbegin.cpp">rbegin(返回指向一個容器或陣列的逆向疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_initializer_list_crbegin.cpp">crbegin(返回指向一個容器或陣列的逆向疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_initializer_list_rend.cpp">rend(返回容器或陣列的逆向尾疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_initializer_list_crend.cpp">crend(返回容器或陣列的逆向尾疊代器)</a>

### <h5 id="cpp_headfile_initializer_list">Defined in header&lt;iterator&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in namespace std</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_iterator_make_reverse_iterator.cpp">make_reverse_iterator(創建擁有從實際參數推出的型別的 std::reverse_iterator)</a>

### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;array&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;deque&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;forward_list&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;iterator&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;list&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;map&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;regex&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;set&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;span&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;string&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;string_view&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;unordered_map&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;unordered_set&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;vector&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in namespace std</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_stl_begin.cpp">begin(返回指向容器或陣列起始的疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_stl_cbegin.cpp">cbegin(返回指向容器或陣列起始的疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_stl_end.cpp">end(返回指向容器或陣列結尾的疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_stl_cend.cpp">cend(返回指向容器或陣列結尾的疊代器)</a>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_stl_rbegin.cpp">rbegin(返回指向一個容器或陣列的逆向疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_stl_crbegin.cpp">crbegin(返回指向一個容器或陣列的逆向疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_stl_rend.cpp">rend(返回容器或陣列的逆向尾疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_14/001_stl_crend.cpp">crend(返回容器或陣列的逆向尾疊代器)</a>	


<!--	
* [函式回傳值型別推導](https://github.com/0voice/cpp_new_features/blob/main/cpp_14/README.md#cpp_14_01)
* [lambda參數auto](https://github.com/0voice/cpp_new_features/blob/main/cpp_14/README.md#cpp_14_02)
* [變數樣板](https://github.com/0voice/cpp_new_features/blob/main/cpp_14/README.md#cpp_14_03)
* [別名樣板](https://github.com/0voice/cpp_new_features/blob/main/cpp_14/README.md#cpp_14_04)
* [[[deprecated]]標記](https://github.com/0voice/cpp_new_features/blob/main/cpp_14/README.md#cpp_14_05)
* [二進制字面量與整形字面量分隔符](https://github.com/0voice/cpp_new_features/blob/main/cpp_14/README.md#cpp_14_06)
* [std::make_unique](https://github.com/0voice/cpp_new_features/blob/main/cpp_14/README.md#cpp_14_07)
* [std::shared_timed_mutex與std::shared_lock](https://github.com/0voice/cpp_new_features/blob/main/cpp_14/README.md#cpp_14_08)
* [std::integer_sequence](https://github.com/0voice/cpp_new_features/blob/main/cpp_14/README.md#cpp_14_09)
* [std::exchange](https://github.com/0voice/cpp_new_features/blob/main/cpp_14/README.md#cpp_14_10)
* [std::quoted](https://github.com/0voice/cpp_new_features/blob/main/cpp_14/README.md#cpp_14_11)
-->
	
-----

<div id="cpp_17" align=center>
	
<img width="30%" height="30%" src="https://user-images.githubusercontent.com/87457873/134302312-2c3ddfc0-7942-4263-9b02-4cec08c18e2f.jpg"/>

</div>	
	

### <h3 id="cpp_17_keywords">關鍵字</h3>

#### <h5 id="cpp_17_meaning_changed__OR__new_meaning_added">含義變化或者新增含義關鍵字（meaning changed or new meaning added）</h5>

* [register](https://github.com/0voice/cpp_new_features/blob/main/cpp_17/001_keywords_README.md#register)
	
### <h3 id="cpp_17_RTTI">型別支援（基本型別、RTTI、型別特性）</h3>
	
### <h5 id="cpp_headfile_type_traits">Defined in header&lt;type_traits&gt;</h5>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_byte.cpp">byte(位元元組型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_is_aggregate.cpp">is_aggregate(檢查型別是否聚合型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_is_swappable_with.cpp">is_swappable_with(檢查一個型別的物件是否能與同型別或不同型別的物件交換)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_is_swappable.cpp">is_swappable(檢查一個型別的物件是否能與同型別或不同型別的物件交換)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_is_nothrow_swappable_with.cpp">is_nothrow_swappable_with(檢查一個型別的物件是否能與同型別或不同型別的物件交換)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_is_nothrow_swappable.cpp">is_nothrow_swappable(檢查一個型別的物件是否能與同型別或不同型別的物件交換)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_is_invocable.cpp">is_invocable(檢查型別能否以給定的實際參數型別調用（如同以 std::invoke）)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_is_invocable_r.cpp">is_invocable_r(檢查型別能否以給定的實際參數型別調用（如同以 std::invoke）)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_is_nothrow_invocable.cpp">is_nothrow_invocable(檢查型別能否以給定的實際參數型別調用（如同以 std::invoke）)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_is_nothrow_invocable_r.cpp">is_nothrow_invocable_r(檢查型別能否以給定的實際參數型別調用（如同以 std::invoke）)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_invoke_result.cpp">invoke_result(推導以一組實際參數調用一個可調用物件的結果型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_void_t.cpp">void_t(變參別名樣板)</a>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_conjunction.cpp">conjunction(變參的邏輯與元函式)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_disjunction.cpp">disjunction(變參的邏輯或元函式)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_ndisjunctionegation.cpp">ndisjunctionegation(邏輯非元函式)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/002_type_traits_integral_constant.cpp">integral_constant(具有指定值的指定型別的編譯期常數)</a>

### <h5 id="cpp_headfile_utility">Defined in header&lt;utility&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/003_utility_as_const.cpp">as_const(獲得到其實際參數的 const 參照)</a>
<!--
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/003_utility_in_place.cpp">in_place(原位元元建構標籤)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/003_utility_in_place_type.cpp">in_place_type(原位元元建構標籤)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/003_utility_in_place_index.cpp">in_place_index(原位元元建構標籤)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/003_utility_in_place_t.cpp">in_place_t(原位元元建構標籤)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/003_utility_in_place_type_t.cpp">in_place_type_t(原位元元建構標籤)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/003_utility_in_place_index_t.cpp">in_place_index_t(原位元元建構標籤)</a>
-->
	
### <h5 id="cpp_headfile_tuple">Defined in header&lt;tuple&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/004_tuple_apply.cpp">apply(以一個實際參數的元組來調用函式)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/004_tuple_make_from_tuple.cpp">make_from_tuple(以一個實際參數元組建構物件)</a>

### <h5 id="cpp_headfile_optional">Defined in header&lt;optional&gt;</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/005_optional_optional.cpp">optional(可能或可能不保有一個物件的包裝器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/005_optional_make_optional.cpp">make_optional(創建一個 optional 物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/005_optional_std_swap.cpp">std::swap(std::optional)(特化 std::swap 演演算法)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/005_optional_std_hash.cpp">std::hash&lt;std::optional&gt;(特化 std::hash 演演算法)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/005_optional_nullopt_t.cpp">nullopt_t(帶未初始化狀態的 optional 型別的指示器)</a>	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/005_optional_bad_optional_access.cpp">bad_optional_access(指示進行了到不含值的 optional 的有檢查訪問的異常)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/005_optional_nullopt.cpp">nullopt(nullopt_t 型別物件)</a>

### <h5 id="cpp_headfile_variant">Defined in header&lt;variant&gt;</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_variant.cpp">variant(型別安全的可辨識聯合)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_visit.cpp">visit(以一或多個 variant 所保有的各實際參數調用所提供的函式物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_holds_alternative.cpp">holds_alternative(檢查某個 variant 是否當前持有某個給定型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_std_get.cpp">std::get(std::variant)(以給定索引或型別（若型別唯一）讀取 variant 的值，錯誤時拋出異常)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_get_if.cpp">get_if(以給定索引或型別（若其唯一），獲得指向被指向的 variant 的值的指標，錯誤時返回空指標)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_std_swap.cpp">std::swap(std::variant)(特化 std::swap 演演算法)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_monostate.cpp">monostate(用作非可預設建構型別的 variant 的首個可選項的佔位元元符型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_bad_variant_access.cpp">bad_variant_access(非法地訪問 variant 的值時拋出的異常)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_variant_size.cpp">variant_size(在編譯時獲得 variant 可選項列表的大小)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_variant_size_v.cpp">variant_size_v(在編譯時獲得 variant 可選項列表的大小)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_variant_alternative.cpp">variant_alternative(在編譯時獲得以其下標指定的可選項的型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_variant_alternative_t.cpp">variant_alternative_t(在編譯時獲得以其下標指定的可選項的型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_std_hash.cpp">std::hash&lt;std::variant&gt;(特化 std::hash 演演算法)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/006_variant_variant_npos.cpp">variant_npos(非法狀態的 variant 的下標)</a>
	
### <h5 id="cpp_headfile_any">Defined in header&lt;any&gt;</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/007_any_any.cpp">any(可保有任何可複製建構 (CopyConstructible) 型別的實體的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/007_any_std_swap.cpp">std::swap(std::any)(特化 std::swap 演演算法)</a>	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/007_any_any_cast.cpp">any_cast(對被容納物件的型別安全訪問)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/007_any_make_any.cpp">make_any(創建 any 物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/007_any_bad_any_cast.cpp">bad_any_cast(當型別不匹配時按值返回形式的 any_cast 所拋出的異常)</a>

### <h5 id="cpp_headfile_charconv">Defined in header&lt;charconv&gt;</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/008_charconv_to_chars.cpp">to_chars(轉換整數或浮點值到字符序列象)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/008_charconv_from_chars.cpp">from_chars(轉換字符序列到整數或浮點值)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/008_charconv_chars_format.cpp">chars_format(指定 std::to_chars 和 std::from_chars 所用的格式)</a>

### <h5 id="cpp_headfile_initializer_list">Defined in header&lt;initializer_list&gt;</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/009_initializer_list_empty.cpp">empty(檢查容器是否為空)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/009_initializer_list_data.cpp">data(獲得指向底層陣列的指標)</a>

### <h3 id="cpp_17_Containers_library">容器庫</h3>
### <h5 id="cpp_headfile_map">Defined in header&lt;map&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/010_map_insert_or_assign.cpp">insert_or_assign(插入元素，或若鍵已存在則賦值給當前元素)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/010_map_try_emplace.cpp">try_emplace(若鍵不存在則原位元元插入，若鍵存在則不做任何事)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/010_map_extract.cpp">extract(從另一容器釋出結點)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/010_map_merge.cpp">merge(從另一容器接合結點)</a>

### <h5 id="cpp_headfile_unordered_map">Defined in header&lt;unordered_map&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/011_unordered_map_insert_or_assign.cpp">insert_or_assign(插入元素，或若鍵已存在則賦值給當前元素)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/011_unordered_map_try_emplace.cpp">try_emplace(若鍵不存在則原位元元插入，若鍵存在則不做任何事)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/011_unordered_map_extract.cpp">extract(從另一容器釋出結點)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/011_unordered_map_merge.cpp">merge(從另一容器接合結點)</a>

### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;array&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;deque&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;forward_list&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;iterator&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;list&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;map&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;regex&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;set&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;span&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;string&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;string_view&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;unordered_map&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;unordered_set&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;vector&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in namespace std</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/012_stl_size.cpp">size(返回容器或陣列的大小)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/012_stl_empty.cpp">empty(檢查容器是否為空)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_17/012_stl_data.cpp">data(獲得指向底層陣列的指標)</a>

---- 
	
<div id="cpp_20" align=center>
	
<img width="30%" height="30%" src="https://user-images.githubusercontent.com/87457873/134302390-53b4bfe7-eb75-4325-8376-dabd620c3a9d.jpg"/>

</div>		
	
### <h3 id="cpp_20_keywords">關鍵字</h3>

#### <h5 id="cpp_20_new_keywords">新增關鍵字</h5>

* [char8_t](https://github.com/0voice/cpp_new_features/blob/main/cpp_20/001_keywords_README.md#char8_t)
* [concept](https://github.com/0voice/cpp_new_features/blob/main/cpp_20/001_keywords_README.md#concept)
* [consteval](https://github.com/0voice/cpp_new_features/blob/main/cpp_20/001_keywords_README.md#consteval)
* [co_await](https://github.com/0voice/cpp_new_features/blob/main/cpp_20/001_keywords_README.md#co_await)
* [co_return](https://github.com/0voice/cpp_new_features/blob/main/cpp_20/001_keywords_README.md#co_return)
* [co_yield](https://github.com/0voice/cpp_new_features/blob/main/cpp_20/001_keywords_README.md#co_yield)
* [requires](https://github.com/0voice/cpp_new_features/blob/main/cpp_20/001_keywords_README.md#requires)
	
#### <h5 id="cpp_20_meaning_changed__OR__new_meaning_added">含義變化或者新增含義關鍵字（meaning changed or new meaning added）</h5>

* [export](https://github.com/0voice/cpp_new_features/blob/main/cpp_20/001_keywords_README.md#export)
	
### <h3 id="cpp_20_RTTI">型別支援（基本型別、RTTI、型別特性）</h3>

### <h5 id="cpp_headfile_type_traits">Defined in header&lt;type_traits&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_is_bounded_array.cpp">is_bounded_array(檢查型別是否為有已知邊界的陣列型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_is_unbounded_array.cpp">is_unbounded_array(檢查型別是否為有未知邊界的陣列型別)</a>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_is_layout_compatible.cpp">is_layout_compatible(檢查二個型別是否佈局兼容)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_is_pointer_interconvertible_base_of.cpp">is_pointer_interconvertible_base_of(檢查一個型別是否為另一型別的指標可互轉換（起始）基類)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_is_pointer_interconvertible_with_class.cpp">is_pointer_interconvertible_with_class(檢查一個型別的物件是否與該型別的指定子物件指標可互轉換)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_is_corresponding_member.cpp">is_corresponding_member(檢查二個指定成員是否在二個指定型別中的公共起始序列中彼此對應)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_is_nothrow_convertible.cpp">is_nothrow_convertible(檢查是否能轉換一個型別為另一型別)</a>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_remove_cvref.cpp">remove_cvref(將 std::remove_cv 與 std::remove_reference 結合)</a>
<!--
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_common_reference.cpp">common_reference(確定型別組的共用參照型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_basic_common_reference.cpp">basic_common_reference(確定型別組的共用參照型別)</a>
-->
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_type_identity.cpp">type_identity(返回不更改的型別實際參數)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/002_rtti_is_constant_evaluated.cpp">is_constant_evaluated(檢測調用是否在常數求值的語境內發生)</a>

### <h3 id="cpp_20_Coroutine">協程支援</h3>

### <h5 id="cpp_headfile_coroutine">Defined in header&lt;coroutine&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/003_rtti_coroutine_traits.cpp">coroutine_traits(用於發現協程承諾型別的特徵型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/003_rtti_coroutine_handle.cpp">coroutine_handle(用於指代暫停或執行的協程)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/003_rtti_noop_coroutine.cpp">noop_coroutine(創建在等待或銷燬時無操作的協程柄)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/003_rtti_noop_coroutine_promise.cpp">noop_coroutine_promise(用於無可觀察作用的協程)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/003_rtti_noop_coroutine_handle.cpp">noop_coroutine_handle(std::coroutine_handle&lt;std::noop_coroutine_promise&gt; ，有意用於指代無操作協程)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/003_rtti_suspend_never.cpp">suspend_never(指示 await 表達式應該決不暫停)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/003_rtti_suspend_always.cpp">suspend_always(指示 await 表達式應該始終暫停)</a>

### <h3 id="cpp_20_compare">三路比較</h3>

### <h5 id="cpp_headfile_compare">Defined in header&lt;compare&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_std_coroutine_traits.cpp">std::coroutine_traits</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_std_coroutine_handle.cpp">std::coroutine_handle</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_three_way_comparable.cpp">three_way_comparable(指定運算子 <=> 在給定型別上產生一致的結果)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_three_way_comparable_with.cpp">three_way_comparable_with(指定運算子 <=> 在給定型別上產生一致的結果)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_partial_ordering.cpp">partial_ordering(三路比較的結果型別，支援所有 6 種運算子，不可替換，並允許不可比較的值)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_weak_ordering.cpp">weak_ordering(三路比較的結果型別，支援所有 6 種運算子且不可替換)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_strong_ordering.cpp">strong_ordering(三路比較的結果型別，支援所有 6 種運算子且可替換)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_is_eq.cpp">is_eq(具名比較函式)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_is_neq.cpp">is_neq(具名比較函式)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_is_lt.cpp">is_lt(具名比較函式)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_is_lteq.cpp">is_lteq(具名比較函式)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_is_gt.cpp">is_gt(具名比較函式)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_is_gteq.cpp">is_gteq(具名比較函式)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_compare_three_way.cpp">compare_three_way(實現 x <=> y 的函式物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_compare_three_way_result.cpp">compare_three_way_result(獲得三路比較運算子 <=> 在給定型別上的結果)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_common_comparison_category.cpp">common_comparison_category(給定的全部型別都能轉換到的最強比較類別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_strong_order.cpp">strong_order(進行三路比較併產生 std::strong_ordering 型別結果)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_weak_order.cpp">weak_order(進行三路比較併產生 std::weak_ordering 型別結果)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_partial_order.cpp">partial_order(進行三路比較併產生 std::partial_ordering 型別結果)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_compare_strong_order_fallback.cpp">compare_strong_order_fallback(進行三路比較併產生 std::strong_ordering 型別的結果，即使 operator<=> 不可用)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_compare_weak_order_fallback.cpp">compare_weak_order_fallback(進行三路比較併產生 std::weak_ordering 型別的結果，即使 operator<=> 不可用)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/004_rtti_compare_compare_partial_order_fallback.cpp">compare_partial_order_fallback(進行三路比較併產生 std::partial_ordering 型別的結果，即使 operator<=> 不可用</a>

### <h5 id="cpp_headfile_concepts">Defined in header&lt;concepts&gt;</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/005_rtti_concepts_ranges_swap.cpp">ranges::swap(交換兩個物件的值)</a>

### <h5 id="cpp_headfile_utility">Defined in header&lt;utility&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/006_utility_cmp_equal.cpp">cmp_equal(比較二個整數值，而無轉換所致的值更改)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/006_utility_cmp_not_equal.cpp">cmp_not_equal(比較二個整數值，而無轉換所致的值更改)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/006_utility_cmp_less.cpp">cmp_less(比較二個整數值，而無轉換所致的值更改)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/006_utility_cmp_less_equal.cpp">cmp_less_equal(比較二個整數值，而無轉換所致的值更改)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/006_utility_cmp_greater_equal.cpp">cmp_greater_equal(比較二個整數值，而無轉換所致的值更改)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/006_utility_in_range.cpp">in_range(檢查整數值是否在給定整數型別的範圍內)</a>

<!--
### <h5 id="cpp_headfile_format">Defined in header&lt;format&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_format.cpp">format(在新 string 中存儲參數的格式化表示)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_format_to.cpp">format_to(通過輸出疊代器寫其參數的格式化表示)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_format_to_n.cpp">format_to_n(通過輸出疊代器寫其參數的格式化表示，不超出指定的大小)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_formatted_size.cpp">formatted_size(確定存儲其參數的格式化表示所需的字符數)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_vformat.cpp">vformat(std::format 的使用型別擦除的參數表示的非樣板變體)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_vformat_to.cpp">vformat_to(std::format_to 的使用型別擦除的參數表示的非樣板變體)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_formatter.cpp">formatter(定義給定型別的格式化規則的類樣板)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_format_error.cpp">format_error(格式化錯誤時拋出的異常型別)</a>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_basic_format_arg.cpp">basic_format_arg(提供對用戶定義格式化器的格式化參數的訪問的類樣板)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_basic_format_parse_context.cpp">basic_format_parse_context(格式化字串分析器狀態)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_format_parse_context.cpp">format_parse_context(格式化字串分析器狀態)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_wformat_parse_context.cpp">wformat_parse_context(格式化字串分析器狀態)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_basic_format_context.cpp">basic_format_context(格式化狀態，包括所有格式化參數和輸出疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_format_context.cpp">format_context(格式化狀態，包括所有格式化參數和輸出疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_wformat_context.cpp">wformat_context(格式化狀態，包括所有格式化參數和輸出疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_visit_format_arg.cpp">visit_format_arg(用戶定義格式化器的參數觀覽介面)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_make_format_args.cpp">make_format_args(創建參照所有格式化參數的型別擦除物件，可轉換到 format_args)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_make_wformat_args.cpp">make_wformat_args(創建參照所有格式化參數的型別擦除物件，可轉換到 format_args)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_basic_format_args.cpp">basic_format_args(提供對所有格式化參數的訪問的類)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_format_args.cpp">format_args(提供對所有格式化參數的訪問的類)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/007_format_wformat_args.cpp">wformat_args(提供對所有格式化參數的訪問的類)</a>
-->

### <h5 id="cpp_headfile_memory">Defined in header&lt;memory&gt;</h5>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/008_memory_uninitialized_move.cpp">uninitialized_move(移動一個範圍的物件到未初始化的記憶體區域)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/008_memory_uninitialized_move_n.cpp">uninitialized_move_n(移動一定數量物件到未初始化記憶體區域)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/008_memory_uninitialized_default_construct.cpp">uninitialized_default_construct(在範圍所定義的未初始化的記憶體區域以預設初始化建構物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/008_memory_uninitialized_default_construct_n.cpp">uninitialized_default_construct_n(在起始和計數所定義的未初始化記憶體區域用預設初始化建構物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/008_memory_uninitialized_value_construct.cpp">uninitialized_value_construct(在範圍所定義的未初始化記憶體中用值初始化建構物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/008_memory_uninitialized_value_construct_n.cpp">uninitialized_value_construct_n(在起始和計數所定義的未初始化記憶體區域以值初始化建構物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/008_memory_destroy_at.cpp">destroy_at(銷燬在給定地址的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/008_memory_destroy.cpp">destroy(銷燬一個範圍中的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/008_memory_destroy_n.cpp">destroy_n(銷燬範圍中一定數量的物件)</a>

	
<!--
### <h5 id="cpp_headfile_concepts">Defined in header&lt;memory_resource&gt;</h5>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/009_memory_resource_polymorphic_allocator.cpp">polymorphic_allocator(以 std::memory_resource 建構，支援基於它的運行時多型的分配器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/009_memory_resource_memory_resource.cpp">memory_resource(一個抽象介面，用於各種封裝記憶體資源的類)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/009_memory_resource_new_delete_resource.cpp">new_delete_resource(返回一個靜態的程式範圍 std::pmr::memory_resource，它使用全局 operator new 與 operator delete 分配和解分配記憶體</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/009_memory_resource_null_memory_resource.cpp">null_memory_resource(返回一個不進行任何分配的靜態 std::pmr::memory_resource)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/009_memory_resource_get_default_resource.cpp">get_default_resource(獲取預設 std::pmr::memory_resource)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/009_memory_resource_set_default_resource.cpp">set_default_resource(設置預設 std::pmr::memory_resource)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/009_memory_resource_pool_options.cpp">pool_options(一組池資源的建構函式選項)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/009_memory_resource_synchronized_pool_resource.cpp">synchronized_pool_resource(執行緒安全的 std::pmr::memory_resource，用於管理具有不同塊大小的池中的分配)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/009_memory_resource_unsynchronized_pool_resource.cpp">unsynchronized_pool_resource(執行緒不安全的 std::pmr::memory_resource，用於管理具有不同塊大小的池中的分配)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/009_memory_resource_monotonic_buffer_resource.cpp">monotonic_buffer_resource(一種特殊用途的 std::pmr::memory_resource，僅在資源被銷燬時才釋放所分配記憶體)</a>	
-->

### <h3 id="cpp_20_compare">Concepts library(概念庫)</h3>

### <h5 id="cpp_headfile_concepts">Defined in header&lt;concepts&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_same_as.cpp">same_as(指定一個型別與另一型別相同)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_derived_from.cpp">derived_from(指定一個型別派生自另一型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_convertible_to.cpp">convertible_to(指定一個型別能隱式轉換成另一型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_common_reference_with.cpp">common_reference_with(指定兩個型別共有一個公共參照型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_common_with.cpp">common_with(指定兩個型別共有一個公共型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_integral.cpp">integral(指定型別為整型型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_signed_integral.cpp">signed_integral(指定型別為有符號的整型型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_unsigned_integral.cpp">unsigned_integral(指定型別為無符號的整型型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_floating_point.cpp">floating_point(指定型別為浮點型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_assignable_from.cpp">assignable_from(指定一個型別能從另一型別賦值)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_swappable.cpp">swappable(指定一個型別能進行交換，或兩個型別能彼此交換)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_swappable_with.cpp">swappable_with(指定一個型別能進行交換，或兩個型別能彼此交換)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_destructible.cpp">destructible(指定能銷燬該型別的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_constructible_from.cpp">constructible_from(指定該型別的變數能從一組實際參數型別進行建構，或綁定到一組實際參數型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_default_initializable.cpp">default_initializable(指定能預設建構一個型別的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_move_constructible.cpp">move_constructible(指定能移動建構一個型別的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_copy_constructible.cpp">copy_constructible(指定能複製建構和移動建構一個型別的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_boolean_testable.cpp">boolean-testable(指定能用於布爾語境的型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_equality_comparable.cpp">equality_comparable(指定運算子 == 為等價關係)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_equality_comparable_with.cpp">equality_comparable_with(指定運算子 == 為等價關係)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_totally_ordered.cpp">totally_ordered(指定比較運算子在該型別上產生全序)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_totally_ordered_with.cpp">totally_ordered_with(指定比較運算子在該型別上產生全序)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_movable.cpp">movable(指定能移動及交換一個型別的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_copyable.cpp">copyable(指定能複製、移動及交換一個型別的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_semiregular.cpp">semiregular(指定能賦值、移動、交換及預設建構一個型別的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_regular.cpp">regular(指定型別為正則，即它既為 semiregular 亦為 equality_comparable)</a>	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_invocable.cpp">invocable(指定能以給定的一組實際參數型別調用的可調用型別)</a>	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_regular_invocable.cpp">regular_invocable(指定能以給定的一組實際參數型別調用的可調用型別)</a>	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_predicate.cpp">predicate(指定可調用型別為布爾謂詞)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_relation.cpp">relation(指定可調用型別為二元關係)</a>	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_equivalence_relation.cpp">equivalence_relation(指定 relation 施加等價關係)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/010_concepts_strict_weak_order.cpp">strict_weak_order(指定一個 relation 所強加的是嚴格弱序)</a>

### <h3 id="cpp_20_memory">動態記憶體管理</h3>

### <h5 id="cpp_headfile_memory">Defined in header&lt;memory&gt;</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_uses_allocator_construction_args.cpp">uses_allocator_construction_args(準備匹配給定型別所要求的使用分配器建構的口味的參數列表)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_make_obj_using_allocator.cpp">make_obj_using_allocator(以使用分配器建構的手段創建給型別的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_uninitialized_construct_using_allocator.cpp">uninitialized_construct_using_allocator(以使用分配器建構的手段在指定的記憶體位元元置創建給定型別的物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_construct_at.cpp">construct_at(在給定地址創建物件)</a>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_no-throw-input-iterator.cpp">no-throw-input-iterator(指定疊代器、哨位元元和範圍上的某些操作不拋出)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_no-throw-forward-iterator.cpp">no-throw-forward-iterator(指定疊代器、哨位元元和範圍上的某些操作不拋出)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_no-throw-sentinel-for.cpp">no-throw-sentinel-for(指定疊代器、哨位元元和範圍上的某些操作不拋出)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_no-throw-input-range.cpp">no-throw-input-range(指定疊代器、哨位元元和範圍上的某些操作不拋出)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_no-throw-forward-range.cpp">no-throw-forward-range(指定疊代器、哨位元元和範圍上的某些操作不拋出)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_uninitialized_copy.cpp">ranges::uninitialized_copy(複製元素範圍到未初始化的記憶體區域)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_uninitialized_copy_n.cpp">ranges::uninitialized_copy_n(複製一定量元素到未初始化的記憶體區域)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_uninitialized_fill.cpp">ranges::uninitialized_fill(複製一個物件到範圍所定義的未初始化的記憶體區域)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_uninitialized_fill_n.cpp">ranges::uninitialized_fill_n(複製一個物件到起始與計數所定義的未初始化的記憶體區域)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_uninitialized_move.cpp">ranges::uninitialized_move(移動物件範圍到未初始化的記憶體區域)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_uninitialized_move_n.cpp">ranges::uninitialized_move_n(移動一定量物件到未初始化的記憶體區域)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_uninitialized_default_construct.cpp">ranges::uninitialized_default_construct(在範圍所定義的未初始化的記憶體區域以預設初始化建構物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_uninitialized_default_construct_n.cpp">ranges::uninitialized_default_construct_n(在起始與計數所定義的未初始化的記憶體區域以預設初始化建構物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_uninitialized_value_construct.cpp">ranges::uninitialized_value_construct(在範圍所定義的未初始化的記憶體區域以值初始化建構物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_uninitialized_value_construct_n.cpp">ranges::uninitialized_value_construct_n(在起始與計數所定義的未初始化的記憶體區域以值初始化建構物件)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_destroy_at.cpp">ranges::destroy_at(銷燬位元元於給定地址的元素)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_destroy.cpp">ranges::destroy(銷燬範圍中的元素)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_destroy_n.cpp">ranges::destroy_n(銷燬範圍中一定量的元素)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_ranges_construct_at.cpp">ranges::construct_at(在給定地址創建物件)</a>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_to_address.cpp">to_address(從指標式型別獲得裸指標)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/011_memory_assume_aligned.cpp">assume_aligned(告知編譯器指標已對齊)</a>

### <h3 id="cpp_20_memory">日期和時間工具</h3>

### <h5 id="cpp_headfile_chrono">Defined in header&lt;chrono&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_is_clock.cpp">is_clock(確定型別是否為時鐘 (Clock))</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_is_clock_v.cpp">is_clock_v(確定型別是否為時鐘 (Clock))</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_utc_clock.cpp">utc_clock(協調世界時 (UTC) 的時鐘 (Clock))</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_tai_clock.cpp">tai_clock(國際原子時 (TAI) 的時鐘 (Clock))</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_gps_clock.cpp">gps_clock(GPS 時間的時鐘 (Clock))</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_file_clock.cpp">file_clock(用於檔案時間的時鐘 (Clock))</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_local_t.cpp">local_t(表示本地時間的偽時鐘)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_clock_time_conversion.cpp">clock_time_conversion(定義如何轉換一個時鐘的時間點為另一個的特性類)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_clock_cast.cpp">clock_cast(轉換一個時鐘的時間點為另一個)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_time_of_day.cpp">time_of_day(表示一日中的時間)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_is_am.cpp">is_am(在 12 時和 24 時格式當天時刻之間翻譯)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_is_pm.cpp">is_pm(在 12 時和 24 時格式當天時刻之間翻譯)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_make12.cpp">make12(在 12 時和 24 時格式當天時刻之間翻譯)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_make24.cpp">make24(在 12 時和 24 時格式當天時刻之間翻譯)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_last_spec.cpp">last_spec(指示一個月中最後日期或星期的標籤類)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_day.cpp">day(表示月之日期)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_month.cpp">month(表示年之月份)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_year.cpp">year(表示格里高利曆中的年)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_weekday.cpp">weekday(表示格里高利曆中星期之日)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_weekday_indexed.cpp">weekday_indexed(表示月份的第 n 個 weekday)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_weekday_last.cpp">weekday_last(表示月份的最後一個 weekday)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_month_day.cpp">month_day(表示特定 month 的特定 day)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_month_day_last.cpp">month_day_last(表示特定 month 的最後一日)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_month_weekday.cpp">month_weekday(表示特定 month 的第 n 個 weekday)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_month_weekday_last.cpp">month_weekday_last(表示特定 month 的最後一個 weekday)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_year_month.cpp">year_month(表示特定 year 的特定 month)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_year_month_day.cpp">year_month_day(表示特定的 year 、 month 和 day)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_year_month_day_last.cpp">year_month_day_last(表示特定 year 和 month 的最後一日)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_year_month_weekday.cpp">year_month_weekday(表示特定 year 和 month 的第 n 個 weekday)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_year_month_weekday_last.cpp">year_month_weekday_last(表示特定 year 和 month 的最後一個 weekday)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_operator.cpp">operator/(創建格里高利曆日期的約定語法)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_tzdb.cpp">tzdb(描述 IANA 時區資料庫的副本)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_tzdb_list.cpp">tzdb_list(表示 tzdb 的鏈結串列)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_get_tzdb.cpp">get_tzdb(訪問和控制全球時區資料庫資訊)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_get_tzdb_list.cpp">get_tzdb_list(訪問和控制全球時區資料庫資訊)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_reload_tzdb.cpp">reload_tzdb(訪問和控制全球時區資料庫資訊)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_remote_version.cpp">remote_version(訪問和控制全球時區資料庫資訊)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_locate_zone.cpp">locate_zone(定位元元基於其名稱的 time_zone)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_current_zone.cpp">current_zone(返回當前的 time_zone)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_time_zone.cpp">time_zone(表示時區)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_sys_info.cpp">sys_info(表示在特定時間點的關於時區的資訊)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_local_info.cpp">local_info(表示關於從本地時間轉換到 UNIX 時間的資訊)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_choose.cpp">choose(選擇應如何解析歧義的本地時間)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_zoned_traits.cpp">zoned_traits(zoned_time 所用的時區指標的特性類)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_zoned_time.cpp">zoned_time(表示時區和時間點)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_leap_second.cpp">leap_second(含有關於插入閏秒的資訊)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_time_zone_link.cpp">time_zone_link(表示時區的替用名)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_nonexistent_local_time.cpp">nonexistent_local_time(拋出以報告本地時間不存在的異常)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_ambiguous_local_time.cpp">ambiguous_local_time(拋出以報告本地時間有歧義的異常)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/012_chrono_parse.cpp">parse(從流分析 chrono 物件)</a>
	
### <h3 id="cpp_20_string">字串</h3>

### <h5 id="cpp_headfile_string">Defined in header&lt;string&gt;</h5>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/013_string_starts_with.cpp">starts_with(檢查 string 是否始於給定前綴)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/013_string_ends_with.cpp">ends_with(檢查 string 是否終於給定後綴)</a>
	
### <h5 id="cpp_headfile_string_view">Defined in header&lt;string_view&gt;</h5>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/014_string_view_starts_with.cpp">starts_with(檢查 string_view 是否始於給定前綴)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/014_string_view_ends_with.cpp">ends_with(檢查 string_view 是否終於給定後綴)</a>
	
### <h5 id="cpp_headfile_cuchar">Defined in header&lt;cuchar&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/015_cuchar_mbrtoc8.cpp">mbrtoc8(轉換窄多位元元組字符為 UTF-8 編碼)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/015_cuchar_c8rtomb.cpp">c8rtomb(轉換 UTF-8 字串為窄多位元元組編碼)</a>	

### <h3 id="cpp_20_Containers_library">容器庫</h3>

### <h5 id="cpp_headfile_array">Defined in header&lt;array&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/016_array_to_array.cpp">to_array(從內建陣列創建 std::array 物件)</a>

### <h5 id="cpp_headfile_vector">Defined in header&lt;vector&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/017_vector_erase.cpp">erase(std::vector)(擦除所有滿足特定判別標準的元素)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/017_vector_erase_if.cpp">erase_if(std::vector)(擦除所有滿足特定判別標準的元素)</a>

### <h5 id="cpp_headfile_map">Defined in header&lt;map&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/018_map_contains.cpp">contains(檢查容器是否含有帶特定鍵的元素)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/018_map_erase_if.cpp">erase_if(std::map)(擦除所有滿足特定判別標準的元素)</a>

### <h5 id="cpp_headfile_unordered_map">Defined in header&lt;unordered_map&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/019_unordered_map_contains.cpp">contains(檢查容器是否含有帶特定鍵的元素)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/019_unordered_map_erase_if.cpp">erase_if(std::unordered_map)(擦除所有滿足特定判別標準的元素)</a>

### <h5 id="cpp_headfile_span">Defined in header&lt;span&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/020_span_begin.cpp">begin(返回指向起始的疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/020_span_end.cpp">end(返回指向末尾的疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/020_span_rbegin.cpp">rbegin(返回指向起始的逆向疊代器)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/020_span_rend.cpp">rend(返回指向末尾的逆向疊代器)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/020_span_front.cpp">front(訪問第一個元素)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/020_span_back.cpp">back(訪問最後一個元素)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/020_span_dynamic_extent.cpp">dynamic_extent(size_t 型別常數，指明 span 擁有動態長度)</a>

### <h5 id="cpp_headfile_span">Defined in namespace std</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_indirectly_readable.cpp">indirectly_readable(指定型別通過應用運算子 * 可讀)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_indirectly_writable.cpp">indirectly_writable(指定可向疊代器所參照的物件寫入值)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_weakly_incrementable.cpp">weakly_incrementable(指定 semiregular 型別能以前後自增運算子自增)</a> 	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_incrementable.cpp">incrementable(指定 weakly_incrementable 型別上的自增操作保持相等性，而且該型別為 equality_comparable)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_input_or_output_iterator.cpp">input_or_output_iterator(指定該型別物件可以自增且可以解參照)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_sentinel_for.cpp">sentinel_for(指定型別為某個 input_or_output_iterator 型別的哨位元元型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_sized_sentinel_for.cpp">sized_sentinel_for(指定可對一個疊代器和一個哨位元元應用 - 運算子，以在常數時間計算其距離)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_input_iterator.cpp">input_iterator(指定型別為輸入疊代器，即可讀取其所參照的值，且可前/後自增)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_output_iterator.cpp">output_iterator(指定型別為給定的值型別的輸出疊代器，即可向其寫入該型別的值，且可前/後自增)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_forward_iterator.cpp">forward_iterator(指定 input_iterator 為向前疊代器，支援相等比較與多趟操作)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_bidirectional_iterator.cpp">bidirectional_iterator(指定 forward_iterator 為雙向疊代器，支援向後移動)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_random_access_iterator.cpp">random_access_iterator(指定 bidirectional_iterator 為隨機訪問疊代器，支援常數時間內的前進和下標訪問)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_contiguous_iterator.cpp">contiguous_iterator(指定 random_access_iterator 為連續疊代器，指代記憶體中連續相接的元素)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_indirectly_readable_traits.cpp">indirectly_readable_traits(計算 indirectly_readable 型別的值型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_iter_value_t.cpp">iter_value_t(計算疊代器的關聯型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_iter_reference_t.cpp">iter_reference_t(計算疊代器的關聯型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_iter_difference_t.cpp">iter_difference_t(計算疊代器的關聯型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_iter_rvalue_reference_t.cpp">iter_rvalue_reference_t(計算疊代器的關聯型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_iter_common_reference_t.cpp">iter_common_reference_t(計算疊代器的關聯型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_iterator_traits.cpp">iterator_traits(為疊代器各項性質提供統一介面)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_input_iterator_tag.cpp">input_iterator_tag(用於指示疊代器類別的空類型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_output_iterator_tag.cpp">output_iterator_tag(用於指示疊代器類別的空類型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_forward_iterator_tag.cpp">forward_iterator_tag(用於指示疊代器類別的空類型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_bidirectional_iterator_tag.cpp">bidirectional_iterator_tag(用於指示疊代器類別的空類型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_random_access_iterator_tag.cpp">random_access_iterator_tag(用於指示疊代器類別的空類型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/021_std_contiguous_iterator_tag.cpp">contiguous_iterator_tag(用於指示疊代器類別的空類型別)</a> 

### <h5 id="cpp_headfile_span">Defined in namespace std::ranges</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/022_ranges_iter_move.cpp">iter_move(將解參照疊代器的結果轉型為其關聯的右值參照型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/022_ranges_iter_swap.cpp">iter_swap(交換兩個可解參照物件所參照的值)</a> 

### <h5 id="cpp_headfile_span">Defined in namespace std</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_indirectly_readable.cpp">indirectly_readable(指定型別通過應用運算子 * 可讀)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_indirectly_writable.cpp">indirectly_writable(指定可向疊代器所參照的物件寫入值)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_weakly_incrementable.cpp">weakly_incrementable(指定 semiregular 型別能以前後自增運算子自增)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_incrementable.cpp">incrementable(指定 weakly_incrementable 型別上的自增操作保持相等性，而且該型別為 equality_comparable)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_input_or_output_iterator.cpp">input_or_output_iterator(指定該型別物件可以自增且可以解參照)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_sentinel_for.cpp">sentinel_for(指定型別為某個 input_or_output_iterator 型別的哨位元元型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_sized_sentinel_for.cpp">sized_sentinel_for(指定可對一個疊代器和一個哨位元元應用 - 運算子，以在常數時間計算其距離)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_input_iterator.cpp">input_iterator(指定型別為輸入疊代器，即可讀取其所參照的值，且可前/後自增)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_output_iterator.cpp">output_iterator(指定型別為給定的值型別的輸出疊代器，即可向其寫入該型別的值，且可前/後自增)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_forward_iterator.cpp">forward_iterator(指定 input_iterator 為向前疊代器，支援相等比較與多趟操作)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_bidirectional_iterator.cpp">bidirectional_iterator(指定 forward_iterator 為雙向疊代器，支援向後移動)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_random_access_iterator.cpp">random_access_iterator(指定 bidirectional_iterator 為隨機訪問疊代器，支援常數時間內的前進和下標訪問)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_contiguous_iterator.cpp">contiguous_iterator(指定 random_access_iterator 為連續疊代器，指代記憶體中連續相接的元素)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_incrementable_traits.cpp">incrementable_traits(計算 weakly_incrementable 型別的差型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_indirectly_readable_traits.cpp">indirectly_readable_traits(計算 indirectly_readable 型別的值型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_iter_value_t.cpp">iter_value_t(計算疊代器的關聯型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_iter_reference_t.cpp">iter_reference_t(計算疊代器的關聯型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_iter_difference_t.cpp">iter_difference_t(計算疊代器的關聯型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_iter_rvalue_reference_t.cpp">iter_rvalue_reference_t(計算疊代器的關聯型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_iter_common_reference_t.cpp">iter_common_reference_t(計算疊代器的關聯型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_iterator_traits.cpp">iterator_traits(為疊代器各項性質提供統一介面)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_input_iterator_tag.cpp">input_iterator_tag(用於指示疊代器類別的空類型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_output_iterator_tag.cpp">output_iterator_tag(用於指示疊代器類別的空類型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_forward_iterator_tag.cpp">forward_iterator_tag(用於指示疊代器類別的空類型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_bidirectional_iterator_tag.cpp">bidirectional_iterator_tag(用於指示疊代器類別的空類型別)</a>	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_random_access_iterator_tag.cpp">random_access_iterator_tag(用於指示疊代器類別的空類型別)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/023_std_contiguous_iterator_tag.cpp">contiguous_iterator_tag(用於指示疊代器類別的空類型別)</a>
	
### <h5 id="cpp_headfile_span">Defined in header <iterator></h5>
### <h5 id="cpp_headfile_span">Defined in namespace std</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirectly_unary_invocable.cpp">indirectly_unary_invocable(指定可調用型別能以解參照某個 indirectly_readable 型別的結果進行調用)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirectly_regular_unary_invocable.cpp">indirectly_regular_unary_invocable(指定可調用型別能以解參照某個 indirectly_readable 型別的結果進行調用)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirect_unary_predicate.cpp">indirect_unary_predicate(指定可調用型別，在以解參照一個 indirectly_readable 型別的結果進行調用時，滿足 predicate)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirect_binary_predicate.cpp">indirect_binary_predicate(指定可調用型別，在以解參照兩個 indirectly_readable 型別的結果進行調用時，滿足 predicate)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirect_equivalence_relation.cpp">indirect_equivalence_relation(指定可調用型別，在以解參照兩個 indirectly_readable 型別的結果進行調用時，滿足 equivalence_relation)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirect_strict_weak_order.cpp">indirect_strict_weak_order(指定可調用型別，在以解參照兩個 indirectly_readable 型別的結果進行調用時，滿足 strict_weak_order)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirectly_movable.cpp">indirectly_movable(指定可從 indirectly_readable 型別移動值給 indirectly_writable 型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirectly_movable_storable.cpp">indirectly_movable_storable(指定可從 indirectly_readable 型別移動值給 indirectly_writable 型別，且該移動可以通過中間物件進行)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirectly_copyable.cpp">indirectly_copyable(指定可從 indirectly_readable 型別複製值給 indirectly_writable 型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirectly_copyable_storable.cpp">indirectly_copyable_storable(指定可從 indirectly_readable 型別複製值給 indirectly_writable 型別，且該複製可以通過中間物件進行)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirectly_swappable.cpp">indirectly_swappable(指定能交換兩個 indirectly_readable 型別所參照的值)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirectly_comparable.cpp">indirectly_comparable(指定能比較兩個 indirectly_readable 型別所參照的值)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_permutable.cpp">permutable(指定在原位元元重排元素的演演算法的共用要求)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_mergeable.cpp">mergeable(指定通過複製元素將已排序序列歸併到輸出序列中的演演算法的要求)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_sortable.cpp">sortable(指定重排序列為有序序列的演演算法的共用要求)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_indirect_result_t.cpp">indirect_result_t(計算在解參照某組 indirectly_readable 型別的結果上調用可調用物件的結果)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_projected.cpp">projected(用於對接受投影的演演算法指定約束的輔助樣板)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_move_sentinel.cpp">move_sentinel(用於 std::move_iterator 的哨位元元適配器)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_common_iterator.cpp">common_iterator(適配一個疊代器型別及其哨位元元為一個公共疊代器型別)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_default_sentinel_t.cpp">default_sentinel_t(用於知曉其邊界的疊代器的預設哨位元元)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_counted_iterator.cpp">counted_iterator(對到範圍結尾距離進行跟蹤的疊代器適配器)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/024_iterator_unreachable_sentinel_t.cpp">unreachable_sentinel_t(始終與任何 weakly_incrementable 型別比較都不相等的哨位元元)</a> 

### <h5 id="cpp_headfile_span">Defined in header <iterator></h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/025_iterator_ranges_advanc.cpp">ranges::advance(令疊代器前進給定的距離或到給定的邊界)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/025_iterator_ranges_distance.cpp">ranges::distance(返回疊代器與哨位元元間的距離，或範圍起始與結尾間的距離)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/025_iterator_ranges_next.cpp">ranges::next(自增疊代器給定的距離或到邊界)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/025_iterator_ranges_prev.cpp">ranges::prev(自減疊代器給定的距離或到邊界)</a> 

### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;array&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;deque&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;forward_list&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;iterator&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;list&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;map&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;regex&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;set&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;span&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;string&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;string_view&gt;</h5>	
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;unordered_map&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;unordered_set&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in header &lt;vector&gt;</h5>
### <h5 id="cpp_headfile_initializer_list">Defined in namespace std</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/026_std_ssize.cpp">ssize(返回容器或陣列的大小)</a> 

### <h5 id="cpp_headfile_span">Defined in header &lt;ranges&gt;</h5>
### <h5 id="cpp_headfile_span">Defined in header &lt;iterator&gt;</h5>
### <h5 id="cpp_headfile_span">Defined in namespace std::ranges</h5>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_begin.cpp">ranges::begin(返回指向範圍起始的疊代器)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_cbegin.cpp">ranges::cbegin(返回指向只讀範圍起始的疊代器)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_end.cpp">ranges::end(返回指示範圍結尾的哨位元元)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_cend.cpp">ranges::cend(返回指示只讀範圍結尾的哨位元元)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_rbegin.cpp">ranges::rbegin(返回指向範圍的逆向疊代器)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_crbegin.cpp">ranges::crbegin(返回指向只讀範圍的逆向疊代器)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_rend.cpp">ranges::rend(返回指向範圍的逆向尾疊代器)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_crend.cpp">ranges::crend(返回指向只讀範圍的逆向尾疊代器)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_size.cpp">ranges::size(獲得能在常數時間內計算大小的範圍的大小)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_ssize.cpp">ranges::ssize(獲得能在常數時間內計算大小的範圍的大小，並將它轉換成有符號整數)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_empty.cpp">ranges::empty(檢查範圍是否為空)</a> 
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_data.cpp">ranges::data(獲得指向連續範圍的起始的指標)</a> 	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_20/027_ranges_ranges_cdata.cpp">ranges::cdata(獲得指向只讀連續範圍的起始的指標)</a> 


-----
	
<div id="cpp_23" align=center>
	
<img width="30%" height="30%" src="https://user-images.githubusercontent.com/87457873/134302554-85d6bf7c-1e1d-4579-8141-8a4c3e8d92e2.jpg"/>

</div>		
	
### <h3 id="cpp_23_RTTI">型別支援（基本型別、RTTI、型別特性）</h3>

### <h5 id="cpp_headfile_type_traits">Defined in header&lt;type_traits&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/001_rtti_is_scoped_enum.cpp">is_scoped_enum(檢查型別是否為有作用域列舉型別)</a>

### <h5 id="cpp_headfile_utility">Defined in header&lt;utility&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/002_utility_to_underlying.cpp">to_underlying(轉換列舉到其底層型別)</a>

### <h5 id="cpp_headfile_stacktrace">Defined in header&lt;stacktrace&gt;</h5>

* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/003_stacktrace_stacktrace_entry.cpp">stacktrace_entry(棧蹤中求值的表示)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/003_stacktrace_basic_stacktrace.cpp">basic_stacktrace(由棧蹤條目組成的調用序列的近似表示)</a>

### <h3 id="cpp_23_memory">動態記憶體管理</h3>

### <h5 id="cpp_headfile_memory">Defined in header&lt;memory&gt;</h5>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/004_memory_out_ptr_t.cpp">out_ptr_t(與外來指標設置器交互，並在解構時重設智慧指標)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/004_memory_out_ptr.cpp">out_ptr(以關聯的智慧指標和重設參數創建 out_ptr_t)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/004_memory_inout_ptr_t.cpp">inout_ptr_t(與外來指標設置器交互，從智慧指標獲得初始指標值，並在解構時重設它)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/004_memory_inout_ptr.cpp">inout_ptr(以關聯的智慧指標和重設參數創建 inout_ptr_t)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/004_memory_allocation_result.cpp">allocation_result(記錄由 allocate_at_least 分配的存儲的地址與實際大小)</a>
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/004_memory_allocate_at_least.cpp">allocate_at_least(經由分配器分配至少與請求的大小一樣大的存儲)</a>
	
### <h3 id="cpp_23_string">字串</h3>

### <h5 id="cpp_headfile_string">Defined in header&lt;string&gt;</h5>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/005_string_contains.cpp">contains(檢查字串是否含有給定的子串或字符)</a>

### <h5 id="cpp_headfile_string_view">Defined in header&lt;string_view&gt;</h5>
	
* <a href="https://github.com/0voice/cpp_new_features/blob/main/cpp_23/005_string_view_contains.cpp">contains(檢查字串視圖是否含有給定的子串或字符)</a>

---


## 聯繫專欄

#### 零聲教育，專注於c/c++Linux後臺伺服器開發架構技術學習提升。<br>
每天晚上8點【免費技術直播】：[分享Linux，Nginx，ZeroMQ，MySQL，Redis，fastdfs，MongoDB，ZK，流媒體，CDN，P2P，K8S，Docker，TCP/IP，協程，DPDK等技術內容，立即學習。](https://ke.qq.com/course/417774?flowToken=1037711)

#### 關注微信公眾號【後臺服務架構師】——【聯繫我們】，獲取本repo最全PDF學習文件！

<img width="65%" height="65%" src="https://user-images.githubusercontent.com/87457873/130796999-03af3f54-3719-47b4-8e41-2e762ab1c68b.png"/>
