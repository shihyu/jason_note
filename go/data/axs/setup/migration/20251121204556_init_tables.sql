-- +goose Up
CREATE TABLE partition_leader_locks (
    topic TEXT NOT NULL,
    partition INTEGER NOT NULL,
    commit_offset BIGINT NOT NULL,
    updated_msec BIGINT NOT NULL DEFAULT (extract(epoch from now()) * 1000)::BIGINT,
    updater_svc_id TEXT NOT NULL,
    leader_svc_id TEXT,
    lease_expired_msec BIGINT NOT NULL,
    fencing_token BIGINT NOT NULL,
    PRIMARY KEY (topic, partition)
);

CREATE TABLE accounts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    shard_id SMALLINT NOT NULL,
    created_msec BIGINT NOT NULL DEFAULT (extract(epoch from now()) * 1000)::BIGINT
);

CREATE INDEX idx_user ON accounts(user_id);

CREATE TABLE account_balances (
    account_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    shard_id SMALLINT NOT NULL,
    currency_code TEXT NOT NULL,
    available NUMERIC(36, 18) NOT NULL DEFAULT 0,
    frozen    NUMERIC(36, 18) NOT NULL DEFAULT 0,
    updated_msec BIGINT NOT NULL DEFAULT (extract(epoch from now()) * 1000)::BIGINT,
    PRIMARY KEY (account_id, shard_id, currency_code)
) PARTITION BY RANGE (shard_id);


-- -------------------------------------------------------
-- Retail Pools (Shared Infrastructure)
-- -------------------------------------------------------

-- Partition for Retail Group 1 (Shard IDs: 1~2)
CREATE TABLE balances_retail_group_1 PARTITION OF account_balances
    FOR VALUES FROM (1) TO (3); 

-- Partition for Retail Group 2 (Shard IDs: 3~4)
CREATE TABLE balances_retail_group_2 PARTITION OF account_balances
    FOR VALUES FROM (3) TO (5); 

-- Partition for Retail Group 3 (Shard IDs: 5)
CREATE TABLE balances_retail_group_3 PARTITION OF account_balances
    FOR VALUES FROM (5) TO (6);     

-- -------------------------------------------------------
-- Whale Pools (Isolated Infrastructure)
-- -------------------------------------------------------

-- Isolated Partition for Whale 1 (Shard ID: 6 ~ 7)
CREATE TABLE balances_whale_1 PARTITION OF account_balances
    FOR VALUES FROM (6) TO (8);

-- Isolated Partition for Whale 2 (Shard ID: 8 ~ 9)
CREATE TABLE balances_whale_2 PARTITION OF account_balances
    FOR VALUES FROM (8) TO (10);

-- Isolated Partition for Whale 3 (Shard ID: 10)
CREATE TABLE balances_whale_3 PARTITION OF account_balances
    FOR VALUES FROM (10) TO (11);

CREATE INDEX idx_user_currency ON account_balances(user_id, currency_code);

CREATE TABLE balance_change_logs (
    id BIGSERIAL,
    event_id TEXT NOT NULL,
    event_type_id BIGINT NOT NULL,
    idempotency_key TEXT NOT NULL,
    change_id BIGINT NOT NULL,
    status SMALLINT NOT NULL,
    reject_reason TEXT,
    account_id BIGINT NOT NULL,
    account_shard_id SMALLINT NOT NULL,
    user_id BIGINT NOT NULL,
    currency_code TEXT NOT NULL,
    currency_symbol TEXT NOT NULL,
    available_delta NUMERIC(36, 18) NOT NULL,
    frozen_delta NUMERIC(36, 18) NOT NULL,
    fallback_currency_code TEXT,
    fallback_currency_symbol TEXT,
    fallback_available_delta NUMERIC(36, 18),
    fallback_frozen_delta NUMERIC(36, 18),
    use_fallback BOOLEAN NOT NULL DEFAULT FALSE,
    source_svc_id BIGINT NOT NULL,
    related_order_id BIGINT NOT NULL,
    kafka_offset BIGINT,
    kafka_partition INTEGER,
    submitted_msec BIGINT NOT NULL,
    updated_msec BIGINT NOT NULL DEFAULT (extract(epoch from now()) * 1000)::BIGINT,
    insert_msec BIGINT NOT NULL DEFAULT (extract(epoch from now()) * 1000)::BIGINT,
    callback_status SMALLINT,
    ack_msec BIGINT NOT NULL DEFAULT 0,
    ack_status SMALLINT,
    PRIMARY KEY (id)
);


CREATE UNIQUE INDEX idx_idempotency_key_change_id ON balance_change_logs(idempotency_key, change_id);

-- +goose Down
DROP TABLE IF EXISTS account_balances;
DROP TABLE IF EXISTS balance_change_logs;