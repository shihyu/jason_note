cmake_minimum_required(VERSION 3.10)
project(cpp_async_client)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(CURL REQUIRED)
find_package(Threads REQUIRED)

# JSON library (nlohmann/json)
include(FetchContent)
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.2
)
FetchContent_MakeAvailable(nlohmann_json)

# Create executable
add_executable(cpp_client cpp_client.cpp)

# Link libraries
target_link_libraries(cpp_client 
    ${CURL_LIBRARIES}
    Threads::Threads
    nlohmann_json::nlohmann_json
)

# Include directories
target_include_directories(cpp_client PRIVATE ${CURL_INCLUDE_DIRS})

# Compiler flags for optimization
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_options(cpp_client PRIVATE -O3 -march=native)
endif()