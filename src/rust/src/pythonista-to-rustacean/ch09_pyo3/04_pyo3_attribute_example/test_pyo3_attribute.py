import pyo3_attribute_example
from pyo3_attribute_example import run_job, run_job_with_dynamic_default

print(pyo3_attribute_example.function_with_warning())
pyo3_attribute_example.function_with_warning_and_custom_category()


# 1. 最簡潔的呼叫：只提供必要的 positional-only 參數 `source`。
#    `*steps` 會是空 tuple，其他參數則使用預設值。
run_job("s3://my-bucket/data.csv")

# 2. 傳遞 `*args`：除了 `source`，額外的位置參數會被收集到 `steps` 中。
run_job("local/input.json", "clean", "transform", "validate")

# 3. 使用關鍵字參數：明確指定 `retries` 與 `verbose`，覆寫它們的預設值。
#    注意，因為它們在 `*steps` 之後，所以必須用關鍵字來傳遞。
run_job("<ftp://server/files>", retries=5, verbose=True)

# 4. 傳遞 `**kwargs`：任何未定義的關鍵字參數，如 `timeout` 和 `user`，
#    都會被收集到 `extra_config` 這個 dict 中。
run_job(
    "database/connection_string",
    "load_data",
    "process_batch",
    timeout=60,
    user="admin",
)

print(run_job_with_dynamic_default.__text_signature__)