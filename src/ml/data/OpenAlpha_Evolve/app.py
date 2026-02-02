"""
OpenAlpha_Evolve 的 Gradio Web 介面。  # 檔案用途
"""
import gradio as gr  # Gradio UI
import asyncio  # 非同步工具
import json  # JSON 解析
import os  # 路徑操作
import sys  # 系統工具
import time  # 時間工具
import logging  # 日誌系統
from datetime import datetime  # 日期時間
from dotenv import load_dotenv  # 讀取 .env

                                               
# 將專案根目錄加入模組搜尋路徑  # 確保本地模組可匯入
project_root = os.path.abspath(os.path.dirname(__file__))  # 計算根路徑
if project_root not in sys.path:  # 若尚未加入
    sys.path.insert(0, project_root)  # 加入 sys.path

                                           
# 讀取 .env  # 環境變數
load_dotenv()  # 載入環境變數

from core.interfaces import TaskDefinition, Program  # 任務與程式資料結構
from task_manager.agent import TaskManagerAgent  # 任務管理代理
from config import settings  # 設定

                                                
class StringIOHandler(logging.Handler):  # 自訂記憶體 log handler
    def __init__(self):  # 初始化
        super().__init__()  # 呼叫基底
        self.log_capture = []  # 記錄列表
        
    def emit(self, record):  # 收到 log 時
        try:  # 嘗試格式化
            msg = self.format(record)  # 格式化 log
            self.log_capture.append(msg)  # 保存 log
        except Exception:  # 例外處理
            self.handleError(record)  # 交由 logging 處理
    
    def get_logs(self):  # 取得所有 log
        return "\n".join(self.log_capture)  # 合併成字串
    
    def clear(self):  # 清空 log
        self.log_capture = []  # 重置列表

                         
# 記憶體日誌處理器（供 UI 顯示）  # UI log
string_handler = StringIOHandler()  # 建立 handler
string_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))  # 設定格式

                            
# 根 logger 增加記憶體 handler  # root logger
root_logger = logging.getLogger()  # 取得 root logger
root_logger.addHandler(string_handler)  # 加入 handler

                           
# 控制台 handler  # stdout log
console_handler = logging.StreamHandler(sys.stdout)  # 建立 stdout handler
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))  # 設定格式
root_logger.addHandler(console_handler)  # 加入 handler

                                   
# 預設 logger  # 本模組 logger
logger = logging.getLogger(__name__)  # 取得 logger
logger.setLevel(logging.DEBUG)  # 設定等級

                                                     
# 提高關鍵模組的 log 等級  # 方便除錯
for module in ['task_manager.agent', 'code_generator.agent', 'evaluator_agent.agent', 'database_agent.agent', 
              'selection_controller.agent', 'prompt_designer.agent']:  # 模組列表
    logging.getLogger(module).setLevel(logging.DEBUG)  # 設為 DEBUG

                         

                                              
# 儲存最近一次的結果  # UI 結果快取
current_results = []  # 初始化

