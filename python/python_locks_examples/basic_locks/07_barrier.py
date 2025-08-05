#!/usr/bin/env python3
"""
Barrier (屏障) 使用範例
同步多個執行緒，確保它們在某個點一起繼續執行
"""

import threading
import time
import random


class MultiPhaseTask:
    """多階段任務實現"""
    
    def __init__(self, num_workers=3):
        self.num_workers = num_workers
        # 建立屏障，需要指定數量的執行緒同時到達
        self.phase1_barrier = threading.Barrier(num_workers)
        self.phase2_barrier = threading.Barrier(num_workers)
        self.results = []
        self.results_lock = threading.Lock()
        self.phase_data = {
            'phase1_times': [],
            'phase2_times': []
        }
    
    def worker(self, worker_id):
        """多階段工作者"""
        thread_name = threading.current_thread().name
        
        # 階段1: 資料準備
        print(f"📋 工作者 {worker_id} ({thread_name}) 開始階段1: 資料準備")
        preparation_time = random.uniform(1, 3)
        time.sleep(preparation_time)
        
        with self.results_lock:
            self.phase_data['phase1_times'].append(preparation_time)
        
        print(f"✅ 工作者 {worker_id} 完成階段1 (耗時: {preparation_time:.1f}s)")
        
        try:
            # 等待所有工作者完成階段1
            print(f"⏳ 工作者 {worker_id} 等待其他工作者完成階段1...")
            wait_start = time.time()
            index = self.phase1_barrier.wait()  # 返回到達順序
            wait_time = time.time() - wait_start
            
            if index == 0:  # 最後一個到達的執行緒
                print(f"🎉 工作者 {worker_id} 是最後到達階段1屏障的！")
            
            print(f"🚀 工作者 {worker_id} 進入階段2! (等待時間: {wait_time:.1f}s)")
            
        except threading.BrokenBarrierError:
            print(f"❌ 工作者 {worker_id}: 階段1屏障被破壞")
            return
        
        # 階段2: 資料處理
        print(f"⚙️  工作者 {worker_id} 開始階段2: 資料處理")
        processing_time = random.uniform(1.5, 2.5)
        time.sleep(processing_time)
        
        # 儲存結果
        result = {
            'worker_id': worker_id,
            'thread_name': thread_name,
            'phase1_time': preparation_time,
            'phase2_time': processing_time,
            'total_time': preparation_time + processing_time
        }
        
        with self.results_lock:
            self.results.append(result)
            self.phase_data['phase2_times'].append(processing_time)
        
        print(f"✅ 工作者 {worker_id} 完成階段2 (耗時: {processing_time:.1f}s)")
        
        try:
            # 等待所有工作者完成階段2
            print(f"⏳ 工作者 {worker_id} 等待其他工作者完成階段2...")
            wait_start = time.time()
            index = self.phase2_barrier.wait()
            wait_time = time.time() - wait_start
            
            print(f"🎉 工作者 {worker_id} 所有階段完成! (等待時間: {wait_time:.1f}s)")
            
            # 階段3: 結果匯總（只有一個工作者執行）
            if index == 0:  # 最後一個到達的執行緒負責匯總
                self._summarize_results()
                
        except threading.BrokenBarrierError:
            print(f"❌ 工作者 {worker_id}: 階段2屏障被破壞")
            return
    
    def _summarize_results(self):
        """匯總結果（只有一個工作者執行）"""
        print(f"\n📊 開始結果匯總...")
        time.sleep(0.5)  # 模擬匯總時間
        
        print(f"📋 所有工作者結果:")
        for result in sorted(self.results, key=lambda x: x['worker_id']):
            print(f"   👷 工作者 {result['worker_id']}: "
                  f"階段1={result['phase1_time']:.1f}s, "
                  f"階段2={result['phase2_time']:.1f}s, "
                  f"總計={result['total_time']:.1f}s")
        
        # 統計資訊
        phase1_avg = sum(self.phase_data['phase1_times']) / len(self.phase_data['phase1_times'])
        phase2_avg = sum(self.phase_data['phase2_times']) / len(self.phase_data['phase2_times'])
        
        print(f"\n📈 統計資訊:")
        print(f"   階段1平均時間: {phase1_avg:.1f}s")
        print(f"   階段2平均時間: {phase2_avg:.1f}s")
        print(f"   參與工作者數: {len(self.results)}")


