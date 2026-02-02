import logging  # 日誌模組
import asyncio  # 非同步工具
import uuid  # 產生唯一 ID
from typing import List, Dict, Any, Optional  # 型別註解

from core.interfaces import (  # 匯入核心介面與資料結構
    TaskManagerInterface, TaskDefinition, Program, BaseAgent,  # 代理與資料類型
    PromptDesignerInterface, CodeGeneratorInterface, EvaluatorAgentInterface,  # 子代理介面
    DatabaseAgentInterface, SelectionControllerInterface  # 資料庫與選擇控制介面
)
from config import settings  # 匯入設定

from prompt_designer.agent import PromptDesignerAgent  # 提示設計代理
from code_generator.agent import CodeGeneratorAgent  # 程式碼生成代理
from evaluator_agent.agent import EvaluatorAgent  # 評估代理
from database_agent.agent import InMemoryDatabaseAgent  # 記憶體資料庫代理
from selection_controller.agent import SelectionControllerAgent  # 選擇控制代理

logger = logging.getLogger(__name__)  # 取得本模組 logger

class TaskManagerAgent(TaskManagerInterface):  # 任務管理代理
    def __init__(self, task_definition: TaskDefinition, config: Optional[Dict[str, Any]] = None):  # 初始化
        super().__init__(config)  # 呼叫基底初始化
        self.task_definition = task_definition  # 保存任務定義
        # 依序初始化各子代理：提示設計、程式碼生成、評估、資料庫與選擇器  # 子代理建構
        self.prompt_designer: PromptDesignerInterface = PromptDesignerAgent(task_definition=self.task_definition)  # 提示設計代理
        self.code_generator: CodeGeneratorInterface = CodeGeneratorAgent()  # 程式碼生成代理
        self.evaluator: EvaluatorAgentInterface = EvaluatorAgent(task_definition=self.task_definition)  # 評估代理
        
        # 簡化版資料庫初始化（以記憶體為主，並可落盤）  # 建立資料庫代理
        self.database: DatabaseAgentInterface = InMemoryDatabaseAgent()  # 記憶體資料庫
        logger.info(f"Using {settings.DATABASE_TYPE} database (InMemoryDatabaseAgent).")  # 記錄使用的 DB
            
        self.selection_controller: SelectionControllerInterface = SelectionControllerAgent()  # 選擇控制器

        self.population_size = settings.POPULATION_SIZE  # 族群大小
        self.num_generations = settings.GENERATIONS  # 世代數
        self.num_parents_to_select = self.population_size // 2  # 每代選父母數
        self.num_islands = settings.NUM_ISLANDS  # 島嶼數
        self.programs_per_island = self.population_size // self.num_islands  # 每島個體數

    async def initialize_population(self) -> List[Program]:  # 初始化族群
        logger.info(f"Initializing population for task: {self.task_definition.id}")  # 記錄任務 ID
        initial_population = []  # 初始族群列表
        
        # 初始族群用較便宜的模型，擴大探索  # 模型策略
        initial_model = settings.LLM_SECONDARY_MODEL  # 取得次模型
        logger.info(f"Using model '{initial_model}' for initial population generation.")  # 記錄使用模型

        # 產生初始個體  # 建立 LLM 生成任務
        tasks = []  # 生成任務列表
        for i in range(self.population_size):  # 迭代族群大小
            initial_prompt = self.prompt_designer.design_initial_prompt()  # 生成初始提示
            tasks.append(self.code_generator.generate_code(initial_prompt, model_name=initial_model, temperature=0.8))  # 加入生成任務

        generated_codes = await asyncio.gather(*tasks)  # 並行取得 LLM 結果
        for i, generated_code in enumerate(generated_codes):  # 逐一包裝成 Program
            program_id = f"{self.task_definition.id}_gen0_prog{i}"  # 產生程式 ID
            logger.debug(f"Generated initial program {i+1}/{self.population_size} with id {program_id}")  # 記錄 ID
            program = Program(  # 建立 Program 物件
                id=program_id,  # 設定 ID
                code=generated_code,  # 設定程式碼
                generation=0,  # 世代 0
                status="unevaluated"  # 尚未評估
            )
            initial_population.append(program)  # 加入族群
            await self.database.save_program(program)  # 存入資料庫

        # 依島嶼模型初始化分群  # 建立島嶼
        self.selection_controller.initialize_islands(initial_programs=initial_population)  # 初始化島嶼
        
        logger.info(f"Initialized population with {len(initial_population)} programs across {self.num_islands} islands.")  # 記錄初始化完成
        return initial_population  # 回傳初始族群

    async def evaluate_population(self, population: List[Program]) -> List[Program]:  # 評估族群
        logger.info(f"Evaluating population of {len(population)} programs.")  # 記錄族群大小
        evaluated_programs = []  # 評估結果列表
        # 只評估尚未評估的個體  # 避免重算
        evaluation_tasks = [self.evaluator.evaluate_program(prog, self.task_definition) for prog in population if prog.status != "evaluated"]  # 建立評估任務
        
        results = await asyncio.gather(*evaluation_tasks, return_exceptions=True)  # 並行評估
        
        for i, result in enumerate(results):  # 逐一處理結果
            original_program = population[i]  # 對應原始程式
            if isinstance(result, Exception):  # 若評估出錯
                logger.error(f"Error evaluating program {original_program.id}: {result}", exc_info=result)  # 記錄錯誤
                original_program.status = "failed_evaluation"  # 設為失敗
                original_program.errors.append(str(result))  # 記錄錯誤訊息
                evaluated_programs.append(original_program)  # 加入結果
            else:  # 正常評估
                evaluated_programs.append(result)  # 加入結果
            await self.database.save_program(evaluated_programs[-1])  # 更新資料庫
            
        logger.info(f"Finished evaluating population. {len(evaluated_programs)} programs processed.")  # 記錄評估完成
        return evaluated_programs  # 回傳評估後族群

    async def manage_evolutionary_cycle(self):  # 管理演化主流程
        logger.info(f"Starting evolutionary cycle for task: {self.task_definition.description[:50]}...")  # 記錄任務摘要
        current_population = await self.initialize_population()  # 初始化族群
        current_population = await self.evaluate_population(current_population)  # 評估初始族群

        for gen in range(1, self.num_generations + 1):  # 迭代每一世代
            logger.info(f"--- Generation {gen}/{self.num_generations} ---")  # 記錄世代

            # 依島嶼模型選擇父母  # 選擇父母
            parents = self.selection_controller.select_parents(current_population, self.num_parents_to_select)  # 選父母
            if not parents:  # 若無父母
                logger.warning(f"Generation {gen}: No parents selected. Ending evolution early.")  # 記錄警告
                break  # 終止演化
            logger.info(f"Generation {gen}: Selected {len(parents)} parents.")  # 記錄父母數

            # 產生子代  # 子代生成
            offspring_population = []  # 子代列表
            num_offspring_per_parent = (self.population_size + len(parents) - 1) // len(parents)  # 平均子代數
            
            generation_tasks = []  # 子代生成任務
            for i, parent in enumerate(parents):  # 逐一父母
                for j in range(num_offspring_per_parent):  # 為每個父母產生多個子代
                    child_id = f"{self.task_definition.id}_gen{gen}_child{i}_{j}"  # 子代 ID
                    generation_tasks.append(self.generate_offspring(parent, gen, child_id))  # 加入生成任務
            
            generated_offspring_results = await asyncio.gather(*generation_tasks, return_exceptions=True)  # 並行生成

            for result in generated_offspring_results:  # 逐一處理子代
                if isinstance(result, Exception):  # 若生成錯誤
                    logger.error(f"Error generating offspring: {result}", exc_info=result)  # 記錄錯誤
                elif result:  # 若結果有效
                    offspring_population.append(result)  # 加入子代
                    await self.database.save_program(result)  # 儲存子代

            logger.info(f"Generation {gen}: Generated {len(offspring_population)} offspring.")  # 記錄子代數
            if not offspring_population:  # 若無子代
                logger.warning(f"Generation {gen}: No offspring generated. May indicate issues with LLM or prompting.")  # 記錄警告
                if not parents:  # 若也沒有父母
                    break  # 終止

            # 評估子代  # 執行評估
            offspring_population = await self.evaluate_population(offspring_population)  # 評估子代

            # 依島嶼模型選擇存活者  # 選擇存活者
            current_population = self.selection_controller.select_survivors(current_population, offspring_population, self.population_size)  # 更新族群
            logger.info(f"Generation {gen}: New population size: {len(current_population)}.")  # 記錄族群大小

            # 記錄本世代最佳解  # 取本代最佳
            best_program_this_gen = sorted(  # 排序取得最佳
                current_population,  # 族群
                key=lambda p: (p.fitness_scores.get("correctness", -1), -p.fitness_scores.get("runtime_ms", float('inf'))),  # 先正確率再時間
                reverse=True  # 由大到小
            )
            if best_program_this_gen:  # 若有結果
                logger.info(f"Generation {gen}: Best program: ID={best_program_this_gen[0].id}, Fitness={best_program_this_gen[0].fitness_scores}")  # 記錄最佳
            else:  # 若沒有結果
                logger.warning(f"Generation {gen}: No programs in current population after survival selection.")  # 記錄警告
                break  # 終止

        logger.info("Evolutionary cycle completed.")  # 記錄演化完成
        final_best = await self.database.get_best_programs(task_id=self.task_definition.id, limit=1, objective="correctness")  # 取得全域最佳
        if final_best:  # 若有最佳解
            logger.info(f"Overall Best Program: {final_best[0].id}, Code:\n{final_best[0].code}\nFitness: {final_best[0].fitness_scores}")  # 記錄結果
        else:  # 若無最佳解
            logger.info("No best program found at the end of evolution.")  # 記錄無結果
        return final_best  # 回傳最佳解

    async def generate_offspring(self, parent: Program, generation_num: int, child_id: str) -> Optional[Program]:  # 產生子代
        logger.debug(f"Generating offspring from parent {parent.id} for generation {generation_num}")  # 記錄父代與世代
        
        prompt_type = "mutation"  # 預設為突變
        # 預設使用主模型（錯誤修正或高品質突變）  # 模型策略
        chosen_model = settings.LLM_PRIMARY_MODEL  # 先選主模型

        if parent.errors and parent.fitness_scores.get("correctness", 1.0) < settings.BUG_FIX_CORRECTNESS_THRESHOLD:  # 判斷是否走修錯流程
            primary_error = parent.errors[0]  # 取第一個錯誤
            execution_details = None  # 預設無執行輸出
            if len(parent.errors) > 1 and isinstance(parent.errors[1], str) and ("stdout" in parent.errors[1].lower() or "stderr" in parent.errors[1].lower()):  # 若錯誤含 stdout/stderr
                execution_details = parent.errors[1]  # 取執行輸出
            
            mutation_prompt = self.prompt_designer.design_bug_fix_prompt(  # 產生修錯提示
                program=parent,  # 傳入父代
                error_message=primary_error,  # 傳入錯誤訊息
                execution_output=execution_details  # 傳入執行輸出
            )
            logger.info(f"Attempting bug fix for parent {parent.id} using diff. Model: {chosen_model}. Error: {primary_error}")  # 記錄修錯
            prompt_type = "bug_fix"  # 設定提示類型
            # 修錯使用主模型  # 保持 chosen_model
        else:
            # 依父母適應度決定突變模型  # 模型選擇策略
            if parent.fitness_scores.get("correctness", 0.0) >= settings.HIGH_FITNESS_THRESHOLD_FOR_PRIMARY_LLM:  # 高適應度
                # 高適應度維持主模型  # 不變
                logger.info(f"Parent {parent.id} has high fitness, using primary model {chosen_model} for mutation.")  # 記錄使用主模型
            else:
                # 低適應度使用次模型以降低成本  # 省成本
                chosen_model = settings.LLM_SECONDARY_MODEL  # 改用次模型
                logger.info(f"Parent {parent.id} has lower fitness, using secondary model {chosen_model} for mutation.")  # 記錄使用次模型

            feedback = {  # 組合評估回饋
                "errors": parent.errors,  # 錯誤列表
                "correctness_score": parent.fitness_scores.get("correctness"),  # 正確率
                "runtime_ms": parent.fitness_scores.get("runtime_ms")  # 執行時間
            }
            feedback = {k: v for k, v in feedback.items() if v is not None}  # 去除空值

            mutation_prompt = self.prompt_designer.design_mutation_prompt(program=parent, evaluation_feedback=feedback)  # 產生突變提示
            logger.info(f"Attempting mutation for parent {parent.id} using diff. Model: {chosen_model}")  # 記錄突變
        
        # 產生新程式碼（或 diff）並套用  # 呼叫 LLM
        generated_code = await self.code_generator.execute(  # 執行生成
            prompt=mutation_prompt,  # 提示詞
            model_name=chosen_model,  # 模型名稱
            temperature=0.75,  # 取樣溫度
            output_format="diff",  # 要求 diff
            parent_code_for_diff=parent.code  # 父代程式碼
        )

        if not generated_code.strip():  # 若為空
            logger.warning(f"Offspring generation for parent {parent.id} ({prompt_type}) resulted in empty code/diff. Skipping.")  # 記錄警告
            return None  # 不產生子代
        
        if generated_code == parent.code:  # 若無變化
            logger.warning(f"Offspring generation for parent {parent.id} ({prompt_type}) using diff resulted in no change to the code. Skipping.")  # 記錄警告
            return None  # 不產生子代
        
        if "<<<<<<< SEARCH" in generated_code and "=======" in generated_code and ">>>>>>> REPLACE" in generated_code:  # 若看起來是 raw diff
            logger.warning(f"Offspring generation for parent {parent.id} ({prompt_type}) seems to have returned raw diff. LLM or diff application may have failed. Skipping. Content:\n{generated_code[:500]}")  # 記錄警告
            return None  # 不產生子代
        
        if "# Error:" in generated_code[:100]:  # 若 LLM 回傳錯誤訊息
            logger.warning(f"Failed to generate valid code for offspring of {parent.id} ({prompt_type}). LLM Output indicates error: {generated_code[:200]}")  # 記錄警告
            return None  # 不產生子代

        offspring = Program(  # 建立子代 Program
            id=child_id,  # 子代 ID
            code=generated_code,  # 子代程式碼
            generation=generation_num,  # 所屬世代
            parent_id=parent.id,  # 父代 ID
            island_id=parent.island_id,  # 繼承父代的島嶼
            status="unevaluated"  # 尚未評估
        )
        logger.info(f"Successfully generated offspring {offspring.id} from parent {parent.id} ({prompt_type}).")  # 記錄成功
        return offspring  # 回傳子代

    async def execute(self) -> Any:  # 通用執行入口
        return await self.manage_evolutionary_cycle()  # 呼叫主流程

