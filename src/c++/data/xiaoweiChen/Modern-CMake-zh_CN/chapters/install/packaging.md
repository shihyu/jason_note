# 打包

CMake有兩種打包方式：一是使用`CPackConfig.cmake`文件；二是將 CPack 變量放置在 CMakeLists.txt 文件中。若想要包含主構建的相關變量（比如：版本號），可以使用配置文件的方式。這裡，我將展示第二種方式：

```cmake
# Packaging support
set(CPACK_PACKAGE_VENDOR "Vendor name")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Some summary")
set(CPACK_PACKAGE_VERSION_MAJOR ${PROJECT_VERSION_MAJOR})
set(CPACK_PACKAGE_VERSION_MINOR ${PROJECT_VERSION_MINOR})
set(CPACK_PACKAGE_VERSION_PATCH ${PROJECT_VERSION_PATCH})
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENCE")
set(CPACK_RESOURCE_FILE_README "${CMAKE_CURRENT_SOURCE_DIR}/README.md")
```

這些是生成工件包時最常見的變量。工件包使用CMake的安裝機制，已經安裝的東西都會顯示出來。

當然，還可以製作源碼包。可以將相應的正則表達式添加到 `CMAKE_SOURCE_IGNORE_FILES` 中，以確保只打包期望的文件（排除構建目錄或git信息）；否則，`package_source` 會將源目錄中的所有內容打包在一起。這裡，也可以根據自己的喜歡的文件類型，對源碼包生成器進行設置：

```cmake
set(CPACK_SOURCE_GENERATOR "TGZ;ZIP")
set(CPACK_SOURCE_IGNORE_FILES
    /.git
    /dist
    /.*build.*
    /\\\\.DS_Store
)
```

注意，這種方式無法在Windows系統中正常運行，但是生成的源碼包可以在Windows系統中正常使用。

最後，需要包含一下CPack模塊:

```cmake
include(CPack)
```
