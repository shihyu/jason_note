# 第9章 並行和併發

C++11之前，C++原生不支持併發和併發。但這並不意味著無法對線程進行操作，只不過需要使用系統庫的API進行操作(因為線程與操作系統是不可分開的)。

隨著C++11標準的完成，我們有了`std::thread`，其能給予我們可以在所有操作系統上可移植的線程操作。為了同步線程，C++11也添加了互斥量，並且對一些RAII類型的鎖進行了封裝。另外，`std::condition_variable`也能夠靈活的在線程間，進行喚醒操作。

另一些有趣的東西就是`std::async`和`std::future`——我們可以將普通的函數封裝到`std::async`中，可以在後臺異步的運行這些函數。包裝後函數的返回值則用`std::future`來表示，函數的結果將會在運行完成後，放入這個對象中，所以可以在函數完成前，做點別的事情。

另一個STL中值得一提提升就是*執行策略*，其被添加到已有的69種算法中。這樣就可以對現有的STL算法不做任何修改，就能享受其並行化帶來的性能提升。

本章中，我們將通過例子來瞭解其中最為核心的部分。之後，我們也將瞭解到C++17對並行的支持。不會覆蓋所有的細節，但是比較重要的部分肯定會介紹。本書會快速的幫助你瞭解並行編程機制，至於詳細的介紹，可以在線對C++17 STL文檔進行查閱。

最後，本章中最後兩節值的注意。倒數第二節中，我們將並行化[第6章的ASCII曼德爾布羅特渲染器](content/chapter6/chapter6-5-chinese.md)，使用STL進階用法讓代碼改動程度最小。最後一節中，我們將實現一個簡單的庫，其可以用來隱式並行複雜的任務。





