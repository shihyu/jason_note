#include <atomic>
#include <memory>
#include <iostream>
#include <thread>
#include <vector>
#include <chrono>

template<typename T>
class LockFreeQueue {
private:
    struct Node {
        std::atomic<T*> data{nullptr};
        std::atomic<Node*> next{nullptr};
    };
    
    std::atomic<Node*> head{new Node};
    std::atomic<Node*> tail{head.load()};

public:
    ~LockFreeQueue() {
        while (Node* const old_head = head.load()) {
            head.store(old_head->next);
            delete old_head;
        }
    }
    
    void enqueue(T item) {
        Node* new_node = new Node;
        T* data = new T(std::move(item));
        
        Node* prev_tail = tail.exchange(new_node);
        prev_tail->data.store(data);
        prev_tail->next.store(new_node);
    }
    
    bool dequeue(T& result) {
        Node* head_node = head.load();
        Node* next = head_node->next.load();
        
        if (next == nullptr) {
            return false;  // 佇列為空
        }
        
        T* data = next->data.exchange(nullptr);
        if (data == nullptr) {
            return false;  // 其他執行緒已取走
        }
        
        result = *data;
        delete data;
        head.store(next);
        delete head_node;
        return true;
    }
    
    bool empty() {
        Node* head_node = head.load();
        Node* next = head_node->next.load();
        return next == nullptr;
    }
};

// 使用範例
LockFreeQueue<int> queue;
std::atomic<bool> stop_producer{false};
std::atomic<int> total_produced{0};
std::atomic<int> total_consumed{0};

void producer(int producer_id) {
    for (int i = 0; i < 100; ++i) {
        int value = producer_id * 1000 + i;
        queue.enqueue(value);
        total_produced++;
        
        if (i % 20 == 0) {
            std::cout << "Producer " << producer_id << " produced: " << value << std::endl;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    std::cout << "Producer " << producer_id << " finished" << std::endl;
}

void consumer(int consumer_id) {
    int value;
    int consumed_count = 0;
    
    while (!stop_producer.load() || !queue.empty()) {
        if (queue.dequeue(value)) {
            consumed_count++;
            total_consumed++;
            
            if (consumed_count % 30 == 0) {
                std::cout << "Consumer " << consumer_id << " consumed: " << value 
                          << " (total consumed: " << consumed_count << ")" << std::endl;
            }
        } else {
            std::this_thread::yield();  // 等待數據
        }
    }
    
    std::cout << "Consumer " << consumer_id << " finished, consumed " 
              << consumed_count << " items" << std::endl;
}

int main() {
    std::cout << "Starting lock-free queue example..." << std::endl;
    
    std::vector<std::thread> threads;
    
    // 創建3個生產者
    for (int i = 1; i <= 3; ++i) {
        threads.emplace_back(producer, i);
    }
    
    // 創建2個消費者
    for (int i = 1; i <= 2; ++i) {
        threads.emplace_back(consumer, i);
    }
    
    // 等待生產者完成
    for (int i = 0; i < 3; ++i) {
        threads[i].join();
    }
    
    std::cout << "All producers finished, stopping consumers..." << std::endl;
    stop_producer.store(true);
    
    // 等待消費者完成
    for (int i = 3; i < 5; ++i) {
        threads[i].join();
    }
    
    std::cout << "Final stats:" << std::endl;
    std::cout << "  Total produced: " << total_produced << std::endl;
    std::cout << "  Total consumed: " << total_consumed << std::endl;
    std::cout << "  Queue empty: " << (queue.empty() ? "Yes" : "No") << std::endl;
    
    return 0;
}