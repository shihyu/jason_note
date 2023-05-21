# 獲取軟件包（FetchContent） (CMake 3.11+)

有時你想要在配置的時候下載數據或者是包，而不是在編譯的時候下載。這種方法已經被第三方包重複“發明”了好幾次。最終，這種方法在 CMake 3.11 中以 [FetchContent] 模塊的形式出現。

[FetchContent] 模塊有出色的文檔，我在此不會贅述。我會闡述這樣幾個步驟：

* 使用 `FetchContent_Declare(MyName)` 來從 URL、Git 倉庫等地方獲取數據或者是軟件包。
* 使用 `FetchContent_GetProperties(MyName)` 來獲取 `MyName_*` 等變量的值，這裡的 `MyName` 是上一步獲取的軟件包的名字。
* 檢查 `MyName_POPULATED` 是否已經導出，否則使用 `FetchContent_Populate(MyName)` 來導出變量（如果這是一個軟件包，則使用 `add_subdirectory("${MyName_SOURCE_DIR}" "${MyName_BINARY_DIR}")` ）

比如，下載 Catch2 ：

```cmake
FetchContent_Declare(
  catch
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG        v2.13.6
)

# CMake 3.14+
FetchContent_MakeAvailable(catch)
```

如果你不能使用 CMake 3.14+ ，可以使用適用於低版本的方式來加載：

```cmake
# CMake 3.11+
FetchContent_GetProperties(catch)
if(NOT catch_POPULATED)
  FetchContent_Populate(catch)
  add_subdirectory(${catch_SOURCE_DIR} ${catch_BINARY_DIR})
endif()
```

當然，你可以將這些語句封裝到一個宏內：

```cmake
if(${CMAKE_VERSION} VERSION_LESS 3.14)
    macro(FetchContent_MakeAvailable NAME)
        FetchContent_GetProperties(${NAME})
        if(NOT ${NAME}_POPULATED)
    	    FetchContent_Populate(${NAME})
    	    add_subdirectory(${${NAME}_SOURCE_DIR} ${${NAME}_BINARY_DIR})
        endif()
    endmacro()
endif()
```

這樣，你就可以在 CMake 3.11+ 裡使用 CMake 3.14+ 的語法了。

可以在這裡[查看](https://gitlab.com/CLIUtils/modern-cmake/-/tree/master/examples/fetch)例子。

[FetchContent]: https://cmake.org/cmake/help/latest/module/FetchContent.html
