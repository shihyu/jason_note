"""
程式碼生成代理：與 LLM 互動，產生完整程式或 diff，並套用 diff。  # 檔案用途
"""
import logging  # 日誌系統
import re  # 正則表達式
from typing import Optional, Dict, Any  # 型別註解
import asyncio  # 非同步工具

from litellm import acompletion  # LiteLLM 非同步補全
from litellm.exceptions import (  # LiteLLM 例外型別
    APIError,  # API 錯誤
    AuthenticationError,  # 驗證錯誤
    BadRequestError,  # 請求錯誤
    InternalServerError,  # 伺服器錯誤
    RateLimitError  # 速率限制
)

from config import settings  # 匯入設定
from core.interfaces import CodeGeneratorInterface  # 程式碼生成介面

logger = logging.getLogger(__name__)  # 取得本模組 logger

class CodeGeneratorAgent(CodeGeneratorInterface):  # 程式碼生成代理
    def __init__(self, config: Optional[Dict[str, Any]] = None):  # 初始化
        super().__init__(config)  # 呼叫基底初始化
        self.model_name = settings.LITELLM_DEFAULT_MODEL  # 預設模型
        # 預設的生成參數（可被呼叫端覆寫）  # 生成設定
        self.generation_config = {  # 生成參數
            "temperature": settings.LITELLM_TEMPERATURE,  # 溫度
            "top_p": settings.LITELLM_TOP_P,  # top_p
            "top_k": settings.LITELLM_TOP_K,  # top_k
            "max_tokens": settings.LITELLM_MAX_TOKENS,  # 最大 token
        }
        # LiteLLM 其他連線參數  # 額外參數
        self.litellm_extra_params = {  # 連線參數
            "base_url": settings.LITELLM_DEFAULT_BASE_URL,  # base_url
        }
        logger.info(f"CodeGeneratorAgent initialized with model: {self.model_name}")  # 記錄初始化

    async def generate_code(self, prompt: str, model_name: Optional[str] = None, temperature: Optional[float] = None, output_format: str = "code", litellm_extra_params: Optional[Dict[str, Any]] = None) -> str:  # 生成程式碼
        effective_model_name = model_name if model_name else self.model_name  # 決定實際模型
        litellm_extra_params = litellm_extra_params or self.litellm_extra_params  # 決定額外參數
        logger.info(f"Attempting to generate code using model: {effective_model_name}, output_format: {output_format}")  # 記錄生成資訊
        
        # 若需要 diff，追加格式指示  # diff 模式
        if output_format == "diff":  # 若要求 diff
            prompt += '''  # 在提示後面追加 diff 規則

I need you to provide your changes as a sequence of diff blocks in the following format:

<<<<<<< SEARCH
# Original code block to be found and replaced (COPY EXACTLY from original)
=======
# New code block to replace the original
>>>>>>> REPLACE

IMPORTANT DIFF GUIDELINES:
1. The SEARCH block MUST be an EXACT copy of code from the original - match whitespace, indentation, and line breaks precisely
2. Each SEARCH block should be large enough (3-5 lines minimum) to uniquely identify where the change should be made
3. Include context around the specific line(s) you want to change
4. Make multiple separate diff blocks if you need to change different parts of the code
5. For each diff, the SEARCH and REPLACE blocks must be complete, valid code segments
6. Pay special attention to matching the exact original indentation of the code in your SEARCH block, as this is crucial for correct application in environments sensitive to indentation (like Python).

Example of a good diff:
<<<<<<< SEARCH
def calculate_sum(numbers):
    result = 0
    for num in numbers:
        result += num
    return result
=======
def calculate_sum(numbers):
    if not numbers:
        return 0
    result = 0
    for num in numbers:
        result += num
    return result
>>>>>>> REPLACE

Make sure your diff can be applied correctly!
'''
        
        logger.debug(f"Received prompt for code generation (format: {output_format}):\n--PROMPT START--\n{prompt}\n--PROMPT END--")  # 記錄提示
        
        # 複製一份設定以便調整溫度等參數  # 參數調整
        current_generation_config = self.generation_config.copy()  # 複製設定
        if temperature is not None:  # 若有溫度覆寫
            current_generation_config["temperature"] = temperature  # 更新溫度
            logger.debug(f"Using temperature override: {temperature}")  # 記錄溫度

        retries = settings.API_MAX_RETRIES  # 最大重試次數
        delay = settings.API_RETRY_DELAY_SECONDS  # 初始等待時間
        
        # API 重試機制  # 失敗重試
        for attempt in range(retries):  # 逐次重試
            try:  # 嘗試呼叫 API
                logger.debug(f"API Call Attempt {attempt + 1} of {retries} to {effective_model_name}.")  # 記錄嘗試次數
                response = await acompletion(  # 呼叫 LiteLLM
                    model=effective_model_name,  # 模型
                    messages=[{"role": "user", "content": prompt}],  # 訊息內容
                    **(current_generation_config or {}),  # 生成參數
                    **(litellm_extra_params or {})  # 其他參數
                )
                
                if not response.choices:  # 若無回覆選項
                    logger.warning("LLM API returned no choices.")  # 記錄警告
                    return ""  # 回傳空字串

                generated_text = response.choices[0].message.content  # 取得回覆文字
                logger.debug(f"Raw response from LLM API:\n--RESPONSE START--\n{generated_text}\n--RESPONSE END--")  # 記錄原始回覆
                
                if output_format == "code":  # 若需要程式碼
                    if "```python" in generated_text:  # 若含 code fence
                        pass  # 保留在清理時處理
                    cleaned_code = self._clean_llm_output(generated_text)  # 清理輸出
                    logger.debug(f"Cleaned code:\n--CLEANED CODE START--\n{cleaned_code}\n--CLEANED CODE END--")  # 記錄清理後內容
                    return cleaned_code  # 回傳清理後程式碼
                else:  # diff 模式
                    logger.debug(f"Returning raw diff text:\n--DIFF TEXT START--\n{generated_text}\n--DIFF TEXT END--")  # 記錄 diff
                    return generated_text  # 回傳 diff                      
            except (APIError, InternalServerError, TimeoutError, RateLimitError, AuthenticationError, BadRequestError) as e:  # 可預期 API 錯誤
                logger.warning(f"LLM API error on attempt {attempt + 1}: {type(e).__name__} - {e}. Retrying in {delay}s...")  # 記錄錯誤
                if attempt < retries - 1:  # 若尚可重試
                    await asyncio.sleep(delay)  # 等待
                    delay *= 2  # 指數退避
                else:  # 重試耗盡
                    logger.error(f"LLM API call failed after {retries} retries for model {effective_model_name}.")  # 記錄錯誤
                    raise  # 丟出例外
            except Exception as e:  # 其他未知錯誤
                logger.error(f"An unexpected error occurred during code generation with {effective_model_name}: {e}", exc_info=True)  # 記錄錯誤
                raise  # 丟出例外
        
        logger.error(f"Code generation failed for model {effective_model_name} after all retries.")  # 重試失敗
        return ""  # 回傳空字串

    def _clean_llm_output(self, raw_code: str) -> str:  # 清理 LLM 輸出
        """
        清理 LLM 輸出內容（通常移除 markdown 程式碼圍欄）。  # 函式用途
        例如：```python\ncode\n``` -> code  # 範例
        """
        logger.debug(f"Attempting to clean raw LLM output. Input length: {len(raw_code)}")  # 記錄輸入長度
        code = raw_code.strip()  # 去除首尾空白
        
        if code.startswith("```python") and code.endswith("```"):  # Python code fence
            cleaned = code[len("```python"): -len("```")].strip()  # 移除 fence
            logger.debug("Cleaned Python markdown fences.")  # 記錄清理
            return cleaned  # 回傳清理後內容
        elif code.startswith("```") and code.endswith("```"):  # 一般 code fence
            cleaned = code[len("```"): -len("```")].strip()  # 移除 fence
            logger.debug("Cleaned generic markdown fences.")  # 記錄清理
            return cleaned  # 回傳清理後內容
            
        logger.debug("No markdown fences found or standard cleaning applied to the stripped code.")  # 記錄無 fence
        return code  # 回傳原始內容

    def _apply_diff(self, parent_code: str, diff_text: str) -> str:  # 套用 diff
        """
        將 AlphaEvolve 格式的 diff 套用到父代程式碼。  # 函式用途
        Diff format:
        <<<<<<< SEARCH
        # Original code block
        =======
        # New code block
        >>>>>>> REPLACE
        
        使用模糊比對以處理空白與縮排的微小差異。  # 容錯策略
        """
        logger.info("Attempting to apply diff.")  # 記錄開始
        logger.debug(f"Parent code length: {len(parent_code)}")  # 記錄父代長度
        logger.debug(f"Diff text:\n{diff_text}")  # 記錄 diff 內容

        modified_code = parent_code  # 初始化為父代
        diff_pattern = re.compile(r"<<<<<<< SEARCH\s*?\n(.*?)\n=======\s*?\n(.*?)\n>>>>>>> REPLACE", re.DOTALL)  # diff 正則
        
                                                                                
                                                             
        replacements_made = []  # 已替換區間
        
        for match in diff_pattern.finditer(diff_text):  # 逐一 diff 區塊
            search_block = match.group(1)  # SEARCH 內容
            replace_block = match.group(2)  # REPLACE 內容
            
                                                                        
            search_block_normalized = search_block.replace('\r\n', '\n').replace('\r', '\n').strip()  # 標準化換行
            
            try:  # 嘗試套用
                                       
                if search_block_normalized in modified_code:  # 完全匹配
                    logger.debug(f"Found exact match for SEARCH block")  # 記錄匹配
                    modified_code = modified_code.replace(search_block_normalized, replace_block, 1)  # 直接替換
                    logger.debug(f"Applied one diff block. SEARCH:\n{search_block_normalized}\nREPLACE:\n{replace_block}")  # 記錄替換
                else:  # 不完全匹配
                                                                                 
                    normalized_search = re.sub(r'\s+', ' ', search_block_normalized)  # 正規化空白
                    normalized_code = re.sub(r'\s+', ' ', modified_code)  # 正規化程式碼
                    
                    if normalized_search in normalized_code:  # 空白正規化匹配
                        logger.debug(f"Found match after whitespace normalization")  # 記錄匹配
                                                                        
                        start_pos = normalized_code.find(normalized_search)  # 取得起始位置
                        
                                                                          
                        original_pos = 0  # 原始字串位置
                        norm_pos = 0  # 正規化位置
                        
                        while norm_pos < start_pos and original_pos < len(modified_code):  # 對齊正規化位置
                            if not modified_code[original_pos].isspace() or (  # 若為有效字元
                                original_pos > 0 and  # 前一個存在
                                modified_code[original_pos].isspace() and  # 現在是空白
                                not modified_code[original_pos-1].isspace()  # 前一個不是空白
                            ):
                                norm_pos += 1  # 推進正規化位置
                            original_pos += 1  # 推進原始位置
                        
                                               
                        end_pos = original_pos  # 設定結束位置
                        remaining_chars = len(normalized_search)  # 尚需比對字元
                        
                        while remaining_chars > 0 and end_pos < len(modified_code):  # 找到結束位置
                            if not modified_code[end_pos].isspace() or (  # 若為有效字元
                                end_pos > 0 and  # 前一個存在
                                modified_code[end_pos].isspace() and  # 現在是空白
                                not modified_code[end_pos-1].isspace()  # 前一個不是空白
                            ):
                                remaining_chars -= 1  # 減少剩餘
                            end_pos += 1  # 推進結束位置
                        
                                                                                        
                        overlap = False  # 是否重疊
                        for start, end in replacements_made:  # 檢查已替換區間
                            if (start <= original_pos <= end) or (start <= end_pos <= end):  # 若重疊
                                overlap = True  # 標記重疊
                                break  # 跳出
                        
                        if not overlap:  # 若無重疊
                                                               
                            actual_segment = modified_code[original_pos:end_pos]  # 取得實際段落
                            logger.debug(f"Replacing segment:\n{actual_segment}\nWith:\n{replace_block}")  # 記錄替換
                            
                                                 
                            modified_code = modified_code[:original_pos] + replace_block + modified_code[end_pos:]  # 進行替換
                            
                                                     
                            replacements_made.append((original_pos, original_pos + len(replace_block)))  # 記錄替換區間
                        else:  # 若重疊
                            logger.warning(f"Diff application: Skipping overlapping replacement")  # 記錄警告
                    else:  # 正規化也找不到
                                                               
                        search_lines = search_block_normalized.splitlines()  # 拆成行
                        parent_lines = modified_code.splitlines()  # 父代程式碼行
                        
                                                                      
                        if len(search_lines) >= 3:  # 至少三行才做行匹配
                                                                  
                            first_line = search_lines[0].strip()  # 第一行
                            last_line = search_lines[-1].strip()  # 最後一行
                            
                            for i, line in enumerate(parent_lines):  # 逐行搜尋
                                if first_line in line.strip() and i + len(search_lines) <= len(parent_lines):  # 若首行匹配
                                                                     
                                    if last_line in parent_lines[i + len(search_lines) - 1].strip():  # 若末行也匹配
                                                                                       
                                        matched_segment = '\n'.join(parent_lines[i:i + len(search_lines)])  # 取得匹配段落
                                        
                                                              
                                        modified_code = '\n'.join(  # 替換該段落
                                            parent_lines[:i] +  # 前段
                                            replace_block.splitlines() +  # 新段落
                                            parent_lines[i + len(search_lines):]  # 後段
                                        )
                                        logger.debug(f"Applied line-by-line match. SEARCH:\n{matched_segment}\nREPLACE:\n{replace_block}")  # 記錄替換
                                        break  # 跳出
                            else:  # 若沒有找到
                                logger.warning(f"Diff application: SEARCH block not found even with line-by-line search:\n{search_block_normalized}")  # 記錄警告
                        else:  # 若 SEARCH 太短
                            logger.warning(f"Diff application: SEARCH block not found in current code state:\n{search_block_normalized}")  # 記錄警告
            except re.error as e:  # 正則錯誤
                logger.error(f"Regex error during diff application: {e}")  # 記錄錯誤
                continue  # 繼續下一個 diff
            except Exception as e:  # 其他錯誤
                logger.error(f"Error during diff application: {e}", exc_info=True)  # 記錄錯誤
                continue  # 繼續下一個 diff
        
        if modified_code == parent_code and diff_text.strip():  # 有 diff 但無變化
             logger.warning("Diff text was provided, but no changes were applied. Check SEARCH blocks/diff format.")  # 記錄警告
        elif modified_code != parent_code:  # 有變化
             logger.info("Diff successfully applied, code has been modified.")  # 記錄成功
        else:  # 無 diff
             logger.info("No diff text provided or diff was empty, code unchanged.")  # 記錄無變化
             
        return modified_code  # 回傳修改後程式碼

    async def execute(self, prompt: str, model_name: Optional[str] = None, temperature: Optional[float] = None, output_format: str = "code", parent_code_for_diff: Optional[str] = None, litellm_extra_params: Optional[Dict[str, Any]] = None) -> str:  # 通用執行入口
        """
        通用執行方法：  # 方法用途
        - output_format == 'diff'：產生 diff 並套用到 parent_code_for_diff  # diff 模式
        - 其他：直接產生完整程式碼  # code 模式
        """
        logger.debug(f"CodeGeneratorAgent.execute called. Output format: {output_format}")  # 記錄執行
        
        generated_output = await self.generate_code(  # 呼叫 generate_code
            prompt=prompt,  # 提示
            model_name=model_name,  # 模型
            temperature=temperature,  # 溫度
            output_format=output_format,  # 輸出格式
            litellm_extra_params=litellm_extra_params  # 額外參數
        )

        if output_format == "diff":  # 若為 diff 模式
            if not parent_code_for_diff:  # 若缺父代程式碼
                logger.error("Output format is 'diff' but no parent_code_for_diff provided. Returning raw diff.")  # 記錄錯誤
                return generated_output  # 回傳原始 diff
            
            if not generated_output.strip():  # 若 diff 為空
                logger.info("Generated diff is empty. Returning parent code.")  # 記錄狀態
                return parent_code_for_diff  # 回傳父代程式碼

            try:  # 嘗試套用 diff
                logger.info("Applying generated diff to parent code.")  # 記錄開始套用
                modified_code = self._apply_diff(parent_code_for_diff, generated_output)  # 套用 diff
                return modified_code  # 回傳修改後程式碼
            except Exception as e:  # 套用失敗
                logger.error(f"Error applying diff: {e}. Returning raw diff text.", exc_info=True)  # 記錄錯誤
                return generated_output  # 回傳原始 diff
        else:  # code 模式
            return generated_output  # 回傳程式碼

                                                 
