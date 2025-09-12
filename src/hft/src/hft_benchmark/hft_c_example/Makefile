CC = gcc
CFLAGS = -O3 -march=native -mtune=native -Wall -Wextra -pthread -std=c11 -D_GNU_SOURCE
LDFLAGS = -lpthread -lm -lrt

# Performance optimizations
CFLAGS += -ffast-math -funroll-loops -flto
CFLAGS += -fomit-frame-pointer -finline-functions

# AVX2 support for SIMD benchmarks
CFLAGS += -mavx2

TARGETS = hft_trading hft_advanced_test compare_benchmark
OBJS = $(TARGETS:=.o)

all: $(TARGETS)

hft_trading: hft_trading.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

hft_advanced_test: hft_advanced_test.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

compare_benchmark: compare_benchmark.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

run: all
	./hft_trading
	./hft_advanced_test

compare: all
	cd .. && ./hft_c_example/compare_benchmark

perf: hft_trading
	sudo perf record -g ./hft_trading
	sudo perf report

clean:
	rm -f $(TARGETS) $(OBJS) perf.data perf.data.old

.PHONY: all run compare perf clean