# 基礎知識簡介

## 最低版本要求

這是每個 `CMakeLists.txt` 都必須包含的第一行

```cmake
cmake_minimum_required(VERSION 3.1)
```

順便提一下關於 CMake 的語法。命令 «command:`cmake_minimum_required`»  是不區分大小寫的，所以常用的做法是使用小寫[^1]。 `VERSION` 和它後面的版本號是這個函數的特殊關鍵字。在這本書中，你可以點擊命令的名稱來查看它的官方文檔，並且可以使用下拉菜單來切換 `CMake` 的版本。

這一行很特殊[^2]！ `CMake` 的版本與它的特性（policies）相互關聯，這意味著它也定義了 `CMake` 行為的變化。因此，如果你將 `cmake_minimum_required` 中的 `VERSION` 設定為 `2.8`，那麼你將會在 macOS 上產生鏈接錯誤，例如，即使在 `CMake` 最新的版本中，如果你將它設置為 `3.3` 或者更低，那麼你將會得到一個隱藏的標誌行為(symbols behaviour)錯誤等。你可以在 «cmake:policies» 中得到一系列 policies 與 versions 的說明。

從 CMake 3.12 開始，版本號可以聲明為一個範圍，例如 `VERSION 3.1...3.15`；這意味著這個工程最低可以支持 `3.1` 版本，但是也最高在 `3.15` 版本上測試成功過。這對需要更精確(better)設置的用戶體驗很好，並且由於一個語法上的小技巧，它可以向後兼容更低版本的 CMake （儘管在這裡例子中雖然聲明為 `CMake 3.1-3.15` 實際只會設置為 `3.1` 版本的特性，因為這些版本處理這個工程沒有什麼差異）。新的版本特性往往對 macOS 和 Windows 用戶是最重要的，他們通常使用非常新版本的 CMake。

當你開始一個新項目，起始推薦這麼寫：

```cmake
cmake_minimum_required(VERSION 3.7...3.21)

if(${CMAKE_VERSION} VERSION_LESS 3.12)
    cmake_policy(VERSION ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION})
endif()
```

如果 CMake 的版本低於3.12，`if` 塊條件為真，CMake 將會被設置為當前版本。如果 CMake 版本是 3.12 或者更高，`if` 塊條件為假，將會遵守 `cmake_minimum_required` 中的規定，程序將繼續正常運行。

