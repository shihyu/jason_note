#!/usr/bin/env python3
"""
DragonflyDB 綜合測試套件
包含功能測試、性能測試、壓力測試
"""

import redis
import time
import json
import sys
import random
import string
import threading
import multiprocessing
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import statistics
import argparse
from typing import Dict, List, Any

class ColorOutput:
    """彩色輸出工具"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def success(msg): return f"{ColorOutput.OKGREEN}✅ {msg}{ColorOutput.ENDC}"
    @staticmethod
    def fail(msg): return f"{ColorOutput.FAIL}❌ {msg}{ColorOutput.ENDC}"
    @staticmethod
    def warning(msg): return f"{ColorOutput.WARNING}⚠️  {msg}{ColorOutput.ENDC}"
    @staticmethod
    def info(msg): return f"{ColorOutput.OKBLUE}ℹ️  {msg}{ColorOutput.ENDC}"
    @staticmethod
    def header(msg): return f"{ColorOutput.HEADER}{ColorOutput.BOLD}{msg}{ColorOutput.ENDC}"

class DragonflyTestSuite:
    """DragonflyDB 測試套件"""

    def __init__(self, host='localhost', port=6379, verbose=False):
        self.host = host
        self.port = port
        self.verbose = verbose
        self.client = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

    def connect(self) -> bool:
        """連接到 DragonflyDB"""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.client.ping()
            print(ColorOutput.success(f"連接成功 ({self.host}:{self.port})"))
            return True
        except Exception as e:
            print(ColorOutput.fail(f"連接失敗: {e}"))
            return False

    def cleanup_test_data(self):
        """清理測試數據"""
        patterns = ['test:*', 'bench:*', 'stress:*', 'perf:*']
        for pattern in patterns:
            for key in self.client.scan_iter(pattern):
                self.client.delete(key)

    def run_test(self, test_func, test_name):
        """執行單個測試"""
        try:
            if self.verbose:
                print(f"  執行: {test_name}")
            test_func()
            self.test_results['passed'] += 1
            print(ColorOutput.success(f"{test_name}"))
            return True
        except AssertionError as e:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {str(e)}")
            print(ColorOutput.fail(f"{test_name}: {str(e)}"))
            return False
        except Exception as e:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: Unexpected error - {str(e)}")
            print(ColorOutput.fail(f"{test_name}: 未預期錯誤 - {str(e)}"))
            return False

    # ========== 基本功能測試 ==========

    def test_string_operations(self):
        """字串操作測試"""
        print(ColorOutput.header("\n📝 字串操作測試"))

        # SET/GET
        def test_set_get():
            self.client.set('test:str', 'hello world')
            assert self.client.get('test:str') == 'hello world'
        self.run_test(test_set_get, "SET/GET")

        # MSET/MGET
        def test_mset_mget():
            self.client.mset({'test:m1': 'v1', 'test:m2': 'v2', 'test:m3': 'v3'})
            values = self.client.mget('test:m1', 'test:m2', 'test:m3')
            assert values == ['v1', 'v2', 'v3']
        self.run_test(test_mset_mget, "MSET/MGET")

        # APPEND
        def test_append():
            self.client.set('test:append', 'Hello')
            self.client.append('test:append', ' World')
            assert self.client.get('test:append') == 'Hello World'
        self.run_test(test_append, "APPEND")

        # GETRANGE
        def test_getrange():
            self.client.set('test:range', 'Hello World')
            assert self.client.getrange('test:range', 0, 4) == 'Hello'
        self.run_test(test_getrange, "GETRANGE")

    def test_numeric_operations(self):
        """數值操作測試"""
        print(ColorOutput.header("\n🔢 數值操作測試"))

        # INCR/DECR
        def test_incr_decr():
            self.client.set('test:counter', 10)
            self.client.incr('test:counter')
            assert self.client.get('test:counter') == '11'
            self.client.decr('test:counter')
            assert self.client.get('test:counter') == '10'
        self.run_test(test_incr_decr, "INCR/DECR")

        # INCRBYFLOAT
        def test_incrbyfloat():
            self.client.set('test:float', 10.5)
            self.client.incrbyfloat('test:float', 2.5)
            assert float(self.client.get('test:float')) == 13.0
        self.run_test(test_incrbyfloat, "INCRBYFLOAT")

    def test_list_operations(self):
        """列表操作測試"""
        print(ColorOutput.header("\n📋 列表操作測試"))

        # PUSH/POP
        def test_push_pop():
            self.client.lpush('test:list', 'a', 'b', 'c')
            assert self.client.lpop('test:list') == 'c'
            assert self.client.rpop('test:list') == 'a'
        self.run_test(test_push_pop, "LPUSH/LPOP/RPOP")

        # LINDEX/LSET
        def test_lindex_lset():
            self.client.rpush('test:list2', 'a', 'b', 'c')
            assert self.client.lindex('test:list2', 1) == 'b'
            self.client.lset('test:list2', 1, 'B')
            assert self.client.lindex('test:list2', 1) == 'B'
        self.run_test(test_lindex_lset, "LINDEX/LSET")

        # LTRIM
        def test_ltrim():
            self.client.rpush('test:list3', *range(10))
            self.client.ltrim('test:list3', 2, 5)
            assert self.client.llen('test:list3') == 4
        self.run_test(test_ltrim, "LTRIM")

    def test_hash_operations(self):
        """哈希操作測試"""
        print(ColorOutput.header("\n#️⃣  哈希操作測試"))

        # HSET/HGET
        def test_hset_hget():
            self.client.hset('test:hash', 'field1', 'value1')
            assert self.client.hget('test:hash', 'field1') == 'value1'
        self.run_test(test_hset_hget, "HSET/HGET")

        # HINCRBY
        def test_hincrby():
            self.client.hset('test:hash2', 'counter', 5)
            self.client.hincrby('test:hash2', 'counter', 3)
            assert self.client.hget('test:hash2', 'counter') == '8'
        self.run_test(test_hincrby, "HINCRBY")

        # HKEYS/HVALS
        def test_hkeys_hvals():
            self.client.hset('test:hash3', mapping={'a': '1', 'b': '2', 'c': '3'})
            keys = sorted(self.client.hkeys('test:hash3'))
            vals = sorted(self.client.hvals('test:hash3'))
            assert keys == ['a', 'b', 'c']
            assert vals == ['1', '2', '3']
        self.run_test(test_hkeys_hvals, "HKEYS/HVALS")

    def test_set_operations(self):
        """集合操作測試"""
        print(ColorOutput.header("\n🎯 集合操作測試"))

        # SADD/SREM
        def test_sadd_srem():
            self.client.sadd('test:set', 'a', 'b', 'c')
            assert self.client.scard('test:set') == 3
            self.client.srem('test:set', 'b')
            assert self.client.scard('test:set') == 2
        self.run_test(test_sadd_srem, "SADD/SREM/SCARD")

        # Set operations
        def test_set_ops():
            self.client.sadd('test:set1', 'a', 'b', 'c')
            self.client.sadd('test:set2', 'b', 'c', 'd')
            assert set(self.client.sinter('test:set1', 'test:set2')) == {'b', 'c'}
            assert set(self.client.sunion('test:set1', 'test:set2')) == {'a', 'b', 'c', 'd'}
            assert set(self.client.sdiff('test:set1', 'test:set2')) == {'a'}
        self.run_test(test_set_ops, "SINTER/SUNION/SDIFF")

    def test_sorted_set_operations(self):
        """有序集合操作測試"""
        print(ColorOutput.header("\n📊 有序集合操作測試"))

        # ZADD/ZRANGE
        def test_zadd_zrange():
            self.client.zadd('test:zset', {'a': 1, 'b': 2, 'c': 3})
            result = self.client.zrange('test:zset', 0, -1)
            assert result == ['a', 'b', 'c']
        self.run_test(test_zadd_zrange, "ZADD/ZRANGE")

        # ZINCRBY
        def test_zincrby():
            self.client.zadd('test:zset2', {'player1': 100})
            self.client.zincrby('test:zset2', 50, 'player1')
            score = self.client.zscore('test:zset2', 'player1')
            assert score == 150
        self.run_test(test_zincrby, "ZINCRBY")

    def test_key_operations(self):
        """鍵操作測試"""
        print(ColorOutput.header("\n🔑 鍵操作測試"))

        # EXISTS/DEL
        def test_exists_del():
            self.client.set('test:key1', 'value')
            assert self.client.exists('test:key1') == 1
            self.client.delete('test:key1')
            assert self.client.exists('test:key1') == 0
        self.run_test(test_exists_del, "EXISTS/DELETE")

        # EXPIRE/TTL
        def test_expire_ttl():
            self.client.setex('test:temp', 10, 'temp_value')
            ttl = self.client.ttl('test:temp')
            assert 0 < ttl <= 10
        self.run_test(test_expire_ttl, "EXPIRE/TTL")

        # RENAME
        def test_rename():
            self.client.set('test:old', 'value')
            self.client.rename('test:old', 'test:new')
            assert self.client.get('test:new') == 'value'
            assert self.client.exists('test:old') == 0
        self.run_test(test_rename, "RENAME")

    def test_transactions(self):
        """事務測試"""
        print(ColorOutput.header("\n💼 事務測試"))

        def test_pipeline():
            pipe = self.client.pipeline()
            pipe.set('test:tx1', 'v1')
            pipe.set('test:tx2', 'v2')
            pipe.incr('test:tx_counter')
            results = pipe.execute()
            assert self.client.get('test:tx1') == 'v1'
            assert self.client.get('test:tx2') == 'v2'
        self.run_test(test_pipeline, "Pipeline 事務")

    # ========== 性能測試 ==========

    def performance_tests(self, operations=10000):
        """性能測試"""
        print(ColorOutput.header(f"\n⚡ 性能測試 ({operations} 操作)"))

        results = {}

        # SET 性能
        start = time.time()
        for i in range(operations):
            self.client.set(f'perf:key:{i}', 'x' * 100)
        set_time = time.time() - start
        results['SET'] = (set_time, operations / set_time)

        # GET 性能
        start = time.time()
        for i in range(operations):
            self.client.get(f'perf:key:{i}')
        get_time = time.time() - start
        results['GET'] = (get_time, operations / get_time)

        # Pipeline 性能
        start = time.time()
        pipe = self.client.pipeline()
        for i in range(operations):
            pipe.set(f'perf:pipe:{i}', 'x' * 100)
        pipe.execute()
        pipe_time = time.time() - start
        results['Pipeline'] = (pipe_time, operations / pipe_time)

        # 清理
        for i in range(operations):
            self.client.delete(f'perf:key:{i}', f'perf:pipe:{i}')

        # 顯示結果
        print(f"\n  {'操作':<15} {'時間(秒)':<12} {'吞吐量(ops/s)':<15}")
        print("  " + "-" * 42)
        for op, (duration, throughput) in results.items():
            print(f"  {op:<15} {duration:<12.3f} {throughput:<15.0f}")

        return results

    # ========== 壓力測試 ==========

    def stress_test(self, threads=10, operations_per_thread=1000):
        """並發壓力測試"""
        print(ColorOutput.header(f"\n🔥 壓力測試 ({threads} 線程, 每線程 {operations_per_thread} 操作)"))

        def worker(thread_id):
            client = redis.Redis(host=self.host, port=self.port, decode_responses=True)
            latencies = []

            for i in range(operations_per_thread):
                key = f'stress:{thread_id}:{i}'
                value = 'x' * random.randint(10, 1000)

                # 測量延遲
                start = time.perf_counter()
                client.set(key, value)
                client.get(key)
                end = time.perf_counter()

                latencies.append((end - start) * 1000)  # 轉換為毫秒

                # 隨機操作
                if random.random() < 0.3:
                    client.delete(key)

            return latencies

        start_time = time.time()
        all_latencies = []

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker, i) for i in range(threads)]
            for future in as_completed(futures):
                all_latencies.extend(future.result())

        total_time = time.time() - start_time
        total_ops = threads * operations_per_thread * 2  # SET + GET

        # 計算統計
        avg_latency = statistics.mean(all_latencies)
        median_latency = statistics.median(all_latencies)
        p95_latency = sorted(all_latencies)[int(len(all_latencies) * 0.95)]
        p99_latency = sorted(all_latencies)[int(len(all_latencies) * 0.99)]

        print(f"\n  總時間: {total_time:.2f} 秒")
        print(f"  總操作數: {total_ops}")
        print(f"  吞吐量: {total_ops/total_time:.0f} ops/s")
        print(f"\n  延遲統計 (毫秒):")
        print(f"    平均: {avg_latency:.2f}")
        print(f"    中位數: {median_latency:.2f}")
        print(f"    P95: {p95_latency:.2f}")
        print(f"    P99: {p99_latency:.2f}")

        # 清理測試數據
        for key in self.client.scan_iter('stress:*'):
            self.client.delete(key)

    # ========== 特殊功能測試 ==========

    def test_special_features(self):
        """測試特殊功能"""
        print(ColorOutput.header("\n🌟 特殊功能測試"))

        # 大值處理
        def test_large_values():
            large_value = 'x' * 1024 * 1024  # 1MB
            self.client.set('test:large', large_value)
            retrieved = self.client.get('test:large')
            assert len(retrieved) == len(large_value)
        self.run_test(test_large_values, "大值處理 (1MB)")

        # Pub/Sub
        def test_pubsub():
            pubsub = self.client.pubsub()
            pubsub.subscribe('test:channel')
            self.client.publish('test:channel', 'test message')
            # 跳過訂閱確認消息
            msg = pubsub.get_message(timeout=1)
            msg = pubsub.get_message(timeout=1)
            assert msg and msg['data'] == 'test message'
            pubsub.unsubscribe('test:channel')
        self.run_test(test_pubsub, "Pub/Sub 功能")

    # ========== 主測試流程 ==========

    def run_all_tests(self, include_stress=False):
        """執行所有測試"""
        if not self.connect():
            return False

        print(ColorOutput.header("\n" + "="*60))
        print(ColorOutput.header("         DragonflyDB 綜合測試套件"))
        print(ColorOutput.header("="*60))

        # 獲取服務器信息
        info = self.client.info('server')
        print(ColorOutput.info(f"服務器版本: {info.get('redis_version', 'Unknown')}"))
        print(ColorOutput.info(f"運行時間: {info.get('uptime_in_seconds', 0)} 秒"))

        # 清理之前的測試數據
        print(ColorOutput.info("清理測試數據..."))
        self.cleanup_test_data()

        # 執行功能測試
        self.test_string_operations()
        self.test_numeric_operations()
        self.test_list_operations()
        self.test_hash_operations()
        self.test_set_operations()
        self.test_sorted_set_operations()
        self.test_key_operations()
        self.test_transactions()
        self.test_special_features()

        # 執行性能測試
        self.performance_tests(5000)

        # 執行壓力測試（可選）
        if include_stress:
            self.stress_test(threads=5, operations_per_thread=500)

        # 清理測試數據
        print(ColorOutput.info("\n清理所有測試數據..."))
        self.cleanup_test_data()

        # 顯示測試結果
        print(ColorOutput.header("\n" + "="*60))
        print(ColorOutput.header("         測試結果總結"))
        print(ColorOutput.header("="*60))

        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0

        print(f"\n  通過: {ColorOutput.OKGREEN}{self.test_results['passed']}{ColorOutput.ENDC}")
        print(f"  失敗: {ColorOutput.FAIL if self.test_results['failed'] > 0 else ''}{self.test_results['failed']}{ColorOutput.ENDC}")
        print(f"  成功率: {success_rate:.1f}%")

        if self.test_results['errors']:
            print(ColorOutput.header("\n  失敗詳情:"))
            for error in self.test_results['errors']:
                print(f"    {ColorOutput.FAIL}{error}{ColorOutput.ENDC}")

        if self.test_results['failed'] == 0:
            print(ColorOutput.success("\n所有測試通過！"))
            return True
        else:
            print(ColorOutput.fail(f"\n有 {self.test_results['failed']} 個測試失敗"))
            return False

def main():
    parser = argparse.ArgumentParser(description='DragonflyDB 綜合測試套件')
    parser.add_argument('--host', default='localhost', help='DragonflyDB 主機')
    parser.add_argument('--port', type=int, default=6379, help='DragonflyDB 端口')
    parser.add_argument('--stress', action='store_true', help='包含壓力測試')
    parser.add_argument('--verbose', action='store_true', help='詳細輸出')

    args = parser.parse_args()

    tester = DragonflyTestSuite(
        host=args.host,
        port=args.port,
        verbose=args.verbose
    )

    success = tester.run_all_tests(include_stress=args.stress)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()