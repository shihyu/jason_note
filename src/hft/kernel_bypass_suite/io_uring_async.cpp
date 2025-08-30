/*
 * io_uring 非同步 I/O 範例程式
 * 展示使用 Linux io_uring 進行高效能非同步檔案和網路 I/O
 */

#include <liburing.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <poll.h>

#include <iostream>
#include <vector>
#include <chrono>
#include <atomic>
#include <thread>
#include <iomanip>

#define QUEUE_DEPTH 256
#define IO_BLOCK_SIZE 4096  // 改名避免衝突
#define PORT 12345
#define MAX_CONNECTIONS 128
#define MAX_MESSAGE_LEN 2048

enum EventType {
    EVENT_TYPE_ACCEPT,
    EVENT_TYPE_READ,
    EVENT_TYPE_WRITE,
    EVENT_TYPE_FILE_READ,
    EVENT_TYPE_FILE_WRITE
};

struct IoRequest {
    EventType type;
    int fd;
    union {
        struct sockaddr_in client_addr;
        struct {
            char *buffer;
            size_t size;
            off_t offset;
        } io_data;
    };
};

class IoUringServer {
private:
    struct io_uring ring;
    int server_fd;
    std::atomic<bool> running;
    std::atomic<uint64_t> total_requests;
    std::atomic<uint64_t> completed_requests;
    std::atomic<uint64_t> bytes_transferred;
    
public:
    IoUringServer() : server_fd(-1), running(false), 
                      total_requests(0), completed_requests(0),
                      bytes_transferred(0) {}
    
    ~IoUringServer() {
        stop();
    }
    
    bool init(int port) {
        // 初始化 io_uring
        struct io_uring_params params;
        memset(&params, 0, sizeof(params));
        
        if (io_uring_queue_init_params(QUEUE_DEPTH, &ring, &params) < 0) {
            std::cerr << "錯誤：無法初始化 io_uring\n";
            return false;
        }
        
        std::cout << "io_uring 初始化成功\n";
        std::cout << "特性標誌: 0x" << std::hex << params.features << std::dec << "\n";
        
        // 檢查支援的功能
        if (params.features & IORING_FEAT_FAST_POLL) {
            std::cout << "  - 支援快速輪詢 (FAST_POLL)\n";
        }
        if (params.features & IORING_SETUP_SQPOLL) {
            std::cout << "  - 支援 SQ 輪詢執行緒 (SQPOLL)\n";
        }
        
        // 創建伺服器 socket
        server_fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);
        if (server_fd < 0) {
            std::cerr << "錯誤：無法創建 socket\n";
            return false;
        }
        
