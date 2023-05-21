# 在 CMake 中運行其他的程序

## 在配置時運行一條命令

在配置時運行一條命令是相對比較容易的。可以使用 [`execute_process`][execute_process] 來運行一條命令並獲得他的結果。一般來說，在 CMkae 中避免使用硬編碼路徑是一個好的習慣，你也可以使用 `${CMAKE_COMMAND}` , `find_package(Git)` , 或者`find_program` 來獲取命令的運行權限。可以使用 `RESULT_VARIABLE` 變量來檢查返回值，使用 `OUTPUT_VARIABLE` 來獲得命令的輸出。 

下面是一個更新所有 git 子模塊的例子：

```cmake
find_package(Git QUIET)

if(GIT_FOUND AND EXISTS "${PROJECT_SOURCE_DIR}/.git")
    execute_process(COMMAND ${GIT_EXECUTABLE} submodule update --init --recursive
                    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                    RESULT_VARIABLE GIT_SUBMOD_RESULT)
    if(NOT GIT_SUBMOD_RESULT EQUAL "0")
        message(FATAL_ERROR "git submodule update --init --recursive failed with ${GIT_SUBMOD_RESULT}, please checkout submodules")
    endif()
endif()
```

## 在構建時運行一條命令

在構建時運行一條命令有點難。主要是目標系統使這變的很難，你希望你的命令在什麼時候運行？它是否會產生另一個目標需要的輸出？記住這些需求，然後我們來看一個關於調用 Python 腳本生成頭文件的例子：

```cmake
find_package(PythonInterp REQUIRED)
add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/include/Generated.hpp"
    COMMAND "${PYTHON_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/scripts/GenerateHeader.py" --argument
    DEPENDS some_target)

add_custom_target(generate_header ALL
    DEPENDS "${CMAKE_CURRENT_BINARY_DIR}/include/Generated.hpp")

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/include/Generated.hpp DESTINATION include)
```

在這裡，當你在 `add_custom_target` 命令中添加 `ALL` 關鍵字，頭文件的生成過程會在 `some_target` 這些依賴目標完成後自動執行。當你把這個目標作為另一個目標的依賴，你也可以不加 `ALL` 關鍵字，那這樣他會在被依賴目標構建時會自動執行。或者，你也可以顯示的直接構建 `generate_header` 這個目標。

{% hint style='info' %}

譯者注：這裡翻譯的有一些拗口，後續會改善。

{% endhint %}

## CMake 中包含的常用的工具

在編寫跨平臺的 CMake 工程時，一個有用的工具是 `cmake -E <mode>`（在 `CMakeLists.txt` 中被寫作 `${CMAKE_COMMAND} -E`）。通過指定後面的 `<mode>` 允許 CMake 在不顯式調用系統工具的情況下完成一系列事情，例如 `copy(複製)`，`make_directory(創建文件夾)`，和 `remove(移除)` 。**這都是構建時經常使用的命令。** 需要注意的是，一個非常有用的 mode——`create_symlink`，只有在基於 Unix 的系統上可用，但是在 CMake 3.13 後的 Windows 版本中也存在此 `mode`。[點擊這裡查看對應文檔](https://cmake.org/cmake/help/latest/manual/cmake.1.html#command-line-tool-mode)。

[execute_process]: https://cmake.org/cmake/help/latest/command/execute_process.html
