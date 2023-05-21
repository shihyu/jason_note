# 測試

## General Testing Information

你需要在你的主 CMakeLists.txt 文件中添加如下函數調用（而不是在子文件夾 CMakeLists.txt 中）：

```cmake
if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME)
    include(CTest)
endif()
```

這麼做將可以使得具有 CMake 測試功能，並且具有一個 `BUILD_TESTING` 選項使得用戶可以選擇開啟或關閉測試（還有[一些其他的設置](https://gitlab.kitware.com/cmake/cmake/blob/master/Modules/CTest.cmake)）。或者你可以直接通過調用 `enable_testing()` 函數來開啟測試。 

當你添加你自己的測試文件夾時，你應該這麼做：

```cmake
if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME AND BUILD_TESTING)
    add_subdirectory(tests)
endif()
```

這麼做的（譯者注：需要添加 `CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME`）的原因是，如果有他人包含了你的包，並且他們開啟了 `BUILD_TESTING` 選項，但他們並不想構建你包內的測試單元，這樣會很有用。在極少數的情況下他們可能真的想要開啟所有包的測試功能，你可以提供給他們一個可以覆蓋的變量（如下例的 `MYPROJECT_BUILD_TESTING`，當設置 `MYPROJECT_BUILD_TESTING` 為 ON 時，會開啟該項目的測試功能）：

```cmake
if((CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME OR MYPROJECT_BUILD_TESTING) AND BUILD_TESTING)
    add_subdirectory(tests)
endif()
```

本書中的[示例](https://github.com/Modern-CMake-CN/Modern-CMake-zh_CN/blob/master/examples/extended-project/CMakeLists.txt)就使用了覆蓋變量的形式來開啟所有測試，因為主 CMake 項目確實想要運行所有子項目的測試功能。

你可以這樣註冊一個測試目標(targets)：

```cmake
add_test(NAME TestName COMMAND TargetName)
```

如果你在 `COMMAND` 後寫了除 `TargetName` 之外的東西，他將會被註冊為在命令行運行的指令。在這裡寫生成器表達式(generator-expression)也是有效的：

```cmake
add_test(NAME TestName COMMAND $<TARGET_FILE:${TESTNAME}>)
```

這麼寫將會使用該目標生成的文件（也就是生成的可執行文件）的路徑作為參數。

## 將構建作為測試的一部分

如果你想在測試時運行 CMake 構建一個項目，這也是可以的（事實上，這也是 CMake 如何進行自我測試的）。例如，如果你的主項目名為 `MyProject` 並且你有一個 `examples/simple` 項目需要在測試時構建，那麼可以這麼寫：

```cmake
add_test(
  NAME
    ExampleCMakeBuild
  COMMAND
    "${CMAKE_CTEST_COMMAND}"
             --build-and-test "${My_SOURCE_DIR}/examples/simple"
                              "${CMAKE_CURRENT_BINARY_DIR}/simple"
             --build-generator "${CMAKE_GENERATOR}"
             --test-command "${CMAKE_CTEST_COMMAND}"
)
```

## 測試框架

可以查看子章節瞭解主流測試框架的使用方式(recipes)：

* [GoogleTest](testing/googletest.md): 一個 Google 出品的主流測試框架。不過開發可能有點慢。
* [Catch2](testing/catch.md): 一個現代的，具有靈巧的宏的 PyTest-like 的測試框架。
* [DocTest](https://github.com/onqtam/doctest):  一個 Catch2 框架的替代品，並且編譯速度更快、更乾淨(cleaner)。See Catch2 chapter and replace with DocTest. 