**WARNING**:  MSVC 的 CMake 服務器模式起初解析這個語法的時候[有一個bug](https://github.com/fmtlib/fmt/issues/809)，所以如果你需要支持舊版本的 MSVC 的非命令行的 Windows 構建，你應該這麼寫：

```cmake
cmake_minimum_required(VERSION 3.7)

if(${CMAKE_VERSION} VERSION_LESS 3.21)
    cmake_policy(VERSION ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION})
else()
    cmake_policy(VERSION 3.21)
endif()
```

{% hint style='info' %}

如果你真的需要在這裡設置為一個低版本，你可以使用 «command:`cmake_policy`» 來有條件的提高特性級別或者設置一個特殊的特性。請至少為你的 macOS 用戶進行設置！
{% endhint %}


## 設置一個項目

現在，每一個頂層 CMakelists 文件都應該有下面這一行：

```cmake
project(MyProject VERSION 1.0
                  DESCRIPTION "Very nice project"
                  LANGUAGES CXX)
```

現在我們看到了更多的語法。這裡的字符串是帶引號的，因此內容中可以帶有空格。項目名稱是這裡的第一個參數。所有的關鍵字參數都可選的。`VERSION` 設置了一系列變量，例如 `MyProject_VERSION` 和 `PROJECT_VERSION`。語言可以是  `C`,`CXX`,`Fortran`,`ASM`,`CUDA`(CMake 3.8+),`CSharp`(3.8+),`SWIFT`(CMake 3.15+  experimental)，默認是`C CXX`。在 CMake 3.9，可以通過`DESCRIPTION` 關鍵詞來添加項目的描述。這個關於 «command:`project`»  的文檔可能會有用。

{% hint style='info' %}

你可以用 `#` 來添加[註釋](https://cmake.org/cmake/help/latest/manual/cmake-language.7.html#comments)。CMake 也有一個用於註釋的內聯語法，但是那極少用到。
{% endhint %}

項目名稱沒有什麼特別的用處。這裡沒有添加任何的目標(target)。

## 生成一個可執行文件

儘管庫要有趣的多，並且我們會將把大部分時間花在其上。但是現在，先讓我們從一個簡單的可執行文件開始吧！

```cmake
add_executable(one two.cpp three.h)
```

這裡有一些語法需要解釋。`one` 既是生成的可執行文件的名稱，也是創建的 `CMake` 目標(target)的名稱(我保證，你很快會聽到更多關於目標的內容)。緊接著的是源文件的列表，你想列多少個都可以。CMake 很聰明 ，它根據拓展名只編譯源文件。在大多數情況下，頭文件將會被忽略；列出他們的唯一原因是為了讓他們在 IDE 中被展示出來，目標文件在許多 IDE 中被顯示為文件夾。你可以在 «cmake:buildsystem» 中找到更多關於一般構建系統與目標的信息。

## 生成一個庫

製作一個庫是通過 «command:`add_library`» 命令完成的，並且非常簡單：

```cmake
add_library(one STATIC two.cpp three.h)
```

你可以選擇庫的類型，可以是 `STATIC`,`SHARED`, 或者`MODULE`.如果你不選擇它，CMake 將會通過 `BUILD_SHARED_LIBS` 的值來選擇構建 STATIC 還是 SHARED 類型的庫。

在下面的章節中你將會看到，你經常需要生成一個虛構的目標，也就是說，一個不需要編譯的目標。例如，只有一個頭文件的庫。這被叫做 `INTERFACE` 庫，這是另一種選擇，和上面唯一的區別是後面不能有文件名。

你也可以用一個現有的庫做一個 `ALIAS` 庫，這只是給已有的目標起一個別名。這麼做的一個好處是，你可以製作名稱中帶有 `::` 的庫（你將會在後面看到）[^3] 。

## 目標時常伴隨著你

現在我們已經指定了一個目標，那我們如何添加關於它的信息呢？例如，它可能需要包含一個目錄：

```cmake
target_include_directories(one PUBLIC include)
```

«command:`target_include_directories`»  為目標添加了一個目錄。 `PUBLIC` 對於一個二進制目標沒有什麼含義；但對於庫來說，它讓 CMake 知道，任何鏈接到這個目標的目標也必須包含這個目錄。其他選項還有 `PRIVATE`（隻影響當前目標，不影響依賴），以及 `INTERFACE`（隻影響依賴）。

接下來我們可以將目標之間鏈接起來：

```cmake
add_library(another STATIC another.cpp another.h)
target_link_libraries(another PUBLIC one)
```

«command:`target_link_libraries`» 可能是 CMake 中最有用也最令人迷惑的命令。它指定一個目標，並且在給出目標的情況下添加一個依賴關係。如果不存在名稱為 `one` 的目標，那他會添加一個鏈接到你路徑中 `one` 庫（這也是命令叫 `target_link_libraries` 的原因）。或者你可以給定一個庫的完整路徑，或者是鏈接器標誌。最後再說一個有些迷惑性的知識：），經典的 CMake 允許你省略 `PUBLIC` 關鍵字，但是你在目標鏈中省略與不省略混用，那麼 CMake 會報出錯誤。

只要記得在任何使用目標的地方都指定關鍵字，那麼就不會有問題。

目標可以有包含的目錄、鏈接庫（或鏈接目標）、編譯選項、編譯定義、編譯特性（見C++11 章節）等等。正如你將在之後的兩個項目章節中看到的，你經常可以得到目標（並且經常是指定目標）來代表所有你使用的庫。甚至有些不是真正的庫，像 `OpenMP`，就可以用目標來表示。這也是為什麼現代 CMake 如此的棒！


## 更進一步

看看你是否能理解以下文件。它生成了一個簡單的 C++11 的庫並且在程序中使用了它。沒有依賴。我將在之後討論更多的 C++ 標準選項，代碼中使用的是 CMake 3.8。

```cmake
cmake_minimum_required(VERSION 3.8)

project(Calculator LANGUAGES CXX)

add_library(calclib STATIC src/calclib.cpp include/calc/lib.hpp)
target_include_directories(calclib PUBLIC include)
target_compile_features(calclib PUBLIC cxx_std_11)

add_executable(calc apps/calc.cpp)
target_link_libraries(calc PUBLIC calclib)

```

[^1]: 在這本書中，我主要避免向你展示錯誤的做事方式。你可以在網上找到很多關於這個的例子。我偶爾會提到替代方法，但除非是絕對必要，否則不推薦使用這些替代的方法，通常他們只是為了幫助你閱讀更舊的 CMake 代碼。
[^2]: 有時你會在這裡看到 `FATAL_ERROR`，那是為了支持在 CMake < 2.6 時的錯誤，現在應該不會有問題了。
[^3]: `::` 語法最初是為了 `INTERFACE IMPORTED` 庫準備的，這些庫應該是在當前項目之外定義的。但是，因為如此，大多數的 `target_*` 命令對 `IMPORTED` 庫不起作用，這使得它們難以自己設置。所以，暫時不要使用 `IMPORTED` 關鍵字，而使用 `ALIAS` 目標；它在你開始導出目標之前，都表現的很好。這個限制在 CMake 3.11 中得以修復。

