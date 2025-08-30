/*
 * RDMA (Remote Direct Memory Access) 通訊範例程式
 * 展示使用 InfiniBand/RoCE 進行零拷貝網路通訊
 */

#include <infiniband/verbs.h>
#include <rdma/rdma_cma.h>
#include <rdma/rdma_verbs.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
#include <signal.h>

#include <iostream>
#include <cstring>
#include <thread>
#include <atomic>
#include <chrono>
#include <vector>
#include <iomanip>

#define BUFFER_SIZE 4096
#define MAX_WR 128
#define CQ_CAPACITY 128
#define DEFAULT_PORT "12345"
#define TIMEOUT_IN_MS 500

struct Connection {
    struct rdma_cm_id *id;
    struct ibv_qp *qp;
    struct ibv_mr *recv_mr;
    struct ibv_mr *send_mr;
    char *recv_buffer;
    char *send_buffer;
    uint64_t bytes_sent;
    uint64_t bytes_received;
};

class RDMANode {
protected:
    struct rdma_event_channel *ec;
    struct rdma_cm_id *listener;
    struct ibv_pd *pd;
    struct ibv_cq *cq;
    struct ibv_comp_channel *comp_channel;
    std::vector<Connection*> connections;
    std::atomic<bool> running;
    std::atomic<uint64_t> total_messages;
    std::atomic<uint64_t> total_bytes;
    
public:
    RDMANode() : ec(nullptr), listener(nullptr), pd(nullptr), 
                 cq(nullptr), comp_channel(nullptr), running(false),
                 total_messages(0), total_bytes(0) {}
    
    virtual ~RDMANode() {
        cleanup();
    }
    
protected:
    bool setup_connection(struct rdma_cm_id *id) {
        Connection *conn = new Connection;
        conn->id = id;
        conn->bytes_sent = 0;
        conn->bytes_received = 0;
        
        // 分配記憶體緩衝區
        conn->recv_buffer = new char[BUFFER_SIZE];
        conn->send_buffer = new char[BUFFER_SIZE];
        
        // 註冊記憶體區域
        conn->recv_mr = ibv_reg_mr(pd, conn->recv_buffer, BUFFER_SIZE,
                                   IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE);
        if (!conn->recv_mr) {
            std::cerr << "錯誤：無法註冊接收記憶體區域\n";
            delete conn;
            return false;
        }
        
        conn->send_mr = ibv_reg_mr(pd, conn->send_buffer, BUFFER_SIZE,
                                   IBV_ACCESS_LOCAL_WRITE);
        if (!conn->send_mr) {
            std::cerr << "錯誤：無法註冊傳送記憶體區域\n";
            ibv_dereg_mr(conn->recv_mr);
            delete conn;
            return false;
        }
        
        id->context = conn;
        connections.push_back(conn);
        
        // 建立 QP (Queue Pair)
        struct ibv_qp_init_attr qp_attr;
        memset(&qp_attr, 0, sizeof(qp_attr));
        qp_attr.send_cq = cq;
        qp_attr.recv_cq = cq;
        qp_attr.qp_type = IBV_QPT_RC;
        qp_attr.cap.max_send_wr = MAX_WR;
        qp_attr.cap.max_recv_wr = MAX_WR;
        qp_attr.cap.max_send_sge = 1;
        qp_attr.cap.max_recv_sge = 1;
        
        if (rdma_create_qp(id, pd, &qp_attr) != 0) {
            std::cerr << "錯誤：無法創建 QP\n";
            return false;
        }
        
        conn->qp = id->qp;
        
        // 發佈接收請求
        post_receive(conn);
        
        return true;
    }
    
    bool post_receive(Connection *conn) {
        struct ibv_recv_wr wr, *bad_wr = nullptr;
        struct ibv_sge sge;
        
        memset(&wr, 0, sizeof(wr));
        
        wr.wr_id = reinterpret_cast<uintptr_t>(conn);
        wr.sg_list = &sge;
        wr.num_sge = 1;
        
        sge.addr = reinterpret_cast<uintptr_t>(conn->recv_buffer);
        sge.length = BUFFER_SIZE;
        sge.lkey = conn->recv_mr->lkey;
        
        if (ibv_post_recv(conn->qp, &wr, &bad_wr) != 0) {
            std::cerr << "錯誤：無法發佈接收請求\n";
            return false;
        }
        
        return true;
    }
    
