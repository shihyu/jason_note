#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <math.h>
#include <unistd.h>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <stdatomic.h>
#include <immintrin.h>

#define CACHE_LINE_SIZE 64
#define PAGE_SIZE 4096
#define WARMUP_ITERATIONS 100000
#define TEST_ITERATIONS 10000000

// Aligned allocation macro
#define ALIGNED_ALLOC(size, align) aligned_alloc(align, size)

// Memory barrier macros
#define MEMORY_BARRIER() __sync_synchronize()
#define COMPILER_BARRIER() __asm__ __volatile__("" ::: "memory")

// Performance counter structure
typedef struct {
    uint64_t min_latency;
    uint64_t max_latency;
    uint64_t total_latency;
    uint64_t count;
    double mean;
    double stddev;
    uint64_t* samples;
    size_t sample_count;
} PerfStats;

// Test configuration
typedef struct {
    size_t iterations;
    size_t warmup_iterations;
    int cpu_affinity;
    bool use_huge_pages;
    bool prefetch_enabled;
} TestConfig;

// Initialize performance stats
PerfStats* perf_stats_init(size_t max_samples) {
    PerfStats* stats = (PerfStats*)calloc(1, sizeof(PerfStats));
    if (!stats) return NULL;
    
    stats->min_latency = UINT64_MAX;
    stats->max_latency = 0;
    stats->total_latency = 0;
    stats->count = 0;
    stats->samples = (uint64_t*)malloc(max_samples * sizeof(uint64_t));
    stats->sample_count = 0;
    
    return stats;
}

// Free performance stats
void perf_stats_free(PerfStats* stats) {
    if (stats) {
        free(stats->samples);
        free(stats);
    }
}

// Add sample to stats
static inline void perf_stats_add(PerfStats* stats, uint64_t latency) {
    if (latency < stats->min_latency) stats->min_latency = latency;
    if (latency > stats->max_latency) stats->max_latency = latency;
    stats->total_latency += latency;
    stats->count++;
    
    if (stats->samples && stats->sample_count < TEST_ITERATIONS) {
        stats->samples[stats->sample_count++] = latency;
    }
}

// Calculate statistics
void perf_stats_calculate(PerfStats* stats) {
    if (stats->count == 0) return;
    
    stats->mean = (double)stats->total_latency / stats->count;
    
    // Calculate standard deviation
    double sum_sq = 0;
    for (size_t i = 0; i < stats->sample_count; i++) {
        double diff = stats->samples[i] - stats->mean;
        sum_sq += diff * diff;
    }
    stats->stddev = sqrt(sum_sq / stats->sample_count);
}

// Compare function for qsort
int compare_uint64(const void* a, const void* b) {
    uint64_t val_a = *(const uint64_t*)a;
    uint64_t val_b = *(const uint64_t*)b;
    return (val_a > val_b) - (val_a < val_b);
}

// Calculate percentiles
void calculate_percentiles(PerfStats* stats, double* p50, double* p95, double* p99, double* p999) {
    if (stats->sample_count == 0) return;
    
    qsort(stats->samples, stats->sample_count, sizeof(uint64_t), compare_uint64);
    
    size_t idx_50 = (size_t)(stats->sample_count * 0.50);
    size_t idx_95 = (size_t)(stats->sample_count * 0.95);
    size_t idx_99 = (size_t)(stats->sample_count * 0.99);
    size_t idx_999 = (size_t)(stats->sample_count * 0.999);
    
    *p50 = stats->samples[idx_50];
    *p95 = stats->samples[idx_95];
    *p99 = stats->samples[idx_99];
    *p999 = stats->samples[idx_999];
}

// High-resolution timestamp using RDTSC
static inline uint64_t rdtsc() {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

// Get timestamp in nanoseconds
static inline uint64_t get_ns_timestamp() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}

// CPU affinity setup
void set_cpu_affinity(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    
    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
        fprintf(stderr, "Warning: Failed to set CPU affinity to core %d\n", cpu_id);
    } else {
        printf("Thread pinned to CPU core %d\n", cpu_id);
    }
}

// Set process priority
void set_realtime_priority() {
    struct sched_param param;
    param.sched_priority = sched_get_priority_max(SCHED_FIFO);
    
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        fprintf(stderr, "Warning: Failed to set real-time priority (need root)\n");
    } else {
        printf("Real-time priority set\n");
    }
}

