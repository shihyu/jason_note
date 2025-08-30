#include <iostream>
#include <vector>
#include <queue>
#include <thread>
#include <atomic>
#include <chrono>
#include <cstring>
#include <memory>
#include <array>
#include <algorithm>
#include <iomanip>
#include <unordered_map>

#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>

using namespace std;
using namespace chrono;

// 無鎖環形緩衝區
template<typename T, size_t Size>
class LockFreeRingBuffer {
private:
    alignas(64) atomic<size_t> write_index{0};
    alignas(64) atomic<size_t> read_index{0};
    alignas(64) array<T, Size> buffer;
    
public:
    bool push(const T& item) {
        size_t current_write = write_index.load(memory_order_relaxed);
        size_t next_write = (current_write + 1) % Size;
        
        if (next_write == read_index.load(memory_order_acquire)) {
            return false;  // Buffer full
        }
        
        buffer[current_write] = item;
        write_index.store(next_write, memory_order_release);
        return true;
    }
    
    bool pop(T& item) {
        size_t current_read = read_index.load(memory_order_relaxed);
        
        if (current_read == write_index.load(memory_order_acquire)) {
            return false;  // Buffer empty
        }
        
        item = buffer[current_read];
        read_index.store((current_read + 1) % Size, memory_order_release);
        return true;
    }
    
    bool empty() const {
        return read_index.load(memory_order_acquire) == 
               write_index.load(memory_order_acquire);
    }
};

// 事件驅動伺服器 (正確的 IO 模型)
class EventDrivenServer {
private:
    static constexpr int MAX_EVENTS = 1024;
    static constexpr int BUFFER_SIZE = 65536;
    static constexpr int BACKLOG = 511;
    
    int listen_fd;
    int epoll_fd;
    atomic<bool> running{true};
    
    struct ClientConnection {
        int fd;
        vector<char> read_buffer;
        vector<char> write_buffer;
        size_t write_offset;
        steady_clock::time_point last_activity;
        
        ClientConnection(int fd) : 
            fd(fd), 
            write_offset(0),
            last_activity(steady_clock::now()) {
            read_buffer.reserve(BUFFER_SIZE);
            write_buffer.reserve(BUFFER_SIZE);
        }
    };
    
    unordered_map<int, unique_ptr<ClientConnection>> clients;
    
    // 性能統計
    atomic<size_t> total_connections{0};
    atomic<size_t> active_connections{0};
    atomic<size_t> total_messages{0};
    atomic<size_t> total_bytes{0};
    
public:
    EventDrivenServer(int port) {
        setup_server(port);
    }
    
    ~EventDrivenServer() {
        if (epoll_fd >= 0) close(epoll_fd);
        if (listen_fd >= 0) close(listen_fd);
    }
    
    void setup_server(int port) {
        // 創建監聽 socket
        listen_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (listen_fd < 0) {
            throw runtime_error("創建 socket 失敗");
        }
        
        // 設置 socket 選項
        int opt = 1;
        setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        setsockopt(listen_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));
        setsockopt(listen_fd, IPPROTO_TCP, TCP_NODELAY, &opt, sizeof(opt));
        
        // 設置非阻塞
        set_nonblocking(listen_fd);
        
