CXX = g++
CXXFLAGS = -std=c++17 -O3 -march=native -mtune=native -Wall -Wextra
CXXFLAGS += -fno-exceptions -fno-rtti -flto -pthread
LDFLAGS = -lpthread -lrt

TARGETS = hft_trading hft_advanced_test

all: $(TARGETS)

hft_trading: hft_trading.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

hft_advanced_test: hft_advanced_test.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

debug: CXXFLAGS = -std=c++17 -g -O0 -Wall -Wextra -pthread
debug: $(TARGETS)

clean:
	rm -f $(TARGETS) test_output.txt

run: hft_trading
	./hft_trading 30

test: hft_advanced_test
	./hft_advanced_test 5 0

.PHONY: all clean run debug test
