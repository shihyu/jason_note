.PHONY: help build debug clean

# 預設目標：顯示說明
.DEFAULT_GOAL := help

help:  ## 顯示此說明訊息
	@echo "可用目標："
	@echo "  make build   - 編譯程式（帶 debug symbols）"
	@echo "  make debug   - 啟動 GDB 調試"
	@echo "  make clean   - 清理建置產物"
	@echo ""
	@echo "使用範例："
	@echo "  make build"
	@echo "  make debug"

build:  ## 編譯程式（禁用優化和內聯）
	@echo "編譯 test.go..."
	go build -gcflags="all=-N -l" -o test test.go
	@echo "編譯完成: ./test"

debug:  ## 啟動 GDB 調試（自動設置斷點）
	@echo "啟動 GDB（自動設置斷點）..."
	@{ \
		echo "break main.main"; \
		echo "break runtime.makechan"; \
		echo "break runtime.newproc"; \
		echo "break runtime.chansend1"; \
		echo "break runtime.chanrecv1"; \
		echo "info breakpoints"; \
	} > /tmp/gdb_cmds_test_go.txt && \
	gdb -x /tmp/gdb_cmds_test_go.txt ./test; \
	rm -f /tmp/gdb_cmds_test_go.txt

clean:  ## 清理建置產物
	@echo "清理建置產物..."
	rm -f test
	@echo "清理完成"
