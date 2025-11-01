CC = gcc
CFLAGS = -g -Wall
INCLUDE = -I../include -I../ggml/include
LDFLAGS = -L../build/bin -lllama -lggml -lggml-base -lggml-cpu
RPATH = -Wl,-rpath,../build/bin

all: test_4_so

test_4_so: test_4_so.c
	$(CC) $(CFLAGS) -o test_4_so test_4_so.c $(INCLUDE) $(LDFLAGS) $(RPATH)

clean:
	rm -f test_4_so

test: test_4_so
	./test_final.sh

.PHONY: all clean test
