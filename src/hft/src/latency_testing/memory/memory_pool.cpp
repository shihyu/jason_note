#include <iostream>
#include <vector>
#include <memory>
#include <cstring>
#include <random>
#include <sys/mman.h>
#include "../utils/timer.hpp"

template<typename T, size_t PoolSize = 1024>
class MemoryPool {
private:
    struct Block {
        T data;
        Block* next;
    };

    std::vector<std::unique_ptr<Block[]>> chunks_;
    Block* free_list_;
    size_t chunk_size_;
    size_t allocated_;
    size_t freed_;

public:
    MemoryPool(size_t chunk_size = 1024) 
        : free_list_(nullptr), chunk_size_(chunk_size), allocated_(0), freed_(0) {
        allocate_chunk();
    }

    void allocate_chunk() {
        auto chunk = std::make_unique<Block[]>(chunk_size_);
        
        // Link all blocks in the chunk to the free list
        for (size_t i = 0; i < chunk_size_ - 1; ++i) {
            chunk[i].next = &chunk[i + 1];
        }
        chunk[chunk_size_ - 1].next = free_list_;
        free_list_ = &chunk[0];
        
        chunks_.push_back(std::move(chunk));
    }

    T* allocate() {
        if (!free_list_) {
            allocate_chunk();
        }
        
        Block* block = free_list_;
        free_list_ = free_list_->next;
        allocated_++;
        
        return &block->data;
    }

    void deallocate(T* ptr) {
        if (!ptr) return;
        
        Block* block = reinterpret_cast<Block*>(ptr);
        block->next = free_list_;
        free_list_ = block;
        freed_++;
    }

    size_t get_allocated() const { return allocated_; }
    size_t get_freed() const { return freed_; }
    size_t get_active() const { return allocated_ - freed_; }
};

class RingBufferAllocator {
private:
    char* buffer_;
    size_t size_;
    size_t head_;
    size_t tail_;
    bool use_hugepages_;

public:
    RingBufferAllocator(size_t size, bool use_hugepages = false) 
        : size_(size), head_(0), tail_(0), use_hugepages_(use_hugepages) {
        
        if (use_hugepages) {
            // Allocate with huge pages (2MB pages)
            buffer_ = static_cast<char*>(mmap(nullptr, size,
                PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                -1, 0));
            
            if (buffer_ == MAP_FAILED) {
                std::cerr << "Failed to allocate huge pages, falling back to normal allocation" << std::endl;
                buffer_ = new char[size];
                use_hugepages_ = false;
            }
        } else {
            buffer_ = new char[size];
        }
    }

    ~RingBufferAllocator() {
        if (use_hugepages_ && buffer_ != MAP_FAILED) {
            munmap(buffer_, size_);
        } else {
            delete[] buffer_;
        }
    }

    void* allocate(size_t bytes) {
        size_t aligned_size = (bytes + 7) & ~7;  // 8-byte alignment
        
        if (head_ + aligned_size > size_) {
            head_ = 0;  // Wrap around
        }
        
        void* ptr = buffer_ + head_;
        head_ += aligned_size;
        
        return ptr;
    }

    void reset() {
        head_ = 0;
        tail_ = 0;
    }

    size_t get_used() const {
        return head_ >= tail_ ? head_ - tail_ : size_ - tail_ + head_;
    }
};

struct TestObject {
    uint64_t id;
    uint64_t timestamp;
    double price;
    uint64_t quantity;
    char symbol[16];
    char padding[32];  // Simulate realistic object size
};

void test_allocation_strategies() {
    const int NUM_OPERATIONS = 1000000;
    const int BATCH_SIZE = 100;
    
    LatencyStats heap_stats, pool_stats, ring_stats;
    
    std::cout << "\n========== Allocation Strategy Comparison ==========" << std::endl;
    std::cout << "Object size: " << sizeof(TestObject) << " bytes" << std::endl;
    std::cout << "Operations: " << NUM_OPERATIONS << std::endl;

    // Test 1: Standard heap allocation
    {
        std::vector<TestObject*> objects;
        objects.reserve(BATCH_SIZE);
        
        for (int i = 0; i < NUM_OPERATIONS; ++i) {
            auto t1 = Timer::now();
            
            TestObject* obj = new TestObject();
            obj->id = i;
            obj->timestamp = Timer::rdtsc();
            objects.push_back(obj);
            
            if (objects.size() >= BATCH_SIZE) {
                for (auto* ptr : objects) {
                    delete ptr;
                }
                objects.clear();
            }
            
            auto t2 = Timer::now();
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            heap_stats.add_sample(static_cast<double>(duration));
        }
        
        for (auto* ptr : objects) {
            delete ptr;
        }
    }

    // Test 2: Memory pool allocation
    {
        MemoryPool<TestObject, 10000> pool(10000);
        std::vector<TestObject*> objects;
        objects.reserve(BATCH_SIZE);
        
        for (int i = 0; i < NUM_OPERATIONS; ++i) {
            auto t1 = Timer::now();
            
            TestObject* obj = pool.allocate();
            obj->id = i;
            obj->timestamp = Timer::rdtsc();
            objects.push_back(obj);
            
            if (objects.size() >= BATCH_SIZE) {
                for (auto* ptr : objects) {
                    pool.deallocate(ptr);
                }
                objects.clear();
            }
            
            auto t2 = Timer::now();
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            pool_stats.add_sample(static_cast<double>(duration));
        }
        
        std::cout << "Pool stats - Allocated: " << pool.get_allocated() 
                  << ", Freed: " << pool.get_freed() 
                  << ", Active: " << pool.get_active() << std::endl;
    }

    // Test 3: Ring buffer allocation
    {
        RingBufferAllocator ring(100 * 1024 * 1024);  // 100MB ring buffer
        
        for (int i = 0; i < NUM_OPERATIONS; ++i) {
            auto t1 = Timer::now();
            
            TestObject* obj = static_cast<TestObject*>(ring.allocate(sizeof(TestObject)));
            obj->id = i;
            obj->timestamp = Timer::rdtsc();
            
            // Ring buffer doesn't need explicit deallocation
            if (i % 10000 == 0) {
                ring.reset();  // Periodic reset to simulate batch processing
            }
            
            auto t2 = Timer::now();
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            ring_stats.add_sample(static_cast<double>(duration));
        }
        
        std::cout << "Ring buffer used: " << ring.get_used() << " bytes" << std::endl;
    }

    heap_stats.print_summary("Heap Allocation (new/delete)");
    pool_stats.print_summary("Memory Pool");
    ring_stats.print_summary("Ring Buffer");
}

