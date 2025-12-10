DELETE FROM balance_change_logs;
DELETE FROM accounts;
DELETE FROM account_balances;
DELETE FROM partition_leader_locks;


SELECT batch_insert_account_balances(1, 300, 1, ARRAY['USDT', 'BTC', 'ETH', 'SOL', 'BNB'], 1000);
SELECT batch_insert_account_balances(301, 600, 2, ARRAY['USDT', 'BTC', 'ETH', 'SOL', 'BNB'], 1000);


INSERT INTO accounts
(id, user_id, shard_id, created_msec)
VALUES(1000, 1000, 1, 1764148212170);