# ClickHouse Docker Makefile
# 使用方式: make [command]

.PHONY: help install up down restart status logs shell db backup restore clean reset test monitor docker-rmv

# 預設目標 - 顯示說明
help:
	@echo "ClickHouse Docker 管理指令："
	@echo ""
	@echo "  make install   - 安裝 Docker Compose"
	@echo "  make up        - 啟動 ClickHouse 服務"
	@echo "  make down      - 停止 ClickHouse 服務"
	@echo "  make restart   - 重啟 ClickHouse 服務"
	@echo "  make status    - 查看服務狀態"
	@echo "  make logs      - 查看服務日誌"
	@echo "  make shell     - 進入 ClickHouse CLI"
	@echo "  make db        - 建立資料庫和表"
	@echo "  make test      - 執行測試查詢"
	@echo "  make backup    - 執行備份"
	@echo "  make restore   - 還原備份"
	@echo "  make monitor   - 執行監控"
	@echo "  make docker-rmv - 移除 Docker volumes"
	@echo "  make clean     - 停止並清理所有資料（危險！）"
	@echo "  make reset     - 清理並重新部署（完全重置）"

# 安裝 Docker Compose
install:
	@echo "安裝 Docker Compose..."
	@if ! command -v docker-compose &> /dev/null; then \
		sudo curl -L "https://github.com/docker/compose/releases/download/v2.30.3/docker-compose-Linux-x86_64" -o /usr/local/bin/docker-compose && \
		sudo chmod +x /usr/local/bin/docker-compose && \
		echo "✅ Docker Compose 安裝成功"; \
	else \
		echo "Docker Compose 已安裝: $$(docker-compose --version)"; \
	fi

# 啟動服務
up:
	@echo "啟動 ClickHouse 服務..."
	@docker-compose up -d
	@echo "等待服務啟動..."
	@sleep 10
	@echo "✅ ClickHouse 服務已啟動"
	@make status

# 停止服務
down:
	@echo "停止 ClickHouse 服務..."
	@docker-compose down
	@echo "✅ 服務已停止"

# 重啟服務
restart:
	@echo "重啟 ClickHouse 服務..."
	@docker-compose restart
	@sleep 10
	@echo "✅ 服務已重啟"
	@make status

# 查看狀態
status:
	@echo "=== ClickHouse 服務狀態 ==="
	@docker-compose ps
	@echo ""
	@docker exec clickhouse-server clickhouse-client --query "SELECT 'ClickHouse 運行正常!'" 2>/dev/null || echo "⚠️  ClickHouse 未運行"

# 查看日誌
logs:
	@docker-compose logs --tail=50 -f

# 進入 ClickHouse CLI
shell:
	@docker exec -it clickhouse-server clickhouse-client --user trader --password SecurePass123!

# 建立資料庫和表
db:
	@echo "建立資料庫和表..."
	@docker exec clickhouse-server clickhouse-client --user trader --password SecurePass123! --multiquery --query "\
		CREATE DATABASE IF NOT EXISTS market_data; \
		USE market_data; \
		CREATE TABLE IF NOT EXISTS market_ticks ( \
			ts DateTime64(3), \
			symbol String, \
			close Decimal32(2), \
			volume UInt32, \
			bid_price Decimal32(2), \
			bid_volume UInt32, \
			ask_price Decimal32(2), \
			ask_volume UInt32, \
			tick_type UInt8 \
		) ENGINE = MergeTree() \
		PARTITION BY toYYYYMM(ts) \
		ORDER BY (symbol, ts); \
		SELECT 'Database and table created successfully!';"

# 建立優化的表結構
db-optimized:
	@echo "建立優化的表結構..."
	@docker exec -i clickhouse-server clickhouse-client --user trader --password SecurePass123! \
		--database market_data < scripts/create_optimized_tables.sql
	@echo "✅ 優化表結構建立完成"

# 執行測試
test: db
	@echo "=== 執行測試查詢 ==="
	@if [ -f test_data.csv ]; then \
		echo "導入測試資料..."; \
		docker exec -i clickhouse-server clickhouse-client --user trader --password SecurePass123! \
			--database market_data --query "INSERT INTO market_ticks FORMAT CSVWithNames" < test_data.csv; \
	fi
	@docker exec clickhouse-server clickhouse-client --user trader --password SecurePass123! \
		--database market_data --query "\
		SELECT '資料筆數: ' || toString(count(*)) FROM market_ticks \
		UNION ALL \
		SELECT '股票數量: ' || toString(uniq(symbol)) FROM market_ticks \
		UNION ALL \
		SELECT '時間範圍: ' || toString(min(ts)) || ' 到 ' || toString(max(ts)) FROM market_ticks;"

