-- ClickHouse 優化表設計 for Tick Data
-- 適用於處理幾百GB的金融交易數據

-- 1. 創建主要 tick 數據表（優化版）
CREATE TABLE IF NOT EXISTS tick_data_optimized (
    -- 時間戳使用 DateTime64 提供毫秒精度
    timestamp DateTime64(3) CODEC(DoubleDelta),

    -- 使用 LowCardinality 優化重複值多的字串
    symbol LowCardinality(String),
    exchange LowCardinality(String),

    -- 價格欄位使用適當精度（簡化編碼避免錯誤）
    price Decimal64(4),
    volume UInt64 CODEC(T64),

    -- 使用 Enum 固定選項
    side Enum8('buy' = 1, 'sell' = 2),

    -- 額外欄位
    bid_price Decimal64(4),
    ask_price Decimal64(4),
    bid_volume UInt32 CODEC(T64),
    ask_volume UInt32 CODEC(T64)

) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)  -- 按月分區
ORDER BY (symbol, timestamp)      -- 優化按symbol查詢
PRIMARY KEY (symbol, timestamp)
TTL toDateTime(timestamp) + INTERVAL 90 DAY   -- 90天後自動清理
SETTINGS
    index_granularity = 8192;

-- 2. 添加索引優化查詢性能
ALTER TABLE tick_data_optimized
    ADD INDEX idx_price price TYPE minmax GRANULARITY 4;

ALTER TABLE tick_data_optimized
    ADD INDEX idx_symbol symbol TYPE bloom_filter(0.01) GRANULARITY 1;

-- 3. 創建1分鐘K線物化視圖（預聚合）
CREATE MATERIALIZED VIEW IF NOT EXISTS tick_1min_mv
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(minute)
ORDER BY (symbol, minute)
AS SELECT
    symbol,
    toStartOfMinute(timestamp) as minute,
    argMinState(price, timestamp) as open,
    maxState(price) as high,
    minState(price) as low,
    argMaxState(price, timestamp) as close,
    sumState(toUInt64(volume)) as volume,
    countState() as tick_count
FROM tick_data_optimized
GROUP BY symbol, minute;

-- 4. 創建5分鐘K線物化視圖
CREATE MATERIALIZED VIEW IF NOT EXISTS tick_5min_mv
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(minute_5)
ORDER BY (symbol, minute_5)
AS SELECT
    symbol,
    toStartOfFiveMinutes(timestamp) as minute_5,
    argMinState(price, timestamp) as open,
    maxState(price) as high,
    minState(price) as low,
    argMaxState(price, timestamp) as close,
    sumState(toUInt64(volume)) as volume,
    countState() as tick_count
FROM tick_data_optimized
GROUP BY symbol, minute_5;

-- 5. 創建每日統計物化視圖
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_stats_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (symbol, date)
AS SELECT
    symbol,
    toDate(timestamp) as date,
    count() as trades_count,
    sum(volume) as total_volume,
    avg(price) as avg_price,
    max(price) as max_price,
    min(price) as min_price,
    stddevPop(toFloat64(price)) as price_stddev
FROM tick_data_optimized
GROUP BY symbol, date;

-- 6. 創建投影優化特定查詢
ALTER TABLE tick_data_optimized ADD PROJECTION symbol_daily_projection
(
    SELECT
        symbol,
        toDate(timestamp) as date,
        avg(price) as avg_price,
        sum(volume) as total_volume,
        count() as tick_count
    GROUP BY symbol, date
);

-- 7. 創建分散式表（如果使用集群）
-- CREATE TABLE tick_data_distributed AS tick_data_optimized
-- ENGINE = Distributed(cluster_name, currentDatabase(), tick_data_optimized, cityHash64(symbol));

-- 8. 創建採樣表（用於快速統計分析）
-- 註：採樣需要在 ORDER BY 中包含採樣表達式
-- CREATE TABLE IF NOT EXISTS tick_data_sample
-- ENGINE = MergeTree()
-- PARTITION BY toYYYYMM(timestamp)
-- ORDER BY (symbol, timestamp, intHash32(toUInt32(timestamp)))
-- SAMPLE BY intHash32(toUInt32(timestamp));

-- 9. 查詢示例

-- 獲取最新價格
-- SELECT symbol, max(timestamp) as latest, argMax(price, timestamp) as latest_price
-- FROM tick_data_optimized
-- WHERE timestamp >= now() - INTERVAL 1 MINUTE
-- GROUP BY symbol;

-- 獲取1分鐘K線
-- SELECT
--     symbol,
--     minute,
--     argMinMerge(open) as open,
--     maxMerge(high) as high,
--     minMerge(low) as low,
--     argMaxMerge(close) as close,
--     sumMerge(volume) as volume
-- FROM tick_1min_mv
-- WHERE symbol = 'AAPL' AND minute >= today()
-- GROUP BY symbol, minute
-- ORDER BY minute;

-- 10. 維護指令

-- 優化表（定期執行）
-- OPTIMIZE TABLE tick_data_optimized FINAL;

-- 更新投影
-- ALTER TABLE tick_data_optimized MATERIALIZE PROJECTION symbol_daily_projection;

-- 查看分區狀態
-- SELECT
--     partition,
--     count() as parts_count,
--     sum(rows) as total_rows,
--     formatReadableSize(sum(bytes_on_disk)) as disk_size
-- FROM system.parts
-- WHERE table = 'tick_data_optimized' AND active
-- GROUP BY partition
-- ORDER BY partition;