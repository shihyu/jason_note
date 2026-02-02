"""
提示詞設計代理：產生初始提示、突變提示與修錯提示。  # 檔案用途
"""
from typing import Optional, Dict, Any  # 型別註解
import logging  # 日誌系統

from core.interfaces import PromptDesignerInterface, Program, TaskDefinition, BaseAgent  # 匯入介面與資料結構

logger = logging.getLogger(__name__)  # 取得本模組 logger

class PromptDesignerAgent(PromptDesignerInterface, BaseAgent):  # 提示詞設計代理
    def __init__(self, task_definition: TaskDefinition):  # 初始化
        super().__init__()  # 呼叫基底初始化
        self.task_definition = task_definition  # 保存任務定義
        logger.info(f"PromptDesignerAgent initialized for task: {self.task_definition.id}")  # 記錄初始化

    def design_initial_prompt(self) -> str:  # 產生初始提示
        logger.info(f"Designing initial prompt for task: {self.task_definition.id}")  # 記錄任務 ID
                                                           
        expert_knowledge_section = ""  # 預設無專家知識段落
        if self.task_definition.expert_knowledge:  # 若任務有專家知識
            # 需要提供專家知識時，加入額外段落  # 提示強化
            expert_knowledge_section = f"Relevant Expert Knowledge or Context:\\n{self.task_definition.expert_knowledge}\\n\\n"  # 組合專家段落

        prompt = (  # 組合完整提示
            f"You are an expert Python programmer. Your task is to write a Python function based on the following specifications.\\n\\n"  # 角色與目標
            f"Task Description: {self.task_definition.description}\\n\\n"  # 任務描述
            f"{expert_knowledge_section}"  # 專家知識
            f"Function to Implement: `{self.task_definition.function_name_to_evolve}`\\n\\n"  # 函式名稱
            f"Input/Output Examples:\n"  # 範例標題
                                         
            f"{self._format_input_output_examples()}\n\n"  # 插入測試範例
            f"Evaluation Criteria: {self.task_definition.evaluation_criteria}\n\n"  # 評估準則
            f"Allowed Standard Library Imports: {self.task_definition.allowed_imports}. Do not use any other external libraries or packages.\n\n"  # 限制 import
            f"Your Response Format:\n"  # 回覆格式要求
            f"Please provide *only* the complete Python code for the function `{self.task_definition.function_name_to_evolve}`. "  # 僅輸出程式碼
            f"The code should be self-contained or rely only on the allowed imports. "  # 自洽限制
            f"Do not include any surrounding text, explanations, comments outside the function, or markdown code fences (like ```python or ```)."  # 禁止多餘輸出
        )
        logger.debug(f"Designed initial prompt:\n--PROMPT START--\n{prompt}\n--PROMPT END--")  # 記錄提示內容
        return prompt  # 回傳提示

    def _format_input_output_examples(self) -> str:  # 格式化測試範例
        """格式化輸入/輸出案例以放入提示詞。"""  # 方法用途
        examples = []  # 收集範例字串
        
        # YAML 格式（tests）  # 新格式
        if self.task_definition.tests:  # 若有 tests
            for test_group in self.task_definition.tests:  # 逐一測試群組
                for test_case in test_group['test_cases']:  # 逐一測試案例
                    if 'output' in test_case:  # 直接輸出比對
                        examples.append(f"Input: {test_case['input']}\nOutput: {test_case['output']}")  # 加入範例
                    elif 'validation_func' in test_case:  # 自訂驗證
                        examples.append(f"Input: {test_case['input']}\nValidation: {test_case['validation_func']}")  # 加入範例
        
        # 舊版格式（input_output_examples）  # 舊格式
        elif self.task_definition.input_output_examples:  # 若有舊格式
            for example in self.task_definition.input_output_examples:  # 逐一案例
                input_str = str(example.get('input'))  # 取得輸入
                output_str = str(example.get('output'))  # 取得輸出
                examples.append(f"Input: {input_str}\nOutput: {output_str}")  # 加入範例
        
        if not examples:  # 若無任何範例
            return "No input/output examples provided."  # 回傳預設訊息
        
        return "\n\n".join(examples)  # 用空行分隔

    def _format_evaluation_feedback(self, program: Program, evaluation_feedback: Optional[Dict[str, Any]]) -> str:  # 格式化評估回饋
        if not evaluation_feedback:  # 若沒有回饋
            return "No detailed evaluation feedback is available for the previous version of this code. Attempt a general improvement or refinement."  # 回傳預設訊息

        correctness = evaluation_feedback.get("correctness_score", None)  # 取得正確率
        runtime = evaluation_feedback.get("runtime_ms", None)  # 取得執行時間
        errors = evaluation_feedback.get("errors", [])  # 取得錯誤列表                          
                                                                                               
        stderr = evaluation_feedback.get("stderr", None)  # 取得 stderr

        # 將評估結果整理成可讀摘要  # 生成摘要
        feedback_parts = []  # 摘要段落列表
        if correctness is not None:  # 若有正確率
            feedback_parts.append(f"- Correctness Score: {correctness*100:.2f}%")  # 加入正確率
        if runtime is not None:  # 若有執行時間
            feedback_parts.append(f"- Runtime: {runtime:.2f} ms")  # 加入時間
        
        if errors:  # 若有錯誤
            error_messages = "\n".join([f"  - {e}" for e in errors])  # 格式化錯誤列表
            feedback_parts.append(f"- Errors Encountered During Evaluation:\n{error_messages}")  # 加入錯誤摘要
        elif stderr:  # 若有 stderr
            feedback_parts.append(f"- Standard Error Output During Execution:\n{stderr}")  # 加入 stderr 摘要
        elif correctness is not None and correctness < 1.0:  # 若正確率未滿
            feedback_parts.append("- The code did not achieve 100% correctness but produced no explicit errors or stderr. Review logic for test case failures.")  # 建議檢查邏輯
        elif correctness == 1.0:  # 若正確率滿分
            feedback_parts.append("- The code achieved 100% correctness. Consider optimizing for efficiency or exploring alternative correct solutions.")  # 建議優化
        
        if not feedback_parts:  # 若沒有任何摘要
             return "The previous version was evaluated, but no specific feedback details were captured. Try a general improvement."  # 回傳預設

        return "Summary of the previous version's evaluation:\n" + "\n".join(feedback_parts)  # 回傳摘要

    def design_mutation_prompt(self, program: Program, evaluation_feedback: Optional[Dict[str, Any]] = None) -> str:  # 產生突變提示
        logger.info(f"Designing mutation prompt for program: {program.id} (Generation: {program.generation})")  # 記錄程式 ID
        logger.debug(f"Parent program code (to be mutated):\\n{program.code}")  # 記錄父代程式碼
        
        expert_knowledge_section = ""  # 預設無專家知識
        if self.task_definition.expert_knowledge:  # 若有專家知識
            expert_knowledge_section = f"Relevant Expert Knowledge or Context (applies to the overall task):\\n{self.task_definition.expert_knowledge}\\n\\n"  # 組合段落

        feedback_summary = self._format_evaluation_feedback(program, evaluation_feedback)  # 產生評估摘要
        logger.debug(f"Formatted evaluation feedback for prompt:\n{feedback_summary}")  # 記錄摘要

        # 要求模型以差異區塊格式回傳  # diff 規格
        diff_instructions = (  # 組合 diff 指令
            "Your Response Format:\n"
            "Propose improvements to the 'Current Code' below by providing your changes as a sequence of diff blocks. "
            "Each diff block must follow this exact format:\n"
            "<<<<<<< SEARCH\n"
            "# Exact original code lines to be found and replaced\n"
            "=======\n"
            "# New code lines to replace the original\n"
            ">>>>>>> REPLACE\n\n"
            "- The SEARCH block must be an *exact* segment from the 'Current Code'. Do not paraphrase or shorten it."
            "- If you are adding new code where nothing existed, the SEARCH block can be a comment indicating the location, or an adjacent existing line."
            "- If you are deleting code, the REPLACE block should be empty."
            "- Provide all suggested changes as one or more such diff blocks. Do not include any other text, explanations, or markdown outside these blocks."
        )

        prompt = (  # 組合最終提示
            f"You are an expert Python programmer. Your task is to improve an existing Python function based on its previous performance and the overall goal.\\n\\n"  # 角色與任務
            f"Overall Task Description: {self.task_definition.description}\\n\\n"  # 任務描述
            f"{expert_knowledge_section}"  # 專家知識
            f"Function to Improve: `{self.task_definition.function_name_to_evolve}`\\n\\n"  # 待改善函式名稱
            f"Allowed Standard Library Imports: {self.task_definition.allowed_imports}. Do not use other external libraries or packages.\n\n"  # import 限制
            f"Current Code (Version from Generation {program.generation}):\n"  # 當前程式碼標題
            f"```python\n{program.code}\n```\n\n"  # 插入程式碼
            f"Evaluation Feedback on the 'Current Code':\n{feedback_summary}\n\n"  # 評估回饋
            f"Your Improvement Goal:\n"  # 改善目標
            f"Based on the task, the 'Current Code', and its 'Evaluation Feedback', your goal is to propose modifications to improve the function `{self.task_definition.function_name_to_evolve}`. "  # 目標敘述
            f"Prioritize fixing any errors or correctness issues. If correct, focus on improving efficiency or exploring alternative robust logic. "  # 優先順序
            f"Consider the original evaluation criteria: {self.task_definition.evaluation_criteria}\n\n"  # 評估準則
            f"{diff_instructions}"  # diff 規則
        )
        logger.debug(f"Designed mutation prompt (requesting diff):\n--PROMPT START--\n{prompt}\n--PROMPT END--")  # 記錄提示
        return prompt  # 回傳提示

    def design_bug_fix_prompt(self, program: Program, error_message: str, execution_output: Optional[str] = None) -> str:  # 產生修錯提示
        logger.info(f"Designing bug-fix prompt for program: {program.id} (Generation: {program.generation})")  # 記錄程式 ID
        logger.debug(f"Buggy program code:\\n{program.code}")  # 記錄錯誤程式碼
        
        expert_knowledge_section = ""  # 預設無專家知識
        if self.task_definition.expert_knowledge:  # 若有專家知識
            expert_knowledge_section = f"Relevant Expert Knowledge or Context (applies to the overall task):\\n{self.task_definition.expert_knowledge}\\n\\n"  # 組合段落

        logger.debug(f"Primary error message: {error_message}")  # 記錄主要錯誤
        if execution_output:  # 若有額外輸出
            logger.debug(f"Additional execution output (stdout/stderr): {execution_output}")  # 記錄 stdout/stderr

        # 加入執行輸出（若有）以協助修錯  # 組合輸出段落
        output_segment = f"Execution Output (stdout/stderr that might be relevant):\n{execution_output}\n" if execution_output else "No detailed execution output was captured beyond the error message itself.\n"  # 組合輸出說明
        
        # 要求修錯仍以差異區塊格式輸出  # diff 規格
        diff_instructions = (  # diff 規則
            "Your Response Format:\n"
            "Propose fixes to the 'Buggy Code' below by providing your changes as a sequence of diff blocks. "
            "Each diff block must follow this exact format:\n"
            "<<<<<<< SEARCH\n"
            "# Exact original code lines to be found and replaced\n"
            "=======\n"
            "# New code lines to replace the original\n"
            ">>>>>>> REPLACE\n\n"
            "- The SEARCH block must be an *exact* segment from the 'Buggy Code'."
            "- Provide all suggested changes as one or more such diff blocks. Do not include any other text, explanations, or markdown outside these blocks."
        )

        prompt = (  # 組合修錯提示
            f"You are an expert Python programmer. Your task is to fix a bug in an existing Python function.\\n\\n"  # 角色與任務
            f"Overall Task Description: {self.task_definition.description}\\n\\n"  # 任務描述
            f"{expert_knowledge_section}"  # 專家知識
            f"Function to Fix: `{self.task_definition.function_name_to_evolve}`\\n\\n"  # 函式名稱
            f"Allowed Standard Library Imports: {self.task_definition.allowed_imports}. Do not use other external libraries or packages.\n\n"  # import 限制
            f"Buggy Code (Version from Generation {program.generation}):\n"  # 錯誤程式碼標題
            f"```python\n{program.code}\n```\n\n"  # 插入程式碼
            f"Error Encountered: {error_message}\n"  # 錯誤訊息
            f"{output_segment}\n"  # 輸出段落
            f"Your Goal:\n"  # 目標說明
            f"Analyze the 'Buggy Code', the 'Error Encountered', and any 'Execution Output' to identify and fix the bug(s). "  # 分析與修正
            f"The corrected function must adhere to the overall task description and allowed imports.\n\n"  # 約束
            f"{diff_instructions}"  # diff 規則
        )
        logger.debug(f"Designed bug-fix prompt (requesting diff):\n--PROMPT START--\n{prompt}\n--PROMPT END--")  # 記錄提示
        return prompt  # 回傳提示

    async def execute(self, *args, **kwargs) -> Any:  # 通用執行入口（不支援）
        # 提示設計代理不提供通用 execute，必須呼叫特定方法  # 使用方式說明
        raise NotImplementedError("PromptDesignerAgent.execute() is not the primary way to use this agent. Call specific design methods.")  # 拋出錯誤

                
