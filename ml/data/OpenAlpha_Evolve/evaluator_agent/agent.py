"""
評估代理：在隔離環境（Docker）中執行候選程式並計分。  # 檔案用途
"""
import asyncio  # 非同步工具
import json  # JSON 操作
import logging  # 日誌系統
import math  # 數學函式
import os  # 檔案與路徑操作
import sys  # 系統操作
import tempfile  # 暫存檔案
import time  # 時間相關
from typing import Optional, Dict, Any, Tuple, List  # 型別註解

from config import settings  # 匯入設定
from core.interfaces import EvaluatorAgentInterface, Program, TaskDefinition, BaseAgent  # 匯入介面與資料結構

logger = logging.getLogger(__name__)  # 取得本模組 logger

class EvaluatorAgent(EvaluatorAgentInterface, BaseAgent):  # 評估代理
    def __init__(self, task_definition: Optional[TaskDefinition] = None):  # 初始化
        super().__init__()  # 呼叫基底初始化
        self.task_definition = task_definition  # 保存任務定義
        self.evaluation_model_name = settings.EVALUATION_MODEL  # 評估模型名稱（目前未用於 eval）
        self.evaluation_timeout_seconds = settings.EVALUATION_TIMEOUT_SECONDS  # 評估超時
        logger.info(f"EvaluatorAgent initialized with model: {self.evaluation_model_name}, timeout: {self.evaluation_timeout_seconds}s")  # 記錄初始化
        if self.task_definition:  # 若有任務
            logger.info(f"EvaluatorAgent task_definition: {self.task_definition.id}")  # 記錄任務 ID

    def _check_syntax(self, code: str) -> List[str]:  # 語法檢查
        """先做語法檢查，避免無效程式進入執行階段。"""  # 方法用途
        errors = []  # 錯誤列表
        try:  # 嘗試 compile
            compile(code+"\n", "tmp.py", 'exec')  # 編譯程式碼
        except SyntaxError as e:  # 語法錯誤
            errors.append(f"SyntaxError: {e.msg} at line {e.lineno}, offset {e.offset}")  # 加入錯誤訊息
        except Exception as e:  # 其他錯誤
            errors.append(f"Unexpected error during syntax check: {str(e)}")  # 加入錯誤訊息
        return errors  # 回傳錯誤列表

    async def _execute_code_safely(  # 安全執行
        self,  # self
        code: str,  # 待執行程式碼
        task_for_examples: TaskDefinition,  # 測試用任務
        timeout_seconds: Optional[int] = None  # 超時設定
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:  # 回傳執行結果或錯誤
        """在 Docker 中安全執行程式，回傳結果或錯誤訊息。"""  # 方法用途
        timeout = timeout_seconds if timeout_seconds is not None else self.evaluation_timeout_seconds  # 決定超時
        results = {"test_outputs": [], "average_runtime_ms": 0.0}  # 初始化結果

        # 無測試案例時直接回傳  # 早期退出
        if not task_for_examples.input_output_examples:  # 若沒有測試案例
            logger.warning("No input/output examples provided to _execute_code_safely.")  # 記錄警告
            return results, "No test cases to run."  # 回傳空結果

        # 必須指定待測函式名稱  # 必要欄位檢查
        if not task_for_examples.function_name_to_evolve:  # 若未指定函式
            logger.error(f"Task {task_for_examples.id} does not specify 'function_name_to_evolve'. Cannot execute code.")  # 記錄錯誤
            return None, "Task definition is missing 'function_name_to_evolve'."  # 回傳錯誤

        temp_dir = tempfile.mkdtemp()  # 建立暫存資料夾
        temp_file_path = os.path.join(temp_dir, "temp_script.py")  # 暫存腳本路徑

        # 將特殊浮點值序列化（避免 JSON 問題）  # 內部工具
        def serialize_arg(arg):  # 參數序列化
            if isinstance(arg, (float, int)) and (arg == float('inf') or arg == float('-inf') or arg != arg):  # 特殊浮點
                return f"float('{str(arg)}')"  # 回傳 Python 表示
            return json.dumps(arg)  # 回傳 JSON


        # 將測試案例序列化為 Python 可用的字串  # JSON -> Python
        test_cases_str = json.dumps(task_for_examples.input_output_examples)  # 序列化
        test_cases_str = test_cases_str.replace('"Infinity"', 'float("inf")')  # 替換 Infinity
        test_cases_str = test_cases_str.replace('"-Infinity"', 'float("-inf")')  # 替換 -Infinity
        test_cases_str = test_cases_str.replace('"NaN"', 'float("nan")')  # 替換 NaN

        test_cases_str = test_cases_str.replace('true', 'True').replace('false', 'False').replace('null', 'None')  # JSON 布林/空值

        # 測試用執行腳本（將被寫入暫存檔並在 Docker 內執行）  # 建立腳本
        test_harness_code = f"""
import json
import time
import sys
import math  # 匯入 math 以支援 inf/nan

# 使用者程式（待測函式）
{code}

# 測試執行邏輯
results = []
total_execution_time = 0
num_tests = 0

# 測試用特殊常數
Infinity = float('inf')
NaN = float('nan')

test_cases = {test_cases_str} 
function_to_test_name = "{task_for_examples.function_name_to_evolve}"

# 確保 function_to_test 可在全域範圍取得
if function_to_test_name not in globals():
    # 若函式被定義在類別內（LLM 常見輸出），嘗試從類別找出
    # 這是簡易啟發式方法，必要時可再改良
    found_func = None
    for name, obj in list(globals().items()):
        if isinstance(obj, type):
            if hasattr(obj, function_to_test_name):
                method = getattr(obj, function_to_test_name)
                if callable(method):
                    globals()[function_to_test_name] = method
                    found_func = True
                    break
    if not found_func:
        print(json.dumps({{"error": f"Function '{{function_to_test_name}}' not found in the global scope or as a callable method of a defined class."}}))
        sys.exit(1)
        
function_to_test = globals()[function_to_test_name]

for i, test_case in enumerate(test_cases):
    input_args = test_case.get("input")
    
    start_time = time.perf_counter()
    try:
        if isinstance(input_args, list):
            actual_output = function_to_test(*input_args)
        elif isinstance(input_args, dict):
            actual_output = function_to_test(**input_args)
        elif input_args is None:
            actual_output = function_to_test()
        else:
            actual_output = function_to_test(input_args)
            
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000
        total_execution_time += execution_time_ms
        num_tests += 1
        results.append({{"test_case_id": i, "output": actual_output, "runtime_ms": execution_time_ms, "status": "success"}})
    except Exception as e:
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000
        error_output = {{
            "test_case_id": i,
            "error": str(e), 
            "error_type": type(e).__name__,
            "runtime_ms": execution_time_ms,
            "status": "error"
        }}
        try:
            json.dumps(error_output)
        except TypeError:
            error_output["error"] = "Unserializable error object"
        results.append(error_output)

final_output = {{"test_outputs": results}}
if num_tests > 0:
    final_output["average_runtime_ms"] = total_execution_time / num_tests

def custom_json_serializer(obj):
    if isinstance(obj, float):
        if obj == float('inf'):
            return 'Infinity'
        elif obj == float('-inf'):
            return '-Infinity'
        elif obj != obj:
            return 'NaN'
    raise TypeError(f"Object of type {{type(obj).__name__}} is not JSON serializable")

print(json.dumps(final_output, default=custom_json_serializer))
"""
        with open(temp_file_path, "w") as f:  # 開啟暫存檔
            f.write(test_harness_code)  # 寫入測試腳本

        # 產生唯一容器名稱，便於 timeout 時停止/刪除
        container_name = f"evaluator-{task_for_examples.id}-{time.time_ns()}"  # 生成容器名稱
        
        # Docker 命令組裝
        cmd = [  # Docker 命令列表
            "docker", "run",  # docker run
            "--rm",  # 執行後刪除容器
            "--name", container_name,  # 指定容器名稱
            "-i",  # 互動模式（stdin）
            # 視需要禁止網路
            # "-v", f"{os.path.abspath(temp_dir)}:/app/user_code",  # 動態加入 volume
            "-w", "/app/user_code",  # 工作目錄
            # settings.DOCKER_IMAGE_NAME,  # 動態加入鏡像名稱
            # "python", "temp_script.py"   # 動態加入執行指令
        ]

        if settings.DOCKER_NETWORK_DISABLED:  # 若禁止網路
            cmd.extend(["--network", "none"])  # 加入 network none
        
        # 加入 volume 掛載、鏡像名稱與執行命令
        cmd.extend([  # 加入 volume 與執行命令
            "-v", f"{os.path.abspath(temp_dir)}:/app/user_code",  # 掛載暫存目錄
            settings.DOCKER_IMAGE_NAME,  # Docker 映像
            "python", "temp_script.py"  # 執行腳本
        ])

        proc = None  # 預設沒有子行程
        try:  # 嘗試執行 Docker
            logger.debug(f"Executing code in Docker: {' '.join(cmd)}")  # 記錄命令
            start_time = time.monotonic()  # 起始時間
            proc = await asyncio.create_subprocess_exec(  # 建立子行程
                *cmd,  # 傳入命令
                stdout=asyncio.subprocess.PIPE,  # 擷取 stdout
                stderr=asyncio.subprocess.PIPE  # 擷取 stderr
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)  # 等待結束（含超時）
            duration = time.monotonic() - start_time  # 計算執行時間
            logger.debug(f"Docker execution finished in {duration:.2f}s. Exit code: {proc.returncode}")  # 記錄結束

            stdout_str = stdout.decode('utf-8', errors='replace').strip()  # 解碼 stdout
            stderr_str = stderr.decode('utf-8', errors='replace').strip()  # 解碼 stderr

            if proc.returncode != 0:  # 若 exit code 非 0
                # stdout 為空且 stderr 有內容，多半是 Docker/腳本啟動錯誤
                if not stdout_str and stderr_str:
                    error_message = f"Execution failed with exit code {proc.returncode}. Docker error: '{stderr_str}'"  # 組合錯誤訊息
                    logger.warning(error_message)  # 記錄警告
                    return None, error_message  # 回傳錯誤
                # stdout 有內容但 exit 非 0：可能有 traceback，但仍嘗試解析 stdout
                logger.warning(f"Execution completed with non-zero exit code {proc.returncode}. Stdout: '{stdout_str}', Stderr: '{stderr_str}'. Attempting to parse stdout.")  # 記錄警告

            # 腳本結束但沒有 stdout
            if not stdout_str and proc.returncode == 0:  # 無 stdout 但正常結束
                 logger.warning(f"Execution produced no stdout, but exited cleanly. Stderr: '{stderr_str}'")  # 記錄警告
                 return None, f"No output from script. Stderr: '{stderr_str}'"  # 回傳錯誤
            
            # 無 stdout 且 exit 非 0
            if not stdout_str and proc.returncode != 0:  # 無 stdout 且 exit 非 0
                 return None, f"Execution failed with exit code {proc.returncode}. No stdout. Stderr: '{stderr_str}'"  # 回傳錯誤


            try:  # 嘗試解析 JSON
                # 將 Infinity/NaN 還原後再解析 JSON  # 自訂解析
                def json_loads_with_infinity(s):  # 內部解析器
                    s = s.replace('"Infinity"', 'float("inf")')  # 還原 Infinity
                    s = s.replace('"-Infinity"', 'float("-inf")')  # 還原 -Infinity
                    s = s.replace('"NaN"', 'float("nan")')  # 還原 NaN
                    return json.loads(s)  # JSON 解析

                parsed_output = json_loads_with_infinity(stdout_str)  # 解析 stdout
                logger.debug(f"Parsed execution output: {parsed_output}")  # 記錄解析結果
                return parsed_output, None  # 回傳結果
            except json.JSONDecodeError as e:  # JSON 解析失敗
                error_message = f"Failed to decode JSON output: {e}. Raw output: '{stdout_str}'"  # 組合錯誤
                logger.error(error_message)  # 記錄錯誤
                return None, error_message  # 回傳錯誤
            except Exception as e:  # 其他錯誤
                error_message = f"Error processing script output: {e}. Raw output: '{stdout_str}'"  # 組合錯誤
                logger.error(error_message)  # 記錄錯誤
                return None, error_message  # 回傳錯誤

        except asyncio.TimeoutError:  # 發生超時
            logger.warning(f"Execution for container '{container_name}' initiating timeout handling.")  # 記錄超時
            if proc and proc.returncode is None:  # 檢查子行程是否仍在執行
                logger.info(f"Attempting to stop Docker container: {container_name}")  # 記錄停止
                stop_cmd = ["docker", "stop", container_name]  # docker stop 命令
                try:  # 嘗試停止
                    stop_proc = await asyncio.create_subprocess_exec(*stop_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)  # 啟動 stop
                    _, stop_stderr_bytes = await asyncio.wait_for(stop_proc.communicate(), timeout=10)  # docker stop 最多 10 秒
                    if stop_proc.returncode != 0:  # stop 失敗
                        logger.error(f"Failed to stop container {container_name}. Exit: {stop_proc.returncode}. Stderr: {stop_stderr_bytes.decode(errors='replace')}")  # 記錄錯誤
                        kill_cmd = ["docker", "kill", container_name]  # docker kill 命令
                        kill_proc = await asyncio.create_subprocess_exec(*kill_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)  # 啟動 kill
                        kill_stdout_bytes, kill_stderr_bytes = await asyncio.wait_for(kill_proc.communicate(), timeout=5)  # docker kill 最多 5 秒
                        if kill_proc.returncode == 0:  # kill 成功
                             logger.info(f"Successfully killed container {container_name} after stop failed.")  # 記錄成功
                        else:  # kill 失敗
                             logger.error(f"Failed to kill container {container_name}. Exit: {kill_proc.returncode}. Stderr: {kill_stderr_bytes.decode(errors='replace')}")  # 記錄錯誤
                    else:  # stop 成功
                        logger.info(f"Successfully stopped container {container_name}.")  # 記錄成功
                except asyncio.TimeoutError:  # stop/kill 超時
                    logger.error(f"Timeout trying to stop/kill container {container_name}. It might be orphaned.")  # 記錄錯誤
                except Exception as e_stop:  # 其他錯誤
                    logger.error(f"Error stopping/killing container {container_name}: {e_stop}")  # 記錄錯誤
            
            if proc:  # 原始 docker run 的子行程
                try:  # 嘗試 kill
                    if proc.returncode is None: proc.kill()  # 若還在跑就 kill
                    await proc.wait()  # 等待結束
                except ProcessLookupError: pass  # 行程不存在
                except Exception as e_kill: logger.error(f"Error trying to kill original subprocess after docker stop/kill: {e_kill}")  # 記錄錯誤
            
            logger.warning(f"Code execution in Docker container '{container_name}' timed out after {timeout} seconds.")  # 記錄超時
            return None, f"Execution timed out after {timeout} seconds (container {container_name})."  # 回傳超時錯誤
        except Exception as e:  # 其他例外
            logger.error(f"An unexpected error occurred during code execution: {e}", exc_info=True)  # 記錄錯誤
            return None, f"Unexpected execution error: {str(e)}"  # 回傳錯誤
        finally:  # 清理暫存
            try:  # 嘗試清理
                if os.path.exists(temp_file_path):  # 若檔案存在
                    os.remove(temp_file_path)  # 刪除檔案
                if os.path.exists(temp_dir):  # 若資料夾存在
                    try:  # 嘗試刪除資料夾
                        # 多次嘗試刪除資料夾（避免 Docker 殘留鎖）  # 容錯清理
                        for _ in range(3):  # 最多 3 次
                            try:  # 嘗試刪除
                                if os.path.exists(temp_file_path): os.remove(temp_file_path)  # 再次刪除檔案
                                os.rmdir(temp_dir)  # 移除資料夾
                                break  # 成功
                            except OSError:  # 若刪除失敗
                                await asyncio.sleep(0.1)  # 略等再重試
                        else:  # 3 次都失敗
                            logger.error(f"Failed to remove temp_dir {temp_dir} after multiple retries.")  # 記錄錯誤
                    except Exception as e_rmdir:  # 捕捉其他刪除錯誤
                         logger.error(f"Error removing temp_dir {temp_dir}: {e_rmdir}.")  # 記錄錯誤
            except Exception as e_cleanup:  # 清理失敗的通用錯誤
                logger.error(f"Error during cleanup of temp files: {e_cleanup}")  # 記錄錯誤

    def _assess_correctness(self, execution_results: Dict[str, Any], expected_outputs: List[Dict[str, Any]]) -> Tuple[float, int, int]:  # 計算正確率
        passed_tests = 0  # 通過數
        total_tests = len(expected_outputs)  # 總測試數

        # 確保執行結果格式正確  # 格式檢查
        if not execution_results or "test_outputs" not in execution_results:  # 若缺少結果
            logger.warning("Execution results are missing 'test_outputs' field.")  # 記錄警告
            return 0.0, 0, total_tests  # 回傳 0 分

        actual_test_outputs = execution_results["test_outputs"]  # 取得實際輸出列表

        if len(actual_test_outputs) != total_tests:  # 若數量不一致
            logger.warning(f"Mismatch in number of test outputs ({len(actual_test_outputs)}) and expected outputs ({total_tests}). Some tests might have crashed before producing output.")  # 記錄警告

        for i, expected in enumerate(expected_outputs):  # 逐一檢查
            actual_output_detail = next((res for res in actual_test_outputs if res.get("test_case_id") == i), None)  # 取得對應結果

            if actual_output_detail and actual_output_detail.get("status") == "success":  # 若成功
                actual = actual_output_detail.get("output")  # 取得實際輸出

                logger.debug(f"Test case {i}: Actual output: {actual}")  # 記錄輸出

                # 若有驗證函式，優先使用它  # 驗證函式
                if "validation_func" in expected:  # 若有驗證函式
                    logger.debug(f"Test case {i}: Using validation function.")  # 記錄使用驗證
                    try:  # 嘗試執行
                        # 建立 namespace 以執行驗證函式  # 執行環境
                        namespace = {}  # 建立 namespace
                        # 執行驗證函式定義  # exec
                        exec(expected["validation_func"], namespace)  # 執行驗證程式碼
                        # 取得 validate 函式  # 取得函式
                        validate_func = namespace.get("validate")  # 取得 validate
                        if validate_func and callable(validate_func):  # 若可呼叫
                            # 只傳入實際輸出  # 驗證輸出
                            if validate_func(actual):  # 驗證通過
                                passed_tests += 1  # 增加通過數
                                logger.debug(f"Test case {i}: Validation function returned True.")  # 記錄通過
                            else:  # 驗證失敗
                                logger.debug(f"Test case {i}: Validation function returned False.")  # 記錄失敗
                        else:  # validate 不存在或不可呼叫
                            logger.warning(f"Validation function not found or not callable in test case {i}")  # 記錄警告
                    except Exception as e:  # 驗證過程例外
                        logger.error(f"Error executing validation function for test case {i}: {str(e)}", exc_info=True)  # 記錄例外詳情
                # 若提供 expected output，直接比對  # 直接比對
                elif "output" in expected:  # 若有期望輸出
                    expected_val = expected["output"]  # 取得期望值
                    logger.debug(f"Test case {i}: Comparing with expected output: {expected_val}")  # 記錄比對
                    if self._compare_outputs(actual, expected_val):  # 比對成功
                        passed_tests += 1  # 增加通過數
                        logger.debug(f"Test case {i}: Comparison returned True.")  # 記錄通過
                    else:  # 比對失敗
                        logger.debug(f"Test case {i}: Comparison returned False.")  # 記錄失敗
                else:  # 無驗證也無輸出
                    logger.warning(f"Test case {i} has neither validation function nor expected output")  # 記錄警告
            elif actual_output_detail:  # 有結果但失敗
                logger.debug(f"Test case {i} had error: {actual_output_detail.get('error')}")  # 記錄錯誤
            else:  # 沒有結果
                logger.debug(f"Test case {i}: No output found in results.")  # 記錄無結果

        logger.debug(f"Finished assessing correctness. Passed tests: {passed_tests}/{total_tests}")  # 記錄總結
        if total_tests == 0:  # 若無測試
            return 1.0, 0, 0  # 預設正確率 1

        correctness = passed_tests / total_tests  # 計算正確率
        return correctness, passed_tests, total_tests  # 回傳結果

    async def evaluate_program(self, program: Program, task: TaskDefinition) -> Program:  # 評估程式
        logger.info(f"Evaluating program: {program.id} for task: {task.id}")  # 記錄開始
        program.status = "evaluating"  # 設定狀態
        program.errors = []  # 清空錯誤
        program.fitness_scores = {"correctness": 0.0, "runtime_ms": float('inf'), "passed_tests": 0.0, "total_tests": 0.0}  # 初始化適應度

        syntax_errors = self._check_syntax(program.code)  # 語法檢查
        if syntax_errors:  # 若有語法錯誤
            program.errors.extend(syntax_errors)  # 記錄錯誤
            program.fitness_scores["correctness"] = 0.0  # 正確率歸零
            program.status = "failed_evaluation"  # 設定失敗
            logger.warning(f"Syntax errors found in program {program.id}: {syntax_errors}")  # 記錄警告
            return program  # 回傳

        logger.debug(f"Syntax check passed for program {program.id}.")  # 記錄通過

        overall_passed_tests = 0  # 全部通過數
        overall_total_tests = 0  # 全部測試數
        last_successful_level_avg_runtime = float('inf')  # 最後成功層平均時間
        highest_level_passed = -1  # 最高通過層級

        # 決定要執行的測試集合
        test_groups_to_run = []  # 測試群組列表
        if task.tests:  # 新結構（含層級）
            # 依層級排序，未指定者視為 0  # 排序
            sorted_test_groups = sorted(task.tests, key=lambda g: g.get('level', 0))  # 排序測試群組
            for group in sorted_test_groups:  # 逐一加入
                test_groups_to_run.append({  # 轉換格式
                    "name": group.get('name', f"level_{group.get('level', 0)}"),  # 群組名稱
                    "level": group.get('level', 0),  # 群組層級
                    "test_cases": group.get('test_cases', [])  # 測試案例
                })
        elif task.input_output_examples:  # 舊版格式
            logger.warning(f"Task {task.id} uses legacy 'input_output_examples'. Consider migrating to 'tests' with levels.")  # 記錄警告
            test_groups_to_run.append({  # 轉成群組
                "name": "default_level",  # 預設名稱
                "level": 0,  # 預設層級
                "test_cases": task.input_output_examples  # 測試案例
            })
        
        if not test_groups_to_run:  # 若無測試群組
            logger.info(f"No tests or input/output examples provided for task {task.id}. Skipping execution.")  # 記錄跳過
            program.fitness_scores["correctness"] = 0.5  # 無測試時給預設分
            program.fitness_scores["runtime_ms"] = 0.0  # 無測試時間
            program.status = "evaluated"  # 沒有測試可失敗
            return program  # 回傳

        for group_idx, test_group in enumerate(test_groups_to_run):  # 逐一群組
            level_name = test_group['name']  # 群組名稱
            current_level = test_group['level']  # 群組層級
            current_level_test_cases = test_group['test_cases']  # 測試案例

            if not current_level_test_cases:  # 若群組無測試
                logger.info(f"Test group '{level_name}' (Level {current_level}) has no test cases. Skipping.")  # 記錄跳過
                continue  # 跳過

            logger.info(f"Executing program {program.id} against test group '{level_name}' (Level {current_level}) with {len(current_level_test_cases)} test cases.")  # 記錄執行
            
            # 建立暫時的 TaskDefinition 只含該層測試  # 子任務
            temp_task_def_for_level = TaskDefinition(  # 建立臨時任務
                id=f"{task.id}_level_{current_level}",  # 任務 ID
                description=task.description,  # 雖非必需，但保留描述
                function_name_to_evolve=task.function_name_to_evolve,  # 待測函式
                input_output_examples=current_level_test_cases,  # 核心測試案例
                allowed_imports=task.allowed_imports  # 執行上下文
            )

            execution_results, execution_error = await self._execute_code_safely(program.code, task_for_examples=temp_task_def_for_level)  # 執行測試
            
            if execution_error:  # 若執行錯誤
                logger.warning(f"Execution error for program {program.id} at level {current_level} ('{level_name}'): {execution_error}")  # 記錄警告
                program.errors.append(f"Execution Error at Level {current_level} ('{level_name}'): {execution_error}")  # 記錄錯誤
                program.status = "failed_evaluation"  # 設定失敗
                break  # 終止級聯評估
            
            if execution_results is None:  # 若無結果
                logger.warning(f"No execution results for program {program.id} at level {current_level} ('{level_name}').")  # 記錄警告
                program.errors.append(f"Execution Error: No results at Level {current_level} ('{level_name}').")  # 記錄錯誤
                program.status = "failed_evaluation"  # 設定失敗
                break  # 終止級聯評估

            level_correctness, level_passed_tests, level_total_tests = self._assess_correctness(execution_results, current_level_test_cases)  # 計算該層正確率
            
            overall_passed_tests += level_passed_tests  # 累加通過數
            overall_total_tests += level_total_tests  # 累加測試數

            current_level_avg_runtime = execution_results.get("average_runtime_ms", float('inf'))  # 取得平均時間
            if not isinstance(current_level_avg_runtime, (float, int)):  # 若格式異常
                current_level_avg_runtime = float('inf')  # 設為無限大

            logger.info(f"Program {program.id} Level {current_level} ('{level_name}') Correctness: {level_correctness:.2f} ({level_passed_tests}/{level_total_tests}), Avg Runtime: {current_level_avg_runtime}ms")  # 記錄評估

            if level_correctness < 1.0:  # 若未滿分
                error_msg = f"Failed {level_total_tests - level_passed_tests} of {level_total_tests} tests at Level {current_level} ('{level_name}')."  # 失敗訊息
                program.errors.append(error_msg)  # 記錄錯誤
                program.status = "failed_evaluation"  # 設定失敗
                # 只計算到失敗層級的分數  # 部分結果
                program.fitness_scores["correctness"] = overall_passed_tests / overall_total_tests if overall_total_tests > 0 else 0.0  # 計算正確率
                program.fitness_scores["passed_tests"] = float(overall_passed_tests)  # 通過數
                program.fitness_scores["total_tests"] = float(overall_total_tests)  # 總數
                # runtime 取最後成功層級平均時間  # 時間策略
                program.fitness_scores["runtime_ms"] = last_successful_level_avg_runtime  # 設定時間
                break  # 終止級聯評估
            else:  # 若此層全部通過
                highest_level_passed = current_level  # 更新最高層級
                last_successful_level_avg_runtime = current_level_avg_runtime  # 更新時間
                # 若是最後一層且全通過，標記為 evaluated  # 設定狀態
                if group_idx == len(test_groups_to_run) - 1:  # 最後一層
                    program.status = "evaluated"  # 設定已評估
        
        # 迴圈結束後的最終分數整理  # 整合分數
        if overall_total_tests > 0:  # 若有測試
            program.fitness_scores["correctness"] = overall_passed_tests / overall_total_tests  # 計算正確率
        elif not program.errors:  # 沒有測試但也沒有錯誤
            program.fitness_scores["correctness"] = 0.5  # 無測試預設
        # 若有錯誤則維持 0.0  # 不變

        program.fitness_scores["passed_tests"] = float(overall_passed_tests)  # 記錄通過數
        program.fitness_scores["total_tests"] = float(overall_total_tests)  # 記錄總數
        program.fitness_scores["runtime_ms"] = last_successful_level_avg_runtime if highest_level_passed != -1 else float('inf')  # 設定時間
        program.fitness_scores["highest_level_passed"] = float(highest_level_passed)  # 設定最高層級

        # 依錯誤與正確率整合狀態  # 設定狀態
        if program.errors:  # 若有錯誤
            program.status = "failed_evaluation"  # 失敗
        elif program.fitness_scores.get("correctness", 0.0) == 1.0 and overall_total_tests > 0:  # 全通過
            program.status = "evaluated"  # 評估成功
        elif overall_total_tests == 0 and not program.errors:  # 無測試但也無錯誤
             program.status = "evaluated"  # 視為成功
             program.fitness_scores["correctness"] = 0.5  # 預設正確率
             program.fitness_scores["runtime_ms"] = 0.0  # 預設時間
        elif not program.errors:  # 有測試但未全通過
            program.status = "failed_evaluation"  # 設為失敗
            if f"Achieved {program.fitness_scores['correctness']*100:.0f}% correctness but not all tests passed." not in program.errors:  # 避免重複訊息
                 program.errors.append(f"Achieved {program.fitness_scores['correctness']*100:.0f}% correctness but not all tests passed.")  # 加入訊息

        logger.info(f"Overall evaluation complete for program {program.id}. Status: {program.status}, Fitness: {program.fitness_scores}")  # 記錄總結
        return program  # 回傳程式

    async def execute(self, program: Program, task: TaskDefinition) -> Program:  # 通用執行入口
        return await self.evaluate_program(program, task)  # 呼叫評估

    def _compare_outputs(self, actual: Any, expected: Any) -> bool:  # 輸出比對
        logger.debug(f"Comparing outputs. Actual: {type(actual)}{actual}, Expected: {type(expected)}{expected}")  # 記錄比對
        
        if isinstance(actual, float) and isinstance(expected, float):  # 若皆為浮點
            TOLERANCE = 1e-9  # 可改成設定檔可調
            is_close = math.isclose(actual, expected, rel_tol=TOLERANCE, abs_tol=TOLERANCE)  # 使用容差比對
            if not is_close:  # 若不接近
                logger.debug(f"Float comparison: {actual} vs {expected} is NOT close (tolerance: {TOLERANCE}).")  # 記錄差異
            return is_close  # 回傳結果
        
        # 其他型別採直接相等比較  # 直接比較
        are_equal = actual == expected  # 直接相等

        return are_equal  # 回傳結果

                                                 
                                                              
                                                                                              
                                                         
                                                        
                                                                    
