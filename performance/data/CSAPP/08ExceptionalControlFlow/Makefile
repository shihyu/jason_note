# https://github.com/tch0/MyConfigurations/blob/master/MakefileTemplate/CppTemplate1.mk

# Makefile template 1:
# For C++ sigle files, every C++ file will get a executable.

# make debug=yes to compile with -g
# make system=windows for windows system

.PHONY : allexe all
.PHONY .IGNORE : clean

# for C files
CC = gcc
CCFLAGS += -Wall -Wextra -pedantic-errors -Wshadow
CCFLAGS += -Wno-unused-parameter

# for C++ files
# add your own include path/library path/link library to CXXFLAGS
CXX = g++
CXXFLAGS += -std=c++20
CXXFLAGS += -Wall -Wextra -pedantic-errors -Wshadow
# CXXFLAGS += -Wfatal-errors
CXXFLAGS += -Wno-unused-parameter
RM = rm

# debug
ifeq ($(debug), yes)
CXXFLAGS += -g
CXXFLAGS += -Og
CCFLAGS  += -g
CCFLAGS  += -Og
else
CXXFLAGS += -Og
CXXFLAGS += -DNDEBUG
CCFLAGS  += -O3
CCFLAGS  += -DNDEBUG
endif

# filenames and targets
all_source_files := $(wildcard *.cpp)
all_source_files += $(wildcard *.c)
all_targets             := $(basename $(all_source_files))
all_preprocessed_files  := $(addsuffix .i,$(all_targets))
all_asm_files           := $(addsuffix .s,$(all_targets))
all_object_files        := $(addsuffix .o,$(all_targets))

# all targets
allexe : $(all_targets)
all : $(all_targets) $(all_preprocessed_files) $(all_asm_files) $(all_object_files)

# compile
% : %.cpp
	-$(CXX) $^ -o $@ $(CXXFLAGS)
% : %.c
	-$(CC) $^ -o $@ $(CCFLAGS)

# preprocess
%.i : %.cpp
	-$(CXX) -E $^ -o $@ $(CXXFLAGS)
%.i : %.c
	-$(CC) -E $^ -o $@ $(CCFLAGS)

# compile but do not assemble
%.s : %.cpp
	-$(CXX) -S $^ -o $@ $(CXXFLAGS)
%.s : %.c
	-$(CC) -S $^ -o $@ $(CCFLAGS)

# assemble to target files
%.o : %.cpp
	-$(CXX) -c $^ -o $@ $(CXXFLAGS)
%.o : %.c
	-$(CC) -c $^ -o $@ $(CCFLAGS)

# system: affect how to clean and executable file name
# value: windows/unix
system = unix
ifeq ($(system), windows)
all_targets := $(addsuffix .exe, $(all_targets))
RM := del
endif

# clean
clean :
	-$(RM) $(all_targets) $(all_preprocessed_files) $(all_asm_files) $(all_object_files)
