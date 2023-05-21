# CMake 中一些有用的模組

在 CMake 的 «cmake:modules» 集合了很多有用的模組，但是有一些模塊相比於其他的更有用。以下是一些比較出彩的：

## «module:CMakeDependentOption»

這增加了命令 `cmake_dependent_option` ，它根據另外一組變量是否為真來（決定是否）開啟一個選項。下面是一個例子：

```cmake
include(CMakeDependentOption)
cmake_dependent_option(BUILD_TESTS "Build your tests" ON "VAL1;VAL2" OFF)
```

如上代碼是下面的一個縮寫：

```cmake
if(VAL1 AND VAL2)
    set(BUILD_TESTS_DEFAULT ON)
else()
    set(BUILD_TESTS_DEFAULT OFF)
endif()

option(BUILD_TESTS "Build your tests" ${BUILD_TESTS_DEFAULT})

if(NOT BUILD_TESTS_DEFAULT)
    mark_as_advanced(BUILD_TESTS)
endif()
```

需要注意的是，如果你使用了 `include(CTest)` ，用 `BUILD_TESTING` 來檢測是否啟用是更好的方式，因為它就是為此功能而生的。這裡只是一個 `CMakeDependentOption` 的例子。

## «module:CMakePrintHelpers»

這個模塊包含了幾個方便的輸出函數。`cmake_print_properties` 可以讓你輕鬆的打印屬性，而 `cmake_print_variables` 將打印出你給它任意變量的名稱和值。


## «module:CheckCXXCompilerFlag»

這個模塊允許你檢查編譯器是否支持某個標誌，例如：

```cmake
include(CheckCXXCompilerFlag)
check_cxx_compiler_flag(-someflag OUTPUT_VARIABLE)
```

需要注意的是 `OUTPUT_VARIABLE` 也會出現在打印的配置輸出中，所以請選個不錯的變量名。

這只是許多類似模塊中的一個，例如 `CheckIncludeFileCXX`、`CheckStructHasMember`、`TestBigEndian` 以及`CheckTypeSize`，它們允許你檢查系統的信息（並且你可以在代碼中使用這些信息）。

## «command:`try_compile`»/«command:`try_run`»

準確的說，這不是一個模塊，但是它們對上述列出的許多模塊至關重要。通過它你可以在配置時嘗試編譯（也可能是運行）一部分代碼。這可以讓你在配置時獲取關於系統能力的信息。基本的語法如下：

```cmake
try_compile(
  RESULT_VAR
    bindir
  SOURCES
    source.cpp
)
```

這裡有很多可以添加的選項，例如 `COMPILE_DEFINITIONS`。在 CMake 3.8+ 中， 這將默認遵循 CMake 中 C/C++/CUDA 的標準設置。如果你使用的是 `try_run` 而不是 `try_compile`，它將運行生成的程序並將運行結果存儲在 `RUN_OUTPUT_VARIABLE` 中。

## «module:FeatureSummary»

這是一個十分有用但是也有些奇怪的模塊。它能夠讓你打印出找到的所有軟件包以及你明確設定的所有選項。它和  «command:`find_package`» 有一些聯繫。像其他模塊一樣，你首先要包括模塊：

```cmake
include(FeatureSummary)
```

然後，對於任何你已經運行或者將要運行的  «command:`find_package`» ，你可以這樣拓展它的默認信息：

```cmake
set_package_properties(OpenMP PROPERTIES
    URL "http://www.openmp.org"
    DESCRIPTION "Parallel compiler directives"
    PURPOSE "This is what it does in my package")
```

你也可以將包的 `TYPE` 設置為 `RUNTIME`、`OPTIONAL`、`RECOMMENDED` 或者 `REQUIRED`。但是你不能降低包的類型，如果你已經通過 «command:`find_package`» 添加了一個 `REQUIRED` 類型的包，你將會看到你不能改變它的 `TYPE`：

並且，你可以添加任何選項讓其成為 `feature summary` 的一部分。如果你添加的選項名與包的名字一樣，他們之間會互相產生影響：

```cmake
add_feature_info(WITH_OPENMP OpenMP_CXX_FOUND "OpenMP (Thread safe FCNs only)")
```

然後，你可以將所有特性 (features) 的集合打印到屏幕或日誌文件中：

```cmake
if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME)
    feature_summary(WHAT ENABLED_FEATURES DISABLED_FEATURES PACKAGES_FOUND)
    feature_summary(FILENAME ${CMAKE_CURRENT_BINARY_DIR}/features.log WHAT ALL)
endif()
```

你可以建立一個 `WHAT` 目標來集合任何你想查看的特性 (features)，或者直接使用 `ALL` 目標也行。 
