# 導出與安裝

讓別人使用庫有三種好方法和一種壞方法:

## 查找模塊（不好的方式）

`Find<mypackage>.cmake` 腳本是為那些不支持 CMake 的庫所設計，所以已經使用 CMake 的庫，無需不要創建這個腳本文件！可以使用 `Config<mypackage>.cmake`，具體方式如下所示。

## 添加子項目

可以將項目作為一個子目錄放置於包中，接著使用 `add_subdirectory` 添加相應的子目錄，這適用於純頭文件和快速編譯的庫。還需要注意的是，安裝命令可能會干擾父項目，因此可以使用 `add_subdirectory` 的`EXCLUDE_FROM_ALL`選項；當顯式使用的目標時，仍然會進行構建。

作為庫的作者，請使用 `CMAKE_CURRENT_SOURCE_DIR` 而非 `PROJECT_SOURCE_DIR` (對於其他變量也是如此，比如`CMAKE_CURRRENT_BINARY_DIR`)。通過檢查 `CMAKE_PROJECT_NAME` 和 `PROJECT_NAME` 的內容是否相同 （STREQUAL），可以只添加對項目有意義的選項或默認值。

此外，使用命名空間也是不錯的方式。使用庫的方式應該與下面的一致，應該對所有方法的使用進行標準化。

```cmake
add_library(MyLib::MyLib ALIAS MyLib)
```

這裡的 ALIAS（別名）目標不會在後面導出。


## 導出

第三種方法是 `*Config.cmake` 腳本，這將是下一章的主題。