# 備份
backup:
	@echo "執行備份..."
	@mkdir -p backup
	@DATE=$$(date +%Y%m%d_%H%M%S); \
	docker exec clickhouse-server tar czf /backups/backup_$$DATE.tar.gz \
		/var/lib/clickhouse/data \
		/var/lib/clickhouse/metadata 2>/dev/null && \
	docker cp clickhouse-server:/backups/backup_$$DATE.tar.gz ./backup/ && \
	echo "✅ 備份完成: backup/backup_$$DATE.tar.gz" && \
	ls -lah backup/ | tail -5

# 還原備份
restore:
	@echo "=== 可用備份 ==="
	@ls -la backup/*.tar.gz 2>/dev/null | nl || echo "沒有找到備份檔案"
	@echo ""
	@read -p "輸入要還原的備份檔名 (例如: backup_20250927_003738.tar.gz): " BACKUP_FILE; \
	if [ -f "backup/$$BACKUP_FILE" ]; then \
		echo "⚠️  警告: 這將覆蓋現有資料！"; \
		read -p "確定要還原嗎? (yes/no): " CONFIRM; \
		if [ "$$CONFIRM" = "yes" ]; then \
			docker-compose down && \
			sudo rm -rf data/* && \
			docker-compose up -d && \
			sleep 10 && \
			docker cp backup/$$BACKUP_FILE clickhouse-server:/tmp/ && \
			docker exec clickhouse-server tar xzf /tmp/$$BACKUP_FILE -C / && \
			docker-compose restart && \
			echo "✅ 還原完成"; \
		fi \
	else \
		echo "❌ 備份檔案不存在"; \
	fi

# 監控
monitor:
	@bash scripts/monitor.sh

# 移除 Docker volumes
docker-rmv:
	@echo "⚠️  警告: 這將移除所有 ClickHouse Docker volumes！"
	@read -p "確定要移除 volumes 嗎? (yes/no): " CONFIRM; \
	if [ "$$CONFIRM" = "yes" ]; then \
		echo "停止服務..."; \
		docker-compose down 2>/dev/null || true; \
		echo "移除 volumes..."; \
		docker-compose down -v 2>/dev/null || true; \
		docker volume prune -f 2>/dev/null || true; \
		echo "✅ Docker volumes 已移除"; \
	else \
		echo "取消操作"; \
	fi

# 清理所有資料（危險操作）
clean:
	@echo "⚠️  警告: 這將停止服務並刪除所有資料！"
	@read -p "確定要清理嗎? (yes/no): " CONFIRM; \
	if [ "$$CONFIRM" = "yes" ]; then \
		docker-compose down -v 2>/dev/null || true && \
		sudo rm -rf data/* logs/* && \
		rm -rf config/*.xml 2>/dev/null || true && \
		echo "✅ 清理完成（保留備份）"; \
	else \
		echo "取消清理"; \
	fi

# 完全重置（清理並重新部署）
reset:
	@echo "⚠️  警告: 這將完全重置 ClickHouse 環境！"
	@echo "將執行: 1.停止服務 2.清理資料 3.重新部署 4.建立資料庫"
	@read -p "確定要重置嗎? (yes/no): " CONFIRM; \
	if [ "$$CONFIRM" = "yes" ]; then \
		echo "步驟 1/4: 停止服務..."; \
		docker-compose down -v 2>/dev/null || true; \
		echo "步驟 2/4: 清理資料..."; \
		sudo rm -rf data/* logs/* config/*.xml 2>/dev/null || true; \
		echo "步驟 3/4: 重新啟動服務..."; \
		docker-compose up -d; \
		sleep 15; \
		echo "步驟 4/4: 建立資料庫..."; \
		$(MAKE) db; \
		echo "✅ 重置完成！"; \
		echo ""; \
		$(MAKE) status; \
	else \
		echo "取消重置"; \
	fi

# 快速開始（一鍵安裝並啟動）
quick-start: install up db test
	@echo "✅ ClickHouse 已成功安裝並啟動！"
	@echo "連接資訊: user=trader password=SecurePass123!"
	@echo "使用 'make shell' 進入 CLI"