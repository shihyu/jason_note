# 為 CMake 項目添加選項

CMake 中有許多關於編譯器和鏈接器的設置。當你需要添加一些特殊的需求，你應該首先檢查 CMake 是否支持這個需求，如果支持的話，你就可以不用關心編譯器的版本，一切交給 CMake 來做即可。 更好的是，你可以在 `CMakeLists.txt` 表明你的意圖，而不是通過開啟一系列標誌 (flag) 。

其中最首要，並且最普遍的需求是對 C++ 標準的設定與支持，這個將會單獨開一章節講解。

## 地址無關代碼(Position independent code)

用標誌 `-fPIC` 來設置[這個](https://cmake.org/cmake/help/latest/variable/CMAKE_POSITION_INDEPENDENT_CODE.html)是最常見的。大部分情況下，你不需要去顯式的聲明它的值。CMake 將會在 `SHARED` 以及 `MODULE` 類型的庫中自動的包含此標誌。如果你需要顯式的聲明，可以這麼寫： 

```cmake
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
```

這樣會對全局的目標進行此設置，或者可以這麼寫：

```cmake
set_target_properties(lib1 PROPERTIES POSITION_INDEPENDENT_CODE ON)
```

來對某個目標進行設置是否開啟此標誌。

## Little libraries

如果你需要鏈接到 `dl` 庫，在 Linux 上可以使用 `-ldl` 標誌，不過在 CMake 中只需要在 `target_link_libraries` 命令中使用內置的 CMake 變量 [`${CMAKE_DL_LIBS}` ](https://cmake.org/cmake/help/latest/variable/CMAKE_DL_LIBS.html)。這裡不需要模組或者使用 `find_package` 來尋找它。（這個命令包含了調用 `dlopen` 與 `dlclose` 的一切依賴）

不幸的是，想要鏈接到數學庫沒這麼簡單。如果你需要明確地鏈接到它，你可以使用 `target_link_libraries(MyTarget PUBLIC m)`，但是使用 CMake 通用的 [`find_library`](https://cmake.org/cmake/help/latest/command/find_library.html) 可能更好，如下是一個例子：

```cmake
find_library(MATH_LIBRARY m)
if(MATH_LIBRARY)
    target_link_libraries(MyTarget PUBLIC ${MATH_LIBRARY})
endif()
```

通過快速搜索，你可以很容易地找到這個和其他你需要的庫的 `Find*.cmake` 文件，大多數主要軟件包都具有這個 CMake 模組的輔助庫。更多信息請參見**包含現有軟件包**的章節。

## 程序間優化(Interprocedural optimization)

«prop:tgt:INTERPROCEDURAL_OPTIMIZATION»，最有名的是 *鏈接時間優化* 以及 `-flto` 標誌，這在最新的幾個 CMake 版本中可用。你可以通過變量 «variable:CMAKE_INTERPROCEDURAL_OPTIMIZATION»（ CMake 3.9+ 可用）或對目標指定 «prop:tgt:INTERPROCEDURAL_OPTIMIZATION» 屬性來打開它。在 CMake 3.8 中添加了對 GCC 及 Clang 的支持。如果你設置了 `cmake_minimum_required(VERSION 3.9)` 或者更高的版本（參考 «policy:CMP0069»），當在編譯器不支持 «prop:tgt:INTERPROCEDURAL_OPTIMIZATION» 時，通過變量或屬性啟用該優化會產生報錯。你可以使用內置模塊 «module:CheckIPOSupported» 中的 `check_ipo_supported()` 來檢查編譯器是否支持 IPO 。下面是基於 CMake 3.9 的一個例子：

```cmake
include(CheckIPOSupported)
check_ipo_supported(RESULT result)
if(result)
  set_target_properties(foo PROPERTIES INTERPROCEDURAL_OPTIMIZATION TRUE)
endif()
```
