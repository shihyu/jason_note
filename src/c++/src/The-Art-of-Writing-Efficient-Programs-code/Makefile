# 完整的 Makefile for The Art of Writing Efficient Programs
# 編譯器設定
CXX = g++
CXXFLAGS = -g -O3 -std=c++17 -Wall -pthread
INCLUDES = -I.

# 輸出目錄
BINDIR = bin

# Chapter 02 目標檔案
CH02_TARGETS = \
	$(BINDIR)/ch02_01_substring_sort \
	$(BINDIR)/ch02_01a_substring_sort \
	$(BINDIR)/ch02_02_substring_sort \
	$(BINDIR)/ch02_03_substring_sort \
	$(BINDIR)/ch02_04_substring_sort \
	$(BINDIR)/ch02_05_compare_timer \
	$(BINDIR)/ch02_05a_compare_timer \
	$(BINDIR)/ch02_06_compare_timer \
	$(BINDIR)/ch02_07_compare_timer \
	$(BINDIR)/ch02_08_compare_timer \
	$(BINDIR)/ch02_09_compare_timer \
	$(BINDIR)/ch02_10_compare_mbm \
	$(BINDIR)/ch02_10a_compare_mbm \
	$(BINDIR)/ch02_11_compare_mbm \
	$(BINDIR)/ch02_clocks \
	$(BINDIR)/ch02_example

# Chapter 03 目標檔案
CH03_TARGETS = \
	$(BINDIR)/ch03_01_superscalar \
	$(BINDIR)/ch03_02_branch

# Chapter 04 目標檔案
CH04_TARGETS = \
	$(BINDIR)/ch04_01a_cache_random_read \
	$(BINDIR)/ch04_01b_cache_random_write \
	$(BINDIR)/ch04_01c_cache_sequential_read \
	$(BINDIR)/ch04_01d_cache_sequential_write \
	$(BINDIR)/ch04_01e_cache_sequential_readi \
	$(BINDIR)/ch04_01f_cache_sequential_writei \
	$(BINDIR)/ch04_01_superscalar \
	$(BINDIR)/ch04_02a_cache_random_read \
	$(BINDIR)/ch04_02b_cache_random_read \
	$(BINDIR)/ch04_03_list_vector

# Chapter 05 目標檔案
CH05_TARGETS = \
	$(BINDIR)/ch05_01a_cache_random_read \
	$(BINDIR)/ch05_01b_cache_random_write \
	$(BINDIR)/ch05_01c_cache_sequential_read \
	$(BINDIR)/ch05_01d_cache_sequential_write \
	$(BINDIR)/ch05_01e_cache_sequential_readi \
	$(BINDIR)/ch05_01f_cache_sequential_writei \
	$(BINDIR)/ch05_01_superscalar \
	$(BINDIR)/ch05_02_sharing_incr \
	$(BINDIR)/ch05_03_mutex_incr \
	$(BINDIR)/ch05_04_local_incr \
	$(BINDIR)/ch05_05_barrier_incr \
	$(BINDIR)/ch05_05a_barrier_load \
	$(BINDIR)/ch05_05b_barrier_store

# Chapter 06 目標檔案
CH06_TARGETS = \
	$(BINDIR)/ch06_01a_atomic_count \
	$(BINDIR)/ch06_01b_mutex_count \
	$(BINDIR)/ch06_01c_spinlock_count \
	$(BINDIR)/ch06_01d_ptrlock_count \
	$(BINDIR)/ch06_01e_cas_count \
	$(BINDIR)/ch06_01_sharing_incr_mbm \
	$(BINDIR)/ch06_02_atomic_index \
	$(BINDIR)/ch06_03a_raw_ptr_mbm \
	$(BINDIR)/ch06_03b_shared_ptr_mbm \
	$(BINDIR)/ch06_03_owning_ptr_mbm \
	$(BINDIR)/ch06_04a_shared_ptr_mbm \
	$(BINDIR)/ch06_04b_atomic_shared_ptr_mbm \
	$(BINDIR)/ch06_04_intr_shared_ptr_mbm

# Chapter 07 目標檔案
CH07_TARGETS = \
	$(BINDIR)/ch07_01a_shared_count \
	$(BINDIR)/ch07_01b_per_thread_count \
	$(BINDIR)/ch07_02a_cas_incr \
	$(BINDIR)/ch07_02b_stack_cas \
	$(BINDIR)/ch07_02_stack \
	$(BINDIR)/ch07_03a_atomic_pc_queue \
	$(BINDIR)/ch07_03b_noncst_queue \
	$(BINDIR)/ch07_03_queue

# Chapter 08 目標檔案 (需要 C++20)
CH08_TARGETS = \
	$(BINDIR)/ch08_parallel_algorithm

# Chapter 09 目標檔案（只包含可執行的程式）
CH09_TARGETS = \
	$(BINDIR)/ch09_01_vector_sort \
	$(BINDIR)/ch09_02_rvo \
	$(BINDIR)/ch09_02a_rvo \
	$(BINDIR)/ch09_02b_rvo \
	$(BINDIR)/ch09_02c_rvo \
	$(BINDIR)/ch09_02d_rvo \
	$(BINDIR)/ch09_02e_rvo \
	$(BINDIR)/ch09_03_factory \
	$(BINDIR)/ch09_04_buffer

