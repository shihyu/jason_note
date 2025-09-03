/*
 * AF_XDP Socket 範例程式
 * 展示使用 XDP (eXpress Data Path) 進行高效能封包處理
 */

#include <linux/bpf.h>
#include <linux/if_link.h>
#include <linux/if_xdp.h>
#include <linux/if_ether.h>
#include <net/if.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <xdp/xsk.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>

#include <iostream>
#include <cstring>
#include <thread>
#include <atomic>
#include <chrono>
#include <signal.h>
#include <unistd.h>
#include <poll.h>

#define NUM_FRAMES 4096
#define FRAME_SIZE XSK_UMEM__DEFAULT_FRAME_SIZE
#define BATCH_SIZE 64
#define INVALID_UMEM_FRAME UINT64_MAX

struct xsk_socket_info {
    struct xsk_ring_cons rx;
    struct xsk_ring_prod tx;
    struct xsk_ring_prod fq;
    struct xsk_ring_cons cq;
    struct xsk_socket *xsk;
    struct xsk_umem *umem;
    void *umem_area;
    uint64_t umem_frame_addr[NUM_FRAMES];
    uint32_t umem_frame_free;
    uint32_t outstanding_tx;
};

static std::atomic<bool> global_exit(false);
static std::atomic<uint64_t> rx_packets(0);
static std::atomic<uint64_t> tx_packets(0);
static std::atomic<uint64_t> rx_bytes(0);

static void signal_handler(int sig) {
    std::cout << "\n收到訊號 " << sig << "，準備退出...\n";
    global_exit = true;
}

static uint64_t xsk_alloc_umem_frame(struct xsk_socket_info *xsk) {
    uint64_t frame;
    if (xsk->umem_frame_free == 0)
        return INVALID_UMEM_FRAME;

    frame = xsk->umem_frame_addr[--xsk->umem_frame_free];
    xsk->umem_frame_addr[xsk->umem_frame_free] = INVALID_UMEM_FRAME;
    return frame;
}

static void xsk_free_umem_frame(struct xsk_socket_info *xsk, uint64_t frame) {
    xsk->umem_frame_addr[xsk->umem_frame_free++] = frame;
}

static uint64_t xsk_umem_free_frames(struct xsk_socket_info *xsk) {
    return xsk->umem_frame_free;
}

static struct xsk_socket_info *xsk_configure_socket(const char *ifname, uint32_t queue_id) {
    struct xsk_socket_info *xsk_info;
    struct xsk_socket_config xsk_cfg;
    struct xsk_umem_config umem_cfg;
    int ret;
    void *packet_buffer;
    uint64_t packet_buffer_size;

    xsk_info = (struct xsk_socket_info *)calloc(1, sizeof(*xsk_info));
    if (!xsk_info) {
        std::cerr << "錯誤：無法分配 xsk_info 記憶體\n";
        return nullptr;
    }

    // 分配 UMEM 區域
    packet_buffer_size = NUM_FRAMES * FRAME_SIZE;
    if (posix_memalign(&packet_buffer, getpagesize(), packet_buffer_size)) {
        std::cerr << "錯誤：無法分配封包緩衝區\n";
        free(xsk_info);
        return nullptr;
    }

    xsk_info->umem_area = packet_buffer;

    // 初始化 UMEM frame 表
    for (int i = 0; i < NUM_FRAMES; i++)
        xsk_info->umem_frame_addr[i] = i * FRAME_SIZE;

    xsk_info->umem_frame_free = NUM_FRAMES;

    // 配置 UMEM
    memset(&umem_cfg, 0, sizeof(umem_cfg));
    umem_cfg.fill_size = XSK_RING_PROD__DEFAULT_NUM_DESCS;
    umem_cfg.comp_size = XSK_RING_CONS__DEFAULT_NUM_DESCS;
    umem_cfg.frame_size = FRAME_SIZE;
    umem_cfg.frame_headroom = 0;
    umem_cfg.flags = 0;

    ret = xsk_umem__create(&xsk_info->umem, packet_buffer, packet_buffer_size,
                           &xsk_info->fq, &xsk_info->cq, &umem_cfg);
    if (ret) {
        std::cerr << "錯誤：無法創建 UMEM: " << strerror(-ret) << "\n";
        free(packet_buffer);
        free(xsk_info);
        return nullptr;
    }

    // 配置 AF_XDP socket
    memset(&xsk_cfg, 0, sizeof(xsk_cfg));
    xsk_cfg.rx_size = XSK_RING_CONS__DEFAULT_NUM_DESCS;
    xsk_cfg.tx_size = XSK_RING_PROD__DEFAULT_NUM_DESCS;
    xsk_cfg.xdp_flags = XDP_FLAGS_UPDATE_IF_NOEXIST;
    xsk_cfg.bind_flags = XDP_USE_NEED_WAKEUP;
    xsk_cfg.libbpf_flags = XSK_LIBBPF_FLAGS__INHIBIT_PROG_LOAD;

    ret = xsk_socket__create(&xsk_info->xsk, ifname, queue_id, xsk_info->umem,
                            &xsk_info->rx, &xsk_info->tx, &xsk_cfg);
    if (ret) {
        std::cerr << "錯誤：無法創建 XDP socket: " << strerror(-ret) << "\n";
        xsk_umem__delete(xsk_info->umem);
        free(packet_buffer);
        free(xsk_info);
        return nullptr;
    }

