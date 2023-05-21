# 與你的代碼交互

## 通過 CMake 配置文件

CMake 允許你在代碼中使用 `configure_file` 來訪問 CMake 變量。該命令將一個文件（ 一般以 `.in` 結尾 ）的內容複製到另一個文件中，並替換其中它找到的所有 CMake 變量。如果你想要在你的輸入文件中避免替換掉使用  `${}` 包含的內容，你可以使用 `@ONLY` 關鍵字。還有一個關鍵字 `COPY_ONLY` 可以用來作為 `file(COPY` 的替代字。

{% hint style='info' %}

譯者注：這裡原文講的有些太略，後續補充內容。

{% endhint %}

這個功能在 CMake 中使用的相當頻繁，例如在下面的 `Version.h.in`  中：

#### Version.h.in

```cpp
#pragma once

#define MY_VERSION_MAJOR @PROJECT_VERSION_MAJOR@
#define MY_VERSION_MINOR @PROJECT_VERSION_MINOR@
#define MY_VERSION_PATCH @PROJECT_VERSION_PATCH@
#define MY_VERSION_TWEAK @PROJECT_VERSION_TWEAK@
#define MY_VERSION "@PROJECT_VERSION@"
```

#### CMake lines:
```cmake
configure_file (
    "${PROJECT_SOURCE_DIR}/include/My/Version.h.in"
    "${PROJECT_BINARY_DIR}/include/My/Version.h"
)
```

在構建你的項目時，你也應該包括二進制頭文件路徑。如果你想要在頭文件中包含一些 `true/false` 類型的變量，CMake 對 C 語言有特有的 `#cmakedefine` 和 `#cmakedefine01` 替換符來完成上述需求。


你也可以使用（ 並且是常用 ）這個來生成 `.cmake` 文件，例如配置文件（ 見 [installing](https://cliutils.gitlab.io/modern-cmake/chapters/install/installing.html) ）。

## 讀入文件

另外一個方向也是行得通的， 你也可以從源文件中讀取一些東西（ 例如版本號 ）。例如，你有一個僅包含頭文件的庫，你想要其在無論有無 CMake 的情況下都可以使用，上述方式將是你處理版本的最優方案。可以像下面這麼寫：


```cmake
# Assuming the canonical version is listed in a single line
# This would be in several parts if picking up from MAJOR, MINOR, etc.
set(VERSION_REGEX "#define MY_VERSION[ \t]+\"(.+)\"")

# Read in the line containing the version
file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/include/My/Version.hpp"
    VERSION_STRING REGEX ${VERSION_REGEX})

# Pick out just the version
string(REGEX REPLACE ${VERSION_REGEX} "\\1" VERSION_STRING "${VERSION_STRING}")

# Automatically getting PROJECT_VERSION_MAJOR, My_VERSION_MAJOR, etc.
project(My LANGUAGES CXX VERSION ${VERSION_STRING})
```

如上所示， `file(STRINGS file_name variable_name REGEX regex)` 選擇了與正則表達式相匹配的行，並且使用了相同的正則表達式來匹配出其中版本號的部分。
