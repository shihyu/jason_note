#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <math.h>

typedef struct {
    double user_time;
    double sys_time;
    double real_time;
    long max_rss_kb;
    double orders_per_sec;
    double avg_latency_us;
} BenchmarkResult;

// Run command and capture output
int run_command_with_stats(const char* cmd, BenchmarkResult* result) {
    struct timeval start, end;
    struct rusage usage_before, usage_after;
    
    getrusage(RUSAGE_CHILDREN, &usage_before);
    gettimeofday(&start, NULL);
    
    FILE* pipe = popen(cmd, "r");
    if (!pipe) {
        fprintf(stderr, "Failed to run command: %s\n", cmd);
        return -1;
    }
    
    char buffer[256];
    char* output = (char*)malloc(65536);  // Increase buffer size
    if (!output) {
        pclose(pipe);
        return -1;
    }
    output[0] = '\0';
    size_t output_len = 0;
    size_t output_size = 65536;
    while (fgets(buffer, sizeof(buffer), pipe)) {
        size_t buf_len = strlen(buffer);
        if (output_len + buf_len >= output_size - 1) {
            // Just truncate if too much output
            break;
        }
        strcpy(output + output_len, buffer);
        output_len += buf_len;
        printf("%s", buffer);
    }
    
    int status = pclose(pipe);
    
    gettimeofday(&end, NULL);
    getrusage(RUSAGE_CHILDREN, &usage_after);
    
    // Calculate times
    result->real_time = (end.tv_sec - start.tv_sec) + 
                       (end.tv_usec - start.tv_usec) / 1000000.0;
    
    result->user_time = (usage_after.ru_utime.tv_sec - usage_before.ru_utime.tv_sec) +
                       (usage_after.ru_utime.tv_usec - usage_before.ru_utime.tv_usec) / 1000000.0;
    
    result->sys_time = (usage_after.ru_stime.tv_sec - usage_before.ru_stime.tv_sec) +
                      (usage_after.ru_stime.tv_usec - usage_before.ru_stime.tv_usec) / 1000000.0;
    
    result->max_rss_kb = usage_after.ru_maxrss;
    
    // Parse output for metrics
    char* line = strtok(output, "\n");
    while (line) {
        if (strstr(line, "Orders per second:")) {
            sscanf(line, "Orders per second: %lf", &result->orders_per_sec);
        } else if (strstr(line, "Average latency:")) {
            double latency_ns;
            sscanf(line, "Average latency: %lf ns", &latency_ns);
            result->avg_latency_us = latency_ns / 1000.0;
        }
        line = strtok(NULL, "\n");
    }
    
    free(output);
    return status;
}

void print_comparison_table(const char* test_name, 
                          BenchmarkResult* c_result, 
                          BenchmarkResult* cpp_result) {
    printf("\n┌─────────────────────────────────────────────────────────────┐\n");
    printf("│ %-59s │\n", test_name);
    printf("├─────────────────────┬───────────────┬──────────────────────┤\n");
    printf("│ Metric              │ C             │ C++                  │\n");
    printf("├─────────────────────┼───────────────┼──────────────────────┤\n");
    
    // Performance metrics
    if (c_result->orders_per_sec > 0 && cpp_result->orders_per_sec > 0) {
        printf("│ Orders/sec          │ %13.2f │ %13.2f (%+.1f%%) │\n",
               c_result->orders_per_sec, cpp_result->orders_per_sec,
               ((cpp_result->orders_per_sec - c_result->orders_per_sec) / c_result->orders_per_sec) * 100);
    }
    
    if (c_result->avg_latency_us > 0 && cpp_result->avg_latency_us > 0) {
        printf("│ Avg Latency (µs)    │ %13.3f │ %13.3f (%+.1f%%) │\n",
               c_result->avg_latency_us, cpp_result->avg_latency_us,
               ((cpp_result->avg_latency_us - c_result->avg_latency_us) / c_result->avg_latency_us) * 100);
    }
    
    // Resource usage
    printf("│ User Time (s)       │ %13.3f │ %13.3f (%+.1f%%) │\n",
           c_result->user_time, cpp_result->user_time,
           ((cpp_result->user_time - c_result->user_time) / c_result->user_time) * 100);
    
    printf("│ System Time (s)     │ %13.3f │ %13.3f (%+.1f%%) │\n",
           c_result->sys_time, cpp_result->sys_time,
           ((cpp_result->sys_time - c_result->sys_time) / c_result->sys_time) * 100);
    
    printf("│ Real Time (s)       │ %13.3f │ %13.3f (%+.1f%%) │\n",
           c_result->real_time, cpp_result->real_time,
           ((cpp_result->real_time - c_result->real_time) / c_result->real_time) * 100);
    
    printf("│ Max RSS (MB)        │ %13.2f │ %13.2f (%+.1f%%) │\n",
           c_result->max_rss_kb / 1024.0, cpp_result->max_rss_kb / 1024.0,
           ((cpp_result->max_rss_kb - c_result->max_rss_kb) / (double)c_result->max_rss_kb) * 100);
    
    printf("└─────────────────────┴───────────────┴──────────────────────┘\n");
}

