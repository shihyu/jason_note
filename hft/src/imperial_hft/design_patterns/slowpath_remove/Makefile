# Default target
all: build

# Build target
build: mybenchmark

mybenchmark: mybenchmark.cc
	g++ mybenchmark.cc -O2 -std=c++20 -isystem benchmark/include -Lbenchmark/build/src -lbenchmark -lpthread -o mybenchmark

# Clean target
clean:
	rm -f mybenchmark *.o