// Memory allocation benchmark
void benchmark_memory_allocation(TestConfig* config) {
    printf("\n=== Memory Allocation Benchmark ===\n");
    
    PerfStats* stats = perf_stats_init(config->iterations);
    size_t alloc_size = 4096;
    
    // Warmup
    for (size_t i = 0; i < config->warmup_iterations; i++) {
        void* ptr = malloc(alloc_size);
        memset(ptr, 0, alloc_size);
        free(ptr);
    }
    
    // Actual benchmark
    for (size_t i = 0; i < config->iterations; i++) {
        uint64_t start = get_ns_timestamp();
        
        void* ptr = ALIGNED_ALLOC(alloc_size, CACHE_LINE_SIZE);
        memset(ptr, 0, alloc_size);
        
        uint64_t end = get_ns_timestamp();
        perf_stats_add(stats, end - start);
        
        free(ptr);
    }
    
    perf_stats_calculate(stats);
    
    double p50, p95, p99, p999;
    calculate_percentiles(stats, &p50, &p95, &p99, &p999);
    
    printf("Results (nanoseconds):\n");
    printf("  Min: %lu ns\n", stats->min_latency);
    printf("  Max: %lu ns\n", stats->max_latency);
    printf("  Mean: %.2f ns\n", stats->mean);
    printf("  StdDev: %.2f ns\n", stats->stddev);
    printf("  P50: %.0f ns\n", p50);
    printf("  P95: %.0f ns\n", p95);
    printf("  P99: %.0f ns\n", p99);
    printf("  P99.9: %.0f ns\n", p999);
    
    perf_stats_free(stats);
}

// Cache line benchmark
void benchmark_cache_lines(TestConfig* config) {
    printf("\n=== Cache Line Access Benchmark ===\n");
    
    PerfStats* sequential_stats = perf_stats_init(config->iterations);
    PerfStats* random_stats = perf_stats_init(config->iterations);
    
    const size_t array_size = 1024 * 1024;
    uint64_t* array = (uint64_t*)ALIGNED_ALLOC(array_size * sizeof(uint64_t), PAGE_SIZE);
    
    // Initialize array
    for (size_t i = 0; i < array_size; i++) {
        array[i] = i;
    }
    
    // Sequential access
    printf("\nSequential access:\n");
    for (size_t iter = 0; iter < config->iterations / 1000; iter++) {
        uint64_t start = rdtsc();
        uint64_t sum = 0;
        
        for (size_t i = 0; i < 1000; i++) {
            sum += array[i % array_size];
        }
        
        uint64_t end = rdtsc();
        perf_stats_add(sequential_stats, end - start);
        
        COMPILER_BARRIER();
        volatile uint64_t dummy = sum;
        (void)dummy;
    }
    
    // Random access
    printf("Random access:\n");
    for (size_t iter = 0; iter < config->iterations / 1000; iter++) {
        uint64_t start = rdtsc();
        uint64_t sum = 0;
        
        for (size_t i = 0; i < 1000; i++) {
            size_t idx = (rand() % array_size);
            sum += array[idx];
        }
        
        uint64_t end = rdtsc();
        perf_stats_add(random_stats, end - start);
        
        COMPILER_BARRIER();
        volatile uint64_t dummy = sum;
        (void)dummy;
    }
    
    perf_stats_calculate(sequential_stats);
    perf_stats_calculate(random_stats);
    
    printf("\nSequential - cycles per 1000 accesses:\n");
    printf("  Min: %lu\n", sequential_stats->min_latency);
    printf("  Mean: %.2f\n", sequential_stats->mean);
    
    printf("\nRandom - cycles per 1000 accesses:\n");
    printf("  Min: %lu\n", random_stats->min_latency);
    printf("  Mean: %.2f\n", random_stats->mean);
    
    printf("\nRandom/Sequential ratio: %.2fx slower\n", 
           random_stats->mean / sequential_stats->mean);
    
    free(array);
    perf_stats_free(sequential_stats);
    perf_stats_free(random_stats);
}

