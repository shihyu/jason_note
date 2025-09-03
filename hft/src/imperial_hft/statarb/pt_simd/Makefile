# Default target
all: build

# Build target
build: mybenchmark

mybenchmark: mybenchmark.cc
	g++ mybenchmark.cc -std=c++11 -isystem benchmark/include -Lbenchmark/build/src -lbenchmark -lpthread -mavx -o mybenchmark


# Clean target
clean:
	rm -f mybenchmark *.o
