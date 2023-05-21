# C++11 及後續版本

CMake 中支持 C++11，但是這是針對於 CMake 2.8 及以後的版本來說的。這是為什麼？很容易可以猜到， C++11 在 2009年——CMake 2.0 發佈的時候還不存在。只要你使用 CMake 的是 CMake 3.1 或者更新的版本，你將會得到 C++11 的完美支持，不過這裡有兩種不同的方式來啟用支持。 並且你將看到，在 CMake 3.8+ 中對 C++11 有著更好的支持。我將會在 CMake 3.8+ 的基礎上講解，因為這才叫做 Modern CMake。 


## CMake 3.8+: 元編譯器選項

只要你使用新版的 CMake 來組織你的項目，那你就能夠使用最新的方式來啟用 C++ 的標準。這個方式功能強大，語法優美，並且對最新的標準有著很好的支持。此外，它對目標 (target) 進行混合標準與選項設置有著非常優秀的表現。假設你有一個名叫 `myTarget` 的目標，它看起來像這樣：

```cmake
target_compile_features(myTarget PUBLIC cxx_std_11)
set_target_properties(myTarget PROPERTIES CXX_EXTENSIONS OFF)
```

對於第一行，我們可以在 `cxx_std_11`、`cxx_std_14` 和 `cxx_std_17` 之間選擇。第二行是可選的，但是添加了可以避免 CMake 對選項進行拓展。如果不添加它，CMake 將會添加選項 `-std=g++11` 而不是 `-std=c++11` 。第一行對 `INTERFACE` 這種目標 (target) 也會起作用，第二行只會對實際被編譯的目標有效。

如果在目標的依賴鏈中有目標指定了更高的 C++ 標準，上述代碼也可以很好的生效。這只是下述方法的一個更高級的版本，因此可以很好的生效。

## CMake 3.1+: 編譯器選項

你可以指定開啟某個特定的編譯器選項。這相比與直接指定 C++ 編譯器的版本更加細化，儘管去指定一個包使用的所有編譯器選項可能有點困難，除非這個包是你自己寫的或者你的記憶力非凡。最後 CMake 會檢查你編譯器支持的所有選項，並默認設置使用其中每個最新的版本。因此，你不必指定所有你需要的選項，只需要指定那些和默認有出入的。設置的語法和上一部分相同，只是你需要挑選一個列表裡面存在的選項而不像是 `cxx_std_*` 。這裡有包含[所有選項的列表](https://cmake.org/cmake/help/latest/prop_gbl/CMAKE_CXX_KNOWN_FEATURES.html)。

如果你需要可選的選項，在 CMake 3.3+ 中你可以使用列表 `CMAKE_CXX_COMPILE_FEATURES` 及 `if(... INLIST ...) ` 來查看此選項是否在此項目中被選用，然後來決定是否添加它。可以 [在此](https://cmake.org/cmake/help/latest/manual/cmake-compile-features.7.html) 查看一些其他的使用情況。


## CMake 3.1+: 全局設置以及屬性設置

這是支持 C++ 標準的另一種方式，（在目標及全局級別）設置三個特定屬性的值。這是全局的屬性：

```cmake
set(CMAKE_CXX_STANDARD 11 CACHE STRING "The C++ standard to use")
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
```

第一行設置了 C++ 標準的級別， 第二行告訴 CMake 使用上述設置， 最後一行關閉了拓展，來明確自己使用了 `-std=c++11` 還是 `-std=g++11` 。這個方法中可以在最終包 (final package) 中使用，但是不推薦在庫中使用。你應該總是把它設置為一個緩存變量，這樣你就可以很容易地重寫其內容來嘗試新的標準（或者如果你在庫中使用它的話，這是重寫它的唯一方式。**不過再重申一遍**，不要在庫中使用此方式）。你也可以對目標來設置這些屬性：

```cmake
set_target_properties(myTarget PROPERTIES
    CXX_STANDARD 11
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)
```

這種方式相比於上面來說更好，但是仍然沒法對 `PRIVATE` 和 `INTERFACE` 目標的屬性有明確的控制，所以他們也仍然只對最終目標 (final targets) 有用。

你可以在 [Craig Scott's useful blog post][crascit] 這裡找到更多關於後面兩種方法的信息。 

{% hint style='danger' %}

不要自己設置手動標誌。如果這麼做，你必須對每個編譯器的每個發行版設置正確的標誌，你無法通過不支持的編譯器的報錯信息來解決錯誤，並且 IDE 可能不會去關心手動設置的標誌。
{% endhint %}

[crascit]: https://crascit.com/2015/03/28/enabling-cxx11-in-cmake/
