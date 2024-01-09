CC = g++
CFLAGS = -Wall -Werror -fPIC
LDFLAGS = -Wl,-rpath=.
LIBS = -L. -lexample
EXECUTABLE = main

all: libexample.so $(EXECUTABLE)

libexample.so: example.o
	$(CC) -shared $(LDFLAGS) -o $@ $^

example.o: example.cpp
	$(CC) -c $(CFLAGS) $< -o $@

$(EXECUTABLE): main.o
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

main.o: main.cpp
	$(CC) -c $(CFLAGS) $< -o $@

run: all
	./$(EXECUTABLE)

clean:
	rm -f *.o *.so $(EXECUTABLE)