        // 綁定地址
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port);
        
        if (bind(listen_fd, (sockaddr*)&addr, sizeof(addr)) < 0) {
            throw runtime_error("綁定失敗");
        }
        
        // 開始監聽
        if (listen(listen_fd, BACKLOG) < 0) {
            throw runtime_error("監聽失敗");
        }
        
        // 創建 epoll
        epoll_fd = epoll_create1(EPOLL_CLOEXEC);
        if (epoll_fd < 0) {
            throw runtime_error("創建 epoll 失敗");
        }
        
        // 添加監聽 socket 到 epoll
        epoll_event ev{};
        ev.events = EPOLLIN | EPOLLET;  // 邊緣觸發
        ev.data.fd = listen_fd;
        
        if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listen_fd, &ev) < 0) {
            throw runtime_error("將監聽 socket 加入 epoll 失敗");
        }
        
        cout << "事件驅動伺服器監聽在埠口 " << port << " 上" << endl;
    }
    
    void run() {
        epoll_event events[MAX_EVENTS];
        
        while (running) {
            // 等待事件
            int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, 100);
            
            if (nfds < 0) {
                if (errno == EINTR) continue;
                cerr << "epoll_wait 錯誤: " << strerror(errno) << endl;
                break;
            }
            
            // 處理所有就緒事件
            for (int i = 0; i < nfds; i++) {
                if (events[i].data.fd == listen_fd) {
                    // 新連接
                    accept_all_connections();
                } else {
                    // 客戶端 IO
                    handle_client_event(events[i]);
                }
            }
            
            // 定期清理超時連接
            if (steady_clock::now().time_since_epoch().count() % 1000000000 == 0) {
                cleanup_idle_connections();
            }
        }
    }
    
    void stop() {
        running = false;
    }
    
    void print_stats() const {
        cout << "\n=== 伺服器統計 ===" << endl;
        cout << "總連線數: " << total_connections << endl;
        cout << "活躍連線數: " << active_connections << endl;
        cout << "總訊息數: " << total_messages << endl;
        cout << "總位元組數: " << total_bytes << endl;
    }
    
private:
    void set_nonblocking(int fd) {
        int flags = fcntl(fd, F_GETFL, 0);
        fcntl(fd, F_SETFL, flags | O_NONBLOCK);
    }
    
    void accept_all_connections() {
        // 接受所有待處理的連接 (邊緣觸發模式)
        while (true) {
            sockaddr_in client_addr{};
            socklen_t client_len = sizeof(client_addr);
            
            int client_fd = accept4(listen_fd, 
                                   (sockaddr*)&client_addr, 
                                   &client_len,
                                   SOCK_NONBLOCK | SOCK_CLOEXEC);
            
            if (client_fd < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    break;  // 沒有更多連接
                }
                cerr << "Accept 錯誤: " << strerror(errno) << endl;
                break;
            }
            
            // 設置 TCP 選項
            int opt = 1;
            setsockopt(client_fd, IPPROTO_TCP, TCP_NODELAY, &opt, sizeof(opt));
            
            // 添加到 epoll
            epoll_event ev{};
            ev.events = EPOLLIN | EPOLLOUT | EPOLLET | EPOLLRDHUP;
            ev.data.fd = client_fd;
            
            if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &ev) == 0) {
                // 創建客戶端連接對象
                clients[client_fd] = make_unique<ClientConnection>(client_fd);
                
                total_connections++;
                active_connections++;
                
                char addr_str[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &client_addr.sin_addr, addr_str, sizeof(addr_str));
                cout << "新連線來自 " << addr_str 
                     << ":" << ntohs(client_addr.sin_port)
                     << " (fd=" << client_fd << ")" << endl;
            } else {
                close(client_fd);
            }
        }
    }
    
    void handle_client_event(const epoll_event& event) {
        int fd = event.data.fd;
        auto it = clients.find(fd);
        
        if (it == clients.end()) {
            return;
        }
        
        auto& client = it->second;
        
        // 處理斷開連接
        if (event.events & (EPOLLRDHUP | EPOLLHUP | EPOLLERR)) {
            disconnect_client(fd);
            return;
        }
        
        // 處理可讀事件
        if (event.events & EPOLLIN) {
            if (!handle_read(client.get())) {
                disconnect_client(fd);
                return;
            }
        }
        
        // 處理可寫事件
        if (event.events & EPOLLOUT) {
            if (!handle_write(client.get())) {
                disconnect_client(fd);
                return;
            }
        }
        
        client->last_activity = steady_clock::now();
    }
    
    bool handle_read(ClientConnection* client) {
        char buffer[BUFFER_SIZE];
        
        // 讀取所有可用數據 (邊緣觸發模式)
        while (true) {
            ssize_t n = read(client->fd, buffer, sizeof(buffer));
            
            if (n > 0) {
                total_bytes += n;
                
                // 處理接收到的數據
                process_data(client, buffer, n);
                
            } else if (n == 0) {
                // 連接關閉
                return false;
                
            } else {
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    // 沒有更多數據
                    break;
                }
                // 讀取錯誤
                return false;
            }
        }
        
        return true;
    }
    
    bool handle_write(ClientConnection* client) {
        if (client->write_buffer.empty()) {
            return true;
        }
        
        // 發送緩衝區中的數據
        while (client->write_offset < client->write_buffer.size()) {
            ssize_t n = write(client->fd, 
                            client->write_buffer.data() + client->write_offset,
                            client->write_buffer.size() - client->write_offset);
            
            if (n > 0) {
                client->write_offset += n;
                
            } else if (n < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    // 暫時無法寫入
                    break;
                }
                // 寫入錯誤
                return false;
            }
        }
        
        // 清理已發送的數據
        if (client->write_offset >= client->write_buffer.size()) {
            client->write_buffer.clear();
            client->write_offset = 0;
        }
        
        return true;
    }
    
    void process_data(ClientConnection* client, const char* data, size_t len) {
        // 簡單的回聲服務器
        client->write_buffer.insert(client->write_buffer.end(), data, data + len);
        total_messages++;
        
        // 立即嘗試發送
        handle_write(client);
    }
    
    void disconnect_client(int fd) {
        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, fd, nullptr);
        close(fd);
        clients.erase(fd);
        active_connections--;
        
        cout << "客戶端斷開連線 (fd=" << fd << ")" << endl;
    }
    
    void cleanup_idle_connections() {
        auto now = steady_clock::now();
        const auto timeout = seconds(300);  // 5 分鐘超時
        
        vector<int> to_remove;
        
        for (const auto& [fd, client] : clients) {
            if (now - client->last_activity > timeout) {
                to_remove.push_back(fd);
            }
        }
        
        for (int fd : to_remove) {
            cout << "移除閒置連線 (fd=" << fd << ")" << endl;
            disconnect_client(fd);
        }
    }
};

