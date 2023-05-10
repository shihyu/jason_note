# Install script for directory: /media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/install")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/modules/cmake_install.cmake")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/func_tracker/cmake_install.cmake")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/libcpptrader.a")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin" TYPE STATIC_LIBRARY FILES "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/libcpptrader.a")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-itch_handler" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-itch_handler")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-itch_handler"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-itch_handler")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin" TYPE EXECUTABLE FILES "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/cpptrader-example-itch_handler")
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-itch_handler" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-itch_handler")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-itch_handler")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-market_manager" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-market_manager")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-market_manager"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-market_manager")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin" TYPE EXECUTABLE FILES "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/cpptrader-example-market_manager")
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-market_manager" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-market_manager")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-market_manager")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-matching_engine" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-matching_engine")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-matching_engine"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-matching_engine")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin" TYPE EXECUTABLE FILES "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/cpptrader-example-matching_engine")
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-matching_engine" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-matching_engine")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-example-matching_engine")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-itch_handler" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-itch_handler")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-itch_handler"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-itch_handler")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin" TYPE EXECUTABLE FILES "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/cpptrader-performance-itch_handler")
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-itch_handler" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-itch_handler")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-itch_handler")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin" TYPE EXECUTABLE FILES "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/cpptrader-performance-market_manager")
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin" TYPE EXECUTABLE FILES "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/cpptrader-performance-market_manager_optimized")
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized_aggressive" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized_aggressive")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized_aggressive"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized_aggressive")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin" TYPE EXECUTABLE FILES "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/cpptrader-performance-market_manager_optimized_aggressive")
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized_aggressive" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized_aggressive")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-market_manager_optimized_aggressive")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-matching_engine" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-matching_engine")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-matching_engine"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-matching_engine")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin" TYPE EXECUTABLE FILES "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/cpptrader-performance-matching_engine")
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-matching_engine" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-matching_engine")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-performance-matching_engine")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-tests" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-tests")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-tests"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-tests")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin" TYPE EXECUTABLE FILES "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/cpptrader-tests")
  if(EXISTS "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-tests" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-tests")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/bin/cpptrader-tests")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
