# 1. 選擇合適的 Python 基底映像
FROM python:3.10-slim

# 2. 設定工作目錄
WORKDIR /app

# 3. temp_script.py 會在執行時動態產生並掛載到此目錄
#    WORKDIR 只確保 /app 存在
#    若需從 build context 複製檔案，可在此加入
#    例如：COPY ./my_utility_script.py /app/my_utility_script.py

# 4. 確保 Python 輸出不被緩衝
ENV PYTHONUNBUFFERED=1

# 5. 建置指令（建議名稱：code-evaluator:latest）
#    docker build -t code-evaluator:latest .

# 6. 目前不需額外套件
#    若要安裝依賴，取消註解並修改以下內容：
#    COPY requirements.txt .
#    RUN pip install --no-cache-dir -r requirements.txt
#
#    確保 requirements.txt 與 Dockerfile 在同一個目錄（build context）
#    requirements.txt 範例：
#    # numpy==1.23.5
#    # pandas==1.5.3

# 若每次 `docker run` 都指定命令，預設 CMD 可省略
# 例如：EvaluatorAgent 會傳入 `python temp_script.py`
# CMD ["python"]
