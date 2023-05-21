# CMake 對 IDE 的支持

一般來說，IDE 已經被標準的 CMake 的項目支持。不過這裡有一些額外的東西可以幫助 IDE 表現得更好：

## 用文件夾來組織目標 (target)

一些 IDE，例如 Xcode，支持文件夾。你需要手動的設定 `USE_FOLDERS` 這個全局屬性來允許 CMake 使用文件夾組織你的文件：

```cmake
set_property(GLOBAL PROPERTY USE_FOLDERS ON)
```

然後，你可以在創建目標後，為目標添加文件夾屬性，即將其目標 `MyFile` 歸入到 `Scripts` 文件夾中：

```cmake
set_property(TARGET MyFile PROPERTY FOLDER "Scripts")
```

文件夾可以使用 `/` 進行嵌套。



你可以使用正則表達式或在 [`source_group`](https://cmake.org/cmake/help/latest/command/source_group.html) 使用列表來控制文件在文件夾中是否可見。

## 用文件夾來組織文件

你也可以控制文件夾對目標是否可見。有兩種方式，都是使用 «command:source_group» 命令，傳統的方式是：

```cmake
source_group("Source Files\\New Directory" REGULAR_EXPRESSION ".*\\.c[ucp]p?")
```

你可以用 `FILES` 來明確的列出文件列表，或者使用 `REGULAR_EXPRESSION` 來進行篩選。通過這個方式你可以完全的掌控文件夾的結構。不過，如果你的文件已經在硬盤中組織的很好，你可能只是想在 CMake 中復現這種組織。在 CMake 3.8+ 中，你可以用新版的 «command:source_group» 命令非常容易的做到上述情形：

```cmake
source_group(TREE "${CMAKE_CURRENT_SOURCE_DIR}/base/dir" PREFIX "Header Files" FILES ${FILE_LIST})
```

對於 `TREE` 選項，通常應該給出一個以 `${CMAKE_CURRENT_SOURCE_DIR}` 起始的完整路徑（因為此命令的文件解析路徑是相對於構建目錄的）。這個 `PREFIX` 設置文件將在 IDE 結構中的位置，而 `FILES` 選項是包含一些文件的列表 (FILE_LIST)。CMake 將會解析 `TREE` 路徑下 `FILE_LIST` 中包含的文件，並將每個文件添加到 `PREFIX` 結構下，這構成了 IDE 的文件夾結構。

> 注意：如果你需要支持低於 3.8 版本的CMake，我不建議你使用上述命令，只建議在 CMake 3.8+ 中使用上述文件夾佈局。對於做這種文件夾佈局的舊方法，請參見 [這篇博文][sorting]。

## 在 IDE 中運行CMake

要使用 IDE，如果 CMake 可以生成對應 IDE 的文件（例如 Xcode，Visual Studio），可以通過 `-G"name of IDE"` 來完成，或者如果 IDE 已經內置了對 CMake 的支持（例如 CLion，QtCreator和一些其他的IDE），你可以直接在 IDE 中打開 `CMakeLists.txt` 來運行 CMake。


[sorting]: http://blog.audio-tk.com/2015/09/01/sorting-source-files-and-projects-in-folders-with-cmake-and-visual-studioxcode/
