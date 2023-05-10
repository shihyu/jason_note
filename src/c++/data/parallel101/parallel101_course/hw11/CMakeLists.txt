# 为什么不指定 cmake_minimum_required 会导致下面在 project 处出错？
#cmake_minimum_required(VERSION 3.10)

project(hellocmake VERSION 3.1.4 LANGUAGES CXX)

# 如何让构建类型默认为 Release？
#set(CMAKE_BUILD_TYPE Release)

# 这样设置 C++14 的方式对吗？请改正
set(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS} "-std=c++14")

# （可选）使用 ccache 加速编译
find_program(CCACHE_PROGRAM ccache)

# legacy/CMakeLists.txt 和 mylib/CMakeLists.txt 里还有问题哦！
add_subdirectory(legacy)
add_subdirectory(mylib)

# 这样需要一个个写出所有文件很麻烦，请改成自动批量添加源文件
set(main_sources "src/main.cpp" "src/other.cpp" "src/dummy.cpp" "src/veryusefulfile.cpp")
add_executable(main ${main_sources})

# 请改为项目的正确版本（用变量来获取）
target_compile_definitions(main PRIVATE HELLOCMAKE_VERSION="233.33.33")

# （可选）添加 run 作为伪目标方便命令行调用
