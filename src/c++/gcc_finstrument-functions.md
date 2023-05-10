## GCC finstrument-functions



- 最外層CMakeLists.txt

```c
# Modules
add_subdirectory("func_tracker") # 加入 func_tracker 子目錄
    
add_definitions(-finstrument-functions) #函數追蹤

# Library
target_link_libraries(cpptrader ${LINKLIBS} func_tracker)

```

```sh
func_tracker/
├── CMakeLists.txt
└── FuncTracker.cpp
```

- CMakeLists.txt

  ```Cmake
  cmake_minimum_required(VERSION 3.20)
  
  file(GLOB_RECURSE func_tracker_src
      FuncTracker.cpp
  )
  
  set(TARGET func_tracker)
  add_library(${TARGET} STATIC ${func_tracker_src})
  
  add_definitions(-DLOG_TAG="func_tracker")
  target_include_directories(
      ${TARGET} PRIVATE
  )
  
  target_link_libraries(
      ${TARGET}
  )
  ```

  - FuncTracker.cpp

  ```cpp
  #include <stdio.h>
  #define DUMP(func, call) printf("%s: func = %p, called by = %p/n", __FUNCTION__, func, call)
  
  #ifdef __cplusplus
  extern "C" {
  #endif
  void __cyg_profile_func_enter(void* this_func, void* call_site)
  {
      DUMP(this_func, call_site);
  }
  void __cyg_profile_func_exit(void* this_func, void* call_site)
  {
      DUMP(this_func, call_site);
  }
  #ifdef __cplusplus
  }
  #endif
  
  ```

  

​	