    bool post_send(Connection *conn, const char *data, size_t len) {
        struct ibv_send_wr wr, *bad_wr = nullptr;
        struct ibv_sge sge;
        
        if (len > BUFFER_SIZE) {
            std::cerr << "錯誤：資料太大\n";
            return false;
        }
        
        memcpy(conn->send_buffer, data, len);
        
        memset(&wr, 0, sizeof(wr));
        
        wr.wr_id = reinterpret_cast<uintptr_t>(conn);
        wr.opcode = IBV_WR_SEND;
        wr.sg_list = &sge;
        wr.num_sge = 1;
        wr.send_flags = IBV_SEND_SIGNALED;
        
        sge.addr = reinterpret_cast<uintptr_t>(conn->send_buffer);
        sge.length = len;
        sge.lkey = conn->send_mr->lkey;
        
        if (ibv_post_send(conn->qp, &wr, &bad_wr) != 0) {
            std::cerr << "錯誤：無法發佈傳送請求\n";
            return false;
        }
        
        conn->bytes_sent += len;
        total_bytes += len;
        total_messages++;
        
        return true;
    }
    
    void handle_completion() {
        struct ibv_wc wc[16];
        int ne;
        
        while (running) {
            ne = ibv_poll_cq(cq, 16, wc);
            
            if (ne < 0) {
                std::cerr << "錯誤：輪詢 CQ 失敗\n";
                break;
            }
            
            for (int i = 0; i < ne; i++) {
                Connection *conn = reinterpret_cast<Connection*>(wc[i].wr_id);
                
                if (wc[i].status != IBV_WC_SUCCESS) {
                    std::cerr << "工作完成錯誤: " << ibv_wc_status_str(wc[i].status) << "\n";
                    continue;
                }
                
                if (wc[i].opcode == IBV_WC_RECV) {
                    // 處理接收的資料
                    conn->bytes_received += wc[i].byte_len;
                    total_bytes += wc[i].byte_len;
                    total_messages++;
                    
                    conn->recv_buffer[wc[i].byte_len] = '\0';
                    std::cout << "接收 " << wc[i].byte_len << " 位元組: " 
                              << conn->recv_buffer << "\n";
                    
                    // 回應訊息
                    std::string response = "RDMA 伺服器已收到: ";
                    response += conn->recv_buffer;
                    post_send(conn, response.c_str(), response.length());
                    
                    // 發佈新的接收請求
                    post_receive(conn);
                } else if (wc[i].opcode == IBV_WC_SEND) {
                    std::cout << "傳送完成\n";
                }
            }
            
            if (ne == 0) {
                std::this_thread::sleep_for(std::chrono::microseconds(10));
            }
        }
    }
    
    void cleanup() {
        running = false;
        
        for (Connection *conn : connections) {
            if (conn->send_mr) ibv_dereg_mr(conn->send_mr);
            if (conn->recv_mr) ibv_dereg_mr(conn->recv_mr);
            if (conn->qp) rdma_destroy_qp(conn->id);
            if (conn->id) rdma_destroy_id(conn->id);
            delete[] conn->recv_buffer;
            delete[] conn->send_buffer;
            delete conn;
        }
        connections.clear();
        
        if (listener) rdma_destroy_id(listener);
        if (cq) ibv_destroy_cq(cq);
        if (comp_channel) ibv_destroy_comp_channel(comp_channel);
        if (pd) ibv_dealloc_pd(pd);
        if (ec) rdma_destroy_event_channel(ec);
    }
    
public:
    void print_stats() {
        while (running) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
            
            uint64_t msgs = total_messages.exchange(0);
            uint64_t bytes = total_bytes.exchange(0);
            
            std::cout << "[RDMA 統計] "
                      << "訊息: " << msgs << "/s, "
                      << "傳輸: " << bytes / 1024 << " KB/s, "
                      << "連線數: " << connections.size() << "\n";
        }
    }
};

class RDMAServer : public RDMANode {
public:
    bool init(const char *port) {
        struct sockaddr_in addr;
        
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_ANY);
        addr.sin_port = htons(atoi(port));
        
        // 創建事件通道
        ec = rdma_create_event_channel();
        if (!ec) {
            std::cerr << "錯誤：無法創建事件通道\n";
            return false;
        }
        
