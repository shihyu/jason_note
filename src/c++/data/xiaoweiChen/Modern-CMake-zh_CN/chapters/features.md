# 為 CMake 項目添加特性

本節將會涵蓋如何為你的 CMake 項目添加特性。你將會學到如何為你的 C++ 項目添加一些常用的選項，如 C++11 支持，以及如何支持 IDE 工具等。


## 默認的構建類型

CMake 通常會設置一個 “既不是 Release 也不是Debug” 的空構建類型來作為默認的構建類型，如果你想要自己設置默認的構建類型，你可以參考 [Kitware blog](https://blog.kitware.com/cmake-and-the-default-build-type/) 中指出的方法。

```cmake
set(default_build_type "Release")
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to '${default_build_type}' as none was specified.")
  set(CMAKE_BUILD_TYPE "${default_build_type}" CACHE
      STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()
```

