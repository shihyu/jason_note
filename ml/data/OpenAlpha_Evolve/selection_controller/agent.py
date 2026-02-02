"""
選擇控制代理：負責父母選擇、存活者選擇與島嶼遷移。  # 檔案用途
"""
import random  # 隨機工具
import logging  # 日誌系統
from typing import List, Dict, Any, Optional  # 型別註解

from core.interfaces import SelectionControllerInterface, Program, BaseAgent  # 匯入介面與資料結構
from config import settings  # 匯入設定

logger = logging.getLogger(__name__)  # 取得本模組 logger

class Island:  # 島嶼資料結構
    def __init__(self, island_id: int, initial_programs: Optional[List[Program]] = None):  # 初始化
        self.island_id = island_id  # 島嶼 ID
        self.programs = initial_programs or []  # 島嶼內的程式列表
        self.generation = 0  # 島嶼內部世代計數
        self.best_fitness = 0.0  # 島嶼歷史最佳適應度
        self.last_improvement_generation = 0  # 最後改進世代
        
        if settings.DEBUG:  # 若開啟 debug
            logger.debug(f"Initializing Island {island_id} with {len(self.programs)} programs")  # 記錄初始化
        
        for program in self.programs:  # 逐一分配島嶼
            program.island_id = island_id  # 設定島嶼 ID
            # 單一個體重新播種（遷移）時保留原世代；  # 世代設定策略
            # 若為新島嶼初始化，且世代未設定，則使用島嶼起始世代。  # 重新設定
            if len(self.programs) > 1 and (program.generation is None or program.generation == 0):  # 若是新島且未設定世代
                program.generation = self.generation  # 島嶼目前世代（新島為 0）
                if settings.DEBUG:  # 若開啟 debug
                    logger.debug(f"Set generation for program {program.id} to {self.generation}")  # 記錄世代設定

    def get_best_program(self) -> Optional[Program]:  # 取得島嶼最佳程式
        if not self.programs:  # 若島嶼為空
            return None  # 回傳 None
        # 依正確率、執行時間、世代與建立時間排序  # 排序策略
        best_program = max(  # 取最大值
            self.programs,  # 島嶼程式列表
            key=lambda p: (  # 排序鍵
                p.fitness_scores.get("correctness", 0.0),  # 正確率越高越好
                -p.fitness_scores.get("runtime_ms", float('inf')),  # 執行時間越短越好
                -p.generation,  # 世代越早越好
                -p.created_at  # 建立時間越早越好（決勝）
            )
        )
        if settings.DEBUG:  # 若開啟 debug
            logger.debug(f"Island {self.island_id} best program: ID={best_program.id}, "
                        f"Correctness={best_program.fitness_scores.get('correctness')}, "
                        f"Runtime={best_program.fitness_scores.get('runtime_ms')}, "
                        f"Generation={best_program.generation}")  # 記錄最佳
        return best_program  # 回傳最佳

    def update_metrics(self):  # 更新島嶼指標
        best_program = self.get_best_program()  # 取得最佳程式
        if best_program:  # 若有最佳程式
            current_best = best_program.fitness_scores.get("correctness", 0.0)  # 取得正確率
            if current_best > self.best_fitness:  # 若有改進
                self.best_fitness = current_best  # 更新最佳分數
                self.last_improvement_generation = self.generation  # 更新改進世代
                if settings.DEBUG:  # 若開啟 debug
                    logger.debug(f"Island {self.island_id} new best fitness: {self.best_fitness} "
                               f"at generation {self.generation}")  # 記錄改進
        self.generation += 1  # 世代遞增
        if settings.DEBUG:  # 若開啟 debug
            logger.debug(f"Island {self.island_id} generation incremented to {self.generation}")  # 記錄世代

