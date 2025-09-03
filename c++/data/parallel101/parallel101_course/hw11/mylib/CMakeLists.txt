# 请改用自动批量查找所有 .cpp 和 .h 文件：
set(mylib_sources "mylib/mylib.cpp" "mylib/mylib.h")

# 使用 SHARED 在 Windows 上会遇到什么困难？请尝试修复!
add_library(mylib SHARED ${mylib_sources})
target_compile_definitions(mylib PRIVATE MYLIB_EXPORT)

# 这里应该用 PRIVATE 还是 PUBLIC？
target_include_directories(mylib PRIVATE .)