# Chapter 10 目標檔案（只包含有 main 的檔案）
CH10_TARGETS = \
	$(BINDIR)/ch10_01_template \
	$(BINDIR)/ch10_02_measure \
	$(BINDIR)/ch10_03_restrict \
	$(BINDIR)/ch10_03a_restrict

# Chapter 11 目標檔案（只包含有 main 函數的檔案）
CH11_TARGETS = \
	$(BINDIR)/ch11_01_opt \
	$(BINDIR)/ch11_02_inf \
	$(BINDIR)/ch11_11_ubsan

# Chapter 12 目標檔案
CH12_TARGETS = \
	$(BINDIR)/ch12_01_deque \
	$(BINDIR)/ch12_02_index_tree

# 所有目標
ALL_TARGETS = $(CH02_TARGETS) $(CH03_TARGETS) $(CH04_TARGETS) $(CH05_TARGETS) \
              $(CH06_TARGETS) $(CH07_TARGETS) $(CH08_TARGETS) $(CH09_TARGETS) \
              $(CH10_TARGETS) $(CH11_TARGETS) $(CH12_TARGETS)

# 預設目標
all: $(BINDIR) chapter02 chapter03 chapter04 chapter05 chapter06 chapter07 \
     chapter08 chapter09 chapter10 chapter11 chapter12

# 各章節目標
chapter02: $(CH02_TARGETS)
chapter03: $(CH03_TARGETS)
chapter04: $(CH04_TARGETS)
chapter05: $(CH05_TARGETS)
chapter06: $(CH06_TARGETS)
chapter07: $(CH07_TARGETS)
chapter08: $(CH08_TARGETS)
chapter09: $(CH09_TARGETS)
chapter10: $(CH10_TARGETS)
chapter11: $(CH11_TARGETS)
chapter12: $(CH12_TARGETS)

# 建立輸出目錄
$(BINDIR):
	mkdir -p $(BINDIR)

# Chapter 02 編譯規則
$(BINDIR)/ch02_01_substring_sort: Chapter02/01_substring_sort.C Chapter02/01_substring_sort_a.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $^ -o $@

$(BINDIR)/ch02_01a_substring_sort: Chapter02/01a_substring_sort.C Chapter02/01a_substring_sort_a.C Chapter02/01a_substring_sort_b.C Chapter02/01a_substring_sort_c.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $^ -o $@

$(BINDIR)/ch02_02_substring_sort: Chapter02/02_substring_sort.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $< -o $@

$(BINDIR)/ch02_03_substring_sort: Chapter02/03_substring_sort.C Chapter02/03_substring_sort_a.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $^ -o $@

$(BINDIR)/ch02_04_substring_sort: Chapter02/04_substring_sort.C Chapter02/04_substring_sort_a.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $^ -o $@

# 一般的 Chapter 02 檔案（不需要 benchmark）
$(BINDIR)/ch02_05_compare_timer: Chapter02/05_compare_timer.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $< -o $@

$(BINDIR)/ch02_05a_compare_timer: Chapter02/05a_compare_timer.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $< -o $@

$(BINDIR)/ch02_06_compare_timer: Chapter02/06_compare_timer.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $< -o $@

$(BINDIR)/ch02_07_compare_timer: Chapter02/07_compare_timer.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $< -o $@

$(BINDIR)/ch02_08_compare_timer: Chapter02/08_compare_timer.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $< -o $@

$(BINDIR)/ch02_09_compare_timer: Chapter02/09_compare_timer.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $< -o $@

$(BINDIR)/ch02_clocks: Chapter02/clocks.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $< -o $@

$(BINDIR)/ch02_example: Chapter02/example.C Chapter02/compare.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $^ -o $@

# Chapter 02 需要 benchmark 的檔案
$(BINDIR)/ch02_10_compare_mbm: Chapter02/10_compare_mbm.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $< -lbenchmark -pthread -o $@

$(BINDIR)/ch02_10a_compare_mbm: Chapter02/10a_compare_mbm.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $< -lbenchmark -pthread -o $@

$(BINDIR)/ch02_11_compare_mbm: Chapter02/11_compare_mbm.C Chapter02/11_compare_mbm_a.C Chapter02/11_compare_mbm_b.C Chapter02/11_compare_mbm_c.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter02 $^ -lbenchmark -pthread -o $@

# Chapter 03 編譯規則 (需要 Google Benchmark)
$(BINDIR)/ch03_01_superscalar: Chapter03/01_superscalar.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) $< -lbenchmark -pthread -o $@

$(BINDIR)/ch03_02_branch: Chapter03/02_branch.C Chapter03/02_branch_func.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) $^ -lbenchmark -pthread -o $@

# Chapter 04 編譯規則 (需要 Google Benchmark)
$(BINDIR)/ch04_%: Chapter04/%.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) $< -lbenchmark -pthread -o $@

