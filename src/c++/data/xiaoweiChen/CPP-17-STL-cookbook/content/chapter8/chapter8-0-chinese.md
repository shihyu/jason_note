# 第8章 工具類

本章將關注工具類，這些類能幫助我們很快地解決一些特定的任務。有些工具類我們將會在本書後續的章節中經常使用。

前兩節與時間測量有關，我們將瞭解到如何在兩種不同的時間單位間互相轉換，並如何確定兩個時間點。

然後，我瞭解一下`optional`、`variant`和`any`類型(都是在C++14和C++17中添加的新類)，在接下來的5節中，我們將介紹有關`tuple`的內容。

C++11之後，C++中添加了新的智能指針類型，分別為：`unique_ptr`，`shared_ptr`和`weak_ptr`，因為智能指針方便對內存的管理，所以給智能指針設置了5節內容。

最後，將從大體上瀏覽一下STL中有關於隨機數生成的部分。除了學習STL中隨機數引擎的特性之外，還將瞭解到如何在實際應用中選擇合適的隨機數分佈。