#!/usr/bin/env python3
"""
鎖選擇指南與使用建議
幫助開發者根據使用場景選擇合適的鎖機制
"""

import threading
import time
import random
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod


class LockType(Enum):
    """鎖類型枚舉"""
    LOCK = "Lock"
    RLOCK = "RLock"
    SEMAPHORE = "Semaphore"
    CONDITION = "Condition"
    EVENT = "Event"
    BARRIER = "Barrier"
    THREAD_LOCAL = "ThreadLocal"
    READ_WRITE_LOCK = "ReadWriteLock"


@dataclass
class ScenarioAnalysis:
    """場景分析結果"""
    scenario_name: str
    recommended_lock: LockType
    reasoning: str
    alternatives: List[LockType]
    implementation_notes: str
    performance_notes: str


class LockSelector:
    """鎖選擇器"""
    
    def __init__(self):
        self.scenarios = self._build_scenario_guide()
    
    def _build_scenario_guide(self) -> Dict[str, ScenarioAnalysis]:
        """建立場景指南"""
        return {
            "simple_counter": ScenarioAnalysis(
                scenario_name="簡單計數器",
                recommended_lock=LockType.THREAD_LOCAL,
                reasoning="避免鎖競爭，每個執行緒獨立計數後匯總",
                alternatives=[LockType.LOCK],
                implementation_notes="使用 threading.local 為每個執行緒維護獨立計數器",
                performance_notes="最快，無鎖競爭開銷"
            ),
            
            "shared_resource": ScenarioAnalysis(
                scenario_name="保護共享變數",
                recommended_lock=LockType.LOCK,
                reasoning="基本互斥需求，簡單且高效",
                alternatives=[LockType.RLOCK],
                implementation_notes="使用 with 語句確保正確釋放",
                performance_notes="低開銷，適合短期持有"
            ),
            
            "recursive_function": ScenarioAnalysis(
                scenario_name="遞迴函數同步",
                recommended_lock=LockType.RLOCK,
                reasoning="同一執行緒可能需要多次獲得鎖",
                alternatives=[],
                implementation_notes="避免同一執行緒的自我死鎖",
                performance_notes="比 Lock 稍慢，但支援遞迴"
            ),
            
            "cache_system": ScenarioAnalysis(
                scenario_name="快取系統",
                recommended_lock=LockType.READ_WRITE_LOCK,
                reasoning="多讀少寫，允許並行讀取",
                alternatives=[LockType.LOCK],
                implementation_notes="需要自行實現或使用第三方庫",
                performance_notes="讀取密集場景下效能顯著提升"
            ),
            
            "connection_pool": ScenarioAnalysis(
                scenario_name="連線池管理",
                recommended_lock=LockType.SEMAPHORE,
                reasoning="限制同時使用資源的執行緒數量",
                alternatives=[LockType.CONDITION],
                implementation_notes="信號量值設定為最大連線數",
                performance_notes="有效控制資源使用"
            ),
            
            "producer_consumer": ScenarioAnalysis(
                scenario_name="生產者-消費者",
                recommended_lock=LockType.CONDITION,
                reasoning="需要等待特定條件成立",
                alternatives=[LockType.EVENT],
                implementation_notes="使用 wait() 和 notify() 進行協調",
                performance_notes="避免忙等待，節省 CPU"
            ),
            
            "event_notification": ScenarioAnalysis(
                scenario_name="事件通知",
                recommended_lock=LockType.EVENT,
                reasoning="一對多通知，簡單的狀態信號",
                alternatives=[LockType.CONDITION],
                implementation_notes="set() 通知所有等待者",
                performance_notes="比 Condition 更簡單，適合狀態通知"
            ),
            
            "phase_synchronization": ScenarioAnalysis(
                scenario_name="分階段同步",
                recommended_lock=LockType.BARRIER,
                reasoning="確保所有執行緒同步到達檢查點",
                alternatives=[LockType.CONDITION],
                implementation_notes="所有執行緒到達後一起繼續",
                performance_notes="適合 MapReduce 等分階段處理"
            ),
            
            "request_context": ScenarioAnalysis(
                scenario_name="請求上下文",
                recommended_lock=LockType.THREAD_LOCAL,
                reasoning="每個執行緒需要獨立的上下文資訊",
                alternatives=[],
                implementation_notes="避免在函數間傳遞上下文參數",
                performance_notes="無同步開銷，存取速度快"
            )
        }
    
    def get_recommendation(self, scenario_key: str) -> Optional[ScenarioAnalysis]:
        """獲取場景建議"""
        return self.scenarios.get(scenario_key)
    
    def list_scenarios(self) -> List[str]:
        """列出所有場景"""
        return list(self.scenarios.keys())
    
    def analyze_requirements(self, **requirements) -> LockType:
        """根據需求分析推薦鎖類型"""
        # 簡化的需求分析邏輯
        if requirements.get("recursive", False):
            return LockType.RLOCK
        elif requirements.get("resource_limit"):
            return LockType.SEMAPHORE
        elif requirements.get("condition_wait", False):
            return LockType.CONDITION
        elif requirements.get("event_notification", False):
            return LockType.EVENT
        elif requirements.get("phase_sync", False):
            return LockType.BARRIER
        elif requirements.get("thread_isolation", False):
            return LockType.THREAD_LOCAL
        elif requirements.get("read_heavy", False):
            return LockType.READ_WRITE_LOCK
        else:
            return LockType.LOCK


