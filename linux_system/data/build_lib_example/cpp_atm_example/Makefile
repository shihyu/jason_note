CC = g++
CFLAGS = -Wall -Werror -fPIC
LDFLAGS = -Wl,-rpath=.
LIBS = -L. -lATM
EXECUTABLE = main

all: libATM.so $(EXECUTABLE)

libATM.so: ATM.o
	$(CC) -shared $(LDFLAGS) -o $@ $^

ATM.o: ATM.cpp ATM.h
	$(CC) -c $(CFLAGS) $< -o $@

$(EXECUTABLE): main.o 
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)

main.o: main.cpp ATM.h
	$(CC) -c $(CFLAGS) $< -o $@

clean:
	rm -f *.o *.so $(EXECUTABLE)