if __name__ == '__main__':  # 直接執行測試
    import asyncio  # 測試用 asyncio
    logging.basicConfig(level=logging.DEBUG)  # 設定日誌
    from unittest.mock import Mock  # 測試時用來 mock 物件
    
    async def test_diff_application():  # 測試 diff 套用
        agent = CodeGeneratorAgent()  # 建立代理
        parent = """Line 1
Line 2 to be replaced
Line 3
Another block
To be changed
End of block
Final line"""  # 父代程式碼

        diff = """Some preamble text from LLM...
<<<<<<< SEARCH
Line 2 to be replaced
=======
Line 2 has been successfully replaced
>>>>>>> REPLACE

Some other text...

<<<<<<< SEARCH
Another block
To be changed
End of block
=======
This
Entire
Block
Is New
>>>>>>> REPLACE
Trailing text..."""  # 測試 diff
        expected_output = """Line 1
Line 2 has been successfully replaced
Line 3
This
Entire
Block
Is New
Final line"""  # 期望結果
        
        print("--- Testing _apply_diff directly ---")  # 印出標題
        result = agent._apply_diff(parent, diff)  # 直接呼叫 _apply_diff
        print("Result of diff application:")  # 印出標題
        print(result)  # 印出結果
        assert result.strip() == expected_output.strip(), f"Direct diff application failed.\nExpected:\n{expected_output}\nGot:\n{result}"  # 驗證結果
        print("_apply_diff test passed.")  # 成功訊息

        print("\n--- Testing execute with output_format='diff' ---")  # 印出標題
        async def mock_generate_code(prompt, model_name, temperature, output_format, litellm_extra_params=None):  # 測試時加入額外參數
            return diff  # 回傳固定 diff
        
        agent.generate_code = mock_generate_code  # 取代生成方法
        
        result_execute_diff = await agent.execute(  # 執行 diff 流程
            prompt="doesn't matter for this mock",  # 測試用提示
            parent_code_for_diff=parent,  # 父代程式碼
            output_format="diff",  # diff 模式
            litellm_extra_params={"example_param": "example_value"}  # 測試用參數
        )
        print("Result of execute with diff:")  # 印出標題
        print(result_execute_diff)  # 印出結果
        assert result_execute_diff.strip() == expected_output.strip(), f"Execute with diff failed.\nExpected:\n{expected_output}\nGot:\n{result_execute_diff}"  # 驗證結果
        print("Execute with diff test passed.")  # 成功訊息


    async def test_generation():  # 測試生成
        agent = CodeGeneratorAgent()  # 建立代理
        
        test_prompt_full_code = "Write a Python function that takes two numbers and returns their sum."  # 測試提示
        
        # Mock litellm.acompletion 以測試完整程式碼生成  # 使用 mock
        original_acompletion = litellm.acompletion  # 保存原始函式
        async def mock_litellm_acompletion(*args, **kwargs):  # mock 版本
            mock_response = Mock()  # 建立 mock response
            mock_message = Mock()  # 建立 mock message
            mock_message.content = "def mock_function():\n  return 'mocked_code'"  # 設定回覆內容
            mock_response.choices = [Mock()]  # 建立 choices
            mock_response.choices[0].message = mock_message  # 設定 message
            return mock_response  # 回傳 mock response
        
        litellm.acompletion = mock_litellm_acompletion  # 取代 acompletion
        
        try:  # 測試區塊
            generated_full_code = await agent.execute(test_prompt_full_code, temperature=0.6, output_format="code")  # 執行生成
            print("\n--- Generated Full Code (via execute) ---")  # 印出標題
            print(generated_full_code)  # 印出結果
            print("----------------------")  # 分隔線
            assert "def mock_function" in generated_full_code, "Full code generation with mock seems to have failed."  # 驗證結果
        finally:  # 還原
            litellm.acompletion = original_acompletion  # 還原原始函式

        parent_code_for_llm_diff = '''  # 父代程式碼
def greet(name):
    return f"Hello, {name}!"

def process_data(data):
    # TODO: 實作資料處理
    return data * 2  # 簡易佔位邏輯
'''
        test_prompt_diff_gen = f'''  # diff 測試提示
Current code:
```python
{parent_code_for_llm_diff}
```
Task: Modify the `process_data` function to add 5 to the result instead of multiplying by 2.
Also, change the greeting in `greet` to "Hi, {name}!!!".
'''
                                                                            
                                                           
                                          
                              
                                   
                                                           
           
                                                                       
                                           
                                         
                                                                                                               
                                                                                                           
        
        async def mock_generate_empty_diff(prompt, model_name, temperature, output_format):  # mock 空 diff
            return "  \n  "  # 回傳空白
        
        original_generate_code = agent.generate_code  # 保存原始方法
        agent.generate_code = mock_generate_empty_diff  # 取代生成方法
        
        print("\n--- Testing execute with empty diff from LLM ---")  # 印出標題
        result_empty_diff = await agent.execute(  # 執行 diff 模式
            prompt="doesn't matter",  # 測試提示
            parent_code_for_diff=parent_code_for_llm_diff,  # 父代程式碼
            output_format="diff"  # diff 模式
        )
        assert result_empty_diff == parent_code_for_llm_diff, "Empty diff should return parent code."  # 驗證結果
        print("Execute with empty diff test passed.")  # 成功訊息
        agent.generate_code = original_generate_code  # 還原方法

    async def main_tests():  # 主測試入口
        await test_diff_application()  # 測試 diff 套用
                                                                                     
        print("\nAll selected local tests in CodeGeneratorAgent passed.")  # 完成訊息

    asyncio.run(main_tests())  # 執行測試
