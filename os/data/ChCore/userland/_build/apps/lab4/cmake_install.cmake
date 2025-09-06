# Install script for directory: /chos/userland/apps/lab4

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/chos/userland/_install")
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
  set(CMAKE_CROSSCOMPILING "TRUE")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/user.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/user.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/user.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/user.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab4/user.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/user.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/user.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/user.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/ipc_client.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/ipc_client.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/ipc_client.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/ipc_client.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab4/ipc_client.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/ipc_client.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/ipc_client.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/ipc_client.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/test_mutex.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/test_mutex.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/test_mutex.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/test_mutex.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab4/test_mutex.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/test_mutex.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/test_mutex.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/test_mutex.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/test_sem.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/test_sem.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/test_sem.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/test_sem.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab4/test_sem.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/test_sem.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/test_sem.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/test_sem.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/prodcons.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/prodcons.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/prodcons.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/prodcons.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab4/prodcons.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/prodcons.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/prodcons.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/prodcons.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/yield_single.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/yield_single.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/yield_single.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/yield_single.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab4/yield_single.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/yield_single.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/yield_single.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/yield_single.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/yield_aff.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/yield_aff.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/yield_aff.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/yield_aff.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab4/yield_aff.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/yield_aff.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/yield_aff.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/yield_aff.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/yield_multi_aff.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/yield_multi_aff.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/yield_multi_aff.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/yield_multi_aff.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab4/yield_multi_aff.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/yield_multi_aff.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/yield_multi_aff.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/yield_multi_aff.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/yield_multi.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/yield_multi.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/yield_multi.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/yield_multi.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab4/yield_multi.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/yield_multi.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/yield_multi.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/yield_multi.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/yield_spin.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/yield_spin.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/yield_spin.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/yield_spin.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab4/yield_spin.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/yield_spin.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/yield_spin.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/yield_spin.bin")
    endif()
  endif()
endif()

