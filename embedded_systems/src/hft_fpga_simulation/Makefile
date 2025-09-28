# 簡潔的 HFT FPGA 模擬 Makefile

# Verilator 命令
VERILATOR = verilator

# 編譯器
CXX = g++
CXXFLAGS = -O2 -std=c++11

# 頂層模組
TOP = order_matcher

# 源檔案
VERILOG_SOURCES = order_matcher.v
CPP_SOURCES = tb_hft_simple.cpp

# 預設目標
all: run

# 編譯
verilate:
	@echo "=== Compiling HFT Order Matcher ==="
	$(VERILATOR) --cc --trace --exe --build \
		$(VERILOG_SOURCES) \
		$(CPP_SOURCES) \
		--top-module $(TOP) \
		-o hft_sim

# 運行
run: verilate
	@echo "=== Running HFT Simulation ==="
	./obj_dir/hft_sim
	@echo "=== Simulation Complete ==="
	@echo "=== VCD file: hft_sim.vcd ==="

# 查看波形
wave: run
	@echo "=== Opening waveform ==="
	gtkwave hft_sim.vcd &

# 清理
clean:
	rm -rf obj_dir *.vcd

# 幫助
help:
	@echo "HFT FPGA Simulation Makefile"
	@echo "Commands:"
	@echo "  make        - Compile and run"
	@echo "  make wave   - Run and view waveform"
	@echo "  make clean  - Clean all generated files"
	@echo "  make help   - Show this help"

.PHONY: all verilate run wave clean help