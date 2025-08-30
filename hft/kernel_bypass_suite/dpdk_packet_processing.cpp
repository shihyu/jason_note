/*
 * DPDK 封包處理範例程式
 * 展示 kernel bypass 技術的高效能網路封包處理
 */

#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_mbuf.h>
#include <rte_lcore.h>
#include <rte_cycles.h>
#include <signal.h>
#include <unistd.h>
#include <iostream>
#include <iomanip>
#include <chrono>
#include <atomic>

#define NUM_MBUFS 8191
#define MBUF_CACHE_SIZE 250
#define BURST_SIZE 32
#define RX_RING_SIZE 1024
#define TX_RING_SIZE 1024

static std::atomic<bool> force_quit(false);
static std::atomic<uint64_t> rx_packets(0);
static std::atomic<uint64_t> tx_packets(0);
static std::atomic<uint64_t> rx_bytes(0);

static void signal_handler(int signum) {
    if (signum == SIGINT || signum == SIGTERM) {
        std::cout << "\n\n訊號 " << signum << " 已接收，準備退出...\n";
        force_quit = true;
    }
}

// 初始化網路埠
static int port_init(uint16_t port, struct rte_mempool *mbuf_pool) {
    struct rte_eth_conf port_conf = {};
    const uint16_t rx_rings = 1, tx_rings = 1;
    uint16_t nb_rxd = RX_RING_SIZE;
    uint16_t nb_txd = TX_RING_SIZE;
    int retval;
    struct rte_eth_dev_info dev_info;
    struct rte_eth_txconf txconf;

    if (!rte_eth_dev_is_valid_port(port))
        return -1;

    retval = rte_eth_dev_info_get(port, &dev_info);
    if (retval != 0) {
        std::cerr << "錯誤：無法取得網路埠 " << port << " 的裝置資訊\n";
        return retval;
    }

    // 配置網路埠
    retval = rte_eth_dev_configure(port, rx_rings, tx_rings, &port_conf);
    if (retval != 0)
        return retval;

    retval = rte_eth_dev_adjust_nb_rx_tx_desc(port, &nb_rxd, &nb_txd);
    if (retval != 0)
        return retval;

    // 分配和設置 RX 佇列
    for (uint16_t q = 0; q < rx_rings; q++) {
        retval = rte_eth_rx_queue_setup(port, q, nb_rxd,
                rte_eth_dev_socket_id(port), NULL, mbuf_pool);
        if (retval < 0)
            return retval;
    }

    txconf = dev_info.default_txconf;
    txconf.offloads = port_conf.txmode.offloads;
    
    // 分配和設置 TX 佇列
    for (uint16_t q = 0; q < tx_rings; q++) {
        retval = rte_eth_tx_queue_setup(port, q, nb_txd,
                rte_eth_dev_socket_id(port), &txconf);
        if (retval < 0)
            return retval;
    }

    // 啟動網路埠
    retval = rte_eth_dev_start(port);
    if (retval < 0)
        return retval;

    // 顯示網路埠 MAC 地址
    struct rte_ether_addr addr;
    retval = rte_eth_macaddr_get(port, &addr);
    if (retval != 0)
        return retval;

    std::cout << "網路埠 " << port << " MAC 地址: "
              << std::hex << std::setfill('0') << std::setw(2);
    for (int i = 0; i < 6; i++) {
        std::cout << (int)addr.addr_bytes[i];
        if (i < 5) std::cout << ":";
    }
    std::cout << std::dec << "\n";

    // 啟用混雜模式
    retval = rte_eth_promiscuous_enable(port);
    if (retval != 0)
        return retval;

    return 0;
}

// 封包處理主迴圈
static int lcore_main(void *arg) {
    uint16_t port = *(uint16_t *)arg;
    
    std::cout << "核心 " << rte_lcore_id() << " 正在處理網路埠 " << port << " 的封包\n";
    
    struct rte_mbuf *bufs[BURST_SIZE];
    uint16_t nb_rx;
    auto last_stats_time = std::chrono::steady_clock::now();
    
    while (!force_quit) {
        // 接收封包
        nb_rx = rte_eth_rx_burst(port, 0, bufs, BURST_SIZE);
        
        if (nb_rx) {
            rx_packets += nb_rx;
            
            // 計算接收的位元組數
            for (uint16_t i = 0; i < nb_rx; i++) {
                rx_bytes += bufs[i]->pkt_len;
            }
            
            // 簡單的封包處理：回送封包（迴路測試）
            uint16_t nb_tx = rte_eth_tx_burst(port, 0, bufs, nb_rx);
            tx_packets += nb_tx;
            
            // 釋放未傳送的封包
            if (unlikely(nb_tx < nb_rx)) {
                for (uint16_t buf = nb_tx; buf < nb_rx; buf++)
                    rte_pktmbuf_free(bufs[buf]);
            }
        }
        
        // 每秒顯示統計資訊
        auto now = std::chrono::steady_clock::now();
        if (std::chrono::duration_cast<std::chrono::seconds>(now - last_stats_time).count() >= 1) {
            uint64_t rx_pps = rx_packets.exchange(0);
            uint64_t tx_pps = tx_packets.exchange(0);
            uint64_t rx_bps = rx_bytes.exchange(0);
            
            std::cout << "[統計] 接收: " << rx_pps << " pps, "
                      << rx_bps * 8 / 1000000 << " Mbps | "
                      << "傳送: " << tx_pps << " pps\n";
            
            last_stats_time = now;
        }
    }
    
    return 0;
}

int main(int argc, char *argv[]) {
    struct rte_mempool *mbuf_pool;
    uint16_t nb_ports;
    uint16_t portid = 0;
    
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // 初始化環境抽象層 (EAL)
    int ret = rte_eal_init(argc, argv);
    if (ret < 0) {
        std::cerr << "錯誤：無法初始化 EAL\n";
        return -1;
    }
    
    argc -= ret;
    argv += ret;
    
    nb_ports = rte_eth_dev_count_avail();
    std::cout << "發現 " << nb_ports << " 個可用的網路埠\n";
    
    if (nb_ports == 0) {
        std::cerr << "錯誤：沒有發現以太網路埠\n";
        return -1;
    }
    
    // 創建記憶體池來保存 mbufs
    mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS * nb_ports,
        MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE, rte_socket_id());
    
    if (mbuf_pool == NULL) {
        std::cerr << "錯誤：無法創建 mbuf 池\n";
        return -1;
    }
    
    // 初始化第一個網路埠
    if (port_init(portid, mbuf_pool) != 0) {
        std::cerr << "錯誤：無法初始化網路埠 " << portid << "\n";
        return -1;
    }
    
    std::cout << "\n=== DPDK 封包處理系統啟動 ===\n";
    std::cout << "使用 Ctrl+C 來停止程式\n";
    std::cout << "正在等待封包...\n\n";
    
    // 在主核心上運行封包處理
    lcore_main(&portid);
    
    // 清理
    std::cout << "\n正在關閉網路埠 " << portid << "...\n";
    rte_eth_dev_stop(portid);
    rte_eth_dev_close(portid);
    
    // 清理 EAL
    rte_eal_cleanup();
    
    std::cout << "DPDK 應用程式已退出\n";
    
    return 0;
}