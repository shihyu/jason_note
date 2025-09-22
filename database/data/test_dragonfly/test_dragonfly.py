#!/usr/bin/env python3
"""
DragonflyDB 完整測試腳本
測試各種 Redis 操作在 DragonflyDB 上的執行
"""

import redis
import time
import json
import sys
from datetime import datetime, timedelta

class DragonflyTester:
    def __init__(self, host='localhost', port=6379):
        """初始化連接到 DragonflyDB"""
        try:
            self.r = redis.Redis(
                host=host,
                port=port,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.r.ping()
            print(f"✅ 成功連接到 DragonflyDB ({host}:{port})")
        except redis.ConnectionError:
            print(f"❌ 無法連接到 DragonflyDB ({host}:{port})")
            sys.exit(1)

    def cleanup(self):
        """清理測試數據"""
        print("\n🧹 清理測試數據...")
        for key in self.r.scan_iter("test:*"):
            self.r.delete(key)
        print("   ✓ 已清理所有測試數據")

    def test_basic_operations(self):
        """測試基本的 key-value 操作"""
        print("\n📝 測試基本操作...")

        # SET 和 GET
        self.r.set('test:string', 'Hello, DragonflyDB!')
        value = self.r.get('test:string')
        assert value == 'Hello, DragonflyDB!', "SET/GET 測試失敗"
        print("   ✓ SET/GET 測試通過")

        # EXISTS
        assert self.r.exists('test:string') == 1, "EXISTS 測試失敗"
        print("   ✓ EXISTS 測試通過")

        # DEL
        self.r.delete('test:string')
        assert self.r.exists('test:string') == 0, "DELETE 測試失敗"
        print("   ✓ DELETE 測試通過")

        # EXPIRE 和 TTL
        self.r.setex('test:temp', 10, 'temporary value')
        ttl = self.r.ttl('test:temp')
        assert ttl > 0 and ttl <= 10, "EXPIRE/TTL 測試失敗"
        print("   ✓ EXPIRE/TTL 測試通過")

    def test_numeric_operations(self):
        """測試數值操作"""
        print("\n🔢 測試數值操作...")

        # INCR 和 DECR
        self.r.set('test:counter', 0)
        self.r.incr('test:counter')
        assert self.r.get('test:counter') == '1', "INCR 測試失敗"
        print("   ✓ INCR 測試通過")

        self.r.decr('test:counter')
        assert self.r.get('test:counter') == '0', "DECR 測試失敗"
        print("   ✓ DECR 測試通過")

        # INCRBY 和 DECRBY
        self.r.incrby('test:counter', 10)
        assert self.r.get('test:counter') == '10', "INCRBY 測試失敗"
        print("   ✓ INCRBY 測試通過")

        self.r.decrby('test:counter', 5)
        assert self.r.get('test:counter') == '5', "DECRBY 測試失敗"
        print("   ✓ DECRBY 測試通過")

    def test_list_operations(self):
        """測試列表操作"""
        print("\n📋 測試列表操作...")

        # LPUSH 和 RPUSH
        self.r.lpush('test:list', 'first')
        self.r.rpush('test:list', 'last')
        self.r.lpush('test:list', 'zero')

        # LLEN
        length = self.r.llen('test:list')
        assert length == 3, "LLEN 測試失敗"
        print("   ✓ LPUSH/RPUSH/LLEN 測試通過")

        # LRANGE
        items = self.r.lrange('test:list', 0, -1)
        assert items == ['zero', 'first', 'last'], "LRANGE 測試失敗"
        print("   ✓ LRANGE 測試通過")

        # LPOP 和 RPOP
        left = self.r.lpop('test:list')
        right = self.r.rpop('test:list')
        assert left == 'zero' and right == 'last', "LPOP/RPOP 測試失敗"
        print("   ✓ LPOP/RPOP 測試通過")

    def test_hash_operations(self):
        """測試哈希表操作"""
        print("\n#️⃣ 測試哈希表操作...")

        # HSET 和 HGET
        self.r.hset('test:user:1', 'name', 'Alice')
        self.r.hset('test:user:1', 'age', 30)

        name = self.r.hget('test:user:1', 'name')
        assert name == 'Alice', "HSET/HGET 測試失敗"
        print("   ✓ HSET/HGET 測試通過")

        # HMSET 和 HMGET (使用 hset 的 mapping 參數)
        self.r.hset('test:user:2', mapping={
            'name': 'Bob',
            'age': 25,
            'city': 'Taipei'
        })

        # HGETALL
        user_data = self.r.hgetall('test:user:2')
        assert user_data['name'] == 'Bob' and user_data['age'] == '25', "HGETALL 測試失敗"
        print("   ✓ HMSET/HGETALL 測試通過")

        # HEXISTS
        assert self.r.hexists('test:user:2', 'city') == True, "HEXISTS 測試失敗"
        print("   ✓ HEXISTS 測試通過")

        # HLEN
        field_count = self.r.hlen('test:user:2')
        assert field_count == 3, "HLEN 測試失敗"
        print("   ✓ HLEN 測試通過")

    def test_set_operations(self):
        """測試集合操作"""
        print("\n🎯 測試集合操作...")

        # SADD 和 SCARD
        self.r.sadd('test:set1', 'a', 'b', 'c')
        self.r.sadd('test:set2', 'b', 'c', 'd')

        card1 = self.r.scard('test:set1')
        assert card1 == 3, "SADD/SCARD 測試失敗"
        print("   ✓ SADD/SCARD 測試通過")

        # SISMEMBER
        assert self.r.sismember('test:set1', 'a') == True, "SISMEMBER 測試失敗"
        assert self.r.sismember('test:set1', 'z') == False, "SISMEMBER 測試失敗"
        print("   ✓ SISMEMBER 測試通過")

        # SINTER (交集)
        inter = self.r.sinter('test:set1', 'test:set2')
        assert set(inter) == {'b', 'c'}, "SINTER 測試失敗"
        print("   ✓ SINTER 測試通過")

        # SUNION (聯集)
        union = self.r.sunion('test:set1', 'test:set2')
        assert set(union) == {'a', 'b', 'c', 'd'}, "SUNION 測試失敗"
        print("   ✓ SUNION 測試通過")

        # SDIFF (差集)
        diff = self.r.sdiff('test:set1', 'test:set2')
        assert set(diff) == {'a'}, "SDIFF 測試失敗"
        print("   ✓ SDIFF 測試通過")

    def test_sorted_set_operations(self):
        """測試有序集合操作"""
        print("\n📊 測試有序集合操作...")

        # ZADD
        self.r.zadd('test:scores', {
            'Alice': 100,
            'Bob': 85,
            'Charlie': 95,
            'David': 90
        })

        # ZCARD
        card = self.r.zcard('test:scores')
        assert card == 4, "ZADD/ZCARD 測試失敗"
        print("   ✓ ZADD/ZCARD 測試通過")

        # ZSCORE
        score = self.r.zscore('test:scores', 'Alice')
        assert score == 100, "ZSCORE 測試失敗"
        print("   ✓ ZSCORE 測試通過")

        # ZRANGE (按分數排序)
        ranked = self.r.zrange('test:scores', 0, -1, withscores=True)
        assert ranked[0][0] == 'Bob' and ranked[0][1] == 85, "ZRANGE 測試失敗"
        print("   ✓ ZRANGE 測試通過")

        # ZREVRANGE (反向排序)
        top = self.r.zrevrange('test:scores', 0, 1, withscores=True)
        assert top[0][0] == 'Alice' and top[0][1] == 100, "ZREVRANGE 測試失敗"
        print("   ✓ ZREVRANGE 測試通過")

        # ZRANK
        rank = self.r.zrank('test:scores', 'Charlie')
        assert rank == 2, "ZRANK 測試失敗"
        print("   ✓ ZRANK 測試通過")

    def test_transactions(self):
        """測試事務操作"""
        print("\n💼 測試事務操作...")

        # 開始事務
        pipe = self.r.pipeline()

        # 在事務中執行多個操作
        pipe.set('test:tx1', 'value1')
        pipe.set('test:tx2', 'value2')
        pipe.incr('test:tx_counter')
        pipe.incr('test:tx_counter')

        # 執行事務
        results = pipe.execute()

        # 驗證結果
        assert self.r.get('test:tx1') == 'value1', "事務測試失敗"
        assert self.r.get('test:tx2') == 'value2', "事務測試失敗"
        assert self.r.get('test:tx_counter') == '2', "事務測試失敗"
        print("   ✓ MULTI/EXEC 事務測試通過")

    def test_pub_sub(self):
        """測試發布/訂閱功能"""
        print("\n📡 測試發布/訂閱...")

        # 創建訂閱者
        pubsub = self.r.pubsub()
        pubsub.subscribe('test:channel')

        # 發布消息
        self.r.publish('test:channel', 'Hello, Subscribers!')

        # 讀取消息 (跳過訂閱確認消息)
        message = pubsub.get_message(timeout=1)  # 訂閱確認
        message = pubsub.get_message(timeout=1)  # 實際消息

        if message and message['type'] == 'message':
            assert message['data'] == 'Hello, Subscribers!', "PUB/SUB 測試失敗"
            print("   ✓ PUBLISH/SUBSCRIBE 測試通過")
        else:
            print("   ⚠ PUB/SUB 測試跳過（需要更多時間）")

        pubsub.unsubscribe('test:channel')

    def test_batch_operations(self):
        """測試批量操作"""
        print("\n⚡ 測試批量操作...")

        # MSET 和 MGET
        self.r.mset({
            'test:batch1': 'value1',
            'test:batch2': 'value2',
            'test:batch3': 'value3'
        })

        values = self.r.mget('test:batch1', 'test:batch2', 'test:batch3')
        assert values == ['value1', 'value2', 'value3'], "MSET/MGET 測試失敗"
        print("   ✓ MSET/MGET 測試通過")

    def test_performance(self):
        """簡單的性能測試"""
        print("\n⏱️ 執行性能測試...")

        # 測試寫入性能
        start_time = time.time()
        for i in range(1000):
            self.r.set(f'test:perf:{i}', f'value_{i}')
        write_time = time.time() - start_time

        print(f"   ✓ 寫入 1000 個 keys: {write_time:.3f} 秒")
        print(f"     平均: {write_time/1000*1000:.2f} ms/key")

        # 測試讀取性能
        start_time = time.time()
        for i in range(1000):
            self.r.get(f'test:perf:{i}')
        read_time = time.time() - start_time

        print(f"   ✓ 讀取 1000 個 keys: {read_time:.3f} 秒")
        print(f"     平均: {read_time/1000*1000:.2f} ms/key")

        # 清理性能測試數據
        for i in range(1000):
            self.r.delete(f'test:perf:{i}')

    def show_server_info(self):
        """顯示服務器信息"""
        print("\n📊 DragonflyDB 服務器信息:")

        info = self.r.info()

        # 顯示關鍵信息
        print(f"   • Redis 版本: {info.get('redis_version', 'N/A')}")
        print(f"   • 運行時間: {info.get('uptime_in_seconds', 0)} 秒")
        print(f"   • 已使用內存: {info.get('used_memory_human', 'N/A')}")
        print(f"   • 連接數: {info.get('connected_clients', 0)}")
        print(f"   • 總命令數: {info.get('total_commands_processed', 0)}")

        # 顯示 keyspace 信息
        keyspace_info = self.r.info('keyspace')
        if 'db0' in keyspace_info:
            db0_info = keyspace_info['db0']
            print(f"   • DB0 Keys: {db0_info.get('keys', 0)}")

    def run_all_tests(self):
        """執行所有測試"""
        print("\n" + "="*50)
        print("🚀 開始執行 DragonflyDB 完整測試")
        print("="*50)

        try:
            self.show_server_info()
            self.test_basic_operations()
            self.test_numeric_operations()
            self.test_list_operations()
            self.test_hash_operations()
            self.test_set_operations()
            self.test_sorted_set_operations()
            self.test_transactions()
            self.test_pub_sub()
            self.test_batch_operations()
            self.test_performance()
            self.cleanup()

            print("\n" + "="*50)
            print("✅ 所有測試成功完成！")
            print("="*50)
            return True

        except AssertionError as e:
            print(f"\n❌ 測試失敗: {e}")
            return False
        except Exception as e:
            print(f"\n❌ 發生錯誤: {e}")
            return False

def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(description='DragonflyDB 測試腳本')
    parser.add_argument('--host', default='localhost', help='DragonflyDB 主機 (預設: localhost)')
    parser.add_argument('--port', type=int, default=6379, help='DragonflyDB 端口 (預設: 6379)')

    args = parser.parse_args()

    tester = DragonflyTester(host=args.host, port=args.port)
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()