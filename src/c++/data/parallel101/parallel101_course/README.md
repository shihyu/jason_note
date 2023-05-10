# 高性能並行編程與優化 - 課件

歡迎光臨開源並行課！您將學到現代 C++ 與高性能計算相關知識！
這裡用來存放上課用到的 **源代碼** 和 **課件** 等。

* 每週六14點開播：https://live.bilibili.com/14248205
* 錄播也會上傳到：https://space.bilibili.com/263032155

![CC-BY-NC-SA](tools/cc-by-nc-sa.jpg)

# 下載課件

如果你不知道 Git 如何使用，可以點擊這裡：[一鍵下載](https://github.com/archibate/course/archive/refs/heads/master.zip)。

# 目錄結構

* 01/slides.ppt - 第一課的課件
* 01/01 - 第一課第一小節的代碼
* 01/02 - 第一課第二小節的代碼
* 02/slides.ppt - 第二課的課件
* 以此類推……

每一小節的代碼目錄下都有一個 run.sh，裡面是編譯運行該程序所用的命令。

# 課程大綱

第一季課程分為前半段和後半段，前半段主要介紹現代 C++，後半段主要介紹並行編程與優化。

1. 課程安排與開發環境搭建：cmake與git入門
1. 現代C++入門：常用STL容器，RAII內存管理
1. 現代C++進階：模板元編程與函數式編程
1. 編譯器如何自動優化：從彙編角度看C++
1. C++11起的多線程編程：從mutex到無鎖並行
1. 並行編程常用框架：OpenMP與Intel TBB
1. 被忽視的訪存優化：內存帶寬與cpu緩存機制
1. GPU專題：wrap調度，共享內存，barrier
1. 並行算法實戰：reduce，scan，矩陣乘法等
1. 存儲大規模三維數據的關鍵：稀疏數據結構
1. 物理仿真實戰：鄰居搜索表實現pbf流體求解
1. C++在ZENO中的工程實踐：從primitive說起
1. 結業典禮：總結所學知識與優秀作業點評

第二季正在絕贊連載中...

# 前置條件

硬件要求：
- 64位（32位時代過去了）
- 至少2核4線程（並行課…）
- 英偉達家顯卡（GPU 專題）

軟件要求：
- Visual Studio 2019（Windows用戶）
- GCC 9 及以上（Linux用戶）
- CMake 3.12 及以上（跨平臺作業）
- Git 2.x（作業上傳到 GitHub）
- CUDA Toolkit 10.0 以上（GPU 專題）

# 參考資料

- [C++ 官方文檔](https://en.cppreference.com/w/)
- [C++ 核心開發規範](https://github.com/isocpp/CppCoreGuidelines/blob/master/CppCoreGuidelines.md)
- [Effective Mordern C++ 中文版](https://github.com/kelthuzadx/EffectiveModernCppChinese/blob/master/4.SmartPointers/item22.md)
- [熱心觀眾整理的學習資料](https://github.com/jiayaozhang/OpenVDB_and_TBB)
- [LearnCpp 中文版](https://learncpp-cn.github.io/)
- [Performance Analysis and Tuning on Modern CPUs](http://faculty.cs.niu.edu/~winans/notes/patmc.pdf)
- [C++ 併發編程實戰](https://www.bookstack.cn/read/Cpp_Concurrency_In_Action/README.md)
- [深入理解計算機原理 (CSAPP)](http://csapp.cs.cmu.edu/)
- [並行體系結構與編程 (CMU 15-418)](https://www.bilibili.com/video/av48153629/)
- [因特爾 TBB 編程指南](https://www.inf.ed.ac.uk/teaching/courses/ppls/TBBtutorial.pdf)
- [CMake “菜譜”](https://www.bookstack.cn/read/CMake-Cookbook/README.md)
- [CMake 官方文檔](https://cmake.org/cmake/help/latest/)
- [Git 官方文檔](https://git-scm.com/doc)
- [GitHub 官方文檔](https://docs.github.com/en)
- [助教老師知乎](https://www.zhihu.com/people/AlbertRen/posts)
- [實用網站 CppInsights 解構 C++ 語法糖](https://cppinsights.io)
- [實用網站 GodBolt 查看不同編譯器生成的彙編](http://godbolt.org)

