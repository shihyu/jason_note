# GoogleTest

GoogleTest 和 GoogleMock 是非常經典的選擇；不過就我個人經驗而言，我會推薦你使用 Catch2，因為 GoogleTest 十分遵循谷歌的發展理念；它假定用戶總是想使用最新的技術，因此會很快的拋棄舊的編譯器（不對其適配）等等。添加 GoogleMock 也常常令人頭疼，並且你需要使用 GoogleMock 來獲得匹配器(matchers)，這在 Catch2 是一個默認特性，而不需要手動添加（但 docstest 沒有這個特性）。

## 子模塊(Submodule)的方式（首選）

當使用這種方式，只需要將 GoogleTest 設定(checkout) 為一個子模塊：[^1]

```cmake
git submodule add --branch=release-1.8.0 ../../google/googletest.git extern/googletest
```

然後，在你的主 `CMakeLists.txt` 中：

```cmake
option(PACKAGE_TESTS "Build the tests" ON)
if(PACKAGE_TESTS)
    enable_testing()
    include(GoogleTest)
    add_subdirectory(tests)
endif()
```

我推薦你使用一些像 `PROJECT_NAME STREQUAL CMAKE_PROJECT_NAME` 來設置 `PACKAGE_TEST` 選項的默認值，因為這樣只會在項目為主項目時才構建測試單元。

像之前提到的，你必須在你的主 `CMakeLists.txt` 文件中調用 `enable_testing()` 函數。
現在，在你的 `tests` 目錄中：

```cmake
add_subdirectory("${PROJECT_SOURCE_DIR}/extern/googletest" "extern/googletest")
```

如果你在你的主 `CMakeLists.txt` 中調用它，你可以使用普通的 `add_subdirectory`；這裡因為我們是從子目錄中調用的，所以我們需要一個額外的路徑選項來更正構建路徑。

下面的代碼是可選的，它可以讓你的 `CACHE` 更乾淨：

```cmake
mark_as_advanced(
    BUILD_GMOCK BUILD_GTEST BUILD_SHARED_LIBS
    gmock_build_tests gtest_build_samples gtest_build_tests
    gtest_disable_pthreads gtest_force_shared_crt gtest_hide_internal_symbols
)
```

If you are interested in keeping IDEs that support folders clean, I would also add these lines:

```cmake
set_target_properties(gtest PROPERTIES FOLDER extern)
set_target_properties(gtest_main PROPERTIES FOLDER extern)
set_target_properties(gmock PROPERTIES FOLDER extern)
set_target_properties(gmock_main PROPERTIES FOLDER extern)
```

然後，為了增加一個測試，推薦使用下面的宏：

```cmake
macro(package_add_test TESTNAME)
    # create an exectuable in which the tests will be stored
    add_executable(${TESTNAME} ${ARGN})
    # link the Google test infrastructure, mocking library, and a default main fuction to
    # the test executable.  Remove g_test_main if writing your own main function.
    target_link_libraries(${TESTNAME} gtest gmock gtest_main)
    # gtest_discover_tests replaces gtest_add_tests,
    # see https://cmake.org/cmake/help/v3.10/module/GoogleTest.html for more options to pass to it
    gtest_discover_tests(${TESTNAME}
        # set a working directory so your project root so that you can find test data via paths relative to the project root
        WORKING_DIRECTORY ${PROJECT_DIR}
        PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY "${PROJECT_DIR}"
    )
    set_target_properties(${TESTNAME} PROPERTIES FOLDER tests)
endmacro()

package_add_test(test1 test1.cpp)
```

這可以簡單、快速的添加測試單元。你可以隨意更改來滿足你的需求。如果你之前沒有了解過 `ARGN`，`ARGN ` 是顯式聲明的參數外的所有參數。如 `package_add_test(test1 test1.cpp a b c)`，`ARGN` 包含除 `test1` 與 `test1.cpp` 外的所有參數。

可以更改宏來滿足你的要求。例如，如果你需要鏈接不同的庫來進行不同的測試，你可以這麼寫：

```cmake
macro(package_add_test_with_libraries TESTNAME FILES LIBRARIES TEST_WORKING_DIRECTORY)
    add_executable(${TESTNAME} ${FILES})
    target_link_libraries(${TESTNAME} gtest gmock gtest_main ${LIBRARIES})
    gtest_discover_tests(${TESTNAME}
        WORKING_DIRECTORY ${TEST_WORKING_DIRECTORY}
        PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY "${TEST_WORKING_DIRECTORY}"
    )
    set_target_properties(${TESTNAME} PROPERTIES FOLDER tests)
endmacro()

package_add_test_with_libraries(test1 test1.cpp lib_to_test "${PROJECT_DIR}/european-test-data/")
```


## 下載的方式

你可以通過 CMake 的 `include` 指令使用使用我在 [CMake helper repository][CLIUtils/cmake] 中的下載器，

這是一個 [GoogleTest] 的下載器，基於優秀的 [DownloadProject] 工具。為每個項目下載一個副本是使用 GoogleTest 的推薦方式（so much so, in fact, that they have disabled the automatic CMake install target）, so this respects that design decision. 這個方式在項目配置時下載 GoogleTest，所以 IDEs 可以正確的找到這些庫。這樣使用起來很簡單：

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject CXX)
list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

enable_testing() # Must be in main file

include(AddGoogleTest) # Could be in /tests/CMakeLists.txt
add_executable(SimpleTest SimpleTest.cu)
add_gtest(SimpleTest)
```

> 提示：`add_gtest` 只是一個添加 `gtest`，`gmock` 以及 `gtest_main` 的宏，然後運行 `add_test` 來創建一個具有相同名字的測試單元
>
> ```cmake
> target_link_libraries(SimpleTest gtest gmock gtest_main)
> add_test(SimpleTest SimpleTest)
> ```

## FetchContent: CMake 3.11

這個例子是用 FetchContent 來添加 GoogleTest：

```cmake
include(FetchContent)

FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG        release-1.8.0
)

FetchContent_GetProperties(googletest)
if(NOT googletest_POPULATED)
  FetchContent_Populate(googletest)
  add_subdirectory(${googletest_SOURCE_DIR} ${googletest_BINARY_DIR})
endif()
```

[^1]: 在這裡我假設你在 Github 倉庫中使用 googletest，然後使用的是 googletest 的相對路徑。


[CLIUtils/cmake]:  https://github.com/CLIUtils/cmake
[GoogleTest]:      https://github.com/google/googletest
[DownloadProject]: https://github.com/Crascit/DownloadProject
