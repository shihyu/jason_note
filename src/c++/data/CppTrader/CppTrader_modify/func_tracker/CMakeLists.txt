cmake_minimum_required(VERSION 3.20)

set(CMAKE_CXX_FLAGS "-O0 -ggdb -Wno-unused-result")

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