if __name__ == '__main__':  # 直接執行時
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # 簡易日誌設定

    task_manager = TaskManagerAgent(task_definition=sample_task)

    sample_task = TaskDefinition(
        id="sum_list_task_001",
        description="Write a Python function called `solve(numbers)` that takes a list of integers `numbers` and returns their sum. The function should handle empty lists correctly by returning 0.",
        input_output_examples=[
            {"input": [1, 2, 3], "output": 6},
            {"input": [], "output": 0},
            {"input": [-1, 0, 1], "output": 0},
            {"input": [10, 20, 30, 40, 50], "output": 150}
        ],
        evaluation_criteria={"target_metric": "correctness", "goal": "maximize"},
        initial_code_prompt = "Please provide a Python function `solve(numbers)` that sums a list of integers. Handle empty lists by returning 0."
    )
    
    task_manager.num_generations = 3
    task_manager.population_size = 5
    task_manager.num_parents_to_select = 2

    async def run_task():
        try:
            best_programs = await task_manager.manage_evolutionary_cycle()
            if best_programs:
                print(f"\n*** Evolution Complete! Best program found: ***")
                print(f"ID: {best_programs[0].id}")
                print(f"Generation: {best_programs[0].generation}")
                print(f"Fitness: {best_programs[0].fitness_scores}")
                print(f"Code:\n{best_programs[0].code}")
            else:
                print("\n*** Evolution Complete! No suitable program was found. ***")
        except Exception as e:
            logger.error("An error occurred during the task management cycle.", exc_info=True)

    asyncio.run(run_task()) 
