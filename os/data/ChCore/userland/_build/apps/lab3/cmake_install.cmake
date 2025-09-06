# Install script for directory: /chos/userland/apps/lab3

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
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/badinst1.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/badinst1.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/badinst1.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/badinst1.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab3/badinst1.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/badinst1.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/badinst1.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/badinst1.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/badinst2.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/badinst2.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/badinst2.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/badinst2.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab3/badinst2.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/badinst2.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/badinst2.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/badinst2.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/fault.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/fault.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/fault.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/fault.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab3/fault.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/fault.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/fault.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/fault.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/hello.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/hello.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/hello.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/hello.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab3/hello.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/hello.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/hello.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/hello.bin")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/putget.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/putget.bin")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/chos/userland/_install/putget.bin"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/chos/userland/_install/putget.bin")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
file(INSTALL DESTINATION "/chos/userland/_install" TYPE EXECUTABLE FILES "/chos/userland/_build/apps/lab3/putget.bin")
  if(EXISTS "$ENV{DESTDIR}/chos/userland/_install/putget.bin" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/chos/userland/_install/putget.bin")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "aarch64-linux-gnu-strip" "$ENV{DESTDIR}/chos/userland/_install/putget.bin")
    endif()
  endif()
endif()

