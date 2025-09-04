#include <iostream>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>
#include <signal.h>
#include <atomic>
#include <chrono>
#include <netinet/tcp.h>
#include "../utils/timer.hpp"

std::atomic<bool> running(true);

void signal_handler(int signum) {
    std::cout << "\nShutting down server..." << std::endl;
    running = false;
}

struct Message {
    uint64_t sequence;
    uint64_t timestamp;
    char type;  // 'Q' for quote, 'O' for order, 'A' for ack
    char payload[64];
};

int main(int argc, char* argv[]) {
    int port = 9000;
    if (argc > 1) {
        port = std::atoi(argv[1]);
    }

    signal(SIGINT, signal_handler);

    // Create UDP socket
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        std::cerr << "Failed to create socket" << std::endl;
        return 1;
    }

    // Set socket options for low latency
    int flag = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &flag, sizeof(flag));
    
    // Disable Nagle's algorithm (though not applicable for UDP, good practice)
    setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));

    // Bind socket
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);
    
    if (bind(sock, (sockaddr*)&addr, sizeof(addr)) < 0) {
        std::cerr << "Failed to bind socket to port " << port << std::endl;
        close(sock);
        return 1;
    }

    std::cout << "UDP Server listening on port " << port << std::endl;
    std::cout << "Press Ctrl+C to stop" << std::endl;

    Message msg;
    sockaddr_in client{};
    socklen_t client_len = sizeof(client);
    
    uint64_t total_messages = 0;
    uint64_t total_quotes = 0;
    uint64_t total_orders = 0;
    
    LatencyStats processing_stats;
    auto start_time = std::chrono::steady_clock::now();

    while (running) {
        // Receive message
        int bytes = recvfrom(sock, &msg, sizeof(msg), MSG_DONTWAIT, 
                            (sockaddr*)&client, &client_len);
        
        if (bytes > 0) {
            auto recv_time = Timer::rdtsc();
            
            // Process based on message type
            if (msg.type == 'Q') {
                // Quote message - send market data back
                Message quote;
                quote.sequence = msg.sequence;
                quote.timestamp = recv_time;
                quote.type = 'Q';
                snprintf(quote.payload, sizeof(quote.payload), 
                        "BID:100.50,ASK:100.51");
                
                sendto(sock, &quote, sizeof(quote), 0, 
                      (sockaddr*)&client, client_len);
                total_quotes++;
                
            } else if (msg.type == 'O') {
                // Order message - send acknowledgment
                Message ack;
                ack.sequence = msg.sequence;
                ack.timestamp = recv_time;
                ack.type = 'A';
                snprintf(ack.payload, sizeof(ack.payload), "ORDER_ACK:%lu", msg.sequence);
                
                sendto(sock, &ack, sizeof(ack), 0, 
                      (sockaddr*)&client, client_len);
                total_orders++;
            }
            
            total_messages++;
            
            // Calculate processing time
            auto process_time = Timer::rdtsc() - recv_time;
            processing_stats.add_sample(Timer::tsc_to_ns(process_time));
            
            // Print statistics every 10000 messages
            if (total_messages % 10000 == 0) {
                auto now = std::chrono::steady_clock::now();
                auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - start_time).count();
                
                std::cout << "Messages: " << total_messages 
                         << " (Q:" << total_quotes << ", O:" << total_orders << ")"
                         << " Rate: " << (total_messages / (elapsed + 1)) << " msg/s" 
                         << std::endl;
            }
        } else if (bytes < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            std::cerr << "Error receiving data: " << strerror(errno) << std::endl;
        }
        
        // Small sleep to prevent CPU spinning in non-blocking mode
        if (bytes <= 0) {
            usleep(1);
        }
    }

    // Print final statistics
    std::cout << "\n========== Server Statistics ==========" << std::endl;
    std::cout << "Total messages processed: " << total_messages << std::endl;
    std::cout << "Total quotes: " << total_quotes << std::endl;
    std::cout << "Total orders: " << total_orders << std::endl;
    
    if (processing_stats.count() > 0) {
        processing_stats.print_summary("Message Processing");
    }

    close(sock);
    return 0;
}