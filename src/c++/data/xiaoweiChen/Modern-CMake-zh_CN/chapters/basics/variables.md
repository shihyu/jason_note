# 變量與緩存

## 本地變量
我們首先討論變量。你可以這樣聲明一個本地 ( local ) 變量：

```CMake
set(MY_VARIABLE "value")
```

變量名通常全部用大寫，變量值跟在其後。你可以通過 `${}` 來解析一個變量，例如 `${MY_VARIABLE}`.[^1] CMake 有作用域的概念，在聲明一個變量後，你只可以它的作用域內訪問這個變量。如果你將一個函數或一個文件放到一個子目錄中，這個變量將不再被定義。你可以通過在變量聲明末尾添加 `PARENT_SCOPE` 來將它的作用域置定為當前的上一級作用域。

列表就是簡單地包含一系列變量：

```cmake
set(MY_LIST "one" "two")
```

你也可以通過 `;` 分隔變量，這和空格的作用是一樣的：

```cmake
set(MY_LIST "one;two")
```

有一些和 `list( ` 進行協同的命令， `separate_arguments` 可以把一個以空格分隔的字符串分割成一個列表。需要注意的是，在 CMake 中如果一個值沒有空格，那麼加和不加引號的效果是一樣的。這使你可以在處理知道不可能含有空格的值時不加引號。

當一個變量用 `${}` 括起來的時候，空格的解析規則和上述相同。對於路徑來說要特別小心，路徑很有可能會包含空格，因此你應該總是將解析變量得到的值用引號括起來，也就是，應該這樣 `"${MY_PATH}"` 。

## 緩存變量

CMake 提供了一個緩存變量來允許你從命令行中設置變量。CMake 中已經有一些預置的變量，像 `CMAKE_BUILD_TYPE` 。如果一個變量還沒有被定義，你可以這樣聲明並設置它。

```cmake
set(MY_CACHE_VARIABLE "VALUE" CACHE STRING "Description")
```

這麼寫**不會覆蓋**已定義的值。這是為了讓你只能在命令行中設置這些變量，而不會在 CMake 文件執行的時候被重新覆蓋。如果你想把這些變量作為一個臨時的全局變量，你可以這樣做：

```cmake
set(MY_CACHE_VARIABLE "VALUE" CACHE STRING "" FORCE)
mark_as_advanced(MY_CACHE_VARIABLE)
```

第一行將會強制設置該變量的值，第二行將使得用戶運行 `cmake -L ..` 或使用 GUI 界面的時候不會列出該變量。此外，你也可以通過 `INTERNAL` 這個類型來達到同樣的目的（儘管在技術上他會強制使用 STRING 類型，這不會產生任何的影響）：

```cmake
set(MY_CACHE_VARIABLE "VALUE" CACHE INTERNAL "")
```

因為 `BOOL` 類型非常常見，你可以這樣非常容易的設置它：

 ```cmake
 option(MY_OPTION "This is settable from the command line" OFF)
 ```

對於 `BOOL` 這種數據類型，對於它的 `ON` 和 `OFF` 有幾種不同的說辭 (wordings) 。

你可以查看 [cmake-variables] 來查看 CMake 中已知變量的清單。

## 環境變量

你也可以通過 `set(ENV{variable_name} value)` 和 `$ENV{variable_name}` 來設置和獲取環境變量，不過一般來說，我們最好避免這麼用。

## 緩存

緩存實際上就是個文本文件，`CMakeCache.txt` ，當你運行 CMake 構建目錄時會創建它。 CMake 可以通過它來記住你設置的所有東西，因此你可以不必在重新運行 CMake 的時候再次列出所有的選項。

## 屬性

CMake 也可以通過屬性來存儲信息。這就像是一個變量，但它被附加到一些其他的物體 (item) 上，像是一個目錄或者是一個目標。一個全局的屬性可以是一個有用的非緩存的全局變量。許多目標屬性都是被以 `CMAKE_` 為前綴的變量來初始化的。例如你設置 `CMAKE_CXX_STANDARD` 這個變量，這意味著你之後創建的所有目標的 `CXX_STANDARD` 都將被設為`CMAKE_CXX_STANDARD` 變量的值。

你可以這樣來設置屬性：

```cmake
set_property(TARGET TargetName
             PROPERTY CXX_STANDARD 11)

set_target_properties(TargetName PROPERTIES
                      CXX_STANDARD 11)
```

第一種方式更加通用 ( general ) ，它可以一次性設置多個目標、文件、或測試，並且有一些非常有用的選項。第二種方式是為一個目標設置多個屬性的快捷方式。此外，你可以通過類似於下面的方式來獲得屬性：

```cmake
get_property(ResultVariable TARGET TargetName PROPERTY CXX_STANDARD)
```

可以查看 [cmake-properties] 獲得所有已知屬性的列表。在某些情況下，你也可以自己定義一些屬性[^2]。

[cmake-properties]: https://cmake.org/cmake/help/latest/manual/cmake-properties.7.html
[cmake-variables]: https://cmake.org/cmake/help/latest/manual/cmake-variables.7.html

[^1]:  `if` 的條件部分語法有一些奇怪，因為 `if` 語法比 `${}` 出現的更早，所以它既可以加 `${}` 也可以不加 `${}`。 
[^2]: 對於接口類的目標，可能對允許自定義的屬性有一些限制。
