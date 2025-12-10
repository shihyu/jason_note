-- +goose Up
-- +goose StatementBegin
CREATE OR REPLACE FUNCTION batch_insert_account_balances(
    start_uid BIGINT,
    record_count BIGINT,
    shard_id BIGINT,
    currency_codes TEXT[],
    default_amount NUMERIC
)
RETURNS VOID AS $$
DECLARE
    current_msec BIGINT := (extract(epoch from now()) * 1000)::BIGINT;
    end_uid BIGINT := start_uid + record_count - 1;
    -- 由於需要多次使用，將生成序列定義為 CTE 或子查詢，但為了簡潔，在每個 INSERT 中重複使用 generate_series
BEGIN
    
    -- 1. 插入 accounts 記錄
    INSERT INTO accounts (
        id,
        user_id,
        shard_id,
        created_msec
    )
    SELECT
        gs AS id,            
        gs AS user_id,
        shard_id AS shard_id,
        current_msec AS created_msec
    FROM generate_series(start_uid, end_uid) AS gs;


    -- 2. 插入 account_balances 記錄 (模擬餘額加值)
    INSERT INTO account_balances (
        account_id,
        user_id,
        currency_code,
        available,
        frozen,
        shard_id,
        updated_msec
    )
    SELECT
        gs AS account_id,     
        gs AS user_id,
        cc AS currency_code,
        default_amount AS available,
        0 AS frozen,
        shard_id AS shard_id,
        current_msec AS updated_msec
    FROM generate_series(start_uid, end_uid) AS gs
    CROSS JOIN unnest(currency_codes) AS cc;
    
    
    -- 3. 🌟 插入對應的 balance_change_logs 記錄 (模擬初始加值日誌) 🌟
    INSERT INTO balance_change_logs (
        event_id,
        event_type_id,
        idempotency_key,
        change_id,
        status,
        reject_reason,
        account_id,
        account_shard_id,
        user_id,
        currency_code,
        currency_symbol,
        available_delta,
        frozen_delta,
        source_svc_id,
        related_order_id,
        kafka_offset,
        kafka_partition,
        submitted_msec,
        updated_msec,
        insert_msec,
        callback_status,
        ack_msec,
        ack_status
    )
    SELECT
        -- 核心 ID 和 Key (使用 account_id/currency_code/random 生成，確保唯一性)
        md5(gs::text || cc) AS event_id,         -- 使用 account_id 和 currency_code 組合 ID
        1 AS event_type_id,                      -- 假設 event_type_id=1 代表「初始加值」
        md5(gs::text || cc || random()::text) AS idempotency_key,

        floor(random() * 1000000000)::BIGINT AS change_id,
        
        -- 狀態
        1::SMALLINT AS status,                   -- 假設 1 代表成功 (SUCCESS)
        NULL AS reject_reason,

        -- 關聯 ID
        gs AS account_id,
        shard_id as account_shard_id,
        gs AS user_id,

        -- 餘額細節
        cc AS currency_code,
        cc AS currency_symbol,  -- 根據 currency_code 設置 symbol
        default_amount AS amount_delta,          -- 變動金額等於初始金額 (加值)
        0::NUMERIC(36,18) AS frozen_delta,

        -- 來源 / 訂單
        100::BIGINT AS source_svc_id,            -- 假設 100 代表「初始化服務」
        0 AS related_order_id,

        -- Kafka 資訊 (使用隨機值，如您原來的參考函數)
        -1::BIGINT AS kafka_offset,
        -1::INT AS kafka_partition,

        -- 時間戳
        current_msec AS submitted_msec,
        current_msec AS updated_msec,
        current_msec AS insert_msec,

        -- Callback / ACK (使用預設或隨機值)
        1::SMALLINT AS callback_status,
        current_msec AS ack_msec,
        1::SMALLINT AS ack_status

    FROM generate_series(start_uid, end_uid) AS gs
    CROSS JOIN unnest(currency_codes) AS cc;

END;
$$ LANGUAGE plpgsql;
-- +goose StatementEnd