// Atomic operations benchmark
void benchmark_atomics(TestConfig* config) {
    printf("\n=== Atomic Operations Benchmark ===\n");
    
    PerfStats* cas_stats = perf_stats_init(config->iterations);
    PerfStats* add_stats = perf_stats_init(config->iterations);
    
    atomic_uint_fast64_t atomic_val = ATOMIC_VAR_INIT(0);
    
    // Compare-and-swap benchmark
    printf("\nCompare-and-swap:\n");
    for (size_t i = 0; i < config->iterations; i++) {
        uint64_t expected = atomic_load(&atomic_val);
        uint64_t desired = expected + 1;
        
        uint64_t start = rdtsc();
        atomic_compare_exchange_strong(&atomic_val, &expected, desired);
        uint64_t end = rdtsc();
        
        perf_stats_add(cas_stats, end - start);
    }
    
    // Atomic add benchmark
    printf("Atomic add:\n");
    atomic_store(&atomic_val, 0);
    
    for (size_t i = 0; i < config->iterations; i++) {
        uint64_t start = rdtsc();
        atomic_fetch_add(&atomic_val, 1);
        uint64_t end = rdtsc();
        
        perf_stats_add(add_stats, end - start);
    }
    
    perf_stats_calculate(cas_stats);
    perf_stats_calculate(add_stats);
    
    printf("\nCompare-and-swap (cycles):\n");
    printf("  Min: %lu\n", cas_stats->min_latency);
    printf("  Mean: %.2f\n", cas_stats->mean);
    
    printf("\nAtomic add (cycles):\n");
    printf("  Min: %lu\n", add_stats->min_latency);
    printf("  Mean: %.2f\n", add_stats->mean);
    
    perf_stats_free(cas_stats);
    perf_stats_free(add_stats);
}

// Memory barrier benchmark
void benchmark_memory_barriers(TestConfig* config) {
    printf("\n=== Memory Barrier Benchmark ===\n");
    
    PerfStats* barrier_stats = perf_stats_init(config->iterations);
    PerfStats* no_barrier_stats = perf_stats_init(config->iterations);
    
    volatile uint64_t shared_var = 0;
    
    // With memory barrier
    printf("\nWith memory barrier:\n");
    for (size_t i = 0; i < config->iterations; i++) {
        uint64_t start = rdtsc();
        shared_var = i;
        MEMORY_BARRIER();
        volatile uint64_t read = shared_var;
        uint64_t end = rdtsc();
        
        perf_stats_add(barrier_stats, end - start);
        (void)read;
    }
    
    // Without memory barrier
    printf("Without memory barrier:\n");
    for (size_t i = 0; i < config->iterations; i++) {
        uint64_t start = rdtsc();
        shared_var = i;
        volatile uint64_t read = shared_var;
        uint64_t end = rdtsc();
        
        perf_stats_add(no_barrier_stats, end - start);
        (void)read;
    }
    
    perf_stats_calculate(barrier_stats);
    perf_stats_calculate(no_barrier_stats);
    
    printf("\nWith barrier (cycles):\n");
    printf("  Min: %lu\n", barrier_stats->min_latency);
    printf("  Mean: %.2f\n", barrier_stats->mean);
    
    printf("\nWithout barrier (cycles):\n");
    printf("  Min: %lu\n", no_barrier_stats->min_latency);
    printf("  Mean: %.2f\n", no_barrier_stats->mean);
    
    printf("\nBarrier overhead: %.2f cycles\n", 
           barrier_stats->mean - no_barrier_stats->mean);
    
    perf_stats_free(barrier_stats);
    perf_stats_free(no_barrier_stats);
}

