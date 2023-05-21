# 用 CMake 進行編程

## 控制流程


CMake 有一個 «command:`if`» 語句，儘管經過多次版本迭代它已經變得非常複雜。這裡有一些全大寫的變量你可以在 `if` 語句中使用，並且你既可以直接引用也可以利用 `${}` 來對他進行解析（  `if` 語句在歷史上比變量拓展出現的更早 ）。這是一個 `if` 語句的例子：


```cmake
if(variable)
    # If variable is `ON`, `YES`, `TRUE`, `Y`, or non zero number
else()
    # If variable is `0`, `OFF`, `NO`, `FALSE`, `N`, `IGNORE`, `NOTFOUND`, `""`, or ends in `-NOTFOUND`
endif()
# If variable does not expand to one of the above, CMake will expand it then try again
```


如果你在這裡使用 `${variable}` 可能會有一些奇怪，因為看起來它好像 `variable` 被展開 ( expansion ) 了兩次。在 CMake 3.1+ 版本中加入了一個新的特性 ( «policy:CMP0054» ) ，CMake 不會再展開已經被引號括起來的展開變量。也就是說，如果你的 CMake 版本大於 `3.1` ，那麼你可以這麼寫：


```cmake
if("${variable}")
    # True if variable is not false-like
else()
    # Note that undefined variables would be `""` thus false
endif()
```

這裡還有一些關鍵字可以設置，例如：

* 一元的: `NOT`, `TARGET`, `EXISTS` (文件), `DEFINED`, 等。

* 二元的: `STREQUAL`, `AND`, `OR`, `MATCHES` ( 正則表達式 ), `VERSION_LESS`, `VERSION_LESS_EQUAL` ( CMake 3.7+ ), 等。

* 括號可以用來分組


## «cmake:generator-expressions»


«cmake:generator-expressions» 語句十分強大，不過有點奇怪和專業 ( specialized ) 。大多數 CMake 命令在配置的時候執行，包括我們上面看到的 `if` 語句。但是如果你想要他們在構建或者安裝的時候運行呢，應該怎麼寫？ 生成器表達式就是為此而生[^1]。它們在目標屬性中被評估（ evaluate ）：

最簡單的生成器表達式是信息表達式，其形式為 `$<KEYWORD>`；它會評估和當前配置相關的一系列信息。信息表達式的另一個形式是 `${KEYWORD:value}`，其中 `KEYWORD` 是一個控制評估的關鍵字，而 `value` 則是需要進行比較的值（ 這裡的 `KEYWORD` 也允許使用信息表達式 ）。如果 `KEYWORD` 是一個可以被評估為0或1的生成器表達式或者變量，如果（`KEYWORD`被評估）為1則將會被替換（成`value`），如果是0則不會替換。你可以使用嵌套的生成器表達式，你也可以使用變量來使得自己更容易理解嵌套的變量。一些表達式也可以有多個值，值之間通過逗號分隔[^2]。


{% hint style='info' %}

譯者注：這裡有點類似於 C 語言中的條件運算符。這裡由於譯者英語水平的問題，翻譯的不夠清楚，後續會改善。

{% endhint %}


如果你有一個只想在 DEBUG 模式下開啟的編譯標誌（ flag ），你可以這樣做：

```
target_compile_options(MyTarget PRIVATE "$<$<CONFIG:Debug>:--my-flag>")
```

這是一個相比與指定一些形如 `*_DEBUG` 這樣的變量更加新穎並且更加優雅的方式，並且這對所有支持生成器表達式的設置都通用。需要注意的是，你應該永遠都不要使用配置時間的值作為當前的配置，因為像 IDE 這種多配置生成器不會在配置過程中生成配置時間，只有在構建時可以通過生成器表達式和 `*_<CONFIG>` 這類變量可以獲得。

一些生成器表達式的其他用途：

+ 限制某個項目的語言，例如可以限制其語言為 CXX 來避免它和 CUDA 等語言混在一起，或者可以通過封裝它來使得他對不同的語言有不同的表現。
+ 獲得與屬性相關的配置，例如文件的位置。
+ 為構建和安裝生成不同的位置。

最後一個是常見的。你幾乎會在所有支持安裝的軟件包中看到如下代碼：

```cmake
target_include_directories(
    MyTarget
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
```

## 宏定義與函數

你可以輕鬆地定義你自己的 CMake «command:`function`» 或 «command:`macro`» 。函數和宏只有作用域上存在區別，宏沒有作用域的限制。所以說，如果你想讓函數中定義的變量對外部可見，你需要使用 `PARENT_SCOPE` 來改變其作用域。如果是在嵌套函數中，這會變得異常繁瑣，因為你必須在想要變量對外的可見的所有函數中添加 `PARENT_SCOPE` 標誌。但是這樣也有好處，函數不會像宏那樣對外“洩漏”所有的變量。接下來用函數舉一個例子：

下面十一個簡單的函數的例子：

```cmake
function(SIMPLE REQUIRED_ARG)
    message(STATUS "Simple arguments: ${REQUIRED_ARG}, followed by ${ARGN}")
    set(${REQUIRED_ARG} "From SIMPLE" PARENT_SCOPE)
endfunction()

simple(This Foo Bar)
message("Output: ${This}")
```

輸出如下：

```
-- Simple arguments: This, followed by Foo;Bar
Output: From SIMPLE
```


如果你想要有一個指定的參數，你應該在列表中明確的列出，初此之外的所有參數都會被存儲在 `ARGN` 這個變量中（  `ARGV` 中存儲了所有的變量，包括你明確列出的 ）。CMake 的函數沒有返回值，你可以通過設定變量值的形式來達到同樣地目的。在上面的例子中，你可以通過指定變量名來設置一個變量的值。


## 參數的控制

你應該已經在很多 CMake 函數中見到過，CMake 擁有一個變量命名系統。你可以通過 «command:`cmake_parse_arguments`» 函數來對變量進行命名與解析。如果你想在低於 3.5 版本的CMake 系統中使用它，你應該包含 «module:CMakeParseArguments» 模塊，此函數在 CMake 3.5 之前一直存在與上述模塊中。這是使用它的一個例子：

```cmake
function(COMPLEX)
    cmake_parse_arguments(
        COMPLEX_PREFIX
        "SINGLE;ANOTHER"
        "ONE_VALUE;ALSO_ONE_VALUE"
        "MULTI_VALUES"
        ${ARGN}
    )
endfunction()

complex(SINGLE ONE_VALUE value MULTI_VALUES some other values)
```

在調用這個函數後，會生成以下變量：

```cmake
COMPLEX_PREFIX_SINGLE = TRUE
COMPLEX_PREFIX_ANOTHER = FALSE
COMPLEX_PREFIX_ONE_VALUE = "value"
COMPLEX_PREFIX_ALSO_ONE_VALUE = <UNDEFINED>
COMPLEX_PREFIX_MULTI_VALUES = "some;other;values"
```

如果你查看了官方文檔，你會發現可以通過 set 來避免在 list 中使用分號，你可以根據個人喜好來確定使用哪種結構。你可以在上面列出的位置參數中混用這兩種寫法。此外，其他剩餘的參數（因此參數的指定是可選的）都會被保存在 `COMPLEX_PREFIX_UNPARSED_ARGUMENTS` 變量中。

[^1]: 他們看起來像是在構建或安裝時被評估的，但實際上他們只對每個構建中的配置進行評估。
[^2]: CMake 官方文檔中將表達式分為信息表達式，邏輯表達式和輸出表達式。
