# 安裝

進行安裝時，比如執行 `make install`，安裝命令會將文件或目標“安裝”到安裝樹中。簡單使用目標安裝指令的方式:

```cmake
install(TARGETS MyLib
        EXPORT MyLibTargets
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin
        INCLUDES DESTINATION include
        )
```

當有一個庫、靜態庫或程序要安裝時，才需要將不同的文件安裝到不同的目的地。由於目標不安裝包含目錄，所以 包含（INCLUDES）目標是特殊的。只能在導出的目標上設置包含目錄（通常由`target_include_directories`設置，若想要清理cmake文件，需要檢查MyLibTargets文件，確定沒有多次包含同一個包含目錄）。

給定 CMake 可訪問的版本是個不錯的方式。使用 `find_package` 時，可以這樣指定版本信息:

```cmake
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    MyLibConfigVersion.cmake
    VERSION ${PACKAGE_VERSION}
    COMPATIBILITY AnyNewerVersion
    )
```

接下來有兩個選擇。創建`MyLibConfig.cmake`，可以直接將目標導出放在這個文件中，或者手動寫入，然後包目標文件。若有依賴項（可能只是OpenMP），則需要添加相應的選項。下面是個例子：

首先，創建一個安裝目標文件（類似於在構建目錄中創建的文件）：

```cmake
install(EXPORT MyLibTargets
        FILE MyLibTargets.cmake
        NAMESPACE MyLib::
        DESTINATION lib/cmake/MyLib
         )
```

該文件將獲取導出目標，並將其放入文件中。若沒有依賴項，只需使用 `MyLibConfig.cmake` 代替 `MyLibTargets.cmake` 即可。然後，在源碼樹的某處，創建一個自定義 `MyLibConfig.cmake` 文件。若想要捕獲配置時的變量，可以使用 `.in` 文件，並且可以使用 `@var@` 語法。具體方式如下所示：

```cmake
include(CMakeFindDependencyMacro)

# Capturing values from configure (optional)
set(my-config-var @my-config-var@)

# Same syntax as find_package
find_dependency(MYDEP REQUIRED)

# Any extra setup

# Add the targets file
include("${CMAKE_CURRENT_LIST_DIR}/MyLibTargets.cmake")
```

現在，可以使用配置文件（若使用 `.in` 文件），然後安裝已生成的文件。因為創建了`ConfigVersion`文件，所以可以在這裡安裝它。

```cmake
configure_file(MyLibConfig.cmake.in MyLibConfig.cmake @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/MyLibConfig.cmake"
              "${CMAKE_CURRENT_BINARY_DIR}/MyLibConfigVersion.cmake"
        DESTINATION lib/cmake/MyLib
        )
```

就是這樣！現在，當包安裝完成後，`lib/cmake/MyLib` 中就出現了 CMake 搜索所需的文件（特別是`MyLibConfig.cmake`和`MyLibConfigVersion.cmake`），配置時使用的目標文件應該也在那裡。

當 CMake 搜索包時，將在當前安裝目錄，以及幾個標準位置中進行查找。可以手動將相應的目錄添加到搜索路徑中，包括 `MyLib_PATH`。若沒有找到配置文件，CMake會輸出相應的信息，告知用戶當前的情況。