        // 創建監聽器
        if (rdma_create_id(ec, &listener, nullptr, RDMA_PS_TCP) != 0) {
            std::cerr << "錯誤：無法創建 RDMA ID\n";
            return false;
        }
        
        // 綁定地址
        if (rdma_bind_addr(listener, (struct sockaddr*)&addr) != 0) {
            std::cerr << "錯誤：無法綁定地址\n";
            return false;
        }
        
        // 開始監聽
        if (rdma_listen(listener, 10) != 0) {
            std::cerr << "錯誤：無法監聽\n";
            return false;
        }
        
        std::cout << "RDMA 伺服器正在監聽埠口 " << port << "\n";
        return true;
    }
    
    void run() {
        struct rdma_cm_event *event = nullptr;
        running = true;
        
        while (running) {
            if (rdma_get_cm_event(ec, &event) != 0) {
                if (errno == EINTR) continue;
                std::cerr << "錯誤：無法取得 CM 事件\n";
                break;
            }
            
            switch (event->event) {
                case RDMA_CM_EVENT_CONNECT_REQUEST: {
                    std::cout << "收到連線請求\n";
                    
                    // 第一次連線時建立 PD 和 CQ
                    if (!pd) {
                        pd = ibv_alloc_pd(event->id->verbs);
                        if (!pd) {
                            std::cerr << "錯誤：無法分配 PD\n";
                            break;
                        }
                        
                        comp_channel = ibv_create_comp_channel(event->id->verbs);
                        cq = ibv_create_cq(event->id->verbs, CQ_CAPACITY, 
                                          nullptr, comp_channel, 0);
                        if (!cq) {
                            std::cerr << "錯誤：無法創建 CQ\n";
                            break;
                        }
                        
                        // 啟動完成處理執行緒
                        std::thread([this]() { handle_completion(); }).detach();
                    }
                    
                    if (setup_connection(event->id)) {
                        struct rdma_conn_param cm_params;
                        memset(&cm_params, 0, sizeof(cm_params));
                        cm_params.initiator_depth = 1;
                        cm_params.responder_resources = 1;
                        
                        if (rdma_accept(event->id, &cm_params) == 0) {
                            std::cout << "連線已接受\n";
                        }
                    }
                    break;
                }
                
                case RDMA_CM_EVENT_ESTABLISHED: {
                    std::cout << "連線已建立\n";
                    break;
                }
                
                case RDMA_CM_EVENT_DISCONNECTED: {
                    std::cout << "連線已斷開\n";
                    break;
                }
                
                default:
                    std::cout << "未處理的事件: " << event->event << "\n";
                    break;
            }
            
            rdma_ack_cm_event(event);
        }
    }
};

