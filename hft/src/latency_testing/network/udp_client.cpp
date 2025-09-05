#include <iostream>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>
#include <thread>
#include <chrono>
#include <netinet/tcp.h>
#include "../utils/timer.hpp"

struct Message {
    uint64_t sequence;
    uint64_t timestamp;
    char type;  // 'Q' for quote, 'O' for order, 'A' for ack
    char payload[64];
};

void test_quote_latency(int sock, sockaddr_in& server) {
    const int NUM_TESTS = 10000;
    const int WARMUP = 1000;
    
    Message msg, response;
    LatencyStats rtt_stats;
    
    std::cout << "\n========== Testing Quote Request Latency ==========" << std::endl;
    std::cout << "Warming up with " << WARMUP << " requests..." << std::endl;
    
    // Warmup
    for (int i = 0; i < WARMUP; ++i) {
        msg.sequence = i;
        msg.type = 'Q';
        msg.timestamp = Timer::rdtsc();
        strcpy(msg.payload, "GET_QUOTE");
        
        sendto(sock, &msg, sizeof(msg), 0, (sockaddr*)&server, sizeof(server));
        recvfrom(sock, &response, sizeof(response), 0, nullptr, nullptr);
    }
    
    std::cout << "Running " << NUM_TESTS << " quote requests..." << std::endl;
    
    // Actual test
    for (int i = 0; i < NUM_TESTS; ++i) {
        msg.sequence = i + WARMUP;
        msg.type = 'Q';
        strcpy(msg.payload, "GET_QUOTE");
        
        auto t1 = Timer::now();
        msg.timestamp = Timer::rdtsc();
        
        sendto(sock, &msg, sizeof(msg), 0, (sockaddr*)&server, sizeof(server));
        int bytes = recvfrom(sock, &response, sizeof(response), 0, nullptr, nullptr);
        
        auto t2 = Timer::now();
        
        if (bytes > 0 && response.sequence == msg.sequence) {
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            rtt_stats.add_sample(static_cast<double>(duration));
        }
        
        // Small delay to prevent overwhelming the server
        if (i % 100 == 0) {
            std::this_thread::sleep_for(std::chrono::microseconds(1));
        }
    }
    
    rtt_stats.print_summary("Quote Request RTT");
    rtt_stats.print_histogram();
}

void test_order_latency(int sock, sockaddr_in& server) {
    const int NUM_TESTS = 10000;
    const int WARMUP = 1000;
    
    Message msg, response;
    LatencyStats rtt_stats;
    
    std::cout << "\n========== Testing Order Submission Latency ==========" << std::endl;
    std::cout << "Warming up with " << WARMUP << " orders..." << std::endl;
    
    // Warmup
    for (int i = 0; i < WARMUP; ++i) {
        msg.sequence = i;
        msg.type = 'O';
        msg.timestamp = Timer::rdtsc();
        snprintf(msg.payload, sizeof(msg.payload), "BUY,100,%d", i % 100 + 1);
        
        sendto(sock, &msg, sizeof(msg), 0, (sockaddr*)&server, sizeof(server));
        recvfrom(sock, &response, sizeof(response), 0, nullptr, nullptr);
    }
    
    std::cout << "Running " << NUM_TESTS << " order submissions..." << std::endl;
    
    // Actual test
    for (int i = 0; i < NUM_TESTS; ++i) {
        msg.sequence = i + WARMUP;
        msg.type = 'O';
        snprintf(msg.payload, sizeof(msg.payload), "BUY,100,%d", i % 100 + 1);
        
        auto t1 = Timer::now();
        msg.timestamp = Timer::rdtsc();
        
        sendto(sock, &msg, sizeof(msg), 0, (sockaddr*)&server, sizeof(server));
        int bytes = recvfrom(sock, &response, sizeof(response), 0, nullptr, nullptr);
        
        auto t2 = Timer::now();
        
        if (bytes > 0 && response.sequence == msg.sequence && response.type == 'A') {
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            rtt_stats.add_sample(static_cast<double>(duration));
        }
        
        // Small delay to prevent overwhelming the server
        if (i % 100 == 0) {
            std::this_thread::sleep_for(std::chrono::microseconds(1));
        }
    }
    
    rtt_stats.print_summary("Order Submission RTT");
    rtt_stats.print_histogram();
}

