"""
EvaluatorAgent 的單元測試（Docker 執行與評估流程）。
"""
import asyncio  # 非同步工具
import json  # JSON 操作
import os  # 檔案操作
import unittest  # 測試框架
from unittest.mock import patch, MagicMock, AsyncMock, call  # mock 工具

# 確保測試可找到專案模組
import sys  # 系統工具
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 加入專案路徑

from evaluator_agent.agent import EvaluatorAgent  # 評估代理
from core.interfaces import Program, TaskDefinition  # 資料結構
from config import settings  # 設定

# 建立 mock subprocess 的輔助函式
def create_mock_subprocess(stdout_data, stderr_data, return_code, communicate_raises=None):
    proc = MagicMock(spec=asyncio.subprocess.Process)
    proc.returncode = return_code
    
    if communicate_raises:
        proc.communicate = AsyncMock(side_effect=communicate_raises)
    else:
        proc.communicate = AsyncMock(return_value=(stdout_data.encode(), stderr_data.encode()))
    
    # 需要更複雜情境（如 timeout）時可擴充
    proc.wait = AsyncMock()
    proc.kill = MagicMock()  # 非同步 kill 的替身
    return proc

class TestEvaluatorAgentDockerExecution(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.agent = EvaluatorAgent()
        self.program = Program(id="test_prog", code="def solve():\n  return 42", parent_id=None, fitness_scores={})
        self.task_definition = TaskDefinition(
            id="test_task",
            description="Test task",
            function_name_to_evolve="solve",
            input_output_examples=[
                {"input": [], "output": 42}
            ]
        )
        
        # Docker 設定 mock（可於各測試覆寫）
        self.mock_settings_patcher = patch('evaluator_agent.agent.settings')
        self.mock_settings = self.mock_settings_patcher.start()
        self.mock_settings.DOCKER_IMAGE_NAME = "test-eval-image:latest"
        self.mock_settings.DOCKER_NETWORK_DISABLED = True
        self.mock_settings.EVALUATION_TIMEOUT_SECONDS = 5  # 測試用短 timeout

    async def asyncTearDown(self):
        self.mock_settings_patcher.stop()
        # 若有建立暫存檔可在此清理（tempfile.mkdtemp() 可再行 patch 以固定路徑）

    @patch('asyncio.create_subprocess_exec', new_callable=AsyncMock)
    async def test_execute_code_safely_success(self, mock_create_subprocess_exec):
        # --- 測試：成功執行 ---
        # 腳本預期輸出（JSON）
        expected_script_output = {
            "test_outputs": [{"test_case_id": 0, "output": 42, "runtime_ms": 10.0, "status": "success"}],
            "average_runtime_ms": 10.0
        }
        mock_proc_docker_run = create_mock_subprocess(json.dumps(expected_script_output), "", 0)
        mock_create_subprocess_exec.return_value = mock_proc_docker_run

        results, error = await self.agent._execute_code_safely(self.program.code, self.task_definition)

        self.assertIsNotNone(results)
        self.assertIsNone(error)
        self.assertEqual(results["average_runtime_ms"], 10.0)
        self.assertEqual(results["test_outputs"][0]["output"], 42)
        
        # 檢查 docker 命令
        args, _ = mock_create_subprocess_exec.call_args
        self.assertEqual(args[0], "docker")
        self.assertEqual(args[1], "run")
        self.assertIn(self.mock_settings.DOCKER_IMAGE_NAME, args)
        if self.mock_settings.DOCKER_NETWORK_DISABLED:
            self.assertIn("--network", args)
            self.assertIn("none", args)
        
        # 檢查 volume 掛載格式（路徑因 tempfile 會變動）
        # 例如：-v /tmp/somerandomdir:/app/user_code
        volume_arg_index = -1
        for i, arg in enumerate(args):
            if arg == "-v" and ":/app/user_code" in args[i+1]:
                volume_arg_index = i
                break
        self.assertNotEqual(volume_arg_index, -1, "Volume mount for temp script not found in Docker command.")
        # 若 patch tempfile，可進一步檢查 temp_script.py 路徑

    @patch('asyncio.create_subprocess_exec', new_callable=AsyncMock)
    async def test_execute_code_safely_script_error(self, mock_create_subprocess_exec):
        # --- 測試：腳本錯誤 ---
        script_stderr = "Traceback (most recent call last):\n  File \"temp_script.py\", line X, in <module>\n    raise ValueError(\"Test script error\")\nValueError: Test script error"
        # 腳本失敗時，stdout 可能為空或是部分 JSON
        # Docker 指令本身可能成功，但容器內腳本失敗（或 python exit code 非 0）
        # 目前邏輯：
        # - proc.returncode != 0 且 stdout 空、stderr 有內容 -> 判定為 Docker error
        # - proc.returncode != 0 且 stdout 有內容 -> 仍嘗試解析 stdout
        # - stdout 空且 returncode == 0 -> 無輸出
        
        # 情境：腳本 exit 1、stderr 有錯誤、stdout 無有效 JSON
        mock_proc_docker_run = create_mock_subprocess("", script_stderr, 1)  # stdout, stderr, returncode
        mock_create_subprocess_exec.return_value = mock_proc_docker_run

        results, error = await self.agent._execute_code_safely(self.program.code, self.task_definition)

        self.assertIsNone(results)
        self.assertIsNotNone(error)
        self.assertIn("Execution failed with exit code 1", error)
        self.assertIn("Docker error", error)  # stdout 為空
        self.assertIn("Test script error", error)


    @patch('asyncio.create_subprocess_exec', new_callable=AsyncMock)
    async def test_execute_code_safely_docker_error(self, mock_create_subprocess_exec):
        # --- 測試：Docker 錯誤 ---
        # 例如：鏡像不存在、Docker daemon 問題
        docker_stderr = "Error: No such image: non_existent_image:latest"
        # Docker 命令本身失敗（例如 exit code 125）
        mock_proc_docker_run = create_mock_subprocess("", docker_stderr, 125)
        mock_create_subprocess_exec.return_value = mock_proc_docker_run
        
        results, error = await self.agent._execute_code_safely(self.program.code, self.task_definition)

        self.assertIsNone(results)
        self.assertIsNotNone(error)
        self.assertIn("Execution failed with exit code 125", error)
        self.assertIn("Docker error", error)  # stdout 為空
        self.assertIn(docker_stderr, error)

    @patch('asyncio.create_subprocess_exec', new_callable=AsyncMock)
    async def test_execute_code_safely_timeout(self, mock_create_subprocess_exec):
        # --- 測試：Timeout ---
        # 模擬 docker run 超時，仍在執行時 returncode 應為 None
        mock_proc_docker_run = create_mock_subprocess("", "", None, communicate_raises=asyncio.TimeoutError("Simulated timeout"))
        
        # 後續 docker stop / docker kill 的 mock
        mock_proc_docker_stop = create_mock_subprocess("container_id_stopped", "", 0)  # stdout, stderr, returncode
        mock_proc_docker_kill = create_mock_subprocess("container_id_killed", "", 0)  # 不一定會呼叫

        # 依呼叫順序回傳不同 mock
        # 1st: docker run（timeout）
        # 2nd: docker stop
        # 3rd: docker kill（視情況）
        mock_create_subprocess_exec.side_effect = [
            mock_proc_docker_run, 
            mock_proc_docker_stop,
            mock_proc_docker_kill 
        ]

        results, error = await self.agent._execute_code_safely(self.program.code, self.task_definition, timeout_seconds=1)
        
        self.assertIsNone(results)
        self.assertIsNotNone(error)
        self.assertIn("Execution timed out after 1 seconds", error)

        # 檢查 docker run 呼叫
        run_call = mock_create_subprocess_exec.call_args_list[0]
        self.assertIn("docker", run_call[0][0])
        self.assertIn("run", run_call[0][1])
        
        # 檢查 docker stop 呼叫
        stop_call = mock_create_subprocess_exec.call_args_list[1]
        self.assertIn("docker", stop_call[0][0])
        self.assertIn("stop", stop_call[0][1])
        # 從 run 命令取出容器名稱，確認 stop 命令包含它
        run_args = run_call[0]
        container_name_arg_index = -1
        for i, arg_val in enumerate(run_args):
            if arg_val == "--name":
                container_name_arg_index = i + 1
                break
        self.assertNotEqual(container_name_arg_index, -1, "--name parameter not found in docker run call")
        expected_container_name = run_args[container_name_arg_index]
        self.assertIn(expected_container_name, stop_call[0])

        # agent 應呼叫原始 docker run proc 的 kill
        mock_proc_docker_run.kill.assert_called_once()


    @patch('evaluator_agent.agent.EvaluatorAgent._execute_code_safely', new_callable=AsyncMock)
    async def test_evaluate_program_successful_evaluation(self, mock_execute_code_safely):
        # --- 測試：完整評估成功 ---
        expected_script_output = {
            "test_outputs": [{"test_case_id": 0, "output": 42, "runtime_ms": 10.0, "status": "success"}],
            "average_runtime_ms": 10.0
        }
        mock_execute_code_safely.return_value = (expected_script_output, None)

        evaluated_program = await self.agent.evaluate_program(self.program, self.task_definition)

        self.assertEqual(evaluated_program.status, "evaluated")
        self.assertEqual(evaluated_program.fitness_scores["correctness"], 1.0)
        self.assertEqual(evaluated_program.fitness_scores["passed_tests"], 1.0)
        self.assertEqual(evaluated_program.fitness_scores["total_tests"], 1.0)
        self.assertEqual(evaluated_program.fitness_scores["runtime_ms"], 10.0)
        self.assertEqual(len(evaluated_program.errors), 0)

    @patch('evaluator_agent.agent.EvaluatorAgent._execute_code_safely', new_callable=AsyncMock)
    async def test_evaluate_program_failed_evaluation_due_to_error(self, mock_execute_code_safely):
        # --- 測試：完整評估失敗（腳本錯誤） ---
        mock_execute_code_safely.return_value = (None, "Script crashed badly")

        evaluated_program = await self.agent.evaluate_program(self.program, self.task_definition)

        self.assertEqual(evaluated_program.status, "failed_evaluation")
        self.assertEqual(evaluated_program.fitness_scores["correctness"], 0.0)
        # 若執行失敗，passed/total 可能為 0
        self.assertIn("Execution Error at Level 0 ('default_level'): Script crashed badly", evaluated_program.errors)

    @patch('evaluator_agent.agent.EvaluatorAgent._execute_code_safely', new_callable=AsyncMock)
    async def test_evaluate_program_failed_evaluation_due_to_incorrect_output(self, mock_execute_code_safely):
        # --- 測試：完整評估失敗（輸出錯誤） ---
        expected_script_output = {
            "test_outputs": [{"test_case_id": 0, "output": 0, "runtime_ms": 10.0, "status": "success"}],  # 輸出為 0，預期為 42
            "average_runtime_ms": 10.0
        }
        mock_execute_code_safely.return_value = (expected_script_output, None)

        evaluated_program = await self.agent.evaluate_program(self.program, self.task_definition)

        self.assertEqual(evaluated_program.status, "failed_evaluation")
        self.assertEqual(evaluated_program.fitness_scores["correctness"], 0.0)
        self.assertEqual(evaluated_program.fitness_scores["passed_tests"], 0.0)
        self.assertEqual(evaluated_program.fitness_scores["total_tests"], 1.0)
        self.assertIn("Failed 1 of 1 tests at Level 0 ('default_level').", evaluated_program.errors)

    @patch('evaluator_agent.agent.EvaluatorAgent._execute_code_safely', new_callable=AsyncMock)
    async def test_evaluate_program_with_validation_function(self, mock_execute_code_safely):
        # --- 測試：含驗證函式的評估 ---
        expected_script_output = {
            "test_outputs": [{"test_case_id": 0, "output": 15, "runtime_ms": 10.0, "status": "success"}],
            "average_runtime_ms": 10.0
        }
        mock_execute_code_safely.return_value = (expected_script_output, None)

        # 建立含驗證函式的任務
        task_with_validation = TaskDefinition(
            id="test_task_validation",
            description="Test task with validation function",
            function_name_to_evolve="test_function",
            input_output_examples=[
                {
                    "input": [10],
                    "validation_func": """
def validate(input):
    return input > 10
"""
                }
            ]
        )

        evaluated_program = await self.agent.evaluate_program(self.program, task_with_validation)

        self.assertEqual(evaluated_program.status, "evaluated")
        self.assertEqual(evaluated_program.fitness_scores["correctness"], 1.0)
        self.assertEqual(evaluated_program.fitness_scores["passed_tests"], 1.0)
        self.assertEqual(evaluated_program.fitness_scores["total_tests"], 1.0)
        self.assertEqual(len(evaluated_program.errors), 0)

    @patch('evaluator_agent.agent.EvaluatorAgent._execute_code_safely', new_callable=AsyncMock)
    async def test_evaluate_program_with_failed_validation(self, mock_execute_code_safely):
        # --- 測試：驗證函式失敗 ---
        expected_script_output = {
            "test_outputs": [{"test_case_id": 0, "output": 5, "runtime_ms": 10.0, "status": "success"}],
            "average_runtime_ms": 10.0
        }
        mock_execute_code_safely.return_value = (expected_script_output, None)

        # 建立含驗證函式的任務
        task_with_validation = TaskDefinition(
            id="test_task_validation_fail",
            description="Test task with failing validation function",
            function_name_to_evolve="test_function",
            input_output_examples=[
                {
                    "input": [10],
                    "validation_func": """
def validate(input):
    return input > 10
"""
                }
            ]
        )

        evaluated_program = await self.agent.evaluate_program(self.program, task_with_validation)

        self.assertEqual(evaluated_program.status, "failed_evaluation")
        self.assertEqual(evaluated_program.fitness_scores["correctness"], 0.0)
        self.assertEqual(evaluated_program.fitness_scores["passed_tests"], 0.0)
        self.assertEqual(evaluated_program.fitness_scores["total_tests"], 1.0)
        self.assertIn("Failed 1 of 1 tests at Level 0 ('default_level').", evaluated_program.errors)


if __name__ == '__main__':
    unittest.main()

# 若需更穩定的路徑斷言，可 patch tempfile.mkdtemp 以固定資料夾名稱
# 同時也便於清理。
# from unittest.mock import patch
# @patch('tempfile.mkdtemp', return_value='/tmp/fixed_temp_dir_for_test')
# ... 於測試方法中 ...
# mock_mkdtemp.assert_called_once()
# self.assertTrue(os.path.exists('/tmp/fixed_temp_dir_for_test/temp_script.py'))
# ... 於 tearDown 中 ...
# if os.path.exists('/tmp/fixed_temp_dir_for_test/temp_script.py'):
#     os.remove('/tmp/fixed_temp_dir_for_test/temp_script.py')
# if os.path.exists('/tmp/fixed_temp_dir_for_test'):
#     os.rmdir('/tmp/fixed_temp_dir_for_test')
# 重要性：agent 會將腳本寫入 temp_dir + "/temp_script.py"
# 而該路徑會出現在 `docker run -v` 命令中
# 目前只檢查 `-v` 與 `:/app/user_code`，已是基本保障
# 若要檢查來源路徑，需 patch tempfile
