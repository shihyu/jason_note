#ifndef TIMER_HPP
#define TIMER_HPP

#include <chrono>
#include <vector>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <iostream>
#include <iomanip>
#include <x86intrin.h>

class Timer {
public:
    using TimePoint = std::chrono::high_resolution_clock::time_point;
    using Duration = std::chrono::nanoseconds;

    static TimePoint now() {
        return std::chrono::high_resolution_clock::now();
    }

    static uint64_t rdtsc() {
        return __rdtsc();
    }

    static uint64_t rdtscp() {
        unsigned int aux;
        return __rdtscp(&aux);
    }

    static double tsc_to_ns(uint64_t cycles, double cpu_ghz = 3.0) {
        return cycles / cpu_ghz;
    }
};

class LatencyStats {
private:
    std::vector<double> samples_;
    bool sorted_ = false;

    void ensure_sorted() {
        if (!sorted_) {
            std::sort(samples_.begin(), samples_.end());
            sorted_ = true;
        }
    }

public:
    void add_sample(double latency_ns) {
        samples_.push_back(latency_ns);
        sorted_ = false;
    }

    void clear() {
        samples_.clear();
        sorted_ = false;
    }

    size_t count() const {
        return samples_.size();
    }

    double mean() const {
        if (samples_.empty()) return 0.0;
        double sum = std::accumulate(samples_.begin(), samples_.end(), 0.0);
        return sum / samples_.size();
    }

    double median() {
        if (samples_.empty()) return 0.0;
        ensure_sorted();
        size_t mid = samples_.size() / 2;
        if (samples_.size() % 2 == 0) {
            return (samples_[mid - 1] + samples_[mid]) / 2.0;
        }
        return samples_[mid];
    }

    double percentile(double p) {
        if (samples_.empty()) return 0.0;
        ensure_sorted();
        size_t idx = static_cast<size_t>(samples_.size() * p / 100.0);
        if (idx >= samples_.size()) idx = samples_.size() - 1;
        return samples_[idx];
    }

    double min() {
        if (samples_.empty()) return 0.0;
        ensure_sorted();
        return samples_[0];
    }

    double max() {
        if (samples_.empty()) return 0.0;
        ensure_sorted();
        return samples_[samples_.size() - 1];
    }

    double stddev() const {
        if (samples_.size() < 2) return 0.0;
        double m = mean();
        double sum_sq = 0.0;
        for (double x : samples_) {
            double diff = x - m;
            sum_sq += diff * diff;
        }
        return std::sqrt(sum_sq / (samples_.size() - 1));
    }

    double jitter() {
        if (samples_.size() < 2) return 0.0;
        std::vector<double> diffs;
        for (size_t i = 1; i < samples_.size(); ++i) {
            diffs.push_back(std::abs(samples_[i] - samples_[i - 1]));
        }
        double sum = std::accumulate(diffs.begin(), diffs.end(), 0.0);
        return sum / diffs.size();
    }

    void print_summary(const std::string& label = "Latency Statistics") {
        std::cout << "\n=== " << label << " ===" << std::endl;
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Samples: " << count() << std::endl;
        std::cout << "Mean:    " << mean() << " ns" << std::endl;
        std::cout << "Median:  " << median() << " ns" << std::endl;
        std::cout << "Min:     " << min() << " ns" << std::endl;
        std::cout << "Max:     " << max() << " ns" << std::endl;
        std::cout << "StdDev:  " << stddev() << " ns" << std::endl;
        std::cout << "Jitter:  " << jitter() << " ns" << std::endl;
        std::cout << "P50:     " << percentile(50) << " ns" << std::endl;
        std::cout << "P90:     " << percentile(90) << " ns" << std::endl;
        std::cout << "P95:     " << percentile(95) << " ns" << std::endl;
        std::cout << "P99:     " << percentile(99) << " ns" << std::endl;
        std::cout << "P99.9:   " << percentile(99.9) << " ns" << std::endl;
    }

    void print_histogram(int buckets = 20) {
        if (samples_.empty()) return;
        ensure_sorted();
        
        double min_val = min();
        double max_val = max();
        double range = max_val - min_val;
        double bucket_size = range / buckets;

        std::vector<int> histogram(buckets, 0);
        for (double sample : samples_) {
            int bucket = static_cast<int>((sample - min_val) / bucket_size);
            if (bucket >= buckets) bucket = buckets - 1;
            histogram[bucket]++;
        }

        int max_count = *std::max_element(histogram.begin(), histogram.end());
        int bar_width = 50;

        std::cout << "\n=== Histogram ===" << std::endl;
        for (int i = 0; i < buckets; ++i) {
            double bucket_start = min_val + i * bucket_size;
            double bucket_end = bucket_start + bucket_size;
            
            std::cout << std::setw(10) << std::fixed << std::setprecision(1)
                      << bucket_start << " - " << std::setw(10) << bucket_end << " ns: ";
            
            int bar_len = (histogram[i] * bar_width) / max_count;
            for (int j = 0; j < bar_len; ++j) {
                std::cout << "#";
            }
            std::cout << " " << histogram[i] << std::endl;
        }
    }
};

#endif // TIMER_HPP