serve:
	@mdbook serve

build:
	@echo "清理不必要的檔案..."
	@find src -type d -name "target" -exec rm -rf {} + 2>/dev/null || true
	@find src -type d -name "checkpoints" -exec rm -rf {} + 2>/dev/null || true
	@find src -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@echo "開始建置..."
	@mdbook build 2>&1 | grep -v "search index is very large" || true

clean:
	rm -fr book

github:
	@ghp-import book -p -n
