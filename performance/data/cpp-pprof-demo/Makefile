# 編譯器與設定
CXX = g++
CXXFLAGS = -O2 -g
LDFLAGS = -lprofiler

# 編譯器與設定
CXX = g++
CXXFLAGS = -O2 -g
LDFLAGS = -lprofiler
PROFILER_LIB = /lib/x86_64-linux-gnu/libprofiler.so

# 檔案定義
PPROF = /home/shihyu/go-workspace/bin/pprof
TARGET = app
SRC = main.cpp
PROF_FILE = tests/cpu.prof
PDF_FILE = tests/report.pdf

.DEFAULT_GOAL := help

.PHONY: help
help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build       - 編譯專案"
	@echo "  make run         - 執行程式並產生分析檔案 ($(PROF_FILE))"
	@echo "  make profile-web - 啟動 pprof Web UI 進行互動式分析"
	@echo "  make profile-pdf - 產生 PDF 格式的視覺化圖表 ($(PDF_FILE))"
	@echo "  make clean       - 清理編譯產物與暫存檔"

.PHONY: build
build:  ## 編譯專案
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET) $(LDFLAGS)

.PHONY: run
run: build  ## 執行並產生 profile
	@echo "執行程式中，這可能需要幾秒鐘..."
	LD_PRELOAD=$(PROFILER_LIB) CPUPROFILE=$(PROF_FILE) ./$(TARGET)
	@echo "分析數據已存至 $(PROF_FILE)"

.PHONY: profile-web
profile-web:  ## 啟動 Web UI (需要安裝 graphviz)
	$(PPROF) --http=0.0.0.0:8080 ./$(TARGET) $(PROF_FILE)

.PHONY: profile-pdf
profile-pdf:  ## 產生 PDF (需要安裝 graphviz)
	$(PPROF) --pdf ./$(TARGET) $(PROF_FILE) > $(PDF_FILE)
	@echo "PDF 報告已產生: $(PDF_FILE)"

.PHONY: clean
clean:  ## 清理環境
	rm -f $(TARGET)
	rm -rf tests/*.prof tests/*.pdf
