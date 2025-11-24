// 簡化的 HFT 系統測試平台
#include <verilated.h>
#include <verilated_vcd_c.h>
#include "Vorder_matcher.h"
#include <iostream>
#include <vector>
#include <random>
#include <chrono>

class SimpleHFTTest {
private:
    Vorder_matcher* dut;
    VerilatedVcdC* tfp;
    vluint64_t sim_time;
    std::mt19937 rng;

    // 統計資料
    uint32_t orders_sent = 0;
    uint32_t matches_received = 0;

public:
    SimpleHFTTest() : sim_time(0), rng(42) {  // 固定種子以利重現
        dut = new Vorder_matcher;

        // 設置波形追蹤
        Verilated::traceEverOn(true);
        tfp = new VerilatedVcdC;
        dut->trace(tfp, 99);
        tfp->open("hft_sim.vcd");

        // 初始化
        dut->clk = 0;
        dut->rst = 1;
        dut->order_valid = 0;
    }

    ~SimpleHFTTest() {
        tfp->close();
        delete tfp;
        delete dut;
    }

    void tick() {
        dut->clk = 0;
        dut->eval();
        tfp->dump(sim_time++);

        dut->clk = 1;
        dut->eval();
        tfp->dump(sim_time++);
    }

    void reset() {
        std::cout << "Resetting system..." << std::endl;
        dut->rst = 1;
        for (int i = 0; i < 5; i++) tick();
        dut->rst = 0;
        std::cout << "Reset complete" << std::endl;
    }

    void sendOrder(bool is_buy, uint32_t price, uint16_t qty, uint16_t id) {
        dut->order_valid = 1;
        dut->order_is_buy = is_buy;
        dut->order_price = price;
        dut->order_qty = qty;
        dut->order_id = id;

        tick();
        orders_sent++;

        dut->order_valid = 0;

        // 檢查是否有匹配
        if (dut->match_valid) {
            matches_received++;
            std::cout << "Match! Buy ID: " << dut->match_buy_id
                      << " Sell ID: " << dut->match_sell_id
                      << " Price: " << dut->match_price
                      << " Qty: " << dut->match_qty << std::endl;
        }
    }

    void runSimpleTest() {
        std::cout << "\n=== Simple HFT Order Matching Test ===" << std::endl;

        reset();

        // 測試案例 1: 基本買賣匹配
        std::cout << "\nTest 1: Basic matching" << std::endl;
        sendOrder(false, 100, 10, 1);  // 賣單: 價格100, 數量10
        tick(); tick();
        sendOrder(true, 100, 5, 2);    // 買單: 價格100, 數量5 (應該匹配)
        tick(); tick();

        // 測試案例 2: 價格不匹配
        std::cout << "\nTest 2: Price mismatch" << std::endl;
        sendOrder(false, 105, 10, 3);  // 賣單: 價格105
        tick(); tick();
        sendOrder(true, 103, 10, 4);   // 買單: 價格103 (不應該匹配)
        tick(); tick();

        // 測試案例 3: 批量訂單
        std::cout << "\nTest 3: Batch orders" << std::endl;
        std::uniform_int_distribution<> price_dist(95, 105);
        std::uniform_int_distribution<> qty_dist(1, 20);
        std::bernoulli_distribution buy_dist(0.5);

        for (int i = 5; i < 105; i++) {
            bool is_buy = buy_dist(rng);
            uint32_t price = price_dist(rng);
            uint16_t qty = qty_dist(rng);
            sendOrder(is_buy, price, qty, i);

            // 每10個訂單等待幾個週期
            if (i % 10 == 0) {
                for (int j = 0; j < 5; j++) tick();
            }
        }

        // 運行一段時間讓系統穩定
        std::cout << "\nLetting system settle..." << std::endl;
        for (int i = 0; i < 20; i++) tick();

        // 輸出統計
        printStats();
    }

    void printStats() {
        std::cout << "\n=== Simulation Statistics ===" << std::endl;
        std::cout << "Orders sent: " << orders_sent << std::endl;
        std::cout << "Matches received: " << matches_received << std::endl;
        std::cout << "Match rate: " << (100.0 * matches_received / orders_sent) << "%" << std::endl;
        std::cout << "Total orders (DUT): " << dut->total_orders << std::endl;
        std::cout << "Total matches (DUT): " << dut->total_matches << std::endl;
        std::cout << "Cycles executed: " << dut->cycle_counter << std::endl;

        // 估算性能（假設 200MHz FPGA）
        double fpga_freq = 200e6;  // Hz
        double fpga_time = dut->cycle_counter / fpga_freq;
        double throughput = dut->total_orders / fpga_time;

        std::cout << "\nEstimated FPGA Performance:" << std::endl;
        std::cout << "@ 200MHz clock frequency" << std::endl;
        std::cout << "Execution time: " << (fpga_time * 1e6) << " μs" << std::endl;
        std::cout << "Throughput: " << (throughput / 1e6) << " M orders/sec" << std::endl;

        if (dut->total_matches > 0) {
            double avg_latency = (double)dut->cycle_counter / dut->total_matches;
            std::cout << "Avg match latency: " << (avg_latency * 5) << " ns" << std::endl;
        }
    }
};

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);

    SimpleHFTTest test;
    test.runSimpleTest();

    std::cout << "\nSimulation completed successfully!" << std::endl;
    return 0;
}