// 錯誤示範：執行緒池 IO 模型
class ThreadPoolServer {
private:
    int listen_fd;
    atomic<bool> running{true};
    vector<thread> worker_threads;
    atomic<size_t> thread_count{0};
    
public:
    ThreadPoolServer(int port) {
        setup_server(port);
    }
    
    void setup_server(int port) {
        listen_fd = socket(AF_INET, SOCK_STREAM, 0);
        
        int opt = 1;
        setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port);
        
        bind(listen_fd, (sockaddr*)&addr, sizeof(addr));
        listen(listen_fd, 128);
        
        cout << "執行緒池伺服器監聽在埠口 " << port << " 上" << endl;
    }
    
    void run() {
        while (running) {
            sockaddr_in client_addr{};
            socklen_t client_len = sizeof(client_addr);
            
            // 阻塞等待連接
            int client_fd = accept(listen_fd, (sockaddr*)&client_addr, &client_len);
            
            if (client_fd < 0) continue;
            
            // 錯誤：為每個連接創建執行緒
            thread_count++;
            worker_threads.emplace_back([this, client_fd]() {
                handle_client_blocking(client_fd);
                thread_count--;
            });
            worker_threads.back().detach();
            
            cout << "活躍執行緒數: " << thread_count << endl;
        }
    }
    
private:
    void handle_client_blocking(int fd) {
        char buffer[4096];
        
        // 執行緒阻塞在這裡！
        while (true) {
            ssize_t n = read(fd, buffer, sizeof(buffer));  // 阻塞
            
            if (n <= 0) break;
            
            // 處理數據...
            write(fd, buffer, n);  // 又阻塞！
        }
        
        close(fd);
    }
};

