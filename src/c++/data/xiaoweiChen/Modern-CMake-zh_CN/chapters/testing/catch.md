# Catch

[Catch2]（只有C++11版本）是一個獨立且強大的測試工具，它的理念（philosophy）類似於 Python 中的 Pytest。他比 GTest 支持更多的編譯器版本，並且會緊跟潮流支持新的事物，比如支持在 M1 版本 MacOS 上使用 Catch。他也有一個相似但是更加快速的雙胞胎兄弟，[doctest](https://github.com/onqtam/doctest)，他編譯十分迅速但是缺少了一些類似於匹配器（features）的特性。為了在 CMake 項目中使用 Catch，下面是一些可選的方式：

## 如何配置

Catch 對 CMake 支持很友好，不過你還是需要下載整個倉庫來使用他。無論是使用 submodules 還是FetchContent 都可以。[`extended-project`](https://gitlab.com/CLIUtils/modern-cmake/-/tree/master/examples/extended-project)  與 [`fetch`](https://gitlab.com/CLIUtils/modern-cmake/-/tree/master/examples/fetch) 這兩個示例用的都是 FetchContent 的方式。更多的可以參考[官方文檔](https://github.com/catchorg/Catch2/blob/v2.x/docs/cmake-integration.md#top)。

## Quick download

這可能是最簡單並且對老版本 CMake 適配性更好的方式。你可以一步到位地直接下載一個 All-in-one 的頭文件：

```cmake
add_library(catch_main main.cpp)
target_include_directories(catch_main PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
set(url https://github.com/philsquared/Catch/releases/download/v2.13.6/catch.hpp)
file(
  DOWNLOAD ${url} "${CMAKE_CURRENT_BINARY_DIR}/catch.hpp"
  STATUS status
  EXPECTED_HASH SHA256=681e7505a50887c9085539e5135794fc8f66d8e5de28eadf13a30978627b0f47)
list(GET status 0 error)
if(error)
  message(FATAL_ERROR "Could not download ${url}")
endif()
target_include_directories(catch_main PUBLIC "${CMAKE_CURRENT_BINARY_DIR}")
```

在 Catch 3 發佈後，你可能需要下載兩個文件，因為現在需要兩個文件進行測試（但是你不再需要自己寫 main.cpp 文件）。這個 `main.cpp` 文件看起來像這樣：

```cpp
#define CATCH_CONFIG_MAIN
#include "catch.hpp"
```

## Vendoring

如果你已經把 Catch 加入到你項目的一部分（放到了一個單獨的文件夾中），你可以這樣來使用 Catch：

```cmake
# Prepare "Catch" library for other executables
set(CATCH_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/extern/catch)
add_library(Catch2::Catch IMPORTED INTERFACE)
set_property(Catch2::Catch PROPERTY INTERFACE_INCLUDE_DIRECTORIES "${CATCH_INCLUDE_DIR}")
```

然後，你需要鏈接到 Catch2::Catch。你也可以把它作為一個 INTERFACE 目標，因為你不會導出你的測試模塊。


## Direct inclusion

如果你使用 ExternalProject，FetchContent 或者 git submodules 的形式來添加庫，你也可以使用 `add_subdirectory` 。（CMake 3.1+）

Catch 還提供了兩個 CMake 模塊（modules），你可以通過這個來註冊獨立的測試。

[Catch2]: https://github.com/catchorg/Catch2
