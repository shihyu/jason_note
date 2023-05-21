# 調試代碼

你可能需要對你的 CMake 構建過程或你的 C++ 代碼進行調試。本文將介紹這兩者。

## 調試 CMake

首先，讓我們來盤點一下調試 CMakeLists 和其他 CMake 文件的方法。

### 打印變量

通常我們使用的打印語句如下：

```cmake
message(STATUS "MY_VARIABLE=${MY_VARIABLE}")
```

然而，通過一個內置的模組 `CMakePrintHelpoers` 可以更方便的打印變量：

```cmake
include(CMakePrintHelpers)
cmake_print_variables(MY_VARIABLE)
```

如何你只是想要打印一個變量，那麼上述方法已經很好用了！如何你想要打印一些關於某些目標 (或者是其他擁有變量的項目，比如 `SOURCES`、`DIRECTORIES`、`TESTS` , 或 `CACHE_ENTRIES` - 全局變量好像因為某些原因缺失了) 的變量，與其一個一個打印它們，你可以簡單的列舉並打印它們：

```cmake
cmake_print_properties(
    TARGETS my_target
    PROPERTIES POSITION_INDEPENDENT_CODE
)
```


### 跟蹤運行

你可能想知道構建項目的時候你的 CMake 文件究竟發生了什麼，以及這些都是如何發生的？用 `--trace-source="filename"` 就很不錯，它會打印出你指定的文件現在運行到哪一行，讓你可以知道當前具體在發生什麼。另外還有一些類似的選項，但這些命令通常給出一大堆輸出，讓你找不著頭腦。

例子：

```bash
cmake -S . -B build --trace-source=CMakeLists.txt
```

如果你添加了 `--trace-expand` 選項，變量會直接展開成它們的值。


## 以 debug 模式構建

對於單一構建模式的生成器 (single-configuration generators)，你可以使用參數 `-DCMAKE_BUILD_TYPE=Debug` 來構建項目，以獲得調試標誌 (debugging flags)。對於支持多個構建模式的生成器 (multi-configuration generators)，像是多數IDE，你可以在 IDE 裡打開調試模式。這種模式有不同的標誌（變量以 `_DEBUG` 結尾，而不是 `_RELEASE` 結尾），以及生成器表達式的值 `CONFIG:Debug` 或 `CONFIG:Release`。

如果你使用了 debug 模式構建，你就可以在上面運行調試器了，比如gdb或lldb。
