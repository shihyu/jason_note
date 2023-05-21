# Git 子模組（Submodule）

如果你想要添加一個 Git 倉庫，它與你的項目倉庫使用相同的 Git 託管服務（諸如 GitHub、GitLab、BitBucker 等等），下面是正確的添加一個子模組到 `extern` 目錄中的命令：

```term
gitbook $ git submodule add ../../owner/repo.git extern/repo
```

此處的關鍵是使用相對於你的項目倉庫的相對路徑，它可以保證你使用與主倉庫相同的訪問方式（ ssh 或 https ）訪問子模組。這在大多數情況都能工作得相當好。當你在一個子模組裡的時候，你可以把它看作一個正常的倉庫，而當你在主倉庫裡時，你可以用 `add` 來改變當前的提交指針。

但缺點是你的用戶必須懂 git submodule 命令，這樣他們才可以 `init` 和 `update` 倉庫，或者他們可以在最開始克隆你的倉庫的時候加上 `--recursive` 選項。針對這種情況，CMake 提供了一種解決方案：

```cmake
find_package(Git QUIET)
if(GIT_FOUND AND EXISTS "${PROJECT_SOURCE_DIR}/.git")
# Update submodules as needed
    option(GIT_SUBMODULE "Check submodules during build" ON)
    if(GIT_SUBMODULE)
        message(STATUS "Submodule update")
        execute_process(COMMAND ${GIT_EXECUTABLE} submodule update --init --recursive
                        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                        RESULT_VARIABLE GIT_SUBMOD_RESULT)
        if(NOT GIT_SUBMOD_RESULT EQUAL "0")
            message(FATAL_ERROR "git submodule update --init --recursive failed with ${GIT_SUBMOD_RESULT}, please checkout submodules")
        endif()
    endif()
endif()

if(NOT EXISTS "${PROJECT_SOURCE_DIR}/extern/repo/CMakeLists.txt")
    message(FATAL_ERROR "The submodules were not downloaded! GIT_SUBMODULE was turned off or failed. Please update submodules and try again.")
endif()
```

第一行使用 CMake 自帶的 `FindGit.cmake` 檢測是否安裝了 Git 。然後，如果項目源目錄是一個 git 倉庫，則添加一個選項（默認值為 `ON`），用戶可以自行決定是否打開這個功能。然後我們運行命令來獲取所有需要的倉庫，如果該命令出錯了，則 CMake 配置失敗，同時會有一份很好的報錯信息。最後無論我們以什麼方式獲取了子模組，CMake都會檢查倉庫是否已經被拉取到本地。你也可以使用 `OR` 來列舉其中的幾個。

現在，你的用戶可以完全忽視子模組的存在了，而你同時可以擁有良好的開發體驗！唯一需要開發者注意的一點是，如果你正在子模組裡開發，你會在重新運行 CMake 的時候重置你的子模組。只需要添加一個新的提交到主倉庫的暫存區，就可以避免這個問題。

然後你就可以添加對 CMake 有良好支持的項目了：

```cmake
add_subdirectory(extern/repo)
```

或者，如果這是一個只有頭文件的庫，你可以創建一個接口庫目標 (interface library target) 。或者，如果支持的話，你可以使用`find_package`，可能初始的搜索目錄就是你所添加的目錄（查看文檔或你所使用的`Find*.cmake`文件）。如果你追加到你的`CMAKE_MODULE_PATH`，你也可以包括一個CMake幫助文件目錄，例如添加`pybind11`改進過的`FindPython*.cmake`文件。


### 小貼士：獲取 Git 版本號

將下面的命令加入到上述 Git 更新子倉庫的那段中：

```cmake
execute_process(COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD
                WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
                OUTPUT_VARIABLE PACKAGE_GIT_VERSION
                ERROR_QUIET
                OUTPUT_STRIP_TRAILING_WHITESPACE)
```