class ScenarioDemo(ABC):
    """場景演示基類"""
    
    @abstractmethod
    def demonstrate(self):
        """演示場景"""
        pass
    
    @abstractmethod
    def get_scenario_info(self) -> ScenarioAnalysis:
        """獲取場景資訊"""
        pass


class SimpleCounterDemo(ScenarioDemo):
    """簡單計數器演示"""
    
    def get_scenario_info(self) -> ScenarioAnalysis:
        selector = LockSelector()
        return selector.get_recommendation("simple_counter")
    
    def demonstrate(self):
        print("📊 場景：簡單計數器")
        print("問題：多個執行緒需要增加一個全域計數器")
        
        # 錯誤方式：使用 Lock
        print("\n❌ 錯誤方式：使用 Lock (雖然正確但效能不佳)")
        counter_with_lock = 0
        lock = threading.Lock()
        
        def worker_with_lock(iterations):
            nonlocal counter_with_lock
            for _ in range(iterations):
                with lock:
                    counter_with_lock += 1
        
        start_time = time.time()
        threads = [threading.Thread(target=worker_with_lock, args=(1000,)) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        lock_time = time.time() - start_time
        
        print(f"   使用 Lock: {counter_with_lock}, 耗時: {lock_time:.4f}s")
        
        # 正確方式：使用 ThreadLocal
        print("\n✅ 建議方式：使用 ThreadLocal")
        thread_local_data = threading.local()
        results = []
        results_lock = threading.Lock()
        
        def worker_with_local(iterations):
            thread_local_data.counter = 0
            for _ in range(iterations):
                thread_local_data.counter += 1
            
            with results_lock:
                results.append(thread_local_data.counter)
        
        start_time = time.time()
        threads = [threading.Thread(target=worker_with_local, args=(1000,)) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        local_time = time.time() - start_time
        
        total_count = sum(results)
        print(f"   使用 ThreadLocal: {total_count}, 耗時: {local_time:.4f}s")
        print(f"   效能提升: {(lock_time / local_time):.1f}x")


class CacheSystemDemo(ScenarioDemo):
    """快取系統演示"""
    
    def get_scenario_info(self) -> ScenarioAnalysis:
        selector = LockSelector()
        return selector.get_recommendation("cache_system")
    
    def demonstrate(self):
        print("\n🗄️  場景：快取系統")
        print("問題：多讀少寫的快取，需要支援並行讀取")
        
        # 使用普通 Lock 的快取
        class LockedCache:
            def __init__(self):
                self._cache = {}
                self._lock = threading.Lock()
                self._read_count = 0
                self._write_count = 0
            
            def get(self, key):
                with self._lock:
                    self._read_count += 1
                    return self._cache.get(key)
            
            def put(self, key, value):
                with self._lock:
                    self._write_count += 1
                    self._cache[key] = value
            
            def stats(self):
                return self._read_count, self._write_count
        
        # 模擬讀寫鎖的快取
        class ReadWriteCache:
            def __init__(self):
                self._cache = {}
                self._read_condition = threading.Condition(threading.RLock())
                self._readers = 0
                self._read_count = 0
                self._write_count = 0
            
            def get(self, key):
                self._read_condition.acquire()
                try:
                    self._readers += 1
                    self._read_count += 1
                finally:
                    self._read_condition.release()
                
                try:
                    # 實際讀取
                    time.sleep(0.001)  # 模擬讀取時間
                    return self._cache.get(key)
                finally:
                    self._read_condition.acquire()
                    try:
                        self._readers -= 1
                        if self._readers == 0:
                            self._read_condition.notifyAll()
                    finally:
                        self._read_condition.release()
            
            def put(self, key, value):
                self._read_condition.acquire()
                try:
                    while self._readers > 0:
                        self._read_condition.wait()
                    
                    self._write_count += 1
                    self._cache[key] = value
                    time.sleep(0.002)  # 模擬寫入時間
                finally:
                    self._read_condition.release()
            
            def stats(self):
                return self._read_count, self._write_count
        
        # 測試兩種快取
        def test_cache(cache, name):
            def reader(cache, num_reads):
                for i in range(num_reads):
                    cache.get(f"key_{i % 10}")
            
            def writer(cache, num_writes):
                for i in range(num_writes):
                    cache.put(f"key_{i}", f"value_{i}")
            
            start_time = time.time()
            
            # 更多讀者，少數寫者
            readers = [threading.Thread(target=reader, args=(cache, 50)) for _ in range(8)]
            writers = [threading.Thread(target=writer, args=(cache, 10)) for _ in range(2)]
            
            for t in readers + writers:
                t.start()
            for t in readers + writers:
                t.join()
            
            elapsed = time.time() - start_time
            reads, writes = cache.stats()
            
            print(f"   {name}: {reads} 讀取, {writes} 寫入, 耗時: {elapsed:.3f}s")
            return elapsed
        
        print("\n❌ 使用普通 Lock:")
        locked_time = test_cache(LockedCache(), "普通 Lock")
        
        print("\n✅ 使用讀寫鎖概念:")
        rw_time = test_cache(ReadWriteCache(), "讀寫鎖")
        
        if locked_time > rw_time:
            print(f"   讀寫鎖效能提升: {(locked_time / rw_time):.1f}x")


class ConnectionPoolDemo(ScenarioDemo):
    """連線池演示"""
    
    def get_scenario_info(self) -> ScenarioAnalysis:
        selector = LockSelector()
        return selector.get_recommendation("connection_pool")
    
    def demonstrate(self):
        print("\n🔗 場景：連線池管理")
        print("問題：限制同時使用資源的執行緒數量")
        
        class ConnectionPool:
            def __init__(self, max_connections=3):
                self.semaphore = threading.Semaphore(max_connections)
                self.active_connections = 0
                self.total_requests = 0
                self._lock = threading.Lock()
            
            def get_connection(self):
                self.semaphore.acquire()
                with self._lock:
                    self.active_connections += 1
                    self.total_requests += 1
                    conn_id = f"conn-{self.total_requests}"
                
                print(f"   📞 獲得連線 {conn_id} (活躍: {self.active_connections})")
                return conn_id
            
            def release_connection(self, conn_id):
                with self._lock:
                    self.active_connections -= 1
                
                print(f"   🔙 釋放連線 {conn_id} (活躍: {self.active_connections})")
                self.semaphore.release()
        
        def worker(pool, worker_id):
            conn = pool.get_connection()
            # 模擬使用連線
            time.sleep(random.uniform(0.5, 1.0))
            pool.release_connection(conn)
        
        print("\n✅ 使用 Semaphore 控制連線數量:")
        pool = ConnectionPool(max_connections=2)
        
        threads = [threading.Thread(target=worker, args=(pool, i)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()


def demonstrate_selection_process():
    """演示選擇過程"""
    print("🎯 鎖選擇決策流程")
    print("=" * 60)
    
    selector = LockSelector()
    
    # 顯示所有場景
    print("📋 常見場景與建議:")
    for scenario_key in selector.list_scenarios():
        analysis = selector.get_recommendation(scenario_key)
        if analysis:
            print(f"\n🔸 {analysis.scenario_name}")
            print(f"   推薦: {analysis.recommended_lock.value}")
            print(f"   理由: {analysis.reasoning}")
            if analysis.alternatives:
                alts = [alt.value for alt in analysis.alternatives]
                print(f"   替代: {', '.join(alts)}")
    
    print(f"\n🤖 智慧推薦範例:")
    
    # 需求分析範例
    test_cases = [
        {"recursive": True, "description": "遞迴函數需要鎖"},
        {"resource_limit": 5, "description": "最多5個並行連線"},
        {"condition_wait": True, "description": "等待特定條件"},
        {"event_notification": True, "description": "一對多事件通知"},
        {"thread_isolation": True, "description": "執行緒間隔離"},
        {"read_heavy": True, "description": "讀取密集的快取"}
    ]
    
    for case in test_cases:
        desc = case.pop("description")
        recommendation = selector.analyze_requirements(**case)
        print(f"   {desc} → {recommendation.value}")


def run_scenario_demonstrations():
    """執行場景演示"""
    print(f"\n🎭 實際場景演示")
    print("=" * 60)
    
    demos = [
        SimpleCounterDemo(),
        CacheSystemDemo(),
        ConnectionPoolDemo()
    ]
    
    for demo in demos:
        scenario_info = demo.get_scenario_info()
        print(f"\n📖 場景分析: {scenario_info.scenario_name}")
        print(f"   推薦: {scenario_info.recommended_lock.value}")
        print(f"   理由: {scenario_info.reasoning}")
        print(f"   注意: {scenario_info.implementation_notes}")
        print(f"   效能: {scenario_info.performance_notes}")
        
        demo.demonstrate()


def show_decision_tree():
    """顯示決策樹"""
    print(f"\n🌳 鎖選擇決策樹")
    print("=" * 60)
    
    decision_tree = """
    需要同步嗎？
    ├─ 否 → 無需鎖
    └─ 是
        ├─ 執行緒隔離？ → threading.local
        ├─ 遞迴呼叫？ → RLock
        ├─ 限制資源數量？ → Semaphore
        ├─ 多讀少寫？ → ReadWriteLock
        ├─ 等待條件？ → Condition
        ├─ 事件通知？ → Event
        ├─ 階段同步？ → Barrier
        └─ 基本互斥 → Lock
    """
    
    print(decision_tree)


def show_performance_guidelines():
    """顯示效能指南"""
    print(f"\n⚡ 效能指南")
    print("=" * 60)
    
    guidelines = [
        ("🥇 threading.local", "最快，無鎖競爭，適合執行緒隔離"),
        ("🥈 Lock", "基本互斥鎖，低開銷，適合簡單同步"),
        ("🥉 RLock", "遞迴鎖，稍慢於 Lock，支援重複獲取"),
        ("4️⃣ Event", "事件通知，簡單高效的狀態信號"),
        ("5️⃣ Semaphore", "資源控制，開銷適中"),
        ("6️⃣ Condition", "條件等待，避免忙等待"),
        ("7️⃣ Barrier", "階段同步，適合特定場景"),
        ("8️⃣ ReadWriteLock", "讀寫分離，讀密集場景優勢明顯")
    ]
    
    for rank, description in guidelines:
        print(f"{rank} {description}")
    
    print(f"\n💡 選擇建議:")
    print("   • 優先考慮是否可以避免共享狀態")
    print("   • 其次考慮 threading.local")
    print("   • 然後根據具體需求選擇合適的鎖")
    print("   • 始終使用 with 語句管理鎖")
    print("   • 最小化鎖的持有時間")
    print("   • 在實際場景中測試效能")


if __name__ == "__main__":
    demonstrate_selection_process()
    run_scenario_demonstrations()
    show_decision_tree()
    show_performance_guidelines()