// 性能測試客戶端
class LoadTestClient {
public:
    static void test_server(const string& host, int port, int num_connections, int duration_sec) {
        cout << "\n=== 負載測試 ===" << endl;
        cout << "目標: " << host << ":" << port << endl;
        cout << "連線數: " << num_connections << endl;
        cout << "持續時間: " << duration_sec << " 秒" << endl;
        
        vector<int> sockets;
        atomic<size_t> total_requests{0};
        atomic<size_t> total_responses{0};
        atomic<bool> testing{true};
        
        // 建立連接
        for (int i = 0; i < num_connections; i++) {
            int sock = socket(AF_INET, SOCK_STREAM, 0);
            if (sock < 0) continue;
            
            // 設置非阻塞
            fcntl(sock, F_SETFL, O_NONBLOCK);
            
            sockaddr_in addr{};
            addr.sin_family = AF_INET;
            addr.sin_port = htons(port);
            inet_pton(AF_INET, host.c_str(), &addr.sin_addr);
            
            connect(sock, (sockaddr*)&addr, sizeof(addr));
            sockets.push_back(sock);
        }
        
        cout << "已建立 " << sockets.size() << " 個連線" << endl;
        
        // 測試線程
        vector<thread> test_threads;
        auto start_time = steady_clock::now();
        
        for (size_t i = 0; i < sockets.size(); i++) {
            test_threads.emplace_back([&, sock = sockets[i]]() {
                char send_buf[] = "Hello, Server!";
                char recv_buf[1024];
                
                while (testing) {
                    // 發送請求
                    if (send(sock, send_buf, sizeof(send_buf), MSG_DONTWAIT) > 0) {
                        total_requests++;
                    }
                    
                    // 接收響應
                    if (recv(sock, recv_buf, sizeof(recv_buf), MSG_DONTWAIT) > 0) {
                        total_responses++;
                    }
                    
                    this_thread::sleep_for(microseconds(100));
                }
            });
        }
        
        // 等待測試完成
        this_thread::sleep_for(seconds(duration_sec));
        testing = false;
        
        for (auto& t : test_threads) {
            t.join();
        }
        
        auto duration = steady_clock::now() - start_time;
        auto ms = duration_cast<milliseconds>(duration).count();
        
        // 關閉連接
        for (int sock : sockets) {
            close(sock);
        }
        
        // 輸出結果
        cout << "\n=== 測試結果 ===" << endl;
        cout << "總請求數: " << total_requests << endl;
        cout << "總回應數: " << total_responses << endl;
        cout << "請求/秒: " << (total_requests * 1000) / ms << endl;
        cout << "回應/秒: " << (total_responses * 1000) / ms << endl;
    }
};

int main(int argc, char* argv[]) {
    // 忽略 SIGPIPE
    signal(SIGPIPE, SIG_IGN);
    
    if (argc < 2) {
        cout << "用法: " << argv[0] << " <模式>" << endl;
        cout << "模式:" << endl;
        cout << "  event    - 運行事件驅動伺服器" << endl;
        cout << "  thread   - 運行執行緒池伺服器 (錯誤示範)" << endl;
        cout << "  test     - 運行負載測試客戶端" << endl;
        return 1;
    }
    
    string mode = argv[1];
    
    try {
        if (mode == "event") {
            // 正確的事件驅動模型
            EventDrivenServer server(8080);
            
            // 處理 Ctrl+C
            signal(SIGINT, [](int) {
                cout << "\n正在關閉..." << endl;
                exit(0);
            });
            
            server.run();
            server.print_stats();
            
        } else if (mode == "thread") {
            // 錯誤的執行緒池模型 (示範用)
            cout << "警告: 這是一個錯誤示範！" << endl;
            ThreadPoolServer server(8081);
            server.run();
            
        } else if (mode == "test") {
            // 測試客戶端
            LoadTestClient::test_server("127.0.0.1", 8080, 100, 10);
            
        } else {
            cout << "未知模式: " << mode << endl;
            return 1;
        }
        
    } catch (const exception& e) {
        cerr << "錯誤: " << e.what() << endl;
        return 1;
    }
    
    return 0;
}