class ParallelComputation:
    """並行計算範例"""
    
    def __init__(self, num_threads=4, data_size=1000000):
        self.num_threads = num_threads
        self.data_size = data_size
        self.data = list(range(data_size))
        self.barrier = threading.Barrier(num_threads)
        self.results = [0] * num_threads
        self.chunk_size = data_size // num_threads
    
    def compute_worker(self, worker_id):
        """計算工作者"""
        # 計算這個工作者負責的資料範圍
        start_idx = worker_id * self.chunk_size
        end_idx = start_idx + self.chunk_size
        if worker_id == self.num_threads - 1:  # 最後一個工作者處理剩餘資料
            end_idx = self.data_size
        
        print(f"🧮 工作者 {worker_id} 計算範圍: {start_idx} - {end_idx}")
        
        # 執行計算（這裡是簡單的平方和）
        start_time = time.time()
        result = sum(x * x for x in self.data[start_idx:end_idx])
        compute_time = time.time() - start_time
        
        self.results[worker_id] = result
        print(f"✅ 工作者 {worker_id} 計算完成: {result} (耗時: {compute_time:.3f}s)")
        
        try:
            # 等待所有工作者完成計算
            print(f"⏳ 工作者 {worker_id} 等待其他工作者...")
            index = self.barrier.wait()
            
            # 最後一個到達的工作者負責合併結果
            if index == 0:
                total_result = sum(self.results)
                print(f"\n🎯 最終結果: {total_result}")
                
                # 驗證結果
                expected = sum(x * x for x in self.data)
                print(f"🔍 驗證結果: {'✅ 正確' if total_result == expected else '❌ 錯誤'}")
                
        except threading.BrokenBarrierError:
            print(f"❌ 工作者 {worker_id}: 屏障被破壞")


def test_multi_phase_task():
    """測試多階段任務"""
    print("🧪 測試多階段任務 (Barrier)")
    print("=" * 50)
    
    num_workers = 4
    task = MultiPhaseTask(num_workers=num_workers)
    threads = []
    
    print(f"🎯 啟動 {num_workers} 個工作者執行多階段任務")
    
    start_time = time.time()
    
    # 建立工作者執行緒
    for i in range(num_workers):
        t = threading.Thread(target=task.worker, args=(i,), name=f"Worker-{i}")
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    print(f"\n⏱️  總執行時間: {end_time - start_time:.2f} 秒")


def test_parallel_computation():
    """測試並行計算"""
    print("\n🧪 測試並行計算")
    print("=" * 50)
    
    num_threads = 3
    data_size = 100000
    
    computation = ParallelComputation(num_threads=num_threads, data_size=data_size)
    threads = []
    
    print(f"🎯 使用 {num_threads} 個執行緒計算 {data_size} 個數字的平方和")
    
    start_time = time.time()
    
    # 建立計算執行緒
    for i in range(num_threads):
        t = threading.Thread(target=computation.compute_worker, args=(i,))
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    end_time = time.time()
    print(f"⏱️  並行計算耗時: {end_time - start_time:.3f} 秒")


def test_barrier_broken():
    """測試屏障被破壞的情況"""
    print("\n🧪 測試屏障異常處理")
    print("=" * 50)
    
    barrier = threading.Barrier(3)
    results = []
    
    def normal_worker(worker_id):
        try:
            print(f"👷 正常工作者 {worker_id} 到達屏障")
            barrier.wait()
            results.append(f"工作者{worker_id}完成")
        except threading.BrokenBarrierError:
            print(f"❌ 工作者 {worker_id}: 屏障被破壞")
    
    def problem_worker():
        try:
            print("💥 問題工作者到達屏障")
            time.sleep(0.5)
            # 模擬異常情況
            raise Exception("模擬異常")
        except Exception as e:
            print(f"💥 問題工作者發生異常: {e}")
            barrier.abort()  # 破壞屏障
    
    threads = []
    
    # 建立正常工作者
    for i in range(2):
        t = threading.Thread(target=normal_worker, args=(i,))
        threads.append(t)
        t.start()
    
    # 建立問題工作者
    problem_thread = threading.Thread(target=problem_worker)
    threads.append(problem_thread)
    problem_thread.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    print(f"📊 完成的工作者: {len(results)}")
    print(f"🔍 屏障狀態: {'❌ 已破壞' if barrier.broken else '✅ 正常'}")


if __name__ == "__main__":
    test_multi_phase_task()
    test_parallel_computation()
    test_barrier_broken()