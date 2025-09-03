# CMake generated Testfile for 
# Source directory: /media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify
# Build directory: /media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/temp
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test([=[cpptrader-tests]=] "cpptrader-tests" "--durations" "yes" "--order" "lex")
set_tests_properties([=[cpptrader-tests]=] PROPERTIES  _BACKTRACE_TRIPLES "/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/CMakeLists.txt;98;add_test;/media/shihyu/ssd1/github/jason_note/src/c++/data/CppTrader/CppTrader_modify/CMakeLists.txt;0;")
subdirs("modules")
subdirs("func_tracker")
