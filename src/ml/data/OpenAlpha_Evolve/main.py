"""
OpenAlpha_Evolve 的主進入點。  # 檔案用途說明
負責協調各代理並管理演化迴圈。  # 主責功能摘要
"""
import asyncio  # 非同步事件迴圈
import logging  # 日誌系統
import sys  # 系統相關功能
import os  # 路徑與環境操作
import yaml  # YAML 解析
import argparse  # CLI 參數解析
                                               
# 將專案根目錄加入模組搜尋路徑，確保本地套件可被正確匯入  # 說明用意
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # 計算專案根路徑
if project_root not in sys.path:  # 若尚未加入模組搜尋路徑
    sys.path.insert(0, project_root)  # 將根路徑插入 sys.path

from task_manager.agent import TaskManagerAgent  # 演化流程主控代理
from core.interfaces import TaskDefinition  # 任務定義資料結構
from config import settings  # 全域設定

                   
# 設定全域日誌格式與輸出位置  # 日誌初始化
logging.basicConfig(  # 設定 logging 系統
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),  # 設定日誌等級
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 設定日誌格式
    handlers=[  # 設定輸出來源
        logging.StreamHandler(sys.stdout),  # 輸出到 stdout
        logging.FileHandler(settings.LOG_FILE, mode="a")  # 輸出到檔案
    ]
)
logger = logging.getLogger(__name__)  # 取得本模組 logger

def load_task_from_yaml(yaml_path: str) -> tuple[list, str, str, str, list]:  # 定義 YAML 載入函式
    """從 YAML 檔載入任務設定與測試案例。"""  # 函式用途說明
    try:  # 捕捉解析時的例外
        with open(yaml_path, 'r') as f:  # 以讀取模式開啟 YAML
            data = yaml.safe_load(f)  # 解析 YAML 成 dict
            # 讀取任務基本設定  # 任務欄位
            task_id = data.get('task_id')  # 任務 ID
            task_description = data.get('task_description')  # 任務描述
            function_name = data.get('function_name')  # 待演化函式名稱
            allowed_imports = data.get('allowed_imports', [])  # 允許 import
            
            # 將 YAML 內的測試案例轉為 input_output_examples 格式  # 兼容舊格式
            input_output_examples = []  # 收集測試案例
            for test_group in data.get('tests', []):  # 逐一處理測試群組
                for test_case in test_group.get('test_cases', []):  # 逐一處理群組內測試
                    if 'output' in test_case:  # 若為直接輸出比對
                        input_output_examples.append({  # 新增測試案例
                            'input': test_case['input'],  # 測試輸入
                            'output': test_case['output']  # 期望輸出
                        })
                    elif 'validation_func' in test_case:  # 若為自訂驗證函式
                        input_output_examples.append({  # 新增測試案例
                            'input': test_case['input'],  # 測試輸入
                            'validation_func': test_case['validation_func']  # 驗證函式
                        })
            
            return input_output_examples, task_id, task_description, function_name, allowed_imports  # 回傳解析結果
    except Exception as e:  # 捕捉任何解析錯誤
        logger.error(f"Error loading task from YAML: {e}")  # 記錄錯誤
        return [], "", "", "", []  # 回傳空資料避免崩潰

async def main():  # 主程式入口（非同步）
    # 解析 CLI 參數  # 建立 CLI 參數解析器
    parser = argparse.ArgumentParser(description="Run OpenAlpha_Evolve with a specified YAML configuration file.")  # 初始化 parser
    parser.add_argument("yaml_path", type=str, help="Path to the YAML configuration file")  # 定義 YAML 路徑參數
    args = parser.parse_args()  # 解析 CLI 參數
    yaml_path = args.yaml_path  # 取得 YAML 路徑

    logger.info("Starting OpenAlpha_Evolve autonomous algorithmic evolution")  # 記錄啟動訊息
    logger.info(f"Configuration: Population Size={settings.POPULATION_SIZE}, Generations={settings.GENERATIONS}")  # 記錄設定

    # 從 YAML 載入任務設定與測試案例  # 解析任務
    test_cases, task_id, task_description, function_name, allowed_imports = load_task_from_yaml(yaml_path)  # 載入 YAML
    
    if not test_cases or not task_id or not task_description or not function_name:  # 檢查必要欄位
        logger.error("Missing required task configuration in YAML file. Exiting.")  # 記錄錯誤
        return  # 結束執行

    task = TaskDefinition(  # 建立任務定義
        id=task_id,  # 任務 ID
        description=task_description,  # 任務描述
        function_name_to_evolve=function_name,  # 待演化函式名稱
        input_output_examples=test_cases,  # 測試案例
        allowed_imports=allowed_imports  # 允許 import
    )

    # 建立任務管理代理並執行演化流程  # 啟動演化
    task_manager = TaskManagerAgent(task_definition=task)  # 初始化 TaskManager

    best_programs = await task_manager.execute()  # 執行演化並取得最佳解

    # 輸出最佳結果  # 結果輸出
    if best_programs:  # 若有找到最佳解
        logger.info(f"Evolutionary process completed. Best program(s) found: {len(best_programs)}")  # 記錄數量
        for i, program in enumerate(best_programs):  # 逐一輸出
            logger.info(f"Final Best Program {i+1} ID: {program.id}")  # 輸出 ID
            logger.info(f"Final Best Program {i+1} Fitness: {program.fitness_scores}")  # 輸出適應度
            logger.info(f"Final Best Program {i+1} Code:\n{program.code}")  # 輸出程式碼
    else:  # 若無合適解
        logger.info("Evolutionary process completed, but no suitable programs were found.")  # 記錄無結果

    logger.info("OpenAlpha_Evolve run finished.")  # 記錄結束

if __name__ == "__main__":  # 僅在直接執行時觸發
    asyncio.run(main())  # 啟動非同步主程式
