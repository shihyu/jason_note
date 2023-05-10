# 高性能並行編程與優化 - 第01講的回家作業

通過 pull request 提交作業。會批分數，但是：

沒有結業證書，回家作業僅僅作為評估學習效果和鞏固知識的手段，不必為分數感到緊張 :)
量力而行，只要能在本課中，學到昨天的自己不懂的知識，就是勝利，沒必要和別人攀比。

- 課件：https://github.com/parallel101/course
- 錄播：https://space.bilibili.com/263032155

作業提交時間不限 :) 即使完結了還想交的話我也會看的~ 不過最好在下一講開播前完成。

- 如何開 pull request：https://zhuanlan.zhihu.com/p/51199833
- 如何設置 https 代理：https://www.jianshu.com/p/b481d2a42274

## 作業要求

在 main.cpp 中為了導出兩個"美好的圖像"，使用了 `stb_image_write.h` 這個頭文件。
他在 CMakeLists.txt 中也引用了 stbiw 這個庫，然而這個庫還沒有被定義。

你的任務就是 **定義 stbiw 這個庫**，他的內容應該包含 `stbi_write_png()` 的實現，
以及允許通過尖括號導入頭文件 `<stb_image_write.h>`。

運用上課所學知識，儘量不修改 main.cpp 的內容，只修改 stbiw 子目錄下的內容，
完成任務。最好以子模塊 + 庫的形式，實在不行的話直接改 main.cpp 也可以。

運行成功後，應該會在主程序同目錄發現兩個"美好的圖像"：mandel.png 和 rainbow.png

## 參考信息

stb_image_write.h 原倉庫地址: https://github.com/nothings/stb

你需要在一個且僅一個 .cpp 文件定義了 `STB_IMAGE_WRITE_IMPLEMENTATION` 這個宏，
才能決定讓 stbi 系列函數在這裡實現。

如果你不僅完成了作業，還能解釋清楚為什麼 stbi 必須要這樣設計，可能會給你滿分！

## 採分點提示

像這樣：
```cmake
target_compile_definitions(stbiw PUBLIC -DSTB_IMAGE_WRITE_IMPLEMENTATION)
```
是不行的，因為 mandel.cpp 和 rainbow.cpp 兩個文件都 include 了 stb_image_write.h，
這樣同一個函數會被定義兩遍！
