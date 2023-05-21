# 運行 CMake

在編寫 CMake 之前，要確保你已經清楚瞭如何運行 CMake 來構建文件。 幾乎所有 CMake 項目都一樣。

## 構建項目

除非另行說明，你始終應該建立一個專用於構建的目錄並在那裡構建項目。從技術上來講，你可以進行內部構建（即在源代碼目錄下執行 CMake 構建命令），但是必須注意不要覆蓋文件或者把它們添加到 git，所以別這麼做就好。

這是經典的 CMake 構建流程 （TM）：

{% term %}
~/package $ mkdir build
~/package $ cd build
~/package/build $ cmake ..
~/package/build $ make
{% endterm %}

你可以用 `cmake --build .` 替換 `make` 這一行。它會調用 `make` 或這任何你正在使用的構建工具。如果你正在使用版本比較新的 CMake（除非你正在檢查對於老版本 CMake 的兼容性，否則應該使用較新的版本），你也可以這樣做：

{% term %}
~/package $ cmake -S . -B build
~/package $ cmake --build build
{% endterm %}

以下**任何一條**命令都能夠執行安裝：

{% term %}
# From the build directory (pick one)
~/package/build $ make install
~/package/build $ cmake --build . --target install
~/package/build $ cmake --install . # CMake 3.15+ only

# From the source directory (pick one)
~/package $ make -C build install
~/package $ cmake --build build --target install
~/package $ cmake --install build # CMake 3.15+ only
{% endterm %}

所以你應該選擇哪一種方法？只要你**別忘記**輸入構建目錄作為參數，在構建目錄之外的時間較短，並且從源代碼目錄更改源代碼比較方便就行。你應該試著習慣使用 `--build`，因為它能讓你免於只用 `make` 來構建。需要注意的是，在構建目錄下進行工作一直都非常普遍，並且一些工具和命令（包括 CTest）仍然需要在 build 目錄中才能工作。

額外解釋一下，你可以指定 CMake 工作在**來自構建目錄**的源代碼目錄，也可以工作在任何**現有**的構建目錄。

如果你使用 `cmake --build` 而不是直接調用更底層的構建系統（譯者注：比如直接使用 `make`），你可以用 `-v` 參數在構建時獲得詳細的輸出（CMake 3.14+），用 `-j N` 指定用 N 個 CPU 核心並行構建項目（Cmake 3.12+），以及用 `--target`（任意版本的 CMake）或 `-t`（CMake 3.15+）來選擇一個目標進行部分地構建。這些命令因不同的構建系統而異，例如 `VERBOSE=1 make` 和 `ninja -v`。你也可以使用環境變量替代它們，例如 `CMAKE_BUILD_PARALLEL_LEVEL` (CMake 3.12+) 和 `VERBOSE` (CMake 3.14+)。

## 指定編譯器

指定編譯器必須在第一次運行時在空目錄中進行。這種命令並不屬於 CMake 語法，但你仍可能不太熟悉它。如果要選擇 Clang：

{% term %}
~/package/build $ CC=clang CXX=clang++ cmake ..
{% endterm %}

這條命令設置了 bash 裡的環境變量 CC 和 CXX，並且 CMake 會使用這些參數。這一行命令就夠了，你也只需要調用一次；之後 CMake 會繼續使用從這些變量裡推導出來的路徑。

## 指定生成器

你可以選擇的構建工具有很多；通常默認的是 `make`。要顯示在你的系統上 CMake 可以調用的所有構建工具，運行：

{% term %}
~/package/build $ cmake --help
{% endterm %}

你也可以用 `-G"My Tool"`（僅當構建工具的名字中包含空格時才需要引號）來指定構建工具。像指定編譯器一樣，你應該在一個目錄中第一次調用 CMake 時就指定構建工具。如果有好幾個構建目錄也沒關係，比如 `build/` 和 `buildXcode`。你可以用環境變量 `CMAKE_GENERATOR` 來指定默認的生成器（CMake 3.15+）。需要注意的是，makefiles 只會在你明確地指出線程數目之時才會並行運行，比如 `make -j2`，而 Ninja 卻會自動地並行運行。在較新版本的 CMake 中，你能直接傳遞並行選項，比如`-j2`，到命令 `cmake --build `。

## 設置選項

在 CMake 中，你可以使用 `-D` 設置選項。你能使用 `-L` 列出所有選項，或者用 `-LH` 列出人類更易讀的選項列表。如果你沒有列出源代碼目錄或構建目錄，這條命令將不會重新運行 CMake（使用 `cmake -L` 而不是 `cmake -L .`）。

## 詳細和部分的構建

同樣，這不屬於 CMake，如果你正使用像 `make` 一樣的命令行構建工具，你能獲得詳細的輸出：

{% term %}
~/package/build $ VERBOSE=1 make96

我們已經提到了在構建時可以有詳細輸出，但你也可以看到詳細的 CMake 配置輸出。`--trace` 選項能夠打印出運行的 CMake 的每一行。由於它過於冗長，CMake 3.7 添加了 `--trace-source="filename"` 選項，這讓你可以打印出你想看的特定文件運行時執行的每一行。如果你選擇了要調試的文件的名稱（在調試一個 CMakeLists.txt 時通常選擇父目錄，因為它們名字都一樣），你就會只看到這個文件裡運行的那些行。這很實用！


{% endterm %}

實際上你寫成 `make VERBOSE=1`，make 也能正確工作，但這是 `make` 的一個特性而不是命令行的慣用寫法。

你也可以通過指定一個目標來僅構建一部分，例如指定你已經在 CMake 中定義的庫或可執行文件的名稱，然後 make 將會只構建這一個目標。

## 選項

CMake 支持緩存選項。CMake 中的變量可以被標記為 "cached"，這意味著它會被寫入緩存（構建目錄中名為 `CMakeCache.txt` 的文件）。你可以在命令行中用 `-D` 預先設定（或更改）緩存選項的值。CMake 查找一個緩存的變量時，它就會使用已有的值並且不會覆蓋這個值。

### 標準選項

大部分軟件包中都會用到以下的 CMake 選項：

* `-DCMAKE_BUILD_TYPE=` 從 Release， RelWithDebInfo， Debug， 或者可能存在的更多參數中選擇。
* `-DCMAKE_INSTALL_PREFIX=` 這是安裝位置。UNIX 系統默認的位置是 `/usr/local`，用戶目錄是 `~/.local`，也可以是你自己指定的文件夾。
* `-DBUILD_SHARED_LIBS=` 你可以把這裡設置為 `ON` 或 `OFF` 來控制共享庫的默認值（不過，你也可以明確選擇其他值而不是默認值）
* `-DBUILD_TESTING=` 這是啟用測試的通用名稱，當然不會所有軟件包都會使用它，有時這樣做確實不錯。

## 調試你的 CMake 文件

我們已經提到了在構建時可以有詳細輸出，但你也可以看到詳細的 CMake 配置輸出。`--trace` 選項能夠打印出運行的 CMake 的每一行。由於它過於冗長，CMake 3.7 添加了 `--trace-source="filename"` 選項，這讓你可以打印出你想看的特定文件運行時執行的每一行。如果你選擇了要調試的文件的名稱（在調試 CMakeLists.txt 時通常選擇父目錄，因為它的名字在任何項目中都一樣），你就會只看到這個文件裡運行的那些行。這很實用！