async def run_evolution(  # 執行演化流程
    task_id,  # 任務 ID
    description,  # 任務描述
    function_name,  # 函式名稱
    examples_json,  # JSON 測試範例
    allowed_imports_text,  # 允許 import 文字
    population_size,  # 族群大小
    generations,  # 世代數
    num_islands,  # 島嶼數
    migration_frequency,  # 遷移頻率
    migration_rate  # 遷移比例
):
    """以指定參數執行演化流程。"""  # 方法用途
    progress = gr.Progress()  # 建立進度條
                         
    # 清空之前的 log  # UI 重新開始
    string_handler.clear()  # 清空記憶體 log
    
    try:
                                         
        try:  # 嘗試解析 JSON
            examples = json.loads(examples_json)  # 解析 JSON 字串
            if not isinstance(examples, list):  # 若非 list
                return "Error: Examples must be a JSON list of objects with 'input' and 'output' keys."  # 回傳錯誤
            
                                   
            # 驗證例子格式  # 檢查每個案例
            for i, example in enumerate(examples):  # 逐一檢查
                if not isinstance(example, dict) or "input" not in example or "output" not in example:  # 若格式錯誤
                    return f"Error in example {i+1}: Each example must be an object with 'input' and 'output' keys."  # 回傳錯誤
        except json.JSONDecodeError:  # JSON 解析錯誤
            return "Error: Examples must be valid JSON. Please check the format."  # 回傳錯誤
        
                               
        # 解析允許的 import 清單  # 轉成 list
        allowed_imports = [imp.strip() for imp in allowed_imports_text.split(",") if imp.strip()]  # 拆分文字
        
                                 
        # 將 UI 的參數同步至 settings  # 更新設定
        settings.POPULATION_SIZE = int(population_size)  # 族群大小
        settings.GENERATIONS = int(generations)  # 世代數
        settings.NUM_ISLANDS = int(num_islands)  # 島嶼數
        settings.MIGRATION_FREQUENCY = int(migration_frequency)  # 遷移頻率
        settings.MIGRATION_RATE = float(migration_rate)  # 遷移比例
        
                                  
        # 建立任務定義  # TaskDefinition
        task = TaskDefinition(  # 建立任務
            id=task_id,  # 任務 ID
            description=description,  # 任務描述
            function_name_to_evolve=function_name,  # 函式名稱
            input_output_examples=examples,  # 測試案例
            allowed_imports=allowed_imports  # 允許 import
        )
        
                                    
        # UI 進度回呼  # 更新進度
        async def progress_callback(generation, max_generations, stage, message=""):  # 進度回呼
                                                              
                                                                       
            stage_weight = 0.25  # 階段權重
            gen_progress = generation + (stage * stage_weight)  # 計算世代進度
            total_progress = gen_progress / max_generations  # 計算總進度
            
            # 更新 Gradio 進度條
            progress(min(total_progress, 0.99), f"Generation {generation}/{max_generations}: {message}")  # 更新 UI
            
            # 同步寫入 log
            logger.info(f"Progress: Generation {generation}/{max_generations} - {message}")  # 記錄進度
            
            # 讓 UI 有時間刷新
            await asyncio.sleep(0.1)  # 小延遲以刷新 UI
        
                                                                  
        # 建立任務管理代理  # TaskManager
        task_manager = TaskManagerAgent(task_definition=task)  # 初始化代理
        
                                                                                      
        # 將進度回呼掛到任務管理代理  # 掛載回呼
        task_manager.progress_callback = progress_callback  # 設定回呼
        
                                                                
        # 初始化進度條  # UI 初始化
        progress(0, "Starting evolutionary process...")  # 設定初始進度
        
                                                                      
        # 透過 log 內容推進 UI 進度
        class GenerationProgressListener(logging.Handler):  # 進度監聽器
            def __init__(self):  # 初始化
                super().__init__()  # 呼叫基底
                self.current_gen = 0  # 當前世代
                self.max_gen = settings.GENERATIONS  # 最大世代
                
            def emit(self, record):  # 接收 log
                try:  # 嘗試解析
                    msg = record.getMessage()  # 取得訊息
                                                            
                    # 解析不同階段的 log 以更新進度
                    if "--- Generation " in msg:
                        gen_parts = msg.split("Generation ")[1].split("/")[0]  # 解析世代字串
                        try:
                            self.current_gen = int(gen_parts)  # 更新當前世代
                                                 
                            # 非阻塞更新進度
                            asyncio.create_task(  # 非阻塞更新進度
                                progress_callback(
                                    self.current_gen, 
                                    self.max_gen, 
                                    0, 
                                    "Starting generation"
                                )
                            )
                        except ValueError:
                            pass
                    elif "Evaluating population" in msg:  # 評估中
                        # 評估中
                        asyncio.create_task(  # 更新進度
                            progress_callback(
                                self.current_gen, 
                                self.max_gen, 
                                1, 
                                "Evaluating population"
                            )
                        )
                    elif "Selected " in msg and " parents" in msg:  # 選父母
                        # 選父母
                        asyncio.create_task(  # 更新進度
                            progress_callback(
                                self.current_gen, 
                                self.max_gen, 
                                2, 
                                "Selected parents"
                            )
                        )
                    elif "Generated " in msg and " offspring" in msg:  # 生成子代
                        # 生成子代
                        asyncio.create_task(  # 更新進度
                            progress_callback(
                                self.current_gen, 
                                self.max_gen, 
                                3, 
                                "Generated offspring"
                            )
                        )
                except Exception:  # 任意錯誤
                    pass  # 忽略
        
                                   
        # 安裝 log 監聽器
        progress_listener = GenerationProgressListener()  # 建立監聽器
        progress_listener.setLevel(logging.INFO)  # 設定等級
        root_logger.addHandler(progress_listener)  # 加入 handler
        
        try:
                                              
            # 執行演化流程
            best_programs = await task_manager.execute()  # 執行演化
            progress(1.0, "Evolution completed!")  # 完成進度
            
                                       
            # 保存結果以供 UI 讀取
            global current_results  # 使用全域變數
            current_results = best_programs if best_programs else []  # 更新結果
            
                            
            if best_programs:  # 若有結果
                result_text = f"✅ Evolution completed successfully! Found {len(best_programs)} solution(s).\n\n"  # 組合結果
                for i, program in enumerate(best_programs):  # 逐一輸出
                    result_text += f"### Solution {i+1}\n"  # 標題
                    result_text += f"- ID: {program.id}\n"  # ID
                    result_text += f"- Fitness: {program.fitness_scores}\n"  # 適應度
                    result_text += f"- Generation: {program.generation}\n"  # 世代
                    result_text += f"- Island ID: {program.island_id}\n\n"  # 島嶼
                    result_text += "```python\n" + program.code + "\n```\n\n"  # 程式碼
                return result_text  # 回傳結果
            else:  # 無結果
                return "❌ Evolution completed, but no suitable solutions were found."  # 回傳無解
        finally:
            # 移除 log 監聽器
            root_logger.removeHandler(progress_listener)  # 移除 handler
    
    except Exception as e:  # 捕捉例外
        import traceback  # 匯入 traceback
        return f"Error during evolution: {str(e)}\n\n{traceback.format_exc()}"  # 回傳錯誤

