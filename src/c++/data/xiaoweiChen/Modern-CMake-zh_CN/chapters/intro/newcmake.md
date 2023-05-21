# CMake 各個版本添加的新特性


CMake 修改記錄的簡化版本，這裡僅挑了作者認為的重點。這裡，每個版本的名稱都由作者自行命名，不要太在意。

## [CMake 3.0][]：接口庫

這個版本添加了大量內容，主要是為了填充目標接口。一些需要的功能遺棄了，並在 CMake 3.1 中重新實現。

* 首次發佈於 [2014年6月10日](https://blog.kitware.com/cmake-3-0-0-available-for-download/)
* 更新了文檔
* 添加了 INTERFACE 庫類型
* 支持項目版本關鍵字 VERSION
* 導出構建樹更容易
* 括號參數和支持註釋(未廣泛使用)
* 以及其他很多改進

## [CMake 3.1][]：支持 C++11 和編譯特性

支持 C++11 的第一個版本，並針對 CMake 3.0 新特性進行了修復。如若需要使用舊版 CMake，該版本推薦作為最低。

* 首次發佈於 [2014年12月17日](https://blog.kitware.com/cmake-3-1-0-released/)
* 支持 C++11
* 支持編譯特性
* 源文件可以通過 `target_sources` 在創建目標之後添加
* 優化了生成器表達式和 INTERFACE 目標

## [CMake 3.2][]：UTF8

一個小版本，主要是添加了小功能和對之前功能缺陷的修復。還有一些內部變化有，我認為對Windows和UTF8支持更好這個很重要。

* 首次發佈於 [2015年3月11日](https://blog.kitware.com/cmake-3-2-1-released/)
* 可以在循環中使用 `continue()`
* 新增文件和目錄鎖

## [CMake 3.3][]：if 中添加 IN_LIST

if中添加了 `IN_LIST` 選項，並且可以使用環境變量 `$PATH` (詳見 CMake 3.6) 對庫文件進行搜索，添加了 INTERFACE 庫的依賴關係，還有其他一些改進。隨著支持的語言越來越多， `COMPILE_LANGUAGE` 支持生成器表達式就很有必要了。並且，Makefile 在並行執行時的輸出更好看了。

* 首次發佈於[2015年7月23日](https://blog.kitware.com/cmake-3-3-0-released/)
* `if` 支持 `IN_LIST` 關鍵字
* 新增 `*_INCLUDE_WHAT_YOU_USE` 屬性
* `COMPILE_LANGUAGE` 支持生成器表達式(只有某些生成器支持)

## [CMake 3.4][]：Swift & CCache

這個版本增加了許多有用的工具，對Swift語言的支持，以及常用功能的改進。也開始支持編譯器啟動器，比如 CCache。

* 首次發佈於 [2015年11月12日](https://blog.kitware.com/cmake-3-4-0-released/)
* 支持 `Swift` 語言
* `get_filename_component` 添加`BASE_DIR` 選項
* 新增 `if(TEST ...)` 
* 新增 `string(APPEND ...)` 
* 為 make 和 ninja 添加了新的內置變量 `CMAKE_*_COMPILER_LAUNCHER`
* `TARGET_MESSAGES` 允許 Makefile 在目標完成後打印消息
* 導入目標開始出現在官方的 `Find*.cmake` 文件中

## [CMake 3.5][]：ARM

這個版本將 CMake 擴展到更多的平臺，並且可以使用命令行來控制警告信息。

* 首次發佈於 [2016年3月8日](https://blog.kitware.com/cmake-3-5-0-available-for-download/)
* 多個輸入文件可以對應多個 `cmake -E` 命令。
* 內置 `cmake_parse_arguments` 解析指令
* Boost、GTest 等庫支持導入目標
* 支持 ARMCC，優化對 iOS 的支持
* XCode 反斜槓問題修復

## [CMake 3.6][]：Clang-Tidy

這個版本增加了 Clang-Tidy 支持，添加了更多的工具和對原有功能的改進。 取消了在 Unix 系統上搜索 `$PATH` 的問題，取而代之的是使用 `$CMAKE_PREFIX_PATH`。

* 首次發佈於 [2016年7月7日](https://blog.kitware.com/cmake-3-6-0-available-for-download/)
* 為工程安裝時添加 `EXCLUDE_FROM_ALL`
* 新增 `list(FILTER`
* 工具鏈添加了 `CMAKE_*_STANDARD_INCLUDE_DIRECTORIES`和`CMAKE_*_STANDARD_LIBRARIES`
* 改進了 Try-compile 功能
* 新增 `*_CLANG_TIDY` 屬性
* 外部項目可以是淺克隆，以及其他改進


## [CMake 3.7][]：Android & CMake 的服務器模式

可以使用交叉編譯，構建在 Android 平臺運行的程序。if 的新選項可使代碼可讀性更好。新增的服務器模式是為了提高與IDE的集成(但 CMake 3.14+ 使用另一種方式取而代之)。優化了對 VIM 編輯器的支持。

* 首次發佈於 [November 11, 2016](https://blog.kitware.com/cmake-3-7-0-available-for-download/)
* `cmake_parse_arguments` 新增了 `PARSE_ARGV` 模式
* 改進了在 32 位工程在 64 位環境中的構建
* if 增加了很多好用的比較選項，比如 `VERSION_GREATER_EQUAL` (真的需要這麼久嗎?)
* 新增 `LINK_WHAT_YOU_USE`
* 大量與文件和目錄相關的自定義屬性
* 新增 CMake 服務器模式
* 新增 `--trace-source="filename"`，用於監控某些文件


## [CMake 3.8][]：C# & CUDA

CUDA 作為一種語言加入了 CMake，使用 `cxx_std_11` 作為編譯器元特性。若使用 CMake 3.8+，新的生成器表達式真的很好用!

* 首次發佈於[2017年4月10日](https://blog.kitware.com/cmake-3-8-0-available-for-download/)
* 原生支持 C# 語言
* 原生支持 CUDA 語言
* 新增元特性 `cxx_std_11`(以及14和17)
* 優化 `try_compile` 對語言的支持
* 新增 `BUILD_RPATH` 屬性
* `COMPILE_FLAGS` 支持生成器表達式
* 新增 `*_CPPLINT` 
* 新增 `$<IF:cond,true-value,false-value>` (wow!)
* 新增 `source_group(TREE` (終於可以在 IDE 中顯示項目的文件夾結構了!)

## [CMake 3.9][]：IPO

這個版本對 CUDA 支持進行了大量修復，包括對 `PTX` 和 MSVC 生成器的支持。過程間優化(IPO)已正確支持了。

甚至有更多模塊提供導入的目標，包括 MPI。

* 首次發佈於[2017年7月18日](https://blog.kitware.com/cmake-3-9-0-available-for-download/)
* CUDA 支持 Windows
* 優化部分情況下對對象庫的支持
* `project` 新增 `DESCRIPTION` 關鍵字
* `separate_arguments` 新增 `NATIVE_COMMAND` 模式
* `INTERPROCEDURAL_OPTIMIZATION` 強制執行(以及添加 `CMAKE_*` 初始化器，新增 CheckIPOSupported，支持 Clang 和 GCC )
* 新增了`GoogleTest`模塊
* 對`FindDoxygen`進行了大幅度改進


## [CMake 3.10][]：CppCheck

CMake 現在使用 C++11 編譯器構建，許多改進有助於編寫可讀性更好的代碼。

* 首次發佈於[2017年11月20日](https://blog.kitware.com/cmake-3-10-0-available-for-download/)
* 支持 Fortran 編譯器 flang 
* 將編譯器啟動器添加到 CUDA
* `configure_file` 支持 `#cmakedefines` 
* 新增 `include_guard()`，確保CMake源文件只包含一次
* 新增 `string(PREPEND`
* 新增 `*_CPPCHECK` 屬性
* 目錄添加了 `LABELS` 屬性
* 極大地擴展了 FindMPI 模塊
* 優化了 FindOpenMP 模塊
* `GoogleTest` 可動態發現測試用例
* `cmake_host_system_information` 可獲取更多信息。

## [CMake 3.11][]：更快 & IMPORTED INTERFACE

這個版本運行起來 [應該會][fastercmake] 快很多，還可以直接將 INTERFACE 目標添加到 IMPORTED 庫(內部的 `Find*.cmake`  腳本會更加清晰)。

* 首次發佈於 [2018年3月28日](https://blog.kitware.com/cmake-3-11-0-available-for-download/)
* Fortran 支持編譯器啟動器
* Xcode 和 Visual Studio 支持 `COMPILE_LANGUAGE` 的生成器表達式
* 可以直接將 INTERFACE 目標添加到 IMPORTED INTERFACE 庫中(Wow!)
* 對源文件屬性進行了擴展
* `FetchContent` 模塊現在允許在配置時下載 (Wow)

## [CMake 3.12][]：版本範圍和CONFIGURE_DEPENDS

非常牛的版本，包含了許多長期要求添加的小功能。其中一個是新增了版本範圍，現在可以更容易地設置最低和最高的CMake版本了。也可以在一組使用 `GLOB` 獲取的文件上設置 `CONFIGURE_DEPENDS`，構建系統將檢查這些文件，並在需要時重新運行！還可以對 `find_package` 的搜索路徑使用通用的 `PackageName_ROOT`  。對string和list大量的功能添加、模塊更新、全新的Python查找模塊(2和3版本都有)等等。

* 首次發佈於[2018年7月17日](https://blog.kitware.com/cmake-3-12-0-available-for-download/)
* 支持 `cmake_minimum_required` 的範圍表示（向後兼容）
* 使用命令行 `--build` 構建時，支持 `-j,--parallel` 進行並行構建（傳遞給構建工具）
* 支持編譯選項中的 `SHELL:` 字符串（不刪除）
* 新增 `FindPython` 模塊
* 新增 `string(JOIN`，`list(JOIN` 和 `list(TRANSFORM`
* 新增 `file(TOUCH`  和 `file(GLOB CONFIGURE_DEPENDS`
* 支持 C++20
* CUDA 作為語言的改進：支持 CUDA 7 和 7.5
* 支持 macOS 的OpenMP(僅限命令行)
* 新增了幾個新屬性和屬性初始化器
* CPack可讀取 `CMAKE_PROJECT_VERSION` 變量

## [CMake 3.13][]：連接控制

可以在Windows創建符號鏈接了！新增了許多新函數，響應了CMake的主流請求，如 `add_link_options`, `target_link_directories` 和 `target_link_options`。可以在源目錄之外對目標進行更多的修改，可以更好的實現文件分離。`target_sources` *終於*可以正確地處理相對路徑（策略76）了。

* 首次發佈於 [2018年11月20日](https://blog.kitware.com/cmake-3-13-0-available-for-download/)
* 新增 `ctest --progress` 選項，輸出實時測試進度
* 新增 `target_link_options` 和 `add_link_options`
* 新增 `target_link_directories`
* 創建符號鏈接 `-E create_symlink`，只支持 Windows
* Windows 支持 IPO
* 可對源目錄和構建目錄使用 `-S` 和 `-B`
* 可對當前目標外的目錄使用 `target_link_libraries` 和 `install`
* 新增 `STATIC_LIBRARY_OPTIONS` 屬性
* `target_sources` 現在相對於當前源目錄（CMP0076）
* 若使用 Xcode，可以實驗性地設置 schema 字段

## [CMake 3.14][]：文件工具 (AKA [CMake π](https://blog.kitware.com/kitware-gets-mathematical-with-cmake-π-on-pi-day/))

進行了很多小清理，包括幾個用於文件的工具。生成器表達式可以在更多的地方使用，使用list要優於使用空變量。很多的find包可以產生目標。Visual Studio 16 2019 生成器與舊版本略有不同。不支持 Windows XP 和Vista。

* 首次發佈於 [2019年3月14日](https://blog.kitware.com/cmake-3-14-0-available-for-download/)
* `--build` 命令添加了 `-v/--verbose` 選項。若構建工具支持，可以使用冗餘構建
* FILE指令新增了 `CREATE_LINK`，`READ_SYMLINK` 和 `SIZE` 選項
* «command:get_filename_component» 新增了 `LAST_EXT`  和 `NAME_WLE` 用於獲取文件*最後的*擴展名，比如可以從文件名  `version.1.2.zip` ，獲取後綴名 `.zip` （非常方便!）
* 可以在 «command:if» 語句中使用 `DEFINED CACHE{VAR}`，查看是否在 CACHE 中定義了變量。
* 新增 `BUILD_RPATH_USE_ORIGIN`，以改進對構建目錄中RPath的處理。
* CMake 服務器模式使用一個文件API所取代。從長遠來看，這會影響 IDE。

## [CMake 3.15][]：升級CLI

這個版本有許多較小改進，包括對CMake命令行的改進，比如：通過環境變量控制默認生成器（現在很容易將默認生成器改為 Ninja）。`--build` 模式支持多個目標，添加了 `--install` 模式。CMake支持多級日誌記錄。可以使用一些方便的工具來測試生成器表達式。FindPython 模塊持續改進，FindBoost 與 Boost 1.70 的新 CONFIG 模塊有了更多的內聯。`export(PACKAGE)` 發生了巨大變化，不再將默認目錄設置為 `$HOME/.cmake` (若cmake最小版本為3.15+)，若用戶若想使用它，需要額外的設置步驟。

* 首次發佈於 [2019年7月17日](https://blog.kitware.com/cmake-3-15-0-available-for-download/)
* 新增控制默認生成器的環境變量 «envvar:CMAKE_GENERATOR»
* 命令行可構建多個目標，`cmake . --build --target a b`
* `--target` 可縮寫為 `-t`
* 項目安裝支持命令行選項 `cmake . --install`，該過程不使用構建系統
* 支持日誌級別參數 `--loglevel`，為 `message` 指令添加 `NOTICE`，`VERBOSE`，`DEBUG `和  `TRACE `選項
* «command:list» 指令新增了 `PREPEND`、`POP_FRONT `和 `POP_BACK` 選項
* «command:execute_process» 指令新增了 `COMMAND_ECHO`  選項(«variable:CMAKE_EXECUTE_PROCESS_COMMAND_ECHO») 可以在運行命令之前自動顯示具體命令
* Ninja 的幾個改進，包括對 SWIFT 語言的支持
* 改進編譯器和列表的生成器表達式

## [CMake 3.16][]：統一構建

添加了統一構建模式，允許源文件合併成單獨的構建文件。增加了對預編譯頭文件的支持（可能是為 C++20 的模塊做準備），完成了對許多小功能的修復，特別是對較新的特性，如 FindPython、FindDoxygen 等。

* 首次發佈於 [2019年11月26日](https://blog.kitware.com/cmake-3-16-0-available-for-download/)
* 新增對 Objective C 和 Objective C++ 語言的支持
* 使用 `target_precompile_headers` 支持預編譯頭文件
* 支持使用 “Unity” 或 “Jumbo” 構建時(合併源文件)使用 «variable:CMAKE_UNITY_BUILD» 
* CTest：展開列表，可跳過基於正則表達式的方式
* 控制 RPath 的幾個新特性。
* 生成器表達式可以在更多地方使用，比如構建和安裝路徑
* 可以通過新變量顯式地控制查找位置

## [CMake 3.17][]：原生支持CUDA

添加了 FindCUDAToolkit，允許在不啟用 CUDA 語言的情況下，查找和使用 CUDA 工具包！CUDA 現在更具可配置性，例如：鏈接到動態庫。其他功能做了很多優化，比如：FindPython。並且，可以一次性遍歷多個列表。

* 首次發佈於 [2020年3月20日](https://blog.kitware.com/cmake-3-17-0-available-for-download/)
* `CUDA_RUNTIME_LIBRARY` 終於可以設置為 Shared！
* 新增 FindCUDAToolkit
* `cmake -E rm` 替換舊的刪除命令
* 添加 CUDA 元特性，如`cuda_std_03`等。
* `--debug-find` 可跟蹤包的搜索
* ExternalProject 可以禁用遞歸簽出
* FindPython 更好地與 Conda 集成
* DEPRECATION 可以應用於目標
* 新增 rm 命令
* 幾個新的環境變量
* foreach 新增 `ZIP_LISTS` 選項（一次性遍歷多個列表）

## [CMake 3.18][]：CUDA與Clang & CMake宏特性

CUDA 現在支持 Clang （不可分離編譯）。新增了 CUDA_ARCHITECTURES 屬性，可以更好地支持針對 CUDA 硬件。cmake_language 命令支持從字符串中使用 cmake 命令和表達式。還有許多其他元特性的變化，可以使新功能可用：通過變量調用函數，解析字符串，並使用字符串配置文件。還有許多其他漂亮的小功能添加和功能修復，下面是其中的一些。

* 首次發佈於 [2020年7月15日](https://blog.kitware.com/cmake-3-18-0-available-for-download/)
* `cmake` 命令可使用 `cat` 合併多個文件
* 新增 `cmake` 命令的分析模式
* `cmake_language` 新增 `CALL` 和 `EVAL` 選項
* 若需多次導出，可使用 `export` 的 `APPEND` 選項（CMake 3.18+）
* 可以使用 `file()` 進行打包
* 若需要替換文件中的字符串，`file(CONFIGURE` 是比 `configure_file` 更好的方式
* 其他 `find_*` 命令新增了 `find_package` 的 `REQUIRED` 標誌
* 為 `list(SORT` 新增了 `NATURAL` 比較模式
* 新增處理 DIRECTORY 作用域屬性的多個選項
* 新增 `CUDA_ARCHITECTURES`
* 新增 `LINK_LANGUAGE` 生成器表達式（包括 `DEVICE`/`HOST` 版本）
* 源目錄可以成為 `FetchContent` 的子目錄


## [CMake 3.19][]：預設

可以以 JSON 的方式添加預設，用戶將獲得預設的默認值。`find_package` 支持版本範圍，特殊的查找模塊，比如：FindPython，有對版本範圍的自定義支持。添加了許多新的權限控制，進一步的普及生成器表達式。

* 首次發佈於 [2020年11月18日](https://blog.kitware.com/cmake-3-19-0-available-for-download/)
* [CMake預設文件](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html) —— 可以為每個生成器的項目設置默認值，或者用戶可以進行預設。即使當前項目沒有使用 `CMakePresets.json` ，也可將`CMakeUserPresets.json` 添加到 `.gitignore` 中。
* XCode 12+ 中引入了新的構建系統
* 支持 MSVC 對 Android 的構建
* 新增 `cmake -E create_hardlink`
* `add_test` 正確地支持測試名稱中的空格
* 可將 `cmake_language` 中標記為 `DEFER` 的目錄放在最後進行處理
* 大量新 `file` 選項，如臨時下載和 `ARCHIVE_CREATE` 的 `COMPRESSION_LEVEL` 
* `find_package` 支持版本範圍
* `DIRECTORY` 可以在屬性命令中包含二進制目錄
* `string` 新增 `JSON` 模式
* 新 `OPTIMIZE_DEPENDENCIES` 屬性和 `CMAKE_*` 變量可智能地刪除靜態庫和對象庫的依賴項。
* PCH 支持 `PCH_INSTANTIATE_TEMPLATES` 屬性和 `CMAKE_*` 變量。
* 檢查模塊支持 `CUDA` 和 `ISPC` 語言
* FindPython：新增 `Python*_LINK_OPTIONS`
* ctest 的 `compute-sanitizer` 支持 CUDA 的 memcheck

## [CMake 3.20][]：文檔

CMake 文檔通過添加 “new in” 標籤來快速查看添加的內容，無需切換文檔版本，提高了工作效率！新增C++23的支持。源文件必須列出擴展名，並且始終遵循設置的 LANGUAGE 規則。還做了相當多的清理工作（為了使
工程部署的阻礙最小化，最好使用版本 `...3.20` 對源碼進行測試），繼續改進預設。

* 首次發佈於 [2021年3月23日](https://blog.kitware.com/cmake-3-20-0-available-for-download/)
* 支持 C++23
* 新增 CUDAARCHS 環境變量，用於設置 CUDA 架構
* 支持新的 `IntelLLVM` 編譯器（OneAPI 2021.1）和 `NVHPC`的 NVIDIA HPC SDK
* 一些擴展生成器表達式支持自定義命令/目標，可在安裝時重命名
* 新增的 `cmake_path` 命令可用於路徑
* `try_run` 新增了 `WORKING_DIRECTORY` 選項
* `file(GENERATE` 添加了很多特性
* 一些功能或特性的移除，如 `cmake-server`, `WriteCompilerDetectionHeader`（若策略設置為3.20+），以及一些可用新方法替代的東西。
* 源文件必須包含擴展名




## [CMake 3.21][]：配色

不同的消息類型有不同的顏色！現在有變量可以查看是否在頂級項目中。大量有關持續清理和特化的新特性，如添加HIP語言和C17和C23支持。繼續改進預設。

* 首次發佈於 [2021年7月14日](https://blog.kitware.com/cmake-3-21-0-available-for-download/)
* 初步支持 MSVC 2022
* 為 make 和 ninja 添加了 `CMAKE_<LANG_LINKER_LAUNCHER`
* HIP 作為語言添加
* 新增 C17 和 C23 支持
* 新增 `--install -prefix <dir>` 和 `--toolchain <file>`
* 消息根據消息類型著色！
* 支持 MSYS，包括 `FindMsys`
* `file(` 指令更新，添加了 `EXPAND_TILDE` 屬性
* 支持向 `install` 添加運行時的依賴項和工件
* 新增 `PROJECT_IS_TOP_LEVEL` 和 `<PROJECT-NAME>_IS_TOP_LEVEL`
* `find_` 指令在緩存方面的改進



## [CMake 3.22](https://cmake.org/cmake/help/latest/release/3.22.html)：方便的環境變量

一個較小的版本，在常見的構建方面進行了一些不錯的改進。可以在開發環境中設置 `CMAKE_BUILD_TYPE` 來設置默認的構建類型，還有其他幾個新環境變量和變量的添加。與標準相關的編譯器標誌進行了改進。`cmake_host_system_information` 在操作系統信息方面得到了進一步的改進（從 3.10 開始）。

- 首次發佈於 [2021年11月18日](https://blog.kitware.com/cmake-3-22-0-available-for-download/)
- 新的默認環境變量 `CMAKE_BUILD_TYPE` 和 `CMAKE_CONFIGURATION_TYPES`
- 新增環境變量 `CMAKE_INSTALL_MODE` 用於安裝類型（symlink）
- 新增 `CMAKE_REQUIRE_FIND_PACKAGE_<PackageName> `變量，將可選查找轉換為必選查找
- 新增針對編譯器的 `CMAKE_<LANG>_EXTENSIONS_DEFAULT` 變量
- `CMakeDependentOption` 可使用正常的條件語法
- CTest 可以修改環境變量
- 一些生成器可以在使用 MSVC 時包含外部（系統）頭文件



## [CMake 3.23](https://cmake.org/cmake/help/latest/release/3.23.html)：純頭文件庫

一個可靠的版本，只關注頭文件庫，更多的用戶控件，CMake 預設，以及更好的 CUDA 支持。純頭文件庫有一些強大的新特性，比如：各種 `*_SETS` 目標屬性。有一些新的控件，可以限制 `find_` 查找路徑，以及從現有目標中刪除 `SYSTEM`。還可以獲得了擴展的調試特性，以及將所有鏈接強制指向目標。預設可以包括其他文件。CUDA 和C# 部分進行了更新，並添加了幾個編譯器。

- 首次發佈於 [2022年3月29日](https://blog.kitware.com/cmake-3-23-0-is-available-for-download/)
- CMake 預設的改進，可以包含其他文件。
- 兩個新的編譯器，以及更好的 C# 支持。
- `FILE_SET` 可用於 `install` 和 `target_sources` 純頭文件庫。
- `<INTERFACE_>HEADER_SETS`, `<INTERFACE_>HEADER_DIRS` 為目標頭文件。
- 新增 `CUDA_ARCHITECTURES` 對 all 和 all-major.a 的支持
- 可以為 `find_*` 或 find 模塊啟用 DEBUG 消息。
- `define_property()` 新增了 `INITIALIZE_FROM_VARIABLE` 選項。
- `CMAKE_<SYSTEM_>IGNORE_PREFIX_PATH` 可以控制 `find_*` 的查找路徑。
- 新增 `<CMAKE_>LINK_LIBRARIES_ONLY_TARGETS` 強制只鏈接目標（非常適合查找錯誤！）
- `IMPORTED_NO_SYSTEM` 可強制從目標中刪除 SYSTEM 的新屬性。
- `FindGTest` 在找到 `GMock` 目標的情況下，會添加 `GMock` 目標。



## [CMake 3.24](https://cmake.org/cmake/help/latest/release/3.24.html)：包查找器

一個很棒的版本。軟件包編寫者正在實現`find_package`和`FetchContent`的集成，這可以完成“丟失時下載”的工作，並且可以由軟件包編寫者配置。類似地，作為錯誤的警告可以由包設置，也可以由打包器刪除（最好不要這樣做，除非當前項目作為主項目構建！）。

- 首次發佈於 [2022年8月4日](https://blog.kitware.com/cmake-3-24-0-is-available-for-download/)
- `--fresh` 選項在運行時可刪除舊緩存。
- `find_package` 和 `FetchContent` 現在集成在一起了 —— 可以選擇下載缺失的依賴項。
- `find_package` 新增 `GLOBAL` 選項。
- `CMAKE_PROJECT_TOP_LEVEL_INCLUDES` 允許用戶（像打包器一樣）注入項目代碼。
- 生成器表達式可管理 `PATH`。
- 新增 `CMAKE_COLOR_DIAGNOSTICS` 環境變量和變量，取代 `CMAKE_COLOR_MAKEFILE`。
- 可以禁用 `find_*` 搜索安裝前綴（目錄）。
- 新增 `COMPILE_WARNING_AS_ERROR` 屬性和 `CMAKE_` 變量，可使用 `--compile-no-warning-as-error`禁用。
- CUDA 支持對當前檢測到的 GPU 進行 `native`  編譯。
- `SYSTEM` 的包含路徑可以在 MSVC 生成器上使用。
- 更好地支持 MSVC，XCode 等 IDE 。
- 支持 `LLVMFlang` 編譯器。



## [CMake 3.25](https://cmake.org/cmake/help/latest/release/3.25.html)：塊作用域和 SYSTEM

新增塊作用域指令，可有選擇地控制變量和策略，對 SYSTEM 也有更多的控制。可以在`find_`指令中使用 `VALIDATOR` 選項，並且工作流程也進行了升級。

- 首次發佈於 [2022年11月16日](https://www.kitware.com/cmake-3-25-0-available-for-download/)
- 支持 C++26
- CUDA 的 nvcc 可以使用 LTO
- 新增了工作流預設和包預設。
- `SYSTEM` 可作為目錄屬性添加到 `add_subdirectory` 和 `FetchContent`
- `block()/endblock()` 用於策略/變量範圍， `return()` 中新增 `PROPOGATE` 選項
- 添加了 `BSD` 和 `LINUX` 變量
- `find_*` 新增 `VALIDATOR` 選項。
- 新增的 `SYSTEM` 目標/目錄屬性和 `EXPORT_NO_SYSTEM`，同樣用於 FetchContent 。



## [CMake開發中](https://cmake.org/cmake/help/git-master/release/index.html)：WIP(Work In Process)

- FindPython 可以生成正確的 PyPy SOABI（終於！）





[Releases]: https://cmake.org/cmake/help/latest/release/index.html
[CMake 3.0]: https://cmake.org/cmake/help/latest/release/3.0.html
[CMake 3.1]: https://cmake.org/cmake/help/latest/release/3.1.html
[CMake 3.2]: https://cmake.org/cmake/help/latest/release/3.2.html
[CMake 3.3]: https://cmake.org/cmake/help/latest/release/3.3.html
[CMake 3.4]: https://cmake.org/cmake/help/latest/release/3.4.html
[CMake 3.5]: https://cmake.org/cmake/help/latest/release/3.5.html
[CMake 3.6]: https://cmake.org/cmake/help/latest/release/3.6.html
[CMake 3.7]: https://cmake.org/cmake/help/latest/release/3.7.html
[CMake 3.8]: https://cmake.org/cmake/help/latest/release/3.8.html
[CMake 3.9]: https://cmake.org/cmake/help/latest/release/3.9.html
[CMake 3.10]: https://cmake.org/cmake/help/latest/release/3.10.html
[CMake 3.11]: https://cmake.org/cmake/help/latest/release/3.11.html
[CMake 3.12]: https://cmake.org/cmake/help/latest/release/3.12.html
[CMake 3.13]: https://cmake.org/cmake/help/latest/release/3.13.html
[CMake 3.14]: https://cmake.org/cmake/help/latest/release/3.14.html
[CMake 3.15]: https://cmake.org/cmake/help/latest/release/3.15.html
[CMake 3.16]: https://cmake.org/cmake/help/latest/release/3.16.html
[CMake 3.17]: https://cmake.org/cmake/help/latest/release/3.17.html
[CMake 3.18]: https://cmake.org/cmake/help/latest/release/3.18.html
[CMake 3.19]: https://cmake.org/cmake/help/latest/release/3.19.html
[CMake 3.20]: https://cmake.org/cmake/help/latest/release/3.20.html
[CMake 3.21]: https://cmake.org/cmake/help/latest/release/3.21.html
[CMake master]: https://cmake.org/cmake/help/git-master/release/index.html
[fastercmake]: https://blog.kitware.com/improving-cmakes-runtime-performance/