void print_summary(BenchmarkResult* c_trading, BenchmarkResult* cpp_trading,
                  BenchmarkResult* c_advanced, BenchmarkResult* cpp_advanced) {
    printf("\n");
    printf("╔═══════════════════════════════════════════════════════════════╗\n");
    printf("║                     PERFORMANCE SUMMARY                       ║\n");
    printf("╠═══════════════════════════════════════════════════════════════╣\n");
    
    double c_avg_latency = (c_trading->avg_latency_us + c_advanced->user_time * 1000) / 2;
    double cpp_avg_latency = (cpp_trading->avg_latency_us + cpp_advanced->user_time * 1000) / 2;
    
    printf("║ Average Latency:                                              ║\n");
    printf("║   C:   %.3f µs                                              ║\n", c_avg_latency);
    printf("║   C++: %.3f µs (%.1f%% %s)                                 ║\n", 
           cpp_avg_latency,
           fabs((cpp_avg_latency - c_avg_latency) / c_avg_latency * 100),
           cpp_avg_latency > c_avg_latency ? "slower" : "faster");
    
    printf("║                                                               ║\n");
    printf("║ Memory Efficiency:                                            ║\n");
    printf("║   C:   %.1f MB avg                                          ║\n",
           (c_trading->max_rss_kb + c_advanced->max_rss_kb) / 2048.0);
    printf("║   C++: %.1f MB avg (%.1f%% %s)                            ║\n",
           (cpp_trading->max_rss_kb + cpp_advanced->max_rss_kb) / 2048.0,
           fabs(((cpp_trading->max_rss_kb + cpp_advanced->max_rss_kb) - 
                (c_trading->max_rss_kb + c_advanced->max_rss_kb)) / 
                (double)(c_trading->max_rss_kb + c_advanced->max_rss_kb) * 100),
           (cpp_trading->max_rss_kb + cpp_advanced->max_rss_kb) > 
           (c_trading->max_rss_kb + c_advanced->max_rss_kb) ? "more" : "less");
    
    printf("║                                                               ║\n");
    
    // Winner determination
    int c_wins = 0, cpp_wins = 0;
    
    if (c_trading->orders_per_sec > cpp_trading->orders_per_sec) c_wins++;
    else cpp_wins++;
    
    if (c_trading->avg_latency_us < cpp_trading->avg_latency_us) c_wins++;
    else cpp_wins++;
    
    if (c_trading->max_rss_kb < cpp_trading->max_rss_kb) c_wins++;
    else cpp_wins++;
    
    if (c_advanced->user_time < cpp_advanced->user_time) c_wins++;
    else cpp_wins++;
    
    printf("║ Overall Winner: %-45s ║\n", 
           c_wins > cpp_wins ? "C (Better performance & efficiency)" : 
           "C++ (Better abstractions & features)");
    
    printf("╚═══════════════════════════════════════════════════════════════╝\n");
}

int main() {
    printf("════════════════════════════════════════════════════════════════\n");
    printf("           HFT BENCHMARK: C vs C++ PERFORMANCE COMPARISON       \n");
    printf("════════════════════════════════════════════════════════════════\n\n");
    
    BenchmarkResult c_trading = {0}, cpp_trading = {0};
    BenchmarkResult c_advanced = {0}, cpp_advanced = {0};
    
    // Build all programs first
    printf("Building C programs...\n");
    system("cd hft_c_example && make clean && make");
    
    printf("\nBuilding C++ programs...\n");
    system("cd hft_cpp_example && make clean && make");
    
    printf("\n════════════════════════════════════════════════════════════════\n");
    printf("                     RUNNING BENCHMARKS                         \n");
    printf("════════════════════════════════════════════════════════════════\n");
    
    // Run trading system benchmarks
    printf("\n>>> Running C Trading System...\n");
    printf("────────────────────────────────────────────────────────────────\n");
    run_command_with_stats("./hft_c_example/hft_trading", &c_trading);
    
    printf("\n>>> Running C++ Trading System...\n");
    printf("────────────────────────────────────────────────────────────────\n");
    run_command_with_stats("./hft_cpp_example/hft_trading", &cpp_trading);
    
    // Run advanced test benchmarks
    printf("\n>>> Running C Advanced Test...\n");
    printf("────────────────────────────────────────────────────────────────\n");
    run_command_with_stats("./hft_c_example/hft_advanced_test", &c_advanced);
    
    printf("\n>>> Running C++ Advanced Test...\n");
    printf("────────────────────────────────────────────────────────────────\n");
    run_command_with_stats("./hft_cpp_example/hft_advanced_test", &cpp_advanced);
    
    // Print comparison
    printf("\n════════════════════════════════════════════════════════════════\n");
    printf("                      COMPARISON RESULTS                        \n");
    printf("════════════════════════════════════════════════════════════════\n");
    
    print_comparison_table("Trading System Benchmark", &c_trading, &cpp_trading);
    print_comparison_table("Advanced Performance Test", &c_advanced, &cpp_advanced);
    
    print_summary(&c_trading, &cpp_trading, &c_advanced, &cpp_advanced);
    
    return 0;
}