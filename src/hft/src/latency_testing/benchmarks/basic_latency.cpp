#include <iostream>
#include <vector>
#include <map>
#include <unordered_map>
#include <cstring>
#include <memory>
#include "../utils/timer.hpp"

void test_map_vs_unordered_map() {
    const int NUM_OPERATIONS = 100000;
    const int NUM_WARMUP = 1000;
    
    std::map<int, int> ordered_map;
    std::unordered_map<int, int> hash_map;
    LatencyStats ordered_stats, hash_stats;

    // Warmup
    for (int i = 0; i < NUM_WARMUP; ++i) {
        ordered_map[i] = i * 2;
        hash_map[i] = i * 2;
    }

    // Test std::map insertion
    for (int i = NUM_WARMUP; i < NUM_OPERATIONS; ++i) {
        auto t1 = Timer::now();
        ordered_map[i] = i * 2;
        auto t2 = Timer::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        ordered_stats.add_sample(static_cast<double>(duration));
    }

    // Test std::unordered_map insertion
    for (int i = NUM_WARMUP; i < NUM_OPERATIONS; ++i) {
        auto t1 = Timer::now();
        hash_map[i + NUM_OPERATIONS] = i * 2;
        auto t2 = Timer::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        hash_stats.add_sample(static_cast<double>(duration));
    }

    std::cout << "\n========== Map vs Unordered Map Insertion ==========" << std::endl;
    ordered_stats.print_summary("std::map");
    hash_stats.print_summary("std::unordered_map");
}

void test_memcpy_vs_move() {
    const int NUM_OPERATIONS = 100000;
    const size_t DATA_SIZE = 4096;  // 4KB
    
    LatencyStats memcpy_stats, move_stats;
    
    std::vector<char> src(DATA_SIZE, 'A');
    std::vector<char> dst(DATA_SIZE);

    // Test memcpy
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        auto t1 = Timer::now();
        std::memcpy(dst.data(), src.data(), DATA_SIZE);
        auto t2 = Timer::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        memcpy_stats.add_sample(static_cast<double>(duration));
    }

    // Test std::move with vector
    std::vector<std::vector<char>> vec_src(NUM_OPERATIONS);
    std::vector<std::vector<char>> vec_dst(NUM_OPERATIONS);
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        vec_src[i] = std::vector<char>(DATA_SIZE, 'B');
    }
    
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        auto t1 = Timer::now();
        vec_dst[i] = std::move(vec_src[i]);
        auto t2 = Timer::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        move_stats.add_sample(static_cast<double>(duration));
    }

    std::cout << "\n========== Memcpy vs Move (4KB data) ==========" << std::endl;
    memcpy_stats.print_summary("memcpy");
    move_stats.print_summary("std::move");
}

void test_dynamic_allocation() {
    const int NUM_OPERATIONS = 100000;
    const size_t ALLOC_SIZE = 1024;  // 1KB
    
    LatencyStats new_delete_stats, unique_ptr_stats, malloc_free_stats;

    // Test new/delete
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        auto t1 = Timer::now();
        char* ptr = new char[ALLOC_SIZE];
        delete[] ptr;
        auto t2 = Timer::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        new_delete_stats.add_sample(static_cast<double>(duration));
    }

    // Test unique_ptr
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        auto t1 = Timer::now();
        auto ptr = std::make_unique<char[]>(ALLOC_SIZE);
        ptr.reset();
        auto t2 = Timer::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        unique_ptr_stats.add_sample(static_cast<double>(duration));
    }

    // Test malloc/free
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        auto t1 = Timer::now();
        void* ptr = std::malloc(ALLOC_SIZE);
        std::free(ptr);
        auto t2 = Timer::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        malloc_free_stats.add_sample(static_cast<double>(duration));
    }

    std::cout << "\n========== Dynamic Allocation (1KB) ==========" << std::endl;
    new_delete_stats.print_summary("new/delete");
    unique_ptr_stats.print_summary("unique_ptr");
    malloc_free_stats.print_summary("malloc/free");
}

void test_tsc_vs_chrono() {
    const int NUM_OPERATIONS = 100000;
    const double CPU_GHZ = 3.0;  // Adjust based on your CPU
    
    LatencyStats chrono_stats, tsc_stats, rdtscp_stats;

    // Test chrono overhead
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        auto t1 = Timer::now();
        auto t2 = Timer::now();
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        chrono_stats.add_sample(static_cast<double>(duration));
    }

    // Test rdtsc overhead
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        uint64_t t1 = Timer::rdtsc();
        volatile uint64_t t2 = Timer::rdtsc();
        double duration = Timer::tsc_to_ns(t2 - t1, CPU_GHZ);
        tsc_stats.add_sample(duration);
    }

    // Test rdtscp overhead
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        uint64_t t1 = Timer::rdtscp();
        volatile uint64_t t2 = Timer::rdtscp();
        double duration = Timer::tsc_to_ns(t2 - t1, CPU_GHZ);
        rdtscp_stats.add_sample(duration);
    }

    std::cout << "\n========== Timer Overhead ==========" << std::endl;
    chrono_stats.print_summary("chrono::high_resolution_clock");
    tsc_stats.print_summary("rdtsc");
    rdtscp_stats.print_summary("rdtscp");
}

int main(int argc, char* argv[]) {
    std::cout << "==================================================" << std::endl;
    std::cout << "          Basic Latency Benchmarks               " << std::endl;
    std::cout << "==================================================" << std::endl;

    if (argc > 1) {
        std::string test = argv[1];
        if (test == "map") {
            test_map_vs_unordered_map();
        } else if (test == "copy") {
            test_memcpy_vs_move();
        } else if (test == "alloc") {
            test_dynamic_allocation();
        } else if (test == "timer") {
            test_tsc_vs_chrono();
        } else {
            std::cerr << "Unknown test: " << test << std::endl;
            std::cerr << "Available tests: map, copy, alloc, timer" << std::endl;
            return 1;
        }
    } else {
        // Run all tests
        test_map_vs_unordered_map();
        test_memcpy_vs_move();
        test_dynamic_allocation();
        test_tsc_vs_chrono();
    }

    return 0;
}