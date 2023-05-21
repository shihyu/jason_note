# 如何組織你的項目

下面的說法可能存在一些偏見，但我認為這是一種好的組織方式。我將會講解如何組織項目的目錄結構，這是基於以往的慣例來寫的，這麼做對你有以下好處：

* 可以很容易閱讀以相同模式組織的項目
* 避免可能造成衝突的組織形式
* 避免使目錄結構變得混亂和複雜

首先，如果你創建一個名為 `project` 的項目，它有一個名為 `lib` 的庫，有一個名為 `app` 的可執行文件，那麼目錄結構應該如下所示：

```
- project
  - .gitignore
  - README.md
  - LICENCE.md
  - CMakeLists.txt
  - cmake
    - FindSomeLib.cmake
    - something_else.cmake
  - include
    - project
      - lib.hpp
  - src
    - CMakeLists.txt
    - lib.cpp
  - apps
    - CMakeLists.txt
    - app.cpp
  - tests
    - CMakeLists.txt
    - testlib.cpp
  - docs
    - CMakeLists.txt
  - extern
    - googletest
  - scripts
    - helper.py
```

其中，文件的名稱不是絕對的，你可能會看到關於文件夾名稱為 `tests`  還是 `test` 的爭論，並且應用程序所在的文件夾可能為其他的名稱（ 或者一個項目只有庫文件 ）。你也許也會看到一個名為 `python` 的文件夾，那裡存儲關於 python 綁定器的內容，或者是一個 `cmake` 文件夾用於存儲如 `Find<library>.cmake` 這樣的 `.cmake` 輔助文件。但是一些比較基礎的東西都在上面包括了。

可以注意到一些很明顯的問題， `CMakeLists.txt` 文件被分割到除了 `include` 目錄外的所有源代碼目錄下。這是為了能夠將 `include` 目錄下的所有文件拷貝到 `/usr/include` 目錄或其他類似的目錄下（除了配置的頭文件，這個我將會在另一章講到），因此為了避免衝突等問題，其中不能有除了頭文件外的其他文件。這也是為什麼在 `include` 目錄下有一個名為項目名的目錄。頂層 `CMakeLists.txt` 中應使用 `add_subdirectory` 命令來添加一個包含 `CMakeLists.txt` 的子目錄。

你經常會需要一個 `cmake` 文件夾，裡面包含所有用到的輔助模塊。這是你放置所有 `Find*.cmake` 的文件。你可以在 [github.com/CLIUtils/cmake](https://github.com/CLIUtils/cmake) 找到一些常見的輔助模塊集合。你可以通過以下語句將此目錄添加到你的 CMake Path 中：

```cmake
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake" ${CMAKE_MODULE_PATH})
```

你的 `extern` 應該幾乎只包含 git 子模塊（ submodule ）。通過此方式，你可以明確地控制依賴的版本，並且可以非常輕鬆地升級。關於添加子模塊的例子，可以參見 [Testing](https://modern-cmake-cn.github.io/Modern-CMake-zh_CN/chapters/testing.html) 章節。

你應該在 `.gitignore` 中添加形如 `/build*` 的規則，這樣用戶就可以在源代碼目錄下創建 `build` 目錄來構建項目，而不用擔心將生成的目標文件添加到 `.git` 中。有一些軟件包禁止這麼做，不過這還是相比**做一個真正的外部構建並且針對不同的包來使用不同的構建**要好的多。

如果你想要避免構建目錄在有效的（ valid ）源代碼目錄中，你可以在頂層 `CMakeLists.txt` 文件頭部添加如下語句：

```cmake
### Require out-of-source builds
file(TO_CMAKE_PATH "${PROJECT_BINARY_DIR}/CMakeLists.txt" LOC_PATH)
if(EXISTS "${LOC_PATH}")
    message(FATAL_ERROR "You cannot build in a source directory (or any directory with a CMakeLists.txt file). Please make a build subdirectory. Feel free to remove CMakeCache.txt and CMakeFiles.")
endif()
```

可以在這裡查看 [拓展代碼樣例](https://github.com/Modern-CMake-CN/Modern-CMake-zh_CN/tree/master/examples/extended-project)
