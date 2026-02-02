"""
資料庫代理：以記憶體為主，並將資料持久化到 JSON 檔。  # 檔案用途
"""
import logging  # 日誌系統
from typing import List, Dict, Any, Optional, Literal  # 型別註解
import uuid  # 產生唯一 ID
import json  # JSON 序列化/反序列化
import os  # 檔案存在檢查
import asyncio  # 檔案鎖

from core.interfaces import (  # 匯入介面與資料結構
    DatabaseAgentInterface,  # 資料庫介面
    Program,  # 程式資料結構
    BaseAgent,  # 基底代理
)
from config import settings  # 取得 DATABASE_PATH

logger = logging.getLogger(__name__)  # 取得本模組 logger

class InMemoryDatabaseAgent(DatabaseAgentInterface, BaseAgent):  # 記憶體資料庫代理
    """記憶體資料庫，並持久化至 JSON 檔案。"""  # 類別用途
    def __init__(self):  # 初始化
        super().__init__()  # 呼叫基底初始化
        self._programs: Dict[str, Program] = {}  # 內部儲存 dict
        self._db_file_path = settings.DATABASE_PATH  # JSON 檔路徑
        self._lock = asyncio.Lock()  # 檔案操作鎖
        self._load_from_file()  # 啟動時讀取既有資料
        logger.info(f"InMemoryDatabaseAgent initialized. Data persistence: {self._db_file_path}")  # 記錄初始化

    def _load_from_file(self):  # 從 JSON 載入
        # 初始化時同步讀取；若需非同步，可改由 async context 呼叫  # 設計說明
        if os.path.exists(self._db_file_path):  # 若檔案存在
            try:  # 嘗試讀取
                with open(self._db_file_path, 'r') as f:  # 開啟檔案
                    data = json.load(f)  # 載入 JSON
                    for prog_id, prog_data in data.items():  # 逐一還原
                        # 以 dict 重新建立 Program 物件  # 反序列化
                        self._programs[prog_id] = Program(**prog_data)  # 建立 Program
                logger.info(f"Loaded {len(self._programs)} programs from {self._db_file_path}")  # 記錄載入數量
            except json.JSONDecodeError:  # JSON 解析失敗
                logger.error(f"Error decoding JSON from {self._db_file_path}. Starting with an empty database.")  # 記錄錯誤
                self._programs = {}  # 清空資料
            except Exception as e:  # 其他錯誤
                logger.error(f"Error loading database from {self._db_file_path}: {e}. Starting with an empty database.")  # 記錄錯誤
                self._programs = {}  # 清空資料
        else:  # 檔案不存在
            logger.info(f"Database file {self._db_file_path} not found. Starting with an empty database.")  # 記錄狀態

    async def _save_to_file(self):  # 儲存到 JSON
        async with self._lock:  # 取得鎖
            try:  # 嘗試儲存
                # 將 Program 物件序列化為 dict  # 序列化
                data_to_save = {prog_id: prog.__dict__ for prog_id, prog in self._programs.items()}  # 建立 dict
                with open(self._db_file_path, 'w') as f:  # 開啟檔案
                    json.dump(data_to_save, f, indent=4)  # 寫入 JSON
                logger.debug(f"Successfully saved {len(self._programs)} programs to {self._db_file_path}")  # 記錄成功
            except Exception as e:  # 儲存失敗
                logger.error(f"Error saving database to {self._db_file_path}: {e}")  # 記錄錯誤

    async def save_program(self, program: Program) -> None:  # 儲存程式
        logger.info(f"Saving program: {program.id} (Generation: {program.generation}) to database.")  # 記錄儲存
        async with self._lock:  # 取得鎖
            if program.id in self._programs:  # 若已存在
                logger.warning(f"Program with ID {program.id} already exists. It will be overwritten.")  # 記錄覆寫
            self._programs[program.id] = program  # 寫入 dict
        await self._save_to_file()  # 每次儲存後落盤
        logger.debug(f"Program {program.id} data: {program}")  # 記錄內容

    async def get_program(self, program_id: str) -> Optional[Program]:  # 取得程式
        logger.debug(f"Attempting to retrieve program by ID: {program_id}")  # 記錄查詢
        # 讀取通常不需要鎖（寫入已鎖住）  # 設計說明
        program = self._programs.get(program_id)  # 查詢 dict
        if program:  # 若找到
            logger.info(f"Retrieved program: {program.id}")  # 記錄成功
        else:  # 若未找到
            logger.warning(f"Program with ID: {program_id} not found in database.")  # 記錄警告
        return program  # 回傳程式或 None

    async def get_all_programs(self) -> List[Program]:  # 取得所有程式
        logger.debug(f"Retrieving all {len(self._programs)} programs from database.")  # 記錄數量
        return list(self._programs.values())  # 回傳列表

    async def get_best_programs(  # 取得最佳程式
        self,  # self
        task_id: str,  # 介面需要，但 InMemory 未必用於篩選
        limit: int = 5,  # 回傳數量上限
        objective: Literal["correctness", "runtime_ms"] = "correctness",  # 目標
        sort_order: Literal["asc", "desc"] = "desc",  # 排序方向
    ) -> List[Program]:  # 回傳 Program 列表
        logger.info(f"Retrieving best programs (task: {task_id}). Limit: {limit}, Objective: {objective}, Order: {sort_order}")  # 記錄查詢
        if not self._programs:  # 若無資料
            logger.info("No programs in database to retrieve 'best' from.")  # 記錄狀態
            return []  # 回傳空列表

        all_progs = list(self._programs.values())  # 取得所有程式

        if objective == "correctness":  # 以正確率排序
            sorted_programs = sorted(all_progs, key=lambda p: p.fitness_scores.get("correctness", 0.0), reverse=(sort_order == "desc"))  # 排序
        elif objective == "runtime_ms":  # 以執行時間排序
            # runtime_ms：asc 表示越低越好  # 排序說明
            sorted_programs = sorted(all_progs, key=lambda p: p.fitness_scores.get("runtime_ms", float('inf')), reverse=(sort_order == "desc"))  # 排序
        else:  # 目標未知
            logger.warning(f"Unknown objective: {objective}. Defaulting to no specific sort order beyond Program ID.")  # 記錄警告
            return sorted(all_progs, key=lambda p: p.id)[:limit]  # 以 ID 排序

        logger.debug(f"Sorted {len(sorted_programs)} programs. Top 3 (if available): {[p.id for p in sorted_programs[:3]]}")  # 記錄排序結果
        return sorted_programs[:limit]  # 回傳前 N 名

    async def get_programs_by_generation(self, generation: int) -> List[Program]:  # 依世代取程式
        logger.debug(f"Retrieving programs for generation: {generation}")  # 記錄查詢
        generation_programs = [p for p in self._programs.values() if p.generation == generation]  # 篩選世代
        logger.info(f"Found {len(generation_programs)} programs for generation {generation}.")  # 記錄數量
        return generation_programs  # 回傳列表

    async def get_programs_for_next_generation(self, task_id: str, generation_size: int) -> List[Program]:  # 取得下一代候選
        logger.info(f"Attempting to retrieve {generation_size} programs for next generation for task {task_id}.")  # 記錄需求
        # 依 task_id 篩選（若資料庫含多任務，這步很重要）  # 篩選策略
        all_relevant_progs = [p for p in self._programs.values() if getattr(p, 'task_id', None) == task_id or task_id is None]  # 篩選
        if not all_relevant_progs:  # 若沒有符合
            logger.warning(f"No programs found for task {task_id} in database to select for next generation.")  # 記錄警告
            return []  # 回傳空列表

        if len(all_relevant_progs) <= generation_size:  # 若不足以抽樣
            logger.debug(f"Returning all {len(all_relevant_progs)} programs for task {task_id} as it's <= generation_size {generation_size}.")  # 記錄狀態
            return all_relevant_progs  # 回傳全部
        
        import random  # 匯入 random
        selected_programs = random.sample(all_relevant_progs, generation_size)  # 隨機抽樣
        logger.info(f"Selected {len(selected_programs)} random programs for task {task_id} for next generation.")  # 記錄抽樣
        return selected_programs  # 回傳抽樣結果

    async def count_programs(self) -> int:  # 計數程式數量
        count = len(self._programs)  # 計算數量
        logger.debug(f"Total programs in database: {count}")  # 記錄數量
        return count  # 回傳數量

    async def clear_database(self) -> None:  # 清空資料庫
        logger.info("Clearing all programs from database.")  # 記錄清空
        async with self._lock:  # 取得鎖
            self._programs.clear()  # 清空 dict
        await self._save_to_file()  # 落盤空資料
        logger.info("Database cleared.")  # 記錄完成

    async def execute(self, *args, **kwargs) -> Any:  # 通用執行入口（不支援）
        logger.warning("InMemoryDatabaseAgent.execute() called, but this agent uses specific methods for DB operations.")  # 記錄警告
        raise NotImplementedError("InMemoryDatabaseAgent does not have a generic execute. Use specific methods like save_program, get_program etc.")  # 拋出錯誤

                                      