void test_allocation_patterns() {
    const int NUM_OPERATIONS = 100000;
    
    std::cout << "\n========== Allocation Pattern Testing ==========" << std::endl;
    
    MemoryPool<TestObject, 10000> pool(10000);
    LatencyStats sequential_stats, random_stats, burst_stats;
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dist(1, 100);

    // Sequential allocation/deallocation
    {
        std::cout << "Testing sequential pattern..." << std::endl;
        std::vector<TestObject*> objects;
        
        for (int i = 0; i < NUM_OPERATIONS; ++i) {
            auto t1 = Timer::now();
            
            TestObject* obj = pool.allocate();
            obj->id = i;
            objects.push_back(obj);
            
            if (objects.size() > 100) {
                pool.deallocate(objects[0]);
                objects.erase(objects.begin());
            }
            
            auto t2 = Timer::now();
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            sequential_stats.add_sample(static_cast<double>(duration));
        }
        
        for (auto* obj : objects) {
            pool.deallocate(obj);
        }
    }

    // Random allocation/deallocation
    {
        std::cout << "Testing random pattern..." << std::endl;
        std::vector<TestObject*> objects;
        
        for (int i = 0; i < NUM_OPERATIONS; ++i) {
            auto t1 = Timer::now();
            
            if (dist(gen) < 60 || objects.empty()) {  // 60% allocate
                TestObject* obj = pool.allocate();
                obj->id = i;
                objects.push_back(obj);
            } else {  // 40% deallocate
                std::uniform_int_distribution<> idx_dist(0, objects.size() - 1);
                int idx = idx_dist(gen);
                pool.deallocate(objects[idx]);
                objects.erase(objects.begin() + idx);
            }
            
            auto t2 = Timer::now();
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            random_stats.add_sample(static_cast<double>(duration));
        }
        
        for (auto* obj : objects) {
            pool.deallocate(obj);
        }
    }

    // Burst allocation pattern
    {
        std::cout << "Testing burst pattern..." << std::endl;
        const int BURST_SIZE = 1000;
        
        for (int burst = 0; burst < NUM_OPERATIONS / BURST_SIZE; ++burst) {
            auto t1 = Timer::now();
            
            std::vector<TestObject*> burst_objects;
            
            // Allocate burst
            for (int i = 0; i < BURST_SIZE; ++i) {
                TestObject* obj = pool.allocate();
                obj->id = burst * BURST_SIZE + i;
                burst_objects.push_back(obj);
            }
            
            // Deallocate burst
            for (auto* obj : burst_objects) {
                pool.deallocate(obj);
            }
            
            auto t2 = Timer::now();
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            burst_stats.add_sample(static_cast<double>(duration));
        }
    }

    sequential_stats.print_summary("Sequential Pattern");
    random_stats.print_summary("Random Pattern");
    burst_stats.print_summary("Burst Pattern (per 1000 ops)");
}

void test_cache_effects() {
    const int NUM_OPERATIONS = 100000;
    const int STRIDE_SIZES[] = {1, 8, 64, 512, 4096};
    
    std::cout << "\n========== Cache Effects Testing ==========" << std::endl;
    
    const size_t BUFFER_SIZE = 10 * 1024 * 1024;  // 10MB
    std::vector<char> buffer(BUFFER_SIZE);
    
    for (int stride : STRIDE_SIZES) {
        LatencyStats stride_stats;
        
        for (int i = 0; i < NUM_OPERATIONS; ++i) {
            size_t index = (i * stride) % BUFFER_SIZE;
            
            auto t1 = Timer::now();
            
            // Memory access pattern
            buffer[index] = static_cast<char>(i);
            volatile char value = buffer[index];
            (void)value;  // Prevent optimization
            
            auto t2 = Timer::now();
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            stride_stats.add_sample(static_cast<double>(duration));
        }
        
        std::cout << "\nStride " << stride << " bytes:" << std::endl;
        std::cout << "Mean: " << stride_stats.mean() << " ns, "
                  << "P99: " << stride_stats.percentile(99) << " ns" << std::endl;
    }
}

int main(int argc, char* argv[]) {
    std::cout << "==================================================" << std::endl;
    std::cout << "         Memory Allocation Benchmarks            " << std::endl;
    std::cout << "==================================================" << std::endl;

    if (argc > 1) {
        std::string test = argv[1];
        if (test == "strategies") {
            test_allocation_strategies();
        } else if (test == "patterns") {
            test_allocation_patterns();
        } else if (test == "cache") {
            test_cache_effects();
        } else {
            std::cerr << "Unknown test: " << test << std::endl;
            std::cerr << "Available tests: strategies, patterns, cache" << std::endl;
            return 1;
        }
    } else {
        // Run all tests
        test_allocation_strategies();
        test_allocation_patterns();
        test_cache_effects();
    }

    return 0;
}