-- +goose StatementBegin
CREATE OR REPLACE FUNCTION rand_insert_balance_change_logs(n BIGINT, s SMALLINT DEFAULT NULL)
RETURNS VOID AS $$
BEGIN
    INSERT INTO balance_change_logs (
        event_id,
        event_type_id,
        idempotency_key,
        change_id,
        status,
        reject_reason,
        account_id,
        user_id,
        currency_code,
        currency_symbol,
        amount_delta,
        source_svc_id,
        related_order_id,
        kafka_offset,
        kafka_partition,
        submitted_msec,
        updated_msec,
        insert_msec,
        callback_status,
        ack_msec,
        ack_status
    )
    SELECT
        -- event_id, idempotency_key
        md5(random()::text) AS event_id,
        floor(random() * 100)::BIGINT AS event_type_id,
        md5((random() * 999999)::text) AS idempotency_key,

        -- change_id
        floor(random() * 1000000000)::BIGINT AS change_id,

        -- status
        COALESCE(s, (floor(random() * 3))::SMALLINT)  AS status,  -- 0,1,2

        -- reject_reason
        CASE WHEN random() < 0.1 THEN 'random reject' ELSE NULL END,

        -- account_id, user_id
        floor(random() * 100000)::BIGINT AS account_id,
        floor(random() * 100000)::BIGINT AS user_id,

        -- currency_code, symbol
        (ARRAY['USDT','BTC','ETH','SOL'])[floor(random()*4)+1] AS currency_code,
        (ARRAY['$','₿','Ξ','◎'])[floor(random()*4)+1] AS currency_symbol,

        -- amount_delta
        (random() * 200 - 100)::NUMERIC(36,18) AS amount_delta,   -- -100 ~ +100

        -- source / order
        floor(random() * 50)::BIGINT AS source_svc_id,
        floor(random() * 99999999)::BIGINT AS related_order_id,

        -- kafka info
        floor(random() * 10000000)::BIGINT AS kafka_offset,
        floor(random() * 10)::INT AS kafka_partition,

        -- timestamps (msec)
        (extract(epoch FROM now()) * 1000)::BIGINT AS submitted_msec,
        (extract(epoch FROM now()) * 1000)::BIGINT AS updated_msec,
        (extract(epoch FROM now()) * 1000)::BIGINT AS insert_msec,

        -- callback_status, ack
        (floor(random() * 3))::SMALLINT AS callback_status,
        0::BIGINT AS ack_msec,
        (floor(random() * 2))::SMALLINT AS ack_status
    FROM generate_series(1, n);
END;
$$ LANGUAGE plpgsql;
-- +goose StatementEnd

-- +goose StatementBegin
CREATE OR REPLACE FUNCTION rand_insert_balance_change_logs(
    n BIGINT,
    idem_keys TEXT[],
    change_ids BIGINT[],
    account_ids BIGINT[],
    shard_ids SMALLINT[],
    user_ids BIGINT[],
    currency_codes TEXT[],
    currency_symbols TEXT[],
    available_deltas NUMERIC[],
    frozen_deltas NUMERIC[]
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO balance_change_logs (
        event_id,
        event_type_id,
        idempotency_key,
        change_id,
        status,
        reject_reason,
        account_id,
        account_shard_id,
        user_id,
        currency_code,
        currency_symbol,
        available_delta,
        frozen_delta,
        source_svc_id,
        related_order_id,
        kafka_offset,
        kafka_partition,
        submitted_msec,
        updated_msec,
        insert_msec,
        callback_status,
        ack_msec,
        ack_status
    )
    SELECT
        -- random event_id
        md5(random()::text) AS event_id,

        -- random type
        floor(random() * 100)::BIGINT AS event_type_id,

        -- ⬇️ externally provided fields
        idem_keys[i],
        change_ids[i],
        0::SMALLINT AS status,  -- default to init
        NULL AS reject_reason,
        account_ids[i],
        shard_ids[i],
        user_ids[i],
        currency_codes[i],
        currency_symbols[i],
        available_deltas[i],
        frozen_deltas[i],

        -- random service/order
        floor(random() * 50)::BIGINT AS source_svc_id,
        floor(random() * 99999999)::BIGINT AS related_order_id,

        -- kafka info
        floor(random() * 10000000)::BIGINT AS kafka_offset,
        floor(random() * 10)::INT AS kafka_partition,

        -- timestamps
        (extract(epoch FROM now()) * 1000)::BIGINT AS submitted_msec,
        (extract(epoch FROM now()) * 1000)::BIGINT AS updated_msec,
        (extract(epoch FROM now()) * 1000)::BIGINT AS insert_msec,

        -- callback info
        (floor(random() * 3))::SMALLINT AS callback_status,
        0::BIGINT AS ack_msec,
        (floor(random() * 2))::SMALLINT AS ack_status

    FROM generate_series(1, n) AS gs(i);
END;
$$ LANGUAGE plpgsql;
-- +goose StatementEnd

-- +goose Down
DROP FUNCTION batch_insert_account_balances(BIGINT, BIGINT, BIGINT, TEXT[], NUMERIC);
DROP FUNCTION rand_insert_balance_change_logs(BIGINT, SMALLINT);