if __name__ == "__main__":  # 直接執行測試
    import asyncio  # 測試用 asyncio                                                    
    async def test_db():  # 測試資料庫功能
        logging.basicConfig(level=logging.DEBUG)  # 設定日誌
        
        # 測試用設定  # mock settings
        class MockSettings:  # 定義測試設定
            DATABASE_PATH = "test_inmemory_agent.json"  # 測試檔名
        global settings  # 使用全域 settings
        settings = MockSettings()  # 替換 settings

        # 清理舊測試檔  # 確保乾淨狀態
        if os.path.exists(settings.DATABASE_PATH):  # 若檔案存在
            os.remove(settings.DATABASE_PATH)  # 刪除檔案

        db = InMemoryDatabaseAgent()  # 建立資料庫代理

        prog1_data = {"id":"prog_001", "code":"print('hello')", "generation":0, "fitness_scores":{"correctness": 0.8, "runtime_ms": 100}, "task_id": "test_task"}  # 程式 1
        prog2_data = {"id":"prog_002", "code":"print('world')", "generation":0, "fitness_scores":{"correctness": 0.9, "runtime_ms": 50}, "task_id": "test_task"}  # 程式 2
        prog3_data = {"id":"prog_003", "code":"print('test')", "generation":1, "fitness_scores":{"correctness": 0.85, "runtime_ms": 70}, "task_id": "test_task"}  # 程式 3

        prog1 = Program(**prog1_data)  # 建立程式 1
        prog2 = Program(**prog2_data)  # 建立程式 2
        prog3 = Program(**prog3_data)  # 建立程式 3

        await db.save_program(prog1)  # 儲存程式 1
        await db.save_program(prog2)  # 儲存程式 2
        await db.save_program(prog3)  # 儲存程式 3

        retrieved_prog = await db.get_program("prog_001")  # 取得程式 1
        assert retrieved_prog is not None and retrieved_prog.code == "print('hello')"  # 驗證程式 1
        assert retrieved_prog.task_id == "test_task"  # 驗證 task_id

        all_programs = await db.get_all_programs()  # 取得所有程式
        assert len(all_programs) == 3  # 驗證數量

        # 建立新實例以測試讀檔  # 測試持久化
        db2 = InMemoryDatabaseAgent()  # 新代理
        assert await db2.count_programs() == 3  # 驗證數量
        retrieved_prog2 = await db2.get_program("prog_002")  # 取得程式 2
        assert retrieved_prog2 is not None and retrieved_prog2.fitness_scores.get("correctness") == 0.9  # 驗證正確率

        best_correctness = await db.get_best_programs(task_id="test_task", limit=2, objective="correctness", sort_order="desc")  # 取得最佳正確率
        print(f"Best by correctness (desc): {[p.id for p in best_correctness]}")  # 印出結果
        assert len(best_correctness) == 2  # 驗證數量
        assert best_correctness[0].id == "prog_002"  # 驗證第一名
        assert best_correctness[1].id == "prog_003"  # 驗證第二名

        best_runtime_asc = await db.get_best_programs(task_id="test_task", limit=2, objective="runtime_ms", sort_order="asc")  # 取得最佳 runtime
        print(f"Best by runtime (asc): {[p.id for p in best_runtime_asc]}")  # 印出結果
        assert len(best_runtime_asc) == 2  # 驗證數量
        assert best_runtime_asc[0].id == "prog_002"  # 驗證第一名
        # runtime 升冪：prog3 (70ms) 優於 prog1 (100ms)  # 驗證第二名
        assert best_runtime_asc[1].id == "prog_003"  # 驗證第二名
        
        next_gen_task_programs = await db.get_programs_for_next_generation(task_id="test_task", generation_size=2)  # 取得下一代候選
        assert len(next_gen_task_programs) == 2  # 驗證數量
        for p in next_gen_task_programs:  # 逐一檢查
            assert p.task_id == "test_task"  # 驗證 task_id

        await db.clear_database()  # 清空資料庫
        assert await db.count_programs() == 0  # 驗證清空
        assert not os.path.exists(settings.DATABASE_PATH) or os.path.getsize(settings.DATABASE_PATH) < 5  # 空 JSON 可能是 {} 或 []
        print("InMemoryDatabaseAgent with JSON persistence tests passed.")  # 印出成功

        # 清理測試檔  # 刪除檔案
        if os.path.exists(settings.DATABASE_PATH):  # 若存在
            os.remove(settings.DATABASE_PATH)  # 刪除

    asyncio.run(test_db())  # 執行測試