    return xsk_info;
}

static void rx_and_process(struct xsk_socket_info *xsk_info) {
    unsigned int rcvd, stock_frames, i;
    uint32_t idx_rx = 0, idx_fq = 0;
    int ret;

    rcvd = xsk_ring_cons__peek(&xsk_info->rx, BATCH_SIZE, &idx_rx);
    if (!rcvd) {
        if (xsk_ring_prod__needs_wakeup(&xsk_info->fq)) {
            struct pollfd fds[1];
            memset(fds, 0, sizeof(fds));
            fds[0].fd = xsk_socket__fd(xsk_info->xsk);
            fds[0].events = POLLIN;
            poll(fds, 1, 0);
        }
        return;
    }

    // 處理接收的封包
    stock_frames = xsk_prod_nb_free(&xsk_info->fq, xsk_umem_free_frames(xsk_info));
    if (stock_frames > 0) {
        ret = xsk_ring_prod__reserve(&xsk_info->fq, stock_frames, &idx_fq);
        while (ret != stock_frames)
            ret = xsk_ring_prod__reserve(&xsk_info->fq, rcvd, &idx_fq);

        for (i = 0; i < stock_frames; i++)
            *xsk_ring_prod__fill_addr(&xsk_info->fq, idx_fq++) =
                xsk_alloc_umem_frame(xsk_info);

        xsk_ring_prod__submit(&xsk_info->fq, stock_frames);
    }

    // 計算統計資訊
    for (i = 0; i < rcvd; i++) {
        uint64_t addr = xsk_ring_cons__rx_desc(&xsk_info->rx, idx_rx)->addr;
        uint32_t len = xsk_ring_cons__rx_desc(&xsk_info->rx, idx_rx++)->len;
        
        rx_packets++;
        rx_bytes += len;

        // 這裡可以處理封包內容
        char *pkt = (char *)xsk_umem__get_data(xsk_info->umem_area, addr);
        (void)pkt; // 避免未使用警告

        // 將封包重新加入到 free queue
        xsk_free_umem_frame(xsk_info, addr);
    }

    xsk_ring_cons__release(&xsk_info->rx, rcvd);
}

static void complete_tx(struct xsk_socket_info *xsk_info) {
    unsigned int completed;
    uint32_t idx_cq;

    if (!xsk_info->outstanding_tx)
        return;

    // 檢查 completion queue
    completed = xsk_ring_cons__peek(&xsk_info->cq, XSK_RING_CONS__DEFAULT_NUM_DESCS, &idx_cq);

    if (completed > 0) {
        for (unsigned int i = 0; i < completed; i++) {
            uint64_t addr = *xsk_ring_cons__comp_addr(&xsk_info->cq, idx_cq++);
            xsk_free_umem_frame(xsk_info, addr);
        }

        xsk_ring_cons__release(&xsk_info->cq, completed);
        xsk_info->outstanding_tx -= completed;
        tx_packets += completed;
    }
}

static void print_stats() {
    auto last_time = std::chrono::steady_clock::now();
    
    while (!global_exit) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        
        auto now = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::seconds>(now - last_time).count();
        
        if (duration >= 1) {
            uint64_t rx_pps = rx_packets.exchange(0);
            uint64_t tx_pps = tx_packets.exchange(0);
            uint64_t rx_bps = rx_bytes.exchange(0);
            
            std::cout << "[AF_XDP 統計] "
                      << "接收: " << rx_pps << " pps, "
                      << rx_bps * 8 / 1000000 << " Mbps | "
                      << "傳送: " << tx_pps << " pps\n";
            
            last_time = now;
        }
    }
}

int main(int argc, char **argv) {
    struct xsk_socket_info *xsk_socket;
    struct rlimit rlim = {RLIM_INFINITY, RLIM_INFINITY};
    const char *ifname = "eth0";
    uint32_t queue_id = 0;

    if (argc > 1)
        ifname = argv[1];
    if (argc > 2)
        queue_id = atoi(argv[2]);

    // 設置資源限制
    if (setrlimit(RLIMIT_MEMLOCK, &rlim)) {
        std::cerr << "錯誤：無法設置 rlimit，需要 root 權限\n";
        return 1;
    }

    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    std::cout << "=== AF_XDP Socket 範例程式 ===\n";
    std::cout << "網路介面: " << ifname << "\n";
    std::cout << "佇列 ID: " << queue_id << "\n";
    std::cout << "正在初始化 AF_XDP socket...\n";

    // 配置 XDP socket
    xsk_socket = xsk_configure_socket(ifname, queue_id);
    if (!xsk_socket) {
        std::cerr << "錯誤：無法配置 AF_XDP socket\n";
        return 1;
    }

    std::cout << "AF_XDP socket 已準備就緒\n";
    std::cout << "使用 Ctrl+C 停止程式\n\n";

    // 啟動統計執行緒
    std::thread stats_thread(print_stats);

    // 主處理迴圈
    while (!global_exit) {
        rx_and_process(xsk_socket);
        complete_tx(xsk_socket);
    }

    stats_thread.join();

    // 清理
    std::cout << "\n正在清理資源...\n";
    xsk_socket__delete(xsk_socket->xsk);
    xsk_umem__delete(xsk_socket->umem);
    free(xsk_socket->umem_area);
    free(xsk_socket);

    std::cout << "AF_XDP 程式已退出\n";
    return 0;
}