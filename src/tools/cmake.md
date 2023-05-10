## Cmake

常用的 CMake 參數：

1. `-DCMAKE_BUILD_TYPE`: 用於指定編譯模式，例如 `Debug`、`Release` 等。
2. `-DCMAKE_INSTALL_PREFIX`: 用於指定安裝路徑，預設為 `/usr/local`。
3. `-G`: 用於指定生成的專案文件類型，例如 `Unix Makefiles`、`Visual Studio` 等。
4. `-DCMAKE_C_COMPILER` 和 `-DCMAKE_CXX_COMPILER`: 用於指定 C 和 C++ 編譯器的路徑。
5. `-D`: 用於定義變數，例如 `-DENABLE_FEATURE_A=ON`。
6. `-DBUILD_SHARED_LIBS`: 用於指定是否生成共享庫（動態連結庫），默認為 `OFF`。
7. `-DCMAKE_VERBOSE_MAKEFILE`: 用於顯示詳細的編譯信息，包括編譯器命令和編譯時的選項。
8. `-DCMAKE_C_FLAGS` 和 `-DCMAKE_CXX_FLAGS`: 用於指定編譯器的選項，例如 `-O2`、`-Wall` 等。
9. `-DCMAKE_MODULE_PATH`: 用於指定 CMake 模組的路徑，例如 `/usr/local/share/cmake/Modules`。
10. `-DCMAKE_PREFIX_PATH`: 用於指定查找庫文件和頭文件的路徑，例如 `/usr/local/lib` 和 `/usr/local/include`。

以上是一些常用的 CMake 參數，你可以在需要的情況下使用它們來配置你的項目。

---

在 CMakeLists.txt 中，你可以使用一些指令和變數來配置你的 CMake 項目。以下是一些常用的指令和變數及其解釋：

指令：

1. `cmake_minimum_required(VERSION x.y)`: 指定 CMake 的最低版本需求，例如 `cmake_minimum_required(VERSION 3.10)`。
2. `project(name [LANGUAGES lang1 lang2 ...])`: 指定項目的名稱和支持的語言，例如 `project(MyProject CXX)`。
3. `add_executable(name source1 [source2 ...])`: 指定生成執行文件的名稱和源文件，例如 `add_executable(MyProgram main.cpp)`。
4. `add_library(name type source1 [source2 ...])`: 指定生成靜態庫或動態連結庫的名稱、類型和源文件，例如 `add_library(MyLibrary STATIC lib.cpp)`。
5. `target_link_libraries(target library1 [library2 ...])`: 指定目標文件需要連結的庫文件，例如 `target_link_libraries(MyProgram MyLibrary)`。
6. `include_directories(dir1 [dir2 ...])`: 指定頭文件搜索路徑，例如 `include_directories(include)`。

變數：

1. `CMAKE_C_COMPILER` 和 `CMAKE_CXX_COMPILER`: 指定 C 和 C++ 編譯器的路徑，例如 `set(CMAKE_CXX_COMPILER /usr/bin/g++)`。
2. `CMAKE_BUILD_TYPE`: 指定編譯模式，例如 `set(CMAKE_BUILD_TYPE Release)`。
3. `CMAKE_INSTALL_PREFIX`: 指定安裝路徑，例如 `set(CMAKE_INSTALL_PREFIX /usr/local)`。
4. `CMAKE_CXX_FLAGS` 和 `CMAKE_C_FLAGS`: 指定編譯器的選項，例如 `set(CMAKE_CXX_FLAGS "-O2 -Wall")`。

以上是一些常用的 CMake 指令和變數，你可以在 CMakeLists.txt 文件中使用它們來配置你的項目。

```sh
set(CMAKE_BUILD_TYPE DEBUG)
set(CMAKE_C_FLAGS "-O0 -ggdb")
set(CMAKE_C_FLAGS_DEBUG "-O0 -ggdb")
set(CMAKE_C_FLAGS_RELEASE "-O0 -ggdb")
set(CMAKE_CXX_FLAGS "-O0 -ggdb")
set(CMAKE_CXX_FLAGS_DEBUG "-O0 -ggdb")
set(CMAKE_CXX_FLAGS_RELEASE "-O0 -ggdb")
```