class RDMAClient : public RDMANode {
private:
    struct rdma_cm_id *connection;
    
public:
    bool connect_to_server(const char *server, const char *port) {
        struct addrinfo *addr;
        
        if (getaddrinfo(server, port, nullptr, &addr) != 0) {
            std::cerr << "錯誤：無法解析地址\n";
            return false;
        }
        
        // 創建事件通道
        ec = rdma_create_event_channel();
        if (!ec) {
            std::cerr << "錯誤：無法創建事件通道\n";
            return false;
        }
        
        // 創建連線 ID
        if (rdma_create_id(ec, &connection, nullptr, RDMA_PS_TCP) != 0) {
            std::cerr << "錯誤：無法創建 RDMA ID\n";
            return false;
        }
        
        // 解析地址
        if (rdma_resolve_addr(connection, nullptr, addr->ai_addr, TIMEOUT_IN_MS) != 0) {
            std::cerr << "錯誤：無法解析地址\n";
            return false;
        }
        
        freeaddrinfo(addr);
        
        struct rdma_cm_event *event = nullptr;
        
        // 等待地址解析完成
        if (rdma_get_cm_event(ec, &event) != 0) {
            std::cerr << "錯誤：無法取得事件\n";
            return false;
        }
        
        if (event->event != RDMA_CM_EVENT_ADDR_RESOLVED) {
            std::cerr << "錯誤：地址解析失敗\n";
            rdma_ack_cm_event(event);
            return false;
        }
        
        rdma_ack_cm_event(event);
        
        // 解析路由
        if (rdma_resolve_route(connection, TIMEOUT_IN_MS) != 0) {
            std::cerr << "錯誤：無法解析路由\n";
            return false;
        }
        
        // 等待路由解析完成
        if (rdma_get_cm_event(ec, &event) != 0) {
            std::cerr << "錯誤：無法取得事件\n";
            return false;
        }
        
        if (event->event != RDMA_CM_EVENT_ROUTE_RESOLVED) {
            std::cerr << "錯誤：路由解析失敗\n";
            rdma_ack_cm_event(event);
            return false;
        }
        
        rdma_ack_cm_event(event);
        
        // 建立資源
        pd = ibv_alloc_pd(connection->verbs);
        if (!pd) {
            std::cerr << "錯誤：無法分配 PD\n";
            return false;
        }
        
        comp_channel = ibv_create_comp_channel(connection->verbs);
        cq = ibv_create_cq(connection->verbs, CQ_CAPACITY, nullptr, comp_channel, 0);
        if (!cq) {
            std::cerr << "錯誤：無法創建 CQ\n";
            return false;
        }
        
        if (!setup_connection(connection)) {
            return false;
        }
        
        // 連線到伺服器
        struct rdma_conn_param cm_params;
        memset(&cm_params, 0, sizeof(cm_params));
        cm_params.initiator_depth = 1;
        cm_params.responder_resources = 1;
        
        if (rdma_connect(connection, &cm_params) != 0) {
            std::cerr << "錯誤：無法連線\n";
            return false;
        }
        
        // 等待連線建立
        if (rdma_get_cm_event(ec, &event) != 0) {
            std::cerr << "錯誤：無法取得事件\n";
            return false;
        }
        
        if (event->event != RDMA_CM_EVENT_ESTABLISHED) {
            std::cerr << "錯誤：連線建立失敗\n";
            rdma_ack_cm_event(event);
            return false;
        }
        
        rdma_ack_cm_event(event);
        
        std::cout << "成功連線到 RDMA 伺服器\n";
        running = true;
        
        // 啟動完成處理執行緒
        std::thread([this]() { handle_completion(); }).detach();
        
        return true;
    }
    
    void send_message(const std::string &msg) {
        if (!connections.empty()) {
            post_send(connections[0], msg.c_str(), msg.length());
        }
    }
};

static std::atomic<bool> g_exit(false);

static void signal_handler(int sig) {
    std::cout << "\n收到訊號 " << sig << "，正在退出...\n";
    g_exit = true;
}

int main(int argc, char *argv[]) {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    std::cout << "=== RDMA 通訊範例程式 ===\n";
    
    if (argc < 2) {
        std::cout << "使用方法:\n";
        std::cout << "  伺服器模式: " << argv[0] << " server [port]\n";
        std::cout << "  客戶端模式: " << argv[0] << " client <server_ip> [port]\n";
        return 1;
    }
    
    std::string mode = argv[1];
    const char *port = argc > 3 ? argv[3] : DEFAULT_PORT;
    
    if (mode == "server") {
        RDMAServer server;
        
        if (!server.init(port)) {
            std::cerr << "錯誤：伺服器初始化失敗\n";
            return 1;
        }
        
        std::thread stats_thread(&RDMAServer::print_stats, &server);
        
        std::cout << "RDMA 伺服器執行中，使用 Ctrl+C 停止\n\n";
        server.run();
        
        stats_thread.join();
        
    } else if (mode == "client") {
        if (argc < 3) {
            std::cerr << "錯誤：請指定伺服器地址\n";
            return 1;
        }
        
        RDMAClient client;
        
        if (!client.connect_to_server(argv[2], port)) {
            std::cerr << "錯誤：無法連線到伺服器\n";
            return 1;
        }
        
        std::thread stats_thread(&RDMAClient::print_stats, &client);
        
        std::cout << "輸入訊息傳送到伺服器 (輸入 'quit' 退出):\n";
        
        std::string message;
        while (!g_exit && std::getline(std::cin, message)) {
            if (message == "quit") break;
            client.send_message(message);
        }
        
        g_exit = true;
        stats_thread.join();
        
    } else {
        std::cerr << "錯誤：未知模式 '" << mode << "'\n";
        return 1;
    }
    
    std::cout << "程式已退出\n";
    return 0;
}