def get_code(solution_index):  # 取得指定解
    """取得指定解的程式碼。"""  # 方法用途
    try:  # 嘗試取得
        if current_results and 0 <= solution_index < len(current_results):  # 索引有效
            program = current_results[solution_index]  # 取得程式
            return program.code  # 回傳程式碼
        return "No solution available at this index."  # 無解
    except Exception as e:  # 任意錯誤
        return f"Error retrieving solution: {str(e)}"  # 回傳錯誤

                                   
# 預設 Fibonacci 範例  # UI 預設案例
FIB_EXAMPLES = '''[
    {"input": [0], "output": 0},
    {"input": [1], "output": 1},
    {"input": [5], "output": 5},
    {"input": [10], "output": 55}
]'''

def set_fib_example():  # 設定範例任務
    """將 UI 填入 Fibonacci 範例任務。"""  # 方法用途
    return (  # 回傳 UI 欄位值
        "fibonacci_task",  # 任務 ID
        "Write a Python function that computes the nth Fibonacci number (0-indexed), where fib(0)=0 and fib(1)=1.",  # 描述
        "fibonacci",  # 函式名稱
        FIB_EXAMPLES,  # 範例 JSON
        ""  # 允許 import
    )

                             
# 建立 Gradio 介面  # UI 主體
with gr.Blocks(title="OpenAlpha_Evolve") as demo:  # 建立 Blocks
    gr.Markdown("# 🧬 OpenAlpha_Evolve: Autonomous Algorithm Evolution")  # 標題
    gr.Markdown("""  # 說明文字
    * **Custom Tasks:** Write your own problem definition, examples, and allowed imports in the fields below.
    * **Multi-Model Support:** Additional language model backends coming soon.
    * **Evolutionary Budget:** For novel, complex solutions consider using large budgets (e.g., 100+ generations and population sizes of hundreds or thousands).
    * **Island Model:** The population is divided into islands that evolve independently, with periodic migration between them.
    """)
    
    with gr.Row():  # 主排版 Row
        with gr.Column(scale=1):  # 左側欄位
            # 任務定義區塊  # 輸入區
            gr.Markdown("## Task Definition")  # 區塊標題
            
            task_id = gr.Textbox(  # 任務 ID 輸入
                label="Task ID", 
                placeholder="e.g., fibonacci_task",
                value="fibonacci_task"
            )
            
            description = gr.Textbox(  # 任務描述輸入
                label="Task Description", 
                placeholder="Describe the problem clearly...",
                value="Write a Python function that computes the nth Fibonacci number (0-indexed), where fib(0)=0 and fib(1)=1.",
                lines=5
            )
            
            function_name = gr.Textbox(  # 函式名稱輸入
                label="Function Name to Evolve", 
                placeholder="e.g., fibonacci",
                value="fibonacci"
            )
            
            examples_json = gr.Code(  # JSON 範例輸入
                label="Input/Output Examples (JSON)",
                language="json",
                value=FIB_EXAMPLES,
                lines=10
            )
            
            allowed_imports = gr.Textbox(  # 允許 import
                label="Allowed Imports (comma-separated)",
                placeholder="e.g., math",
                value=""
            )
            
            with gr.Row():  # 族群與世代 Row
                population_size = gr.Slider(  # 族群大小
                    label="Population Size",
                    minimum=2, 
                    maximum=10, 
                    value=3, 
                    step=1
                )
                
                generations = gr.Slider(  # 世代數
                    label="Generations",
                    minimum=1, 
                    maximum=5, 
                    value=2, 
                    step=1
                )
            
            with gr.Row():  # 島嶼參數 Row
                num_islands = gr.Slider(  # 島嶼數
                    label="Number of Islands",
                    minimum=1,
                    maximum=5,
                    value=3,
                    step=1
                )
                
                migration_frequency = gr.Slider(  # 遷移頻率
                    label="Migration Frequency (generations)",
                    minimum=1,
                    maximum=5,
                    value=2,
                    step=1
                )
                
                migration_rate = gr.Slider(  # 遷移比例
                    label="Migration Rate",
                    minimum=0.1,
                    maximum=0.5,
                    value=0.2,
                    step=0.1
                )
            
            # 範例按鈕  # UI 按鈕列
            with gr.Row():  # 按鈕列
                example_btn = gr.Button("📘 Fibonacci Example")  # 範例按鈕
            
            run_btn = gr.Button("🚀 Run Evolution", variant="primary")  # 執行按鈕
        
        with gr.Column(scale=1):  # 右側欄位
            with gr.Tab("Results"):  # 結果分頁
                results_text = gr.Markdown("Evolution results will appear here...")  # 結果顯示
            
                                                                  
    
                    
    # 綁定按鈕事件  # 事件綁定
    example_btn.click(  # 範例按鈕
        set_fib_example,  # 回呼函式
        outputs=[task_id, description, function_name, examples_json, allowed_imports]  # 輸出欄位
    )
    
    run_evolution_event = run_btn.click(  # 綁定執行按鈕
        run_evolution,  # 執行回呼
        inputs=[  # 輸入欄位
            task_id, 
            description, 
            function_name, 
            examples_json,
            allowed_imports,
            population_size, 
            generations,
            num_islands,
            migration_frequency,
            migration_rate
        ],
        outputs=results_text  # 輸出欄位
    )

                
if __name__ == "__main__":  # 直接執行時
    # 啟動 Gradio 服務  # 啟動 UI
    demo.launch(share=True)  # 啟動 Gradio