// SIMD operations benchmark
void benchmark_simd(TestConfig* config) {
    printf("\n=== SIMD Operations Benchmark ===\n");
    
    PerfStats* scalar_stats = perf_stats_init(config->iterations / 1000);
    PerfStats* simd_stats = perf_stats_init(config->iterations / 1000);
    
    const size_t vector_size = 1024;
    float* a = (float*)ALIGNED_ALLOC(vector_size * sizeof(float), 32);
    float* b = (float*)ALIGNED_ALLOC(vector_size * sizeof(float), 32);
    float* c = (float*)ALIGNED_ALLOC(vector_size * sizeof(float), 32);
    
    // Initialize vectors
    for (size_t i = 0; i < vector_size; i++) {
        a[i] = (float)i;
        b[i] = (float)(i * 2);
    }
    
    // Scalar addition
    printf("\nScalar addition:\n");
    for (size_t iter = 0; iter < config->iterations / 1000; iter++) {
        uint64_t start = rdtsc();
        
        for (size_t i = 0; i < vector_size; i++) {
            c[i] = a[i] + b[i];
        }
        
        uint64_t end = rdtsc();
        perf_stats_add(scalar_stats, end - start);
    }
    
    // SIMD addition (AVX2)
    printf("SIMD (AVX2) addition:\n");
    for (size_t iter = 0; iter < config->iterations / 1000; iter++) {
        uint64_t start = rdtsc();
        
        for (size_t i = 0; i < vector_size; i += 8) {
            __m256 va = _mm256_load_ps(&a[i]);
            __m256 vb = _mm256_load_ps(&b[i]);
            __m256 vc = _mm256_add_ps(va, vb);
            _mm256_store_ps(&c[i], vc);
        }
        
        uint64_t end = rdtsc();
        perf_stats_add(simd_stats, end - start);
    }
    
    perf_stats_calculate(scalar_stats);
    perf_stats_calculate(simd_stats);
    
    printf("\nScalar (cycles per 1024 elements):\n");
    printf("  Min: %lu\n", scalar_stats->min_latency);
    printf("  Mean: %.2f\n", scalar_stats->mean);
    
    printf("\nSIMD (cycles per 1024 elements):\n");
    printf("  Min: %lu\n", simd_stats->min_latency);
    printf("  Mean: %.2f\n", simd_stats->mean);
    
    printf("\nSpeedup: %.2fx\n", scalar_stats->mean / simd_stats->mean);
    
    free(a);
    free(b);
    free(c);
    perf_stats_free(scalar_stats);
    perf_stats_free(simd_stats);
}

// System information
void print_system_info() {
    printf("=== System Information ===\n");
    
    // CPU info
    FILE* cpuinfo = fopen("/proc/cpuinfo", "r");
    if (cpuinfo) {
        char line[256];
        while (fgets(line, sizeof(line), cpuinfo)) {
            if (strstr(line, "model name")) {
                printf("CPU: %s", strchr(line, ':') + 2);
                break;
            }
        }
        fclose(cpuinfo);
    }
    
    // Number of CPUs
    long num_cpus = sysconf(_SC_NPROCESSORS_ONLN);
    printf("CPU cores: %ld\n", num_cpus);
    
    // Cache sizes
    long l1_cache = sysconf(_SC_LEVEL1_DCACHE_SIZE);
    long l2_cache = sysconf(_SC_LEVEL2_CACHE_SIZE);
    long l3_cache = sysconf(_SC_LEVEL3_CACHE_SIZE);
    
    if (l1_cache > 0) printf("L1 cache: %ld KB\n", l1_cache / 1024);
    if (l2_cache > 0) printf("L2 cache: %ld KB\n", l2_cache / 1024);
    if (l3_cache > 0) printf("L3 cache: %ld KB\n", l3_cache / 1024);
    
    // Memory page size
    long page_size = sysconf(_SC_PAGESIZE);
    printf("Page size: %ld bytes\n", page_size);
    
    printf("\n");
}

int main(int argc, char* argv[]) {
    printf("=== C HFT Advanced Performance Test ===\n\n");
    
    // Print system information
    print_system_info();
    
    // Configure test
    TestConfig config = {
        .iterations = TEST_ITERATIONS,
        .warmup_iterations = WARMUP_ITERATIONS,
        .cpu_affinity = 0,
        .use_huge_pages = false,
        .prefetch_enabled = true
    };
    
    // Parse command line arguments
    if (argc > 1) {
        config.cpu_affinity = atoi(argv[1]);
    }
    
    // Set CPU affinity
    set_cpu_affinity(config.cpu_affinity);
    
    // Try to set real-time priority
    set_realtime_priority();
    
    // Lock memory
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        fprintf(stderr, "Warning: Failed to lock memory\n");
    }
    
    // Run benchmarks
    benchmark_memory_allocation(&config);
    benchmark_cache_lines(&config);
    benchmark_atomics(&config);
    benchmark_memory_barriers(&config);
    benchmark_simd(&config);
    
    printf("\n=== All benchmarks completed ===\n");
    
    munlockall();
    return 0;
}