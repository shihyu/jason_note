# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/home/shihyu/github/jason_note/src/hft/src/imperial_hft/design_patterns/compile-time dispatch/benchmark/build/third_party/googletest/src"
  "/home/shihyu/github/jason_note/src/hft/src/imperial_hft/design_patterns/compile-time dispatch/benchmark/build/third_party/googletest/build"
  "/home/shihyu/github/jason_note/src/hft/src/imperial_hft/design_patterns/compile-time dispatch/benchmark/build/third_party/googletest"
  "/home/shihyu/github/jason_note/src/hft/src/imperial_hft/design_patterns/compile-time dispatch/benchmark/build/third_party/googletest/tmp"
  "/home/shihyu/github/jason_note/src/hft/src/imperial_hft/design_patterns/compile-time dispatch/benchmark/build/third_party/googletest/stamp"
  "/home/shihyu/github/jason_note/src/hft/src/imperial_hft/design_patterns/compile-time dispatch/benchmark/build/third_party/googletest/download"
  "/home/shihyu/github/jason_note/src/hft/src/imperial_hft/design_patterns/compile-time dispatch/benchmark/build/third_party/googletest/stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/home/shihyu/github/jason_note/src/hft/src/imperial_hft/design_patterns/compile-time dispatch/benchmark/build/third_party/googletest/stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/home/shihyu/github/jason_note/src/hft/src/imperial_hft/design_patterns/compile-time dispatch/benchmark/build/third_party/googletest/stamp${cfgdir}") # cfgdir has leading slash
endif()
