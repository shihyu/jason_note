// tb_counter.cpp - Verilator 測試平台
#include <verilated.h>
#include <verilated_vcd_c.h>
#include "Vcounter.h"
#include <iostream>

int main(int argc, char** argv) {
    // 初始化 Verilator
    Verilated::commandArgs(argc, argv);

    // 創建 DUT (Design Under Test)
    Vcounter* dut = new Vcounter;

    // 設置波形追蹤
    Verilated::traceEverOn(true);
    VerilatedVcdC* tfp = new VerilatedVcdC;
    dut->trace(tfp, 99);
    tfp->open("counter.vcd");

    // 初始化信號
    dut->clk = 0;
    dut->rst = 1;

    // 模擬時間
    vluint64_t sim_time = 0;

    // 運行模擬
    while (sim_time < 100) {
        // 時鐘切換
        dut->clk = !dut->clk;

        // 在時間 10 釋放 reset
        if (sim_time == 10) {
            dut->rst = 0;
        }

        // 評估模型
        dut->eval();

        // 記錄波形
        tfp->dump(sim_time);

        // 顯示輸出（僅在時鐘正緣且非 reset 時）
        if (dut->clk && !dut->rst) {
            std::cout << "Time: " << sim_time
                      << " Count: " << (int)dut->count << std::endl;
        }

        sim_time++;
    }

    // 關閉波形檔案
    tfp->close();

    // 清理記憶體
    delete tfp;
    delete dut;

    std::cout << "Simulation completed!" << std::endl;

    return 0;
}