# 現代的 CMake 的介紹

人們喜愛討厭構建系統。
CppCon17 的講座就是一個開發者們將構建系統當成頭等笑話的例子。
這引出了一個問題：為什麼（人們這樣認為）？
確實，使用構建系統構建項目時不乏這樣那樣的問題。
但我認為，在 2020 年，我們有一個非常好的解決方案來消除其中的一些問題。
那就是 CMake 。但不是 CMake 2.8 ，它比 c++11 還要早出現。
也不是那些糟糕的 CMake 例程（甚至包括那些 KitWare 自己的教程裡發佈的例子）。
我指的是現代的 CMake 。是 CMake 3.4+ ，甚至是 CMake 3.21+ ！
它簡潔、強大、優雅，所以你能夠花費你的大部分時間在編寫代碼上，而不是在一個不可讀、不可維護的 Make （或 CMake 2） 文件上浪費時間。
並且 CMake 3.11+ 的構建速度應該也會更加的快！！！

{% hint style='working' %}
本書是一篇持續維護的文檔。你可以在 [GitLab](https://gitlab.com/CLIUtils/modern-cmake) 上提 issue 或是 合併請求。
你也可以 [下載PDF](https://CLIUtils.gitlab.io/modern-cmake/modern-cmake.pdf) 格式的副本。請務必查看一下 [HSF CMake Training](https://hsf-training.github.io/hsf-training-cmake-webpage/01-intro/index.html) （也是一個 CMake 教程）!
{% endhint %}

簡而言之, 如果你正在考慮使用Modern CMake，以下是你心中最可能存在的問題:

## 為什麼我需要一個好的構建系統？

以下情況是否適用於你？

* 你想避免將路徑硬編碼
* 你需要在不止一臺電腦上構建軟件包
* 你想在項目中使用CI（持續集成）
* 你需要支持不同的操作系統（甚至可能只是Unix的不同版本）
* 你想支持多個編譯器
* 你想使用IDE，但也許不總是使用
* 你想從邏輯上描述你的程序是如何結構的，而不是通過某些標誌和命令
* 你想使用一個第三方庫
* 你想使用工具，比如Clang-Tidy，來幫助你編碼
* 你想使用調試器來debug

如果是這樣，你會從類似CMake的構建系統中受益。

## 為什麼答案一定是CMake？

構建系統是一個熱門話題。當然，有很多構建系統可選。但是，即使是一個真的非常好的構建系統，或者一個使用類似（CMake）的語法的，也不能達到 CMake 的使用體驗。
為什麼？
因為生態。
每個 IDE 都支持 CMake（或者是 CMake 支持那個 IDE）。
使用 CMake 構建的軟件包比使用其他任何構建系統的都多。
所以，如果你想要在你的代碼中包含一個庫，你有兩個選擇，要麼自己寫一個構建系統，要麼使用該庫支持的構建系統中的某個。而那通常包含 CMake。
如何你的工程包含的庫多了，CMake 或很快成為那些庫所支持的構建系統的交集。並且，如果你使用一個預裝在系統中的庫，它有很大可能有一個 find CMake 或者是一個 config CMake 的腳本。


## 為什麼使用現代的 CMake ？

大概在 CMake 2.6-2.8 時， CMake 開始成為主流。它出現在大多數 Linux 操作系統的包管理器中，並被用於許多包中。

接著 Python 3 出現了。

這是一個直到現在某些的工程中進行的非常艱難、醜陋的遷移。

我知道，這和 CMake 沒有任何關係。

但它們有一個 3 ,並且都跟在 2 後面。


所以我相信 CMake 3 跟在 Python 3 後面真是十分倒黴。[^1]
因為儘管每一個版本的CMake都有良好的向後兼容性，但 CMake 3 卻總是被當作新事物來對待。
你會發現像 CentOS7 這樣的操作系統，其上的 GCC 4.8幾乎完全支持 C++14 ，而 CMake 則是在 C++11 之前幾年就已經出現的 CMake 2.8 。

你應該至少使用在你的編譯器之後出現的 CMake 版本，因為它需要知道該版本的編譯器標誌等信息。
而且，由於只會CMake會啟用CMakeLists.txt中的生命力的最低CMake版本所對應的特性，所以即使是在系統範圍內安裝一個新版本的CMake也是相當安全的。
你至少應該在本地安裝它。這很容易（在許多情況下是 1-2 行命令），你會發現 5 分鐘的工作將為你節省數百行和數小時的 CMakeLists.txt 編寫，而且從長遠來看，將更容易維護。

本書試圖解決那些網上氾濫的糟糕例子和所謂”最佳實踐“存在的問題。

## 其他資料

本書原作者的其他資料:

* [HSF CMake Training](https://hsf-training.github.io/hsf-training-cmake-webpage/01-intro/index.html)
* [Interactive Modern CMake talk](https://gitlab.com/CLIUtils/modern-cmake-interactive-talk)

在網上還有一些其他的地方可以找到好的資訊。下面是其中的一些:

* [The official help](https://cmake.org/cmake/help/latest/): 非常棒的文檔。組織得很好，有很好的搜索功能，而且你可以在頂部切換版本。它只是沒有一個很好的 “最佳實踐教程”，而這正是本書試圖解決的內容。
* [Effective Modern CMake](https://gist.github.com/mbinna/c61dbb39bca0e4fb7d1f73b0d66a4fd1): 
一個很好的 do's and don'ts 的清單。
* [Embracing Modern CMake](https://steveire.wordpress.com/2017/11/05/embracing-modern-cmake/): 一篇對術語有很好描述的文章。
* [It's time to do CMake Right](https://pabloariasal.github.io/2018/02/19/its-time-to-do-cmake-right/): 一些現代的 CMake 項目的最佳實踐。
* [The Ultimate Guide to Modern CMake](https://rix0r.nl/blog/2015/08/13/cmake-guide/): 一篇有著本書類似目的稍顯過時的文章。
* [More Modern CMake](https://youtu.be/y7ndUhdQuU8): 來自 Meeting C++ 2018 的一個很棒的演講，推薦使用 CMake 3.12 以上版本。該演講將 CMake 3.0+ 稱為 “現代 CMake”，將 CMake 3.12+ 稱為 “更現代的 CMake”。
* [Oh No! More Modern CMake](https://www.youtube.com/watch?v=y9kSr5enrSk): More Modern CMake 的續篇。
* [toeb/moderncmake](https://github.com/toeb/moderncmake): 關於 CMake 3.5+ 的很好的介紹和例子，包括從語法到項目組織的介紹。

## 製作

Modern CMake 最初由 [Henry Schreiner](https://iscinumpy.gitlab.io) 編寫. 其他的貢獻者可以在 [Gitlab的列表](https://gitlab.com/CLIUtils/modern-cmake/-/network/master) 中找到.

[HSF CMake Training]: https://hsf-training.github.io/hsf-training-cmake-webpage/01-intro/index.html

[^1]: CMake 3.0 同樣從非常老的CMake版本中刪除了幾個早已廢棄的功能，並對與方括號有關的語法做了一個非常微小的向後不兼容的修改，所以這個說法並不完全公正；可能有一些非常非常老的CMake文件會在 CMake 3.0+ 中停止工作，但我從未遇到過。
