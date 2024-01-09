CC = gcc
CFLAGS = -Wall -Wextra -Werror
LDFLAGS = -L. -lmylib
EXECUTABLE = a.out

all: libmylib.so $(EXECUTABLE)

libmylib.so: hello.o world.o
	$(CC) -shared $^ -o $@

$(EXECUTABLE): main.c libmylib.so
	$(CC) $(CFLAGS) $< $(LDFLAGS) -o $@

hello.o: hello.c
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

world.o: world.c
	$(CC) $(CFLAGS) -fPIC -c $< -o $@

run: all
	LD_LIBRARY_PATH=. ./$(EXECUTABLE)

.PHONY: clean

clean:
	rm -f libmylib.so $(EXECUTABLE) hello.o world.o

