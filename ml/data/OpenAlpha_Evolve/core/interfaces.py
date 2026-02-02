from abc import ABC, abstractmethod  # 抽象基底類別與抽象方法
from typing import List, Dict, Any, Optional, Union  # 型別註解
from dataclasses import dataclass, field  # 資料類別工具
import time  # 時間戳

@dataclass  # 標記為資料類別
class Program:  # 候選程式（個體）
    """單一候選程式的資料結構（個體）。"""  # 類別用途
    id: str  # 程式 ID
    code: str  # 程式碼內容
    fitness_scores: Dict[str, float] = field(default_factory=dict)  # 適應度指標
    generation: int = 0  # 所屬世代
    parent_id: Optional[str] = None  # 父代 ID
    island_id: Optional[int] = None  # 所屬島嶼
    errors: List[str] = field(default_factory=list)  # 錯誤訊息列表
    status: str = "unevaluated"  # 狀態（未評估/已評估/失敗）
    created_at: float = field(default_factory=lambda: time.time())  # 追蹤個體建立時間
    task_id: Optional[str] = None  # 任務 ID

@dataclass  # 標記為資料類別
class TaskDefinition:  # 任務定義
    """任務定義（要演化的問題描述與測試規格）。"""  # 類別用途
    id: str  # 任務 ID
    description: str  # 任務描述
    function_name_to_evolve: Optional[str] = None  # 若只演化單一函式可使用
    target_file_path: Optional[str] = None  # 需演化之程式碼所在檔案路徑
    evolve_blocks: Optional[List[Dict[str, Any]]] = None  # 指定檔案內要演化的區塊
    # 例如：[{\"block_id\": \"optimizer_logic\", \"start_marker\": \"# EVOLVE-BLOCK-START optimizer\", \"end_marker\": \"# EVOLVE-BLOCK-END optimizer\"}]  # 區塊格式示例
    input_output_examples: Optional[List[Dict[str, Any]]] = None  # 直接 I/O 測試
    evaluation_criteria: Optional[Dict[str, Any]] = None  # 評估準則
    initial_code_prompt: Optional[str] = "Provide an initial Python solution for the following problem:"  # 初始提示
    allowed_imports: Optional[List[str]] = None  # 允許 import
    tests: Optional[List[Dict[str, Any]]] = None  # 測試群組列表，可含層級與測試案例
    expert_knowledge: Optional[str] = None  # 專家知識或可用片段

class BaseAgent(ABC):  # 抽象基底代理
    """所有代理的基底類別。"""  # 類別用途
    @abstractmethod  # 必須實作
    def __init__(self, config: Optional[Dict[str, Any]] = None):  # 初始化
        self.config = config or {}  # 保存設定

    @abstractmethod  # 必須實作
    async def execute(self, *args, **kwargs) -> Any:  # 通用執行入口
        """代理的主要執行入口。"""  # 方法用途
        pass  # 交由子類實作

class TaskManagerInterface(BaseAgent):  # 任務管理介面
    @abstractmethod  # 必須實作
    async def manage_evolutionary_cycle(self):  # 演化流程主入口
        pass  # 交由子類實作

class PromptDesignerInterface(BaseAgent):  # 提示詞設計介面
    @abstractmethod  # 必須實作
    def design_initial_prompt(self, task: TaskDefinition) -> str:  # 初始提示
        pass  # 交由子類實作

    @abstractmethod  # 必須實作
    def design_mutation_prompt(self, task: TaskDefinition, parent_program: Program, evaluation_feedback: Optional[Dict] = None) -> str:  # 突變提示
        pass  # 交由子類實作

    @abstractmethod  # 必須實作
    def design_bug_fix_prompt(self, task: TaskDefinition, program: Program, error_info: Dict) -> str:  # 修錯提示
        pass  # 交由子類實作

class CodeGeneratorInterface(BaseAgent):  # 程式碼生成介面
    @abstractmethod  # 必須實作
    async def generate_code(self, prompt: str, model_name: Optional[str] = None, temperature: Optional[float] = 0.7, output_format: str = "code") -> str:  # 生成程式碼
        pass  # 交由子類實作

class EvaluatorAgentInterface(BaseAgent):  # 評估代理介面
    @abstractmethod  # 必須實作
    async def evaluate_program(self, program: Program, task: TaskDefinition) -> Program:  # 評估程式
        pass  # 交由子類實作

class DatabaseAgentInterface(BaseAgent):  # 資料庫代理介面
    @abstractmethod  # 必須實作
    async def save_program(self, program: Program):  # 儲存程式
        pass  # 交由子類實作

    @abstractmethod  # 必須實作
    async def get_program(self, program_id: str) -> Optional[Program]:  # 取得程式
        pass  # 交由子類實作

    @abstractmethod  # 必須實作
    async def get_best_programs(self, task_id: str, limit: int = 10, objective: Optional[str] = None) -> List[Program]:  # 取得最佳程式
        pass  # 交由子類實作
    
    @abstractmethod  # 必須實作
    async def get_programs_for_next_generation(self, task_id: str, generation_size: int) -> List[Program]:  # 取得下一代候選
        pass  # 交由子類實作

class SelectionControllerInterface(BaseAgent):  # 選擇控制介面
    @abstractmethod  # 必須實作
    def select_parents(self, evaluated_programs: List[Program], num_parents: int) -> List[Program]:  # 選父母
        pass  # 交由子類實作

    @abstractmethod  # 必須實作
    def select_survivors(self, current_population: List[Program], offspring_population: List[Program], population_size: int) -> List[Program]:  # 選存活者
        pass  # 交由子類實作

    @abstractmethod  # 必須實作
    def initialize_islands(self, initial_programs: List[Program]) -> None:  # 初始化島嶼
        pass  # 交由子類實作

class RLFineTunerInterface(BaseAgent):  # 強化學習微調介面
    @abstractmethod  # 必須實作
    async def update_policy(self, experience_data: List[Dict]):  # 更新策略
        pass  # 交由子類實作

class MonitoringAgentInterface(BaseAgent):  # 監控代理介面
    @abstractmethod  # 必須實作
    async def log_metrics(self, metrics: Dict):  # 記錄指標
        pass  # 交由子類實作

    @abstractmethod  # 必須實作
    async def report_status(self):  # 回報狀態
        pass  # 交由子類實作

                                                                      
