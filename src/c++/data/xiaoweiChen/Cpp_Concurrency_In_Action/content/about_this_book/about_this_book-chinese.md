# 關於這本書

本書是併發和多線程機制指導書籍(基於C++11標準)。從最基本的`std::thread std::mutex`和`std::async`的使用，到複雜的原子操作和內存模型。

## 路線圖

前4章，介紹了標準庫提供的各種庫工具，展示了使用方法。

第5章，涵蓋了底層內存模型和原子操作的實際情況，包括原子操作如何對執行順序進行限制(這章標誌著介紹部分的結束)。

第6、7章，開始討論高級主題，如何使用基本工具去構建複雜的數據結構——第6章是基於鎖的數據結構，第7章是無鎖數據結構。

第8章，對設計多線程代碼給了一些指導意見，覆蓋了性能問題和並行算法。

第9章，線程管理——線程池，工作隊列和中斷操作。

第10章，測試和調試——Bug類型，定位Bug的技巧，以及如何進行測試等等。

附錄，包括新的語言特性的簡要描述，主要是與多線程相關的特性，以及在第4章中提到的消息傳遞庫的實現細節和C++11線程庫的完整的參考。

## 誰應該讀這本書

如果你正在用C++寫一個多線程程序，你應該閱讀本書。如果你正在使用C++標準庫中新的多線程工具，你可以從本書中得到一些指導意見。如果你正在使用其他線程庫，後面章節裡的建議和技術指導也很值得一看。

閱讀本書需要你有較好的C++基礎；雖然，關於多線程編程的知識或者經驗不是必須的，不過這些經驗可能有用。

### 如何使用這本書

如果從來沒有寫過多線程代碼，我建議你從頭到尾閱讀本書；不過，可以跳過第5章中的較為細節的部分。第7章內容依賴於第5章中的內容，因此，如果跳過了第5章，應該保證在讀第7章時，已經讀過第5章。

如果沒有用過C++11的工具，為了跟上這本書的進度，可以先閱讀一下附錄。新工具的使用在文本中已經標註出來，不過，當遇到一些沒見過的工具時，可以隨時回看附錄。

即使有不同環境下寫多線程代碼的經驗，開始的章節仍有必要瀏覽一下，這樣就能清楚地知道，你所熟知的工具在新的C++標準中對應了哪些工具。如果使用原子變量去做一些底層工作，第5章必須閱讀。第8章，有關C++多線程的異常和安全性的內容很值得一看。如果你對某些關鍵詞比較感興趣，索引和目錄能夠幫你快速找到相關的內容。

你可能喜歡回顧主要的章節，並用自己的方式閱讀示例代碼。雖然你已經瞭解C++線程庫，但附錄D還是很有用。例如，查找每個類和函數的細節。

## 代碼公約和下載

為了區分普通文本，清單和正文中的中的所有代碼都採用`像這樣的固定寬度的字體`。許多清單都伴隨著代碼註釋，突出顯示重要的概念。在某些情況下，你可以通過頁下給出的快捷鏈接進行查閱。

本書所有實例的源代碼，可在出版商的網站上進行下載：www.manning.com/cplusplusconcurrencyinaction。

### 軟件需求

使用書中的代碼，可能需要一個較新的C++編譯器(要支持C++11語言的特性(見附錄A))，還需要C++支持標準線程庫。

寫本書的時候，g++是唯一實現標準線程庫的編譯器(儘管Microsoft Visual Studio 2011 preview中也有實現)。g++4.3發佈時添加了線程庫，並且在隨後的發佈版本中進行擴展。g++4.3也支持部分C++11語言特性，更多特性的支持在後續發佈版本中也有添加。更多細節請參考g++ C++11的狀態頁面[1]。

Microsoft Visual Studio 2010支持部分C++11特性，例如：右值引用和lambda函數，但是沒有實現線程庫。

我的公司Software Solutions Ltd，銷售C++11標準線程庫的完整實現，其可以使用在Microsoft Visual Studio 2005, Microsoft Visual Studio 2008, Microsoft Visual Studio 2010，以及各種g++版本上[2]。這個線程庫也可以用來測試本書中的例子。

Boost線程庫[3]提供的API，以及可移植到多個平臺。本書中的大多數例子將`std::`替換為`boost::`，再`#include`引用適當的頭文件，就能使用Boost線程庫來運行。還有部分工具還不支持(例如`std::async`)或在Boost線程庫中有著不同名字(例如：`boost::unique_future`)。

## 作者在線

購買*C++ Concurrency in Action*就能訪問曼寧(*Manning Publications*)的私人網絡論壇，在那裡可以對本書做一些評論，問一些技術問題，獲得作者或其他讀者的幫助。為了能夠訪問論壇和訂閱它的內容，在瀏覽器地址中輸入www.manning.com/CPlusPlusConcurrencyinAction後，頁面將告訴你如何註冊之後訪問論壇，你能獲得什麼樣的幫助，還有論壇中的一些規則。

曼寧保證為本書的讀者提供互相交流，以及和作者交流的場所。雖然曼寧自願維護本書的論壇，但不保證這樣的場所不會收取任何的費用。所以，建議你可以嘗試提一些有挑戰性的問題給作者，免得這樣的地方白白浪費。

在本書印刷時，就可以通過Internet訪問作者的在線論壇和之前討論的文字記錄。

----------


【1】GNU Compiler Collection C++0x/C++11 status page, http://gcc.gnu.org/projects/cxx0x.html.

【2】The `just::thread` implementation of the C++ Standard Thread Library, http://www.stdthread.co.uk.

【3】The Boost C++ library collection, http://www.boost.org.