# Chapter 05 編譯規則 (需要 Google Benchmark)
$(BINDIR)/ch05_%: Chapter05/%.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) $< -lbenchmark -pthread -o $@

# Chapter 06 編譯規則 (需要 Google Benchmark)
$(BINDIR)/ch06_%: Chapter06/%.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter07 $< -lbenchmark -pthread -o $@

# Chapter 07 編譯規則 (需要 Google Benchmark)
$(BINDIR)/ch07_%: Chapter07/%.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) -I./Chapter07 $< -lbenchmark -pthread -o $@

# Chapter 08 編譯規則 (需要 C++20、TBB 和 Benchmark)
$(BINDIR)/ch08_parallel_algorithm: Chapter08/parallel_algorithm.C | $(BINDIR)
	$(CXX) -g -O3 -std=c++20 -Wall $< -ltbb -lbenchmark -pthread -o $@

# Chapter 09 編譯規則 (需要 Google Benchmark)
# 特殊情況：02a_rvo 需要 02a_rvo2.C
$(BINDIR)/ch09_02a_rvo: Chapter09/02a_rvo.C Chapter09/02a_rvo2.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) $^ -o $@

# 其他不需要 benchmark 的測試程式
$(BINDIR)/ch09_02_rvo $(BINDIR)/ch09_02c_rvo \
$(BINDIR)/ch09_02d_rvo $(BINDIR)/ch09_02e_rvo $(BINDIR)/ch09_03_factory: $(BINDIR)/ch09_%: Chapter09/%.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) $< -o $@

# 02b_rvo 預期會編譯失敗（展示禁用移動建構子的效果）
$(BINDIR)/ch09_02b_rvo: Chapter09/02b_rvo.C | $(BINDIR)
	-$(CXX) $(CXXFLAGS) $< -o $@ 2>/dev/null || echo "Note: ch09_02b_rvo expected to fail (demonstrates disabled move constructor)"

# 需要 benchmark 的程式
$(BINDIR)/ch09_01_vector_sort $(BINDIR)/ch09_04_buffer: $(BINDIR)/ch09_%: Chapter09/%.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) $< -lbenchmark -pthread -o $@

# Chapter 10 編譯規則 (需要 Google Benchmark)
$(BINDIR)/ch10_%: Chapter10/%.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) $< -lbenchmark -pthread -o $@

# Chapter 11 編譯規則
$(BINDIR)/ch11_%: Chapter11/%.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) $< -o $@

# Chapter 12 編譯規則 (需要 Google Benchmark)
$(BINDIR)/ch12_%: Chapter12/%.C | $(BINDIR)
	$(CXX) $(CXXFLAGS) $< -lbenchmark -pthread -o $@

# 清理編譯產生的檔案
clean:
	rm -rf $(BINDIR)
	rm -f *.o
	find . -name "*.o" -delete
	find . -name "*~" -delete

# 測試目標 - 編譯並執行簡單的測試
test: chapter02
	@echo "========== 測試 Chapter 02 範例 =========="
	@if [ -f $(BINDIR)/ch02_01_substring_sort ] && [ -s $(BINDIR)/ch02_01_substring_sort ]; then \
		echo "執行 ch02_01_substring_sort:"; \
		$(BINDIR)/ch02_01_substring_sort || true; \
	fi
	@echo "========== 測試完成 =========="

# 幫助訊息
help:
	@echo "使用方式："
	@echo "  make all              - 編譯所有章節的範例"
	@echo "  make chapter02        - 編譯 Chapter 02 所有範例"
	@echo "  make chapter03        - 編譯 Chapter 03 所有範例（需要 Google Benchmark）"
	@echo "  make chapter04        - 編譯 Chapter 04 所有範例（需要 Google Benchmark）"
	@echo "  make chapter05        - 編譯 Chapter 05 所有範例（需要 Google Benchmark）"
	@echo "  make chapter06        - 編譯 Chapter 06 所有範例（需要 Google Benchmark）"
	@echo "  make chapter07        - 編譯 Chapter 07 所有範例（需要 Google Benchmark）"
	@echo "  make chapter08        - 編譯 Chapter 08 所有範例（需要 C++20 和 TBB）"
	@echo "  make chapter09        - 編譯 Chapter 09 所有範例（需要 Google Benchmark）"
	@echo "  make chapter10        - 編譯 Chapter 10 所有範例（需要 Google Benchmark）"
	@echo "  make chapter11        - 編譯 Chapter 11 所有範例"
	@echo "  make chapter12        - 編譯 Chapter 12 所有範例（需要 Google Benchmark）"
	@echo "  make test             - 執行簡單測試"
	@echo "  make clean            - 清理所有編譯產生的檔案"
	@echo "  make help            - 顯示此幫助訊息"
	@echo ""
	@echo "注意事項："
	@echo "  - 部分範例需要 Google Benchmark 函式庫"
	@echo "  - Chapter 08 需要 C++20 支援和 TBB 函式庫"
	@echo "  - 編譯後的執行檔會放在 bin/ 目錄下"

.PHONY: all clean test help chapter02 chapter03 chapter04 chapter05 chapter06 chapter07 chapter08 chapter09 chapter10 chapter11 chapter12