serve:
	@mdbook serve

build:
	@echo "清理不必要的檔案..."
	@find src -type d -name "target" -exec rm -rf {} + 2>/dev/null || true
	@find src -type d -name "checkpoints" -exec rm -rf {} + 2>/dev/null || true
	@find src -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@echo "開始建置..."
	@mdbook build 2>&1 | grep -v "search index is very large" || true
	@echo "套用中文搜尋支援..."
	@cp theme/searcher.js book/searcher.js 2>/dev/null || true
	@echo "清理 book 目錄中的大型檔案..."
	@find book -type d -name "data" -exec rm -rf {} + 2>/dev/null || true
	@find book -type f \( -name "*.tar.bz2" -o -name "*.tar.gz" -o -name "*.zip" -o -name "*.deb" -o -name "*.pdf" -o -name "*.pptx" \) -delete 2>/dev/null || true
	@find book -type f -size +20M -delete 2>/dev/null || true
	@echo "建置完成，已清理大型檔案"

clean:
	rm -fr book

github:
	@ghp-import book -p -n