if __name__ == '__main__':  # 直接執行時的示例
    logging.basicConfig(level=logging.DEBUG)  # 設定日誌等級

    sample_task_def = TaskDefinition(  # 建立範例任務
        id="task_001_designer_test",  # 任務 ID
        description="Create a Python function `sum_list(numbers)` that returns the sum of a list of integers. Handle empty lists by returning 0.",  # 任務描述
        function_name_to_evolve="sum_list",  # 待演化函式
        input_output_examples=[  # 測試案例
            {"input": [1, 2, 3], "output": 6},  # 範例 1
            {"input": [], "output": 0}  # 範例 2
        ],
        evaluation_criteria="Ensure correctness for all cases, including empty lists.",  # 評估標準
        allowed_imports=["math"]  # 允許 import
    )
    designer = PromptDesignerAgent(task_definition=sample_task_def)  # 初始化提示設計代理

    print("--- Initial Prompt ---")  # 印出標題
    initial_prompt = designer.design_initial_prompt()  # 產生初始提示
    print(initial_prompt)  # 印出提示

    sample_program_mutation = Program(  # 建立突變範例程式
        id="prog_mut_001",  # 程式 ID
        code="def sum_list(numbers):\n  # 邏輯稍有偏差\n  s = 0\n  for n in numbers:\n    s += n\n  return s if numbers else 1",  # 程式碼
        fitness_scores={"correctness_score": 0.5, "runtime_ms": 5.0},  # 適應度
        generation=1,  # 世代
        errors=["Test case failed: Input [], Expected 0, Got 1"],  # 錯誤訊息
        status="evaluated"  # 狀態
    )
    mutation_feedback = {  # 組合突變回饋
        "correctness_score": sample_program_mutation.fitness_scores["correctness_score"],  # 正確率
        "runtime_ms": sample_program_mutation.fitness_scores["runtime_ms"],  # 執行時間
        "errors": sample_program_mutation.errors,  # 錯誤列表
        "stderr": None  # stderr
    }
    print("\n--- Mutation Prompt (Requesting Diff) ---")  # 印出標題
    mutation_prompt = designer.design_mutation_prompt(sample_program_mutation, evaluation_feedback=mutation_feedback)  # 產生突變提示
    print(mutation_prompt)  # 印出提示

    sample_program_buggy = Program(  # 建立修錯範例程式
        id="prog_bug_002",  # 程式 ID
        code="def sum_list(numbers):\n  # 有 bug，會造成 TypeError\n  if not numbers:\n    return 0\n  return sum(numbers) + \"oops\"",  # 程式碼
        fitness_scores={"correctness_score": 0.0, "runtime_ms": 2.0},  # 適應度
        generation=2,  # 世代
        errors=["TypeError: unsupported operand type(s) for +: 'int' and 'str'"],  # 錯誤訊息
        status="evaluated"  # 狀態
    )
    print("\n--- Bug-Fix Prompt (Requesting Diff) ---")  # 印出標題
    bug_fix_prompt = designer.design_bug_fix_prompt(sample_program_buggy, error_message=sample_program_buggy.errors[0], execution_output="TypeError occurred during summation.")  # 產生修錯提示
    print(bug_fix_prompt)  # 印出提示
