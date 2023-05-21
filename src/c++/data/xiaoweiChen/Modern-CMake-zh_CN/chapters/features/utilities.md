# CCache 和一些其他的實用工具

在過去的一些版本中，一些能夠幫助你寫好代碼的實用工具已經被添加到了 CMake 中。往往是通過為目標指定屬性，或是設定形如 `CMAKE_*` 的初始化變量的值的形式啟用相應工具。這個啟用的規則不只是對某個特定的工具（program）起作用，一些行為相似的工具都符合此規則。

當需要啟用多個工具時，所有的這些變量都通過 `;` 分隔（CMake 中列表的分隔標準）來描述你在目標源程序上需要使用的工具( program) 以及選項。

## CCache[^1]

通過設置變量 `CMAKE_<LANG>_COMPILER_LAUNCHER` 或設置目標的 `<LANG>_COMPILER_LAUNCHER` 屬性來使用一些像 CCache 的方式來“封裝”目標的編譯。在 CMake 的最新版本中拓展了對 CCache 的支持。在使用時，可以這麼寫：


```cmake
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    set(CMAKE_CXX_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
    set(CMAKE_CUDA_COMPILER_LAUNCHER "${CCACHE_PROGRAM}") # CMake 3.9+
endif()
```


## 一些實用工具

設置以下屬性或是在命令行中設置以 `CMAKE_*` 為起始的變量來啟動這些功能。它們大部分只在 make 或 ninja 生成器生成 C 和 CXX 項目時起作用。

* `<LANG>_CLANG_TIDY`: CMake 3.6+
* `<LANG>_CPPCHECK`
* `<LANG>_CPPLINT`
* `<LANG>_INCLUDE_WHAT_YOU_USE`

## Clang tidy[^2]

這是在命令行中運行 clang-tidy的方法，使用的是一個列表（記住，用分號分隔的字符串是一個列表）。

這是一個使用 Clang-Tidy 的簡單例子：

```term
~/package # cmake -S . -B build-tidy -DCMAKE_CXX_CLANG_TIDY="$(which clang-tidy);-fix"
~/package # cmake --build build -j 1
```

這裡的 `-fix` 部分是可選的，將會修改你的源文件來嘗試修復 clang-tidy 警告 (warning) 的問題。如果你在一個 git 倉庫中工作的話，使用 `-fix` 是相當安全的，因為你可以看到代碼中哪部分被改變了。不過，請確保**不要同時運行你的 makefile/ninja 來進行構建**！如果它嘗試修復一個相同的頭文件兩次，可能會出現預期外的錯誤。

如果你想明確的使用目標的形式來確保自己對某些特定的目標調用了 clang-tidy，為可以設置一個變量（例如像 `DO_CLANG_TIDY`，而不是名為 `CMAKE_CXX_CLANG_TIDY` 的變量），然後在創建目標時，將它添加為目標的屬性。你可以通過以下方式找到路徑中的 clang-tidy：

```cmake
find_program(
    CLANG_TIDY_EXE
    NAMES "clang-tidy"
    DOC "Path to clang-tidy executable"
)
```

## Include what you use[^3]

這是一個使用 `include what you use` 的例子。首先，你需要確保系統中有這個工具，例如在一個 docker 容器中或者通過 macOS 上的 brew 利用 `brew install include-what-you-use` 來安裝它。然後，你可以通過此方式使用此工具，而不需要修改你的源代碼：

```term
~/package # cmake -S . -B build-iwyu -DCMAKE_CXX_INCLUDE_WHAT_YOU_USE=include-what-you-use
```

最後，你可以重定向輸出到文件，然後選擇是否應用此修復：

```term
~/package # cmake --build build-iwyu 2> iwyu.out
~/package # fix_includes.py < iwyu.out
```

（你應該先檢查一下這些修復的正確性，或者在修復後對代碼進行潤色！）

## Link what you use

這是一個布爾類型的目標屬性，`LINK_WHAT_YOU_USE`，它將會在鏈接時檢查與目標不相干的文件。

## Clang-format[^4]

不幸的是，Clang-format 並沒有真正的與 CMake 集成。你可以製作一個自定義的目標（參考 [這篇文章](https://arcanis.me/en/2015/10/17/cppcheck-and-clang-format)，或者你可以嘗試自己手動的去運行它。）一個有趣的項目/想法 [在這裡](https://github.com/kbenzie/git-cmake-format)，不過我還沒有親自嘗試過。它添加了一個格式化 (format) 的目標，並且你甚至沒法提交沒有格式化過的文件。

下面的兩行可以在一個 git 倉庫中，在 `bash ` 中使用 clang-format 工具（假設你有一個 `.clang-format` 文件）：

```term
gitbook $ git ls-files -- '*.cpp' '*.h' | xargs clang-format -i -style=file
gitbook $ git diff --exit-code --color
```



{% hint style='info' %}

譯者注：以下所有的腳註說明都為譯者添加，原文並不包含此信息。腳註的說明資料均來自於互聯網。
{% endhint %}



[^1]: Ccache（或 ”ccache“）是一個編譯器緩存。它通過緩存之前的編譯文件並且利用之前已經完成的編譯過程來[加速重編譯]((https://ccache.dev/performance.html))。Ccache是一個免費的軟件，基於 [GNU General Public License version 3](http://www.gnu.org/licenses/gpl.html) 或之後更新的許可協議發佈。可以查看這裡的 [許可協議頁面](https://ccache.dev/license.html) 。
[^2]: **clang-tidy** 是一個基於 clang 的 C++ 代碼分析工具。它意圖提供一個可擴展的框架，用於診斷和修復典型的編程錯誤，如樣式違規、接口誤用、或通過靜態分析推斷出的錯誤。**clang-tidy** 是一個模塊化的程序，為編寫新的檢查規則提供了方便的接口。
[^3]: 一個與 **clang** 一起使用，用於分析 C 和 C++ 源文件中 **#include** 的工具。
[^4]:  ClangFormat 描述了一套建立在 [LibFormat](https://clang.llvm.org/docs/LibFormat.html) 之上的工具。它可以以各種方式支持你的工作流程，包括獨立的工具和編輯器的集成。
