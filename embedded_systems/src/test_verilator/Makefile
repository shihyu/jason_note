# 簡單的 Verilator Makefile

# Verilator 命令
VERILATOR = verilator

# 編譯器
CXX = g++

# 頂層模組名稱
TOP = counter

# 源檔案
VERILOG_SOURCES = counter.v
CPP_SOURCES = tb_counter.cpp

# 預設目標
all: run

# 編譯 Verilog 並生成 C++ 檔案
verilate:
	@echo "=== Verilating $(TOP).v ==="
	$(VERILATOR) --cc --trace --exe --build \
		$(VERILOG_SOURCES) \
		$(CPP_SOURCES) \
		--top-module $(TOP) \
		-o sim

# 運行模擬
run: verilate
	@echo "=== Running simulation ==="
	./obj_dir/sim
	@echo "=== Simulation complete ==="
	@echo "=== Generated counter.vcd for waveform viewing ==="

# 查看波形
wave: run
	@echo "=== Opening waveform in GTKWave ==="
	gtkwave counter.vcd &

# 清理生成的檔案
clean:
	rm -rf obj_dir *.vcd

# 幫助資訊
help:
	@echo "Simple Verilator Makefile"
	@echo "Commands:"
	@echo "  make        - Compile and run simulation"
	@echo "  make run    - Same as make"
	@echo "  make wave   - Run simulation and view waveform"
	@echo "  make clean  - Clean all generated files"
	@echo "  make help   - Show this help message"

.PHONY: all verilate run wave clean help