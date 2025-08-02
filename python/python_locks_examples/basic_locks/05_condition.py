#!/usr/bin/env python3
"""
Condition (條件變數) 使用範例
實現生產者-消費者模式和任務協調
"""

import threading
import time
import random


class ProducerConsumer:
    """生產者-消費者模式實現"""
    
    def __init__(self, buffer_size=5):
        self.buffer = []
        self.buffer_size = buffer_size
        self.condition = threading.Condition()
        self.produced_count = 0
        self.consumed_count = 0
        self.stop_producing = False
    
    def producer(self, producer_id, items_to_produce=5):
        """生產者方法"""
        for i in range(items_to_produce):
            item = f"產品-{producer_id}-{i}"
            
            with self.condition:
                # 等待緩衝區有空間
                while len(self.buffer) >= self.buffer_size:
                    print(f"🏭 生產者 {producer_id} 等待空間...")
                    self.condition.wait()
                
                # 生產物品
                self.buffer.append(item)
                self.produced_count += 1
                buffer_status = f"({len(self.buffer)}/{self.buffer_size})"
                print(f"✨ 生產者 {producer_id} 生產了 {item} 緩衝區: {buffer_status}")
                
                # 通知消費者
                self.condition.notify_all()
            
            time.sleep(random.uniform(0.1, 0.5))
        
        print(f"🏁 生產者 {producer_id} 完成生產")
    
    def consumer(self, consumer_id, max_items=None):
        """消費者方法"""
        consumed = 0
        
        while True:
            with self.condition:
                # 等待有物品可消費
                while not self.buffer and not self.stop_producing:
                    print(f"👤 消費者 {consumer_id} 等待產品...")
                    self.condition.wait(timeout=1)  # 設定超時
                
                # 檢查是否還有物品可消費
                if not self.buffer and self.stop_producing:
                    print(f"🏁 消費者 {consumer_id} 退出 (已消費 {consumed} 個)")
                    return
                
                if self.buffer:
                    item = self.buffer.pop(0)
                    self.consumed_count += 1
                    consumed += 1
                    buffer_status = f"({len(self.buffer)}/{self.buffer_size})"
                    print(f"🍽️  消費者 {consumer_id} 消費了 {item} 緩衝區: {buffer_status}")
                    
                    # 通知生產者
                    self.condition.notify_all()
                    
                    # 檢查是否達到最大消費數量
                    if max_items and consumed >= max_items:
                        print(f"🏁 消費者 {consumer_id} 完成任務 (消費了 {consumed} 個)")
                        return
            
            # 模擬消費時間
            time.sleep(random.uniform(0.2, 0.8))
    
    def stop_production(self):
        """停止生產"""
        with self.condition:
            self.stop_producing = True
            self.condition.notify_all()


class TaskCoordinator:
    """任務協調器 - 確保所有工作者準備就緒後才開始"""
    
    def __init__(self, target_workers=3):
        self.condition = threading.Condition()
        self.task_ready = False
        self.workers_ready = 0
        self.target_workers = target_workers
        self.results = []
    
    def worker_ready(self, worker_id):
        """工作者報告準備就緒"""
        with self.condition:
            self.workers_ready += 1
            ready_status = f"({self.workers_ready}/{self.target_workers})"
            print(f"👷 工作者 {worker_id} 準備就緒 {ready_status}")
            
            if self.workers_ready >= self.target_workers:
                print("🚀 所有工作者準備就緒，開始任務！")
                self.task_ready = True
                self.condition.notify_all()
            else:
                # 等待其他工作者
                while not self.task_ready:
                    print(f"⏳ 工作者 {worker_id} 等待其他工作者...")
                    self.condition.wait()
    
    def start_task(self, worker_id):
        """開始執行任務"""
        task_time = random.uniform(1, 3)
        print(f"⚙️  工作者 {worker_id} 開始執行任務 (預計 {task_time:.1f}s)")
        time.sleep(task_time)
        
        result = f"工作者{worker_id}的結果"
        self.results.append(result)
        print(f"✅ 工作者 {worker_id} 完成任務")


def producer_worker(pc, producer_id, items=3):
    """生產者工作者"""
    pc.producer(producer_id, items)


def consumer_worker(pc, consumer_id):
    """消費者工作者"""
    pc.consumer(consumer_id)


def coordinator_worker(coordinator, worker_id):
    """協調器工作者"""
    # 模擬準備時間
    prep_time = random.uniform(0.5, 2.0)
    print(f"🔧 工作者 {worker_id} 準備中... ({prep_time:.1f}s)")
    time.sleep(prep_time)
    
    # 報告準備就緒並等待開始信號
    coordinator.worker_ready(worker_id)
    
    # 執行任務
    coordinator.start_task(worker_id)


def test_producer_consumer():
    """測試生產者-消費者模式"""
    print("🧪 測試生產者-消費者模式")
    print("=" * 50)
    
    pc = ProducerConsumer(buffer_size=3)
    threads = []
    
    start_time = time.time()
    
    # 建立生產者執行緒
    num_producers = 2
    items_per_producer = 3
    for i in range(num_producers):
        t = threading.Thread(target=producer_worker, args=(pc, i, items_per_producer))
        threads.append(t)
        t.start()
    
    # 建立消費者執行緒
    num_consumers = 2
    for i in range(num_consumers):
        t = threading.Thread(target=consumer_worker, args=(pc, i))
        threads.append(t)
        t.start()
    
    # 等待生產者完成
    for t in threads[:num_producers]:
        t.join()
    
    # 停止生產並等待消費者完成
    time.sleep(1)
    pc.stop_production()
    
    for t in threads[num_producers:]:
        t.join()
    
    end_time = time.time()
    
    print(f"\n📊 統計結果:")
    print(f"   總生產: {pc.produced_count} 個")
    print(f"   總消費: {pc.consumed_count} 個")
    print(f"   剩餘緩衝: {len(pc.buffer)} 個")
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")


def test_task_coordination():
    """測試任務協調"""
    print("\n🧪 測試任務協調")
    print("=" * 50)
    
    num_workers = 4
    coordinator = TaskCoordinator(target_workers=num_workers)
    threads = []
    
    print(f"🎯 等待 {num_workers} 個工作者準備就緒後開始任務")
    
    start_time = time.time()
    
    # 建立工作者執行緒
    for i in range(num_workers):
        t = threading.Thread(target=coordinator_worker, args=(coordinator, i))
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    print(f"\n📊 協調結果:")
    for result in coordinator.results:
        print(f"   ✅ {result}")
    print(f"⏱️  總耗時: {end_time - start_time:.2f} 秒")


if __name__ == "__main__":
    test_producer_consumer()
    test_task_coordination()