        // 設置 socket 選項
        int enable = 1;
        if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0) {
            std::cerr << "錯誤：無法設置 SO_REUSEADDR\n";
            return false;
        }
        
        // 綁定地址
        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_ANY);
        addr.sin_port = htons(port);
        
        if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
            std::cerr << "錯誤：無法綁定到埠口 " << port << "\n";
            return false;
        }
        
        // 開始監聽
        if (listen(server_fd, MAX_CONNECTIONS) < 0) {
            std::cerr << "錯誤：無法監聽 socket\n";
            return false;
        }
        
        std::cout << "伺服器正在監聽埠口 " << port << "\n";
        return true;
    }
    
    void add_accept_request() {
        struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
        if (!sqe) {
            std::cerr << "錯誤：無法取得 SQE\n";
            return;
        }
        
        IoRequest *req = new IoRequest;
        req->type = EVENT_TYPE_ACCEPT;
        req->fd = server_fd;
        
        io_uring_prep_accept(sqe, server_fd, 
                            (struct sockaddr*)&req->client_addr,
                            new socklen_t(sizeof(req->client_addr)), 0);
        io_uring_sqe_set_data(sqe, req);
        
        total_requests++;
    }
    
    void add_read_request(int client_fd) {
        struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
        if (!sqe) {
            std::cerr << "錯誤：無法取得 SQE\n";
            return;
        }
        
        IoRequest *req = new IoRequest;
        req->type = EVENT_TYPE_READ;
        req->fd = client_fd;
        req->io_data.buffer = new char[MAX_MESSAGE_LEN];
        req->io_data.size = MAX_MESSAGE_LEN;
        
        io_uring_prep_recv(sqe, client_fd, req->io_data.buffer, 
                          MAX_MESSAGE_LEN, 0);
        io_uring_sqe_set_data(sqe, req);
        
        total_requests++;
    }
    
    void add_write_request(int client_fd, const char *data, size_t len) {
        struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
        if (!sqe) {
            std::cerr << "錯誤：無法取得 SQE\n";
            return;
        }
        
        IoRequest *req = new IoRequest;
        req->type = EVENT_TYPE_WRITE;
        req->fd = client_fd;
        req->io_data.buffer = new char[len];
        memcpy(req->io_data.buffer, data, len);
        req->io_data.size = len;
        
        io_uring_prep_send(sqe, client_fd, req->io_data.buffer, len, 0);
        io_uring_sqe_set_data(sqe, req);
        
        total_requests++;
    }
    
    void add_file_read_request(const char *filename) {
        int fd = open(filename, O_RDONLY);
        if (fd < 0) {
            std::cerr << "錯誤：無法開啟檔案 " << filename << "\n";
            return;
        }
        
        struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
        if (!sqe) {
            close(fd);
            return;
        }
        
        IoRequest *req = new IoRequest;
        req->type = EVENT_TYPE_FILE_READ;
        req->fd = fd;
        req->io_data.buffer = new char[IO_BLOCK_SIZE];
        req->io_data.size = IO_BLOCK_SIZE;
        req->io_data.offset = 0;
        
        io_uring_prep_read(sqe, fd, req->io_data.buffer, IO_BLOCK_SIZE, 0);
        io_uring_sqe_set_data(sqe, req);
        
        total_requests++;
    }
    
    void handle_completion(struct io_uring_cqe *cqe) {
        IoRequest *req = (IoRequest*)io_uring_cqe_get_data(cqe);
        int res = cqe->res;
        
        completed_requests++;
        
        if (res < 0) {
            std::cerr << "請求錯誤: " << strerror(-res) << "\n";
        } else {
            switch (req->type) {
                case EVENT_TYPE_ACCEPT: {
                    if (res >= 0) {
                        std::cout << "新連線來自: " 
                                  << inet_ntoa(req->client_addr.sin_addr) 
                                  << ":" << ntohs(req->client_addr.sin_port) << "\n";
                        
                        // 為新連線添加讀取請求
                        add_read_request(res);
                        
                        // 繼續接受新連線
                        add_accept_request();
                    }
                    break;
                }
                
                case EVENT_TYPE_READ: {
                    if (res > 0) {
                        bytes_transferred += res;
                        req->io_data.buffer[res] = '\0';
                        std::cout << "接收 " << res << " 位元組: " 
                                  << req->io_data.buffer << "\n";
                        
                        // 回應客戶端
                        std::string response = "伺服器已收到: ";
                        response += req->io_data.buffer;
                        add_write_request(req->fd, response.c_str(), response.length());
                        
                        // 繼續讀取
                        add_read_request(req->fd);
                    } else if (res == 0) {
                        std::cout << "連線關閉\n";
                        close(req->fd);
                    }
                    break;
                }
                
                case EVENT_TYPE_WRITE: {
                    if (res > 0) {
                        bytes_transferred += res;
                        std::cout << "傳送 " << res << " 位元組\n";
                    }
                    break;
                }
                
                case EVENT_TYPE_FILE_READ: {
                    if (res > 0) {
                        bytes_transferred += res;
                        std::cout << "讀取檔案 " << res << " 位元組\n";
                    }
                    close(req->fd);
                    break;
                }
                
                case EVENT_TYPE_FILE_WRITE: {
                    if (res > 0) {
                        bytes_transferred += res;
                        std::cout << "寫入檔案 " << res << " 位元組\n";
                    }
                    close(req->fd);
                    break;
                }
            }
        }
        
        // 清理資源
        if (req->type == EVENT_TYPE_READ || req->type == EVENT_TYPE_WRITE ||
            req->type == EVENT_TYPE_FILE_READ || req->type == EVENT_TYPE_FILE_WRITE) {
            delete[] req->io_data.buffer;
        }
        delete req;
    }
    
    void run() {
        running = true;
        
        // 添加初始的 accept 請求
        add_accept_request();
        io_uring_submit(&ring);
        
        std::cout << "\nio_uring 伺服器執行中...\n";
        std::cout << "使用 Ctrl+C 停止\n\n";
        
        while (running) {
            struct io_uring_cqe *cqe;
            int ret;
            
            // 等待完成事件
            ret = io_uring_wait_cqe(&ring, &cqe);
            if (ret < 0) {
                if (errno == EINTR) continue;
                std::cerr << "錯誤：io_uring_wait_cqe: " << strerror(-ret) << "\n";
                break;
            }
            
            // 處理所有可用的完成事件
            struct io_uring_cqe *cqes[32];
            unsigned count = io_uring_peek_batch_cqe(&ring, cqes, 32);
            
            for (unsigned i = 0; i < count; i++) {
                handle_completion(cqes[i]);
                io_uring_cqe_seen(&ring, cqes[i]);
            }
            
            // 提交新的請求
            io_uring_submit(&ring);
        }
    }
    
    void stop() {
        running = false;
        if (server_fd >= 0) {
            close(server_fd);
            server_fd = -1;
        }
        io_uring_queue_exit(&ring);
    }
    
    void print_stats() {
        while (running) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
            
            uint64_t reqs = total_requests.exchange(0);
            uint64_t completed = completed_requests.exchange(0);
            uint64_t bytes = bytes_transferred.exchange(0);
            
            std::cout << "[io_uring 統計] "
                      << "請求: " << reqs << "/s, "
                      << "完成: " << completed << "/s, "
                      << "傳輸: " << bytes / 1024 << " KB/s\n";
        }
    }
};

static IoUringServer *g_server = nullptr;

static void signal_handler(int sig) {
    std::cout << "\n收到訊號 " << sig << "，正在關閉...\n";
    if (g_server) {
        g_server->stop();
    }
}

int main(int argc, char *argv[]) {
    int port = PORT;
    
    if (argc > 1) {
        port = atoi(argv[1]);
    }
    
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    std::cout << "=== io_uring 非同步 I/O 伺服器 ===\n";
    
    IoUringServer server;
    g_server = &server;
    
    if (!server.init(port)) {
        std::cerr << "錯誤：伺服器初始化失敗\n";
        return 1;
    }
    
    // 啟動統計執行緒
    std::thread stats_thread(&IoUringServer::print_stats, &server);
    
    // 執行主迴圈
    server.run();
    
    stats_thread.join();
    
    std::cout << "伺服器已關閉\n";
    return 0;
}