class SelectionControllerAgent(SelectionControllerInterface, BaseAgent):  # 選擇控制代理
    def __init__(self):  # 初始化
        super().__init__()  # 呼叫基底初始化
        self.elitism_count = settings.ELITISM_COUNT  # 菁英數量
        self.num_islands = settings.NUM_ISLANDS  # 島嶼數量
        self.migration_interval = settings.MIGRATION_INTERVAL  # 遷移間隔
        self.islands: Dict[int, Island] = {}  # 島嶼容器
        self.current_generation = 0  # 目前世代
        logger.info(f"SelectionControllerAgent initialized with {self.num_islands} islands and elitism_count: {self.elitism_count}")  # 記錄初始化

    def initialize_islands(self, initial_programs: List[Program]) -> None:  # 初始化島嶼
        """以初始族群建立島嶼。"""  # 方法用途
        programs_per_island = len(initial_programs) // self.num_islands  # 每島個體數
        if settings.DEBUG:  # 若開啟 debug
            logger.debug(f"Initializing {self.num_islands} islands with {programs_per_island} programs each")  # 記錄初始化
        
        for i in range(self.num_islands):  # 逐島建立
            start_idx = i * programs_per_island  # 起始索引
            end_idx = start_idx + programs_per_island if i < self.num_islands - 1 else len(initial_programs)  # 結束索引
            island_programs = initial_programs[start_idx:end_idx]  # 切分島嶼程式
            self.islands[i] = Island(i, island_programs)  # 建立 Island
            if settings.DEBUG:  # 若開啟 debug
                logger.debug(f"Initialized Island {i} with {len(island_programs)} programs")  # 記錄結果

    def select_parents(self, population: List[Program], num_parents: int) -> List[Program]:  # 選父母
        # population 為全域族群，但選擇以島嶼為主  # 設計說明
        logger.debug(f"Starting parent selection. Global population size: {len(population)}, Num parents to select: {num_parents}")  # 記錄開始
        
        if num_parents == 0:  # 若不選父母
            logger.info("Number of parents to select is 0. Returning empty list.")  # 記錄狀態
            return []  # 回傳空列表

        all_potential_parents: List[Program] = []  # 保留空集合（目前未用）
        parents_per_island = max(1, num_parents // self.num_islands)  # 每島至少 1 個父母
        remaining_parents_to_select = num_parents  # 剩餘父母名額

        # 先收集各島菁英  # 菁英保留
        all_elites = []  # 菁英列表
        for island_id, island in self.islands.items():  # 逐島
            if not island.programs:  # 若島嶼為空
                logger.warning(f"Island {island_id} is empty. Skipping for elite selection.")  # 記錄警告
                continue  # 跳過

            sorted_island_programs = sorted(  # 島內排序
                island.programs,  # 島內程式
                key=lambda p: (p.fitness_scores.get("correctness", 0.0), -p.fitness_scores.get("runtime_ms", float('inf')), -p.generation),  # 排序鍵
                reverse=True  # 由大到小
            )
            for i in range(min(len(sorted_island_programs), self.elitism_count)):  # 取前 N 個
                 all_elites.append(sorted_island_programs[i])  # 加入菁英
        
        # 去重菁英（遷移可能造成重複）  # 去重
        unique_elites = []  # 去重後列表
        seen_elite_ids = set()  # 已看過 ID
        for elite in sorted(all_elites, key=lambda p: (p.fitness_scores.get("correctness", 0.0), -p.fitness_scores.get("runtime_ms", float('inf')), -p.generation), reverse=True):  # 再排序
            if elite.id not in seen_elite_ids:  # 若未重複
                unique_elites.append(elite)  # 加入
                seen_elite_ids.add(elite.id)  # 記錄 ID
        
        # 直接選入前 N 個菁英  # 菁英直通
        selected_parents = unique_elites[:min(num_parents, len(unique_elites))]  # 取前 N
        remaining_parents_to_select = num_parents - len(selected_parents)  # 更新剩餘名額
        parent_ids_so_far = {p.id for p in selected_parents}  # 已選父母 ID

        if settings.DEBUG:  # 若開啟 debug
            logger.debug(f"Selected {len(selected_parents)} elite parents globally: {[p.id for p in selected_parents]}")  # 記錄選擇

        if remaining_parents_to_select <= 0:  # 若已滿
            return selected_parents  # 回傳父母

        # 其餘名額以輪盤法從非菁英候選中選取  # 輪盤選擇
        all_roulette_candidates_with_island = []  # 候選集合
        for island_id, island in self.islands.items():  # 逐島搜尋
            if not island.programs:  # 若島嶼為空
                continue  # 跳過
            
            # 先排序後挑出非菁英  # 排序
            sorted_island_programs = sorted(  # 排序島內程式
                island.programs,  # 程式列表
                key=lambda p: (p.fitness_scores.get("correctness", 0.0), -p.fitness_scores.get("runtime_ms", float('inf')), -p.generation),  # 排序鍵
                reverse=True  # 由大到小
            )
            for program in sorted_island_programs:  # 逐一加入候選
                if program.id not in parent_ids_so_far:  # 避免重複選到菁英
                    all_roulette_candidates_with_island.append(program)  # 加入候選
        
        # 去除重複候選（遷移可能造成重複）  # 去重
        unique_roulette_candidates = []  # 去重後列表
        seen_roulette_ids = set()  # 已看過 ID
        for cand in all_roulette_candidates_with_island:  # 逐一檢查
            if cand.id not in parent_ids_so_far and cand.id not in seen_roulette_ids:  # 若未重複
                 unique_roulette_candidates.append(cand)  # 加入候選
                 seen_roulette_ids.add(cand.id)  # 記錄 ID

        if not unique_roulette_candidates:  # 若無候選
            logger.warning("No more unique candidates for roulette selection.")  # 記錄警告
            return selected_parents  # 回傳已選父母

        # 對合併候選進行輪盤法  # 計算權重
        total_fitness_roulette = sum(p.fitness_scores.get("correctness", 0.0) + 0.0001 for p in unique_roulette_candidates)  # 加小常數避免全 0

        if total_fitness_roulette <= 0.0001 * len(unique_roulette_candidates):  # 幾乎全為 0
            num_to_select_randomly = min(remaining_parents_to_select, len(unique_roulette_candidates))  # 隨機數量
            random_parents_from_roulette = random.sample(unique_roulette_candidates, num_to_select_randomly)  # 隨機抽取
            selected_parents.extend(random_parents_from_roulette)  # 加入父母
            logger.debug(f"Selected {len(random_parents_from_roulette)} random parents due to low/zero total fitness in roulette pool.")  # 記錄隨機選擇
        else:
            for _ in range(remaining_parents_to_select):  # 逐一選父母
                if not unique_roulette_candidates: break  # 若候選用完
                pick = random.uniform(0, total_fitness_roulette)  # 隨機權重
                current_sum = 0  # 累積權重
                chosen_parent = None  # 選中父母
                for i, program in enumerate(unique_roulette_candidates):  # 逐一累計
                    current_sum += (program.fitness_scores.get("correctness", 0.0) + 0.0001)  # 加權
                    if current_sum >= pick:  # 命中
                        chosen_parent = program  # 設定父母
                        unique_roulette_candidates.pop(i)  # 避免重複選取
                        total_fitness_roulette -= (chosen_parent.fitness_scores.get("correctness", 0.0) + 0.0001)  # 更新總權重
                        break  # 跳出
                
                if chosen_parent:  # 若有選中
                    selected_parents.append(chosen_parent)  # 加入父母
                    parent_ids_so_far.add(chosen_parent.id)  # 追蹤已選父母
                    logger.debug(f"Selected parent via global roulette: {chosen_parent.id} from island {chosen_parent.island_id} with correctness {chosen_parent.fitness_scores.get('correctness')}")  # 記錄選擇
                elif unique_roulette_candidates:  # 例外時的備援選擇
                    fallback_parent = random.choice(unique_roulette_candidates)  # 隨機選一個
                    selected_parents.append(fallback_parent)  # 加入父母
                    unique_roulette_candidates.remove(fallback_parent)  # 移除候選
                    parent_ids_so_far.add(fallback_parent.id)  # 記錄 ID
                    logger.debug(f"Selected fallback parent via global roulette: {fallback_parent.id}")  # 記錄選擇
        
        logger.info(f"Selected {len(selected_parents)} parents in total.")  # 記錄父母數
        return selected_parents  # 回傳父母

    def select_survivors(self, current_population: List[Program], offspring_population: List[Program], population_size: int) -> List[Program]:
        """
        Select survivors for each island, combining current island members with their offspring.
        as island.programs is the source of truth for each island's current members.
        """
        if settings.DEBUG:  # 若開啟 debug
            logger.debug(f"Starting survivor selection. Offspring pop: {len(offspring_population)}, Target pop size: {population_size}")  # 記錄資訊
        
        # 更新島嶼統計  # 更新指標
        for island in self.islands.values():  # 逐島更新
            island.update_metrics()  # 更新指標

        # 檢查是否到遷移時機  # 判斷遷移
        if self.current_generation % self.migration_interval == 0:  # 是否到遷移世代
            if settings.DEBUG:  # 若開啟 debug
                logger.debug(f"Generation {self.current_generation}: Performing migration")  # 記錄遷移
            self._perform_migration()  # 執行遷移

        self.current_generation += 1  # 更新當前世代
        if settings.DEBUG:  # 若開啟 debug
            logger.debug(f"Generation incremented to {self.current_generation}")  # 記錄更新

        # 各島內選出存活者  # 存活者選擇
        all_survivors = []  # 存活者列表
        programs_per_island = population_size // self.num_islands  # 每島保留數

        for island_id, island in self.islands.items():  # 逐島選擇
            if settings.DEBUG:  # 若開啟 debug
                logger.debug(f"Processing Island {island_id} for survivor selection")  # 記錄島嶼
            
            # 取出當前島內成員  # 現存成員
            current_island_members = island.programs  # 成員列表
            
            # 取出屬於本島的子代  # 子代分配
            newly_generated_for_this_island = [  # 子代列表
                p for p in offspring_population if p.island_id == island_id  # 篩選島嶼
            ]
            
            if settings.DEBUG:  # 若開啟 debug
                logger.debug(f"Island {island_id}: {len(current_island_members)} current members, "
                           f"{len(newly_generated_for_this_island)} new offspring")  # 記錄成員數
            
            combined_population = current_island_members + newly_generated_for_this_island  # 合併族群
            if not combined_population:  # 若合併後為空
                island.programs = []  # 島嶼變成空
                if settings.DEBUG:  # 若開啟 debug
                    logger.debug(f"Island {island_id} became empty")  # 記錄空島
                continue  # 跳過

            # 依正確率、執行時間、世代排序  # 排序策略
            sorted_combined = sorted(  # 排序合併族群
                combined_population,  # 合併族群
                key=lambda p: (  # 排序鍵
                    p.fitness_scores.get("correctness", 0.0),  # 正確率越高越好
                    -p.fitness_scores.get("runtime_ms", float('inf')),  # 執行時間越短越好
                    -p.generation  # 世代越早越好
                ),
                reverse=True  # 由大到小
            )

            survivors = []  # 存活者列表
            seen_program_ids = set()  # 去重集合
            for program in sorted_combined:  # 逐一選擇
                if len(survivors) < programs_per_island:  # 若尚未達上限
                    if program.id not in seen_program_ids:  # 去除重複
                        survivors.append(program)  # 加入存活者
                        seen_program_ids.add(program.id)  # 記錄 ID
                        if settings.DEBUG:  # 若開啟 debug
                            logger.debug(f"Island {island_id} selected survivor: {program.id} "
                                       f"with correctness {program.fitness_scores.get('correctness')}")  # 記錄存活者
                else:  # 已滿
                    break  # 停止

            island.programs = survivors  # 更新島嶼程式
            all_survivors.extend(survivors)  # 合併存活者
            if settings.DEBUG:  # 若開啟 debug
                logger.debug(f"Island {island_id} final survivor count: {len(survivors)}")  # 記錄數量

        return all_survivors  # 回傳存活者

    def _perform_migration(self) -> None:  # 執行遷移
        """執行島嶼間遷移。"""  # 方法用途
        if settings.DEBUG:  # 若開啟 debug
            logger.debug("Starting migration process")  # 記錄遷移開始
        
        # 找出較弱的島嶼  # 評估島嶼
        island_performances = [(island_id, island.get_best_program().fitness_scores.get("correctness", 0.0) if island.get_best_program() else 0.0) 
                             for island_id, island in self.islands.items()]  # 計算每島表現
        sorted_islands = sorted(island_performances, key=lambda x: x[1])  # 依表現排序
        
        # 取表現較差的一半島嶼  # 分群
        num_islands_to_reseed = self.num_islands // 2  # 需要重播的島數
        underperforming_islands = [island_id for island_id, _ in sorted_islands[:num_islands_to_reseed]]  # 弱島
        surviving_islands = [island_id for island_id, _ in sorted_islands[num_islands_to_reseed:]]  # 強島
        
        if settings.DEBUG:  # 若開啟 debug
            logger.debug(f"Identified {len(underperforming_islands)} underperforming islands: {underperforming_islands}")  # 記錄弱島
            logger.debug(f"Identified {len(surviving_islands)} surviving islands: {surviving_islands}")  # 記錄強島
        
        # 從強島搬移最佳個體  # 遷移策略
        for underperforming_island_id in underperforming_islands:  # 逐一弱島
            if not surviving_islands:  # 正常不該發生
                logger.warning("No surviving islands to donate for migration.")  # 記錄警告
                break  # 終止

            # 隨機選一個強島作為捐贈者  # 隨機捐贈
            donor_island_id = random.choice(surviving_islands)  # 隨機選強島
            donor_island = self.islands[donor_island_id]  # 捐贈島
            recipient_island = self.islands[underperforming_island_id]  # 接收島
            
            # 取捐贈島最佳個體  # 取得最佳
            best_program_from_donor = donor_island.get_best_program()  # 取得最佳程式
            if best_program_from_donor:  # 若存在最佳程式
                # 若有共享物件風險，可改為 deep copy  # 物件共享
                migrant_program = best_program_from_donor  # 可視情況改為 deep copy
                migrant_program.island_id = underperforming_island_id  # 指派到新島
                # 這裡保留原世代（較溫和的遷移策略）  # 世代策略

                # 加入接收島，避免重複  # 去重
                if not any(p.id == migrant_program.id for p in recipient_island.programs):  # 若未重複
                    recipient_island.programs.append(migrant_program)  # 加入接收島
                    if settings.DEBUG:  # 若開啟 debug
                        logger.debug(f"Migrated program {migrant_program.id} (Correctness: {migrant_program.fitness_scores.get('correctness')}) "
                                   f"from island {donor_island_id} to island {underperforming_island_id}. "
                                   f"Recipient island size now: {len(recipient_island.programs)}")  # 記錄遷移
                else:  # 若重複
                    if settings.DEBUG:  # 若開啟 debug
                        logger.debug(f"Program {migrant_program.id} from donor island {donor_island_id} already exists in recipient {underperforming_island_id}. Skipped migration of this specific program.")  # 記錄跳過
            else:  # 若捐贈島無最佳程式
                if settings.DEBUG:  # 若開啟 debug
                    logger.debug(f"Donor island {donor_island_id} had no best program to migrate.")  # 記錄空捐贈

    async def execute(self, action: str, **kwargs) -> Any:  # 通用執行入口
        # BaseAgent 的通用介面，實際上多數行為直接呼叫具名方法  # 設計說明
        logger.warning(f"SelectionControllerAgent.execute called with action '{action}', but most actions are handled by specific methods.")  # 記錄警告
        if action == "initialize_islands_async_placeholder":  # 若未來需要 async 版本可在此擴充
            # await self.async_initialize_islands(kwargs['initial_programs'])  # 預留擴充
            pass  # 暫不處理
        raise NotImplementedError(f"The generic execute method is not fully implemented for specific action '{action}' in SelectionControllerAgent. Use direct methods.")  # 拋出錯誤

                
if __name__ == '__main__':
    import uuid  # 產生 UUID
    import random  # 隨機工具
    logging.basicConfig(level=logging.DEBUG)  # 設定日誌
    selector = SelectionControllerAgent()  # 建立選擇器

    # 建立測試用個體  # 測試資料
    programs = [  # 程式列表
        Program(
            id=str(uuid.uuid4()),  # 程式 ID
            code="c1",  # 程式碼
            fitness_scores={"correctness": 0.9, "runtime_ms": 100},  # 適應度
            status="evaluated",  # 狀態
            generation=0  # 世代
        ),
        Program(
            id=str(uuid.uuid4()),  # 程式 ID
            code="c2",  # 程式碼
            fitness_scores={"correctness": 1.0, "runtime_ms": 50},  # 適應度
            status="evaluated",  # 狀態
            generation=0  # 世代
        ),
        Program(
            id=str(uuid.uuid4()),  # 程式 ID
            code="c3",  # 程式碼
            fitness_scores={"correctness": 0.7, "runtime_ms": 200},  # 適應度
            status="evaluated",  # 狀態
            generation=0  # 世代
        ),
        Program(
            id=str(uuid.uuid4()),  # 程式 ID
            code="c4",  # 程式碼
            fitness_scores={"correctness": 1.0, "runtime_ms": 60},  # 適應度
            status="evaluated",  # 狀態
            generation=0  # 世代
        ),
        Program(
            id=str(uuid.uuid4()),  # 程式 ID
            code="c5",  # 程式碼
            fitness_scores={"correctness": 0.5},  # 適應度
            status="evaluated",  # 狀態
            generation=0  # 世代
        ),
        Program(
            id=str(uuid.uuid4()),  # 程式 ID
            code="c6",  # 程式碼
            status="unevaluated",  # 狀態
            generation=0  # 世代
        ),
    ]

    # 初始化島嶼  # 測試初始化
    selector.initialize_islands(programs)  # 建立島嶼
    print("\n--- Initial Island Distribution ---")  # 印出標題
    for island_id, island in selector.islands.items():  # 逐島列印
        print(f"Island {island_id}: {len(island.programs)} programs")  # 島嶼資訊
        for p in island.programs:  # 逐一程式
            print(f"  Program {p.id}: Gen={p.generation}, Correctness={p.fitness_scores.get('correctness')}, Runtime={p.fitness_scores.get('runtime_ms')}")  # 程式資訊

    print("\n--- Testing Parent Selection ---")  # 印出標題
    parents = selector.select_parents(programs, num_parents=3)  # 選父母
    for p in parents:  # 逐一父母
        print(f"Selected Parent: {p.id}, Island: {p.island_id}, Gen: {p.generation}, Correctness: {p.fitness_scores.get('correctness')}, Runtime: {p.fitness_scores.get('runtime_ms')}")  # 印出父母資訊

    print("\n--- Testing Survivor Selection ---")  # 印出標題
    current_pop = programs[:2]  # 當前族群
    offspring_pop = [  # 子代族群
        Program(
            id=str(uuid.uuid4()),  # 程式 ID
            code="off1",  # 程式碼
            fitness_scores={"correctness": 1.0, "runtime_ms": 40},  # 適應度
            status="evaluated",  # 狀態
            generation=1,  # 世代
            island_id=0  # 模擬島 0 的子代
        ),
        Program(
            id=str(uuid.uuid4()),  # 程式 ID
            code="off2",  # 程式碼
            fitness_scores={"correctness": 0.6, "runtime_ms": 10},  # 適應度
            status="evaluated",  # 狀態
            generation=1,  # 世代
            island_id=1  # 模擬島 1 的子代
        ),
    ]
    
    # 模擬多世代以測試遷移  # 測試遷移流程
    for gen in range(3):  # 模擬三代
        print(f"\n--- Generation {gen} ---")  # 印出世代
        survivors = selector.select_survivors(current_pop, offspring_pop, population_size=2)  # 選存活者
        print(f"Survivors after generation {gen}:")  # 印出標題
        for s in survivors:  # 逐一存活者
            print(f"  Survivor: {s.id}, Island: {s.island_id}, Gen: {s.generation}, Correctness: {s.fitness_scores.get('correctness')}, Runtime: {s.fitness_scores.get('runtime_ms')}")  # 印出資訊
        
        # 更新目前族群供下一代使用  # 更新族群
        current_pop = survivors  # 以存活者作為新族群
        # 建立新一代子代並遞增世代  # 準備下一代
        # 注意：gen + 2 是正確的，因為：  # 世代計算說明
        # - gen 從 0 開始  # 起始世代
        # - select_survivors 內部會遞增 current_generation  # 內部遞增
        # - 因此下一代應為 current_generation + 1  # 正確世代
        offspring_pop = [  # 產生新子代
            Program(
                id=str(uuid.uuid4()),  # 程式 ID
                code=f"off{gen}_{i}",  # 程式碼
                fitness_scores={"correctness": random.uniform(0.5, 1.0), "runtime_ms": random.randint(10, 200)},  # 隨機適應度
                status="evaluated",  # 狀態
                generation=gen + 2,  # 下一代正確世代
                island_id=i % selector.num_islands  # 分配島嶼
            )
            for i in range(2)  # 產生 2 個子代
        ]