void test_burst_latency(int sock, sockaddr_in& server) {
    const int BURST_SIZE = 100;
    const int NUM_BURSTS = 100;
    
    Message msg, response;
    LatencyStats burst_stats;
    
    std::cout << "\n========== Testing Burst Latency ==========" << std::endl;
    std::cout << "Sending " << NUM_BURSTS << " bursts of " << BURST_SIZE << " messages..." << std::endl;
    
    for (int burst = 0; burst < NUM_BURSTS; ++burst) {
        auto burst_start = Timer::now();
        
        // Send burst
        for (int i = 0; i < BURST_SIZE; ++i) {
            msg.sequence = burst * BURST_SIZE + i;
            msg.type = (i % 2) ? 'Q' : 'O';
            msg.timestamp = Timer::rdtsc();
            
            if (msg.type == 'Q') {
                strcpy(msg.payload, "BURST_QUOTE");
            } else {
                snprintf(msg.payload, sizeof(msg.payload), "BURST_ORDER_%d", i);
            }
            
            sendto(sock, &msg, sizeof(msg), 0, (sockaddr*)&server, sizeof(server));
        }
        
        // Receive responses
        for (int i = 0; i < BURST_SIZE; ++i) {
            recvfrom(sock, &response, sizeof(response), 0, nullptr, nullptr);
        }
        
        auto burst_end = Timer::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(burst_end - burst_start).count();
        burst_stats.add_sample(static_cast<double>(duration));
        
        // Delay between bursts
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    
    std::cout << "Burst latency (microseconds for " << BURST_SIZE << " messages):" << std::endl;
    burst_stats.print_summary("Burst Processing Time");
}

void test_sustained_throughput(int sock, sockaddr_in& server) {
    const int DURATION_SECONDS = 10;
    const int RATE_PER_SECOND = 10000;
    const auto MESSAGE_INTERVAL = std::chrono::microseconds(1000000 / RATE_PER_SECOND);
    
    Message msg, response;
    LatencyStats latency_stats;
    
    std::cout << "\n========== Testing Sustained Throughput ==========" << std::endl;
    std::cout << "Target rate: " << RATE_PER_SECOND << " msg/s for " << DURATION_SECONDS << " seconds" << std::endl;
    
    auto start_time = std::chrono::steady_clock::now();
    auto next_send = start_time;
    uint64_t sequence = 0;
    uint64_t sent = 0;
    uint64_t received = 0;
    
    while (true) {
        auto now = std::chrono::steady_clock::now();
        if (now >= next_send) {
            // Send message
            msg.sequence = sequence++;
            msg.type = (sequence % 3) ? 'Q' : 'O';
            msg.timestamp = Timer::rdtsc();
            
            auto send_start = Timer::now();
            sendto(sock, &msg, sizeof(msg), 0, (sockaddr*)&server, sizeof(server));
            sent++;
            
            // Try to receive any pending responses (non-blocking)
            struct timeval tv;
            tv.tv_sec = 0;
            tv.tv_usec = 0;
            setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
            
            if (recvfrom(sock, &response, sizeof(response), 0, nullptr, nullptr) > 0) {
                auto recv_end = Timer::now();
                auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(recv_end - send_start).count();
                latency_stats.add_sample(static_cast<double>(duration));
                received++;
            }
            
            next_send += MESSAGE_INTERVAL;
        }
        
        // Check if test duration has elapsed
        if (std::chrono::duration_cast<std::chrono::seconds>(now - start_time).count() >= DURATION_SECONDS) {
            break;
        }
    }
    
    // Receive any remaining responses
    struct timeval tv;
    tv.tv_sec = 0;
    tv.tv_usec = 100000;  // 100ms timeout
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    
    while (received < sent && recvfrom(sock, &response, sizeof(response), 0, nullptr, nullptr) > 0) {
        received++;
    }
    
    auto end_time = std::chrono::steady_clock::now();
    auto total_duration = std::chrono::duration_cast<std::chrono::seconds>(end_time - start_time).count();
    
    std::cout << "Sent: " << sent << " messages" << std::endl;
    std::cout << "Received: " << received << " messages" << std::endl;
    std::cout << "Actual rate: " << (sent / total_duration) << " msg/s" << std::endl;
    std::cout << "Loss rate: " << ((sent - received) * 100.0 / sent) << "%" << std::endl;
    
    if (latency_stats.count() > 0) {
        latency_stats.print_summary("Sustained Load Latency");
    }
}

int main(int argc, char* argv[]) {
    const char* server_ip = "127.0.0.1";
    int port = 9000;
    
    if (argc > 1) {
        server_ip = argv[1];
    }
    if (argc > 2) {
        port = std::atoi(argv[2]);
    }

    // Create UDP socket
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        std::cerr << "Failed to create socket" << std::endl;
        return 1;
    }

    // Set socket options for low latency
    int flag = 1;
    setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
    
    // Set receive timeout for blocking operations
    struct timeval tv;
    tv.tv_sec = 1;
    tv.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    // Server address
    sockaddr_in server{};
    server.sin_family = AF_INET;
    server.sin_port = htons(port);
    inet_pton(AF_INET, server_ip, &server.sin_addr);

    std::cout << "==================================================" << std::endl;
    std::cout << "          Network RTT Latency Testing             " << std::endl;
    std::cout << "==================================================" << std::endl;
    std::cout << "Connecting to " << server_ip << ":" << port << std::endl;

    // Run tests
    test_quote_latency(sock, server);
    test_order_latency(sock, server);
    test_burst_latency(sock, server);
    test_sustained_throughput(sock, server);

    close(sock);
    return 0;
}