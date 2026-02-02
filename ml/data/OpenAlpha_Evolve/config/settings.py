"""
專案設定：包含模型、演化參數、Docker 及日誌設定。
"""
import os  # 環境變數與系統操作
from dotenv import load_dotenv  # 讀取 .env

load_dotenv()  # 載入環境變數

# LLM 設定
FLASH_API_KEY = os.getenv("FLASH_API_KEY")  # Flash API Key
FLASH_BASE_URL = os.getenv("FLASH_BASE_URL", None)  # Flash Base URL
FLASH_MODEL = os.getenv("FLASH_MODEL")  # Flash 模型名稱

# PRO_API_KEY = os.getenv("PRO_API_KEY")
# PRO_BASE_URL = os.getenv("PRO_BASE_URL", None)
# PRO_MODEL = os.getenv("PRO_MODEL")

EVALUATION_API_KEY = os.getenv("EVALUATION_API_KEY")  # 評估 API Key
EVALUATION_BASE_URL = os.getenv("EVALUATION_BASE_URL", None)  # 評估 Base URL
EVALUATION_MODEL = os.getenv("EVALUATION_MODEL")  # 評估模型名稱

# LiteLLM 設定
LITELLM_DEFAULT_MODEL = os.getenv("LITELLM_DEFAULT_MODEL", "gpt-3.5-turbo")  # LiteLLM 預設模型
LITELLM_DEFAULT_BASE_URL = os.getenv("LITELLM_DEFAULT_BASE_URL", None)  # LiteLLM Base URL
LITELLM_MAX_TOKENS = os.getenv("LITELLM_MAX_TOKENS")  # 最大 token
LITELLM_TEMPERATURE = os.getenv("LITELLM_TEMPERATURE")  # 溫度
LITELLM_TOP_P = os.getenv("LITELLM_TOP_P")  # top_p
LITELLM_TOP_K = os.getenv("LITELLM_TOP_K")  # top_k

# 特定模型名稱（可與預設模型相同）
LLM_PRIMARY_MODEL = os.getenv("LLM_PRIMARY_MODEL", LITELLM_DEFAULT_MODEL)  # 主模型
LLM_SECONDARY_MODEL = os.getenv("LLM_SECONDARY_MODEL", FLASH_MODEL if FLASH_MODEL else LLM_PRIMARY_MODEL)  # 次模型

# if not PRO_API_KEY:
#     print("警告：未找到 PRO_API_KEY（.env 或環境變數）。目前使用無效佔位值，請在 .env 中設定正確的 API key。")
#     PRO_API_KEY = "Your API key"

# 演化演算法設定
POPULATION_SIZE = 5  # 族群大小
GENERATIONS = 2  # 世代數
# 切換到 bug-fix 提示的門檻
# 若程式有錯誤且正確率低於此值，將使用修錯提示
BUG_FIX_CORRECTNESS_THRESHOLD = float(os.getenv("BUG_FIX_CORRECTNESS_THRESHOLD", "0.1"))  # 修錯門檻
# 使用主模型（可能更強但更貴）的門檻
HIGH_FITNESS_THRESHOLD_FOR_PRIMARY_LLM = float(os.getenv("HIGH_FITNESS_THRESHOLD_FOR_PRIMARY_LLM", "0.8"))  # 高適應度門檻
ELITISM_COUNT = 1  # 菁英數
MUTATION_RATE = 0.7  # 突變率
CROSSOVER_RATE = 0.2  # 交叉率

# 島嶼模型設定
NUM_ISLANDS = 4  # 子族群數量
MIGRATION_INTERVAL = 4  # 遷移間隔（世代）
ISLAND_POPULATION_SIZE = POPULATION_SIZE // NUM_ISLANDS  # 每島個體數
MIN_ISLAND_SIZE = 2  # 每島最小數量
MIGRATION_RATE = 0.2  # 遷移比例

# 除錯設定
DEBUG = os.getenv("DEBUG", "False").lower() == "true"  # 是否除錯
EVALUATION_TIMEOUT_SECONDS = 800  # 評估超時秒數

# Docker 執行設定
DOCKER_IMAGE_NAME = os.getenv("DOCKER_IMAGE_NAME", "code-evaluator:latest")  # Docker 映像名稱
DOCKER_NETWORK_DISABLED = os.getenv("DOCKER_NETWORK_DISABLED", "True").lower() == "true"  # 是否禁網

DATABASE_TYPE = "json"  # 資料庫類型
DATABASE_PATH = "program_database.json"  # 資料庫檔案

# 日誌設定
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"  # 日誌等級
LOG_FILE = "alpha_evolve.log"  # 日誌檔案
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # 日誌格式
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"  # 日期格式

API_MAX_RETRIES = 5  # API 重試次數
API_RETRY_DELAY_SECONDS = 10  # 重試延遲

RL_TRAINING_INTERVAL_GENERATIONS = 50  # RL 訓練間隔
RL_MODEL_PATH = "rl_finetuner_model.pth"  # RL 模型路徑

MONITORING_DASHBOARD_URL = "http://localhost:8080"  # 監控面板 URL

def get_setting(key, default=None):  # 取得設定值
    """
    取得設定值。
    LLM 模型會先使用 primary，如無則回退到 secondary/default。
    """
    return globals().get(key, default)  # 回傳設定

def get_llm_model(model_type="default"):  # 取得 LLM 模型名稱
    if model_type == "default":  # 預設模型
        return LITELLM_DEFAULT_MODEL  # 回傳預設
    elif model_type == "flash":  # flash 模型
        # 若 FLASH_MODEL 有設定則優先使用，否則回退預設模型  # 回退邏輯
        return FLASH_MODEL if FLASH_MODEL else LITELLM_DEFAULT_MODEL  # 若未設定則回預設
    # 其他未處理情況一律回退到預設模型  # 預設回退
    return LITELLM_DEFAULT_MODEL  # 回傳預設

                                 
