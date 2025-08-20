# 【Day 26】- Ollama: 革命性工具讓本地 AI 開發觸手可及 - 從安裝到進階應用的完整指南

## 摘要

這篇文章是一篇關於 Ollama 的詳細指南，介紹了 Ollama 這個開源本地大型語言模型運行框架。文章首先介紹了 Ollama 的背景、特性和優點，強調它為開發者和技術愛好者提供了一個簡單而強大的本地 AI 開發環境。接著文章詳細說明了 Ollama 的安裝、啟動、模型運行、API 呼叫、關閉和更新等步驟，並提供了一些實用的提示和常見問題的解決方案。文章還介紹了如何在 Docker 環境和 Colab 中部署 Ollama，以及如何使用 GGUF 格式將 HuggingFace 模型轉換為 Ollama 支持的格式。最後，文章總結了 Ollama 的進階應用，包括使用 Web UI 來創建一站式的本地 AI 開發環境，以及如何使用自定義模型。文章強調了 Ollama 在本地 AI 開發中的重要性，並鼓勵讀者探索 Ollama 的無限可能。

在人工智能快速發展的今天，大型語言模型（LLM）已成為技術創新的核心驅動力。然而，運行這些模型往往需要強大的雲端資源和專業知識。這就是 Ollama 出現的契機——它為開發者和技術愛好者提供了一個簡單而強大的解決方案，讓在本地環境中運行和管理大型語言模型變得觸手可及。

## 什麼是 Ollama？

Ollama 是一個開源的本地大型語言模型（LLM）運行框架，旨在簡化在本地環境中運行和管理大型語言模型的過程。它支援多種開源的大型語言模型，如 Llama 3、Phi 3、Mistral、Gemma 等，並且可以在 macOS、Linux 和 Windows 平台上運行。

### Ollama 的核心特色

- **豐富的模型庫**：Ollama 提供了一個不斷擴展的預訓練模型庫，從通用模型到針對特定領域的專業模型，應有盡有。
- **簡單易用**：即使是沒有技術背景的用戶也能輕鬆安裝和使用 Ollama。
- **本地運行，保障隱私**：所有模型運行和數據存儲均在本地進行，確保數據隱私和安全。
- **跨平台支持**：支援 macOS、Linux 和 Windows（預覽版），滿足不同用戶的需求。
- **靈活性與可定制性**：用戶可以根據自己的需求自定義模型行為，調整系統提示詞、模型推理溫度、上下文窗口長度等參數。

> **亮點提示**：Ollama 的本地運行特性不僅保護了用戶的數據隱私，還降低了對雲端服務的依賴，為個人和小型團隊提供了更經濟實惠的 AI 開發環境。

## Ollama 安裝與基礎使用

### 安裝步驟

1. 訪問 [Ollama 官網](https://ollama.com)。
2. 根據您的操作系統（macOS、Windows 或 Linux）下載相應的安裝包。
3. 運行安裝程序：

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 啟動 Ollama

打開終端或命令提示符，輸入以下命令啟動 Ollama 服務：

```bash
ollama serve
```

### 下載和運行模型

1. **下載模型**：使用 `ollama pull <模型名稱>` 命令下載所需的模型。例如：

```bash
ollama download gemma:2b
```

2. **運行模型**：使用以下命令啟動模型並與之交互：

```bash
ollama run gemma:2b
```

> **實用提示**：首次下載模型可能需要一些時間，取決於您的網絡速度和模型大小。建議在網絡良好的環境下進行初次設置。

## API 調用

Ollama 提供了 REST API，方便開發者集成到自己的應用中。以下是一個簡單的例子：

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "gemma:2b",
  "messages": [
    { "role": "user", "content": "What is 2+2?" }
  ],
  "stream": false
}'
```

## 關閉 Ollama

值得注意的是，即使終端顯示程序已"結束"，Ollama 的服務可能仍在後台運行。對於 macOS 用戶，可以通過以下步驟完全退出：

這將徹底關閉 Ollama 服務，釋放所有相關資源。

## 更新 Ollama

根據筆者的使用經驗，在 Mac 平台上，每次打開 ollama 時，會自動檢查是否需要更新，而且官方更新也滿頻繁的，建議大家可以 follow 官方連結。如果要更新的話 ollama 圖案旁便會成下載 icon ，點擊 'Restart to Update'，不到一分鐘時間就行了。

## 支持的模型

Ollama 支援多種大型語言模型，以下是部分可供下載的模型列表：

| 模型 | 參數 | 大小 | 下載命令 |
|---|---|---|---|
| Llama 3.1 | 8B | 4.7GB | `ollama run llama3.1` |
| Phi 3 Mini | 3.8B | 2.3GB | `ollama run phi3` |
| Gemma 2 | 2B | 1.6GB | `ollama run gemma2:2b` |
| Mistral | 7B | 4.1GB | `ollama run mistral` |
| Code Llama | 7B | 3.8GB | `ollama run codellama` |

> **注意**：運行 7B 模型需要至少 8GB RAM，13B 模型需要 16GB RAM，33B 模型需要 32GB RAM。

## Docker 部署

對於希望在 Docker 環境中運行 Ollama 的用戶，特別是只有 CPU 的設備，可以使用以下命令：

```bash
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama:latest
```

此指令部署最新 Ollama 鏡像，包含所有必要的庫和依賴

### 運行模型

```bash
docker exec -it ollama ollama run gemma:2b
```

## Colab 部署（演示用途）

這邊只是示範性用法，你可以透過以下指令在 colab 上直接跑起 ollama，更為克難的作法，只是效率極度差。僅用來證明可以跑服務在 colab 上，不具有任何實際價值，建議大家還是跑在電腦上比較好。況且多數語言模型環境可以使用 ollama 進行部署，工作上還是利多的。

```python
%load_ext colabxterm
%xterm
```

接著安裝：

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

並在 terminal 當中輸入：

```bash
ollama serve & ollama pull llama3
```

接著就可以跟模型對話了。

## 進階應用：Ollama + Web UI 完整部署

為了讓 Ollama 的使用更加便捷，我們可以結合 Ollama WebUI 來創建一個完整的本地 AI 開發環境。這個方法不僅簡化了部署過程，還提供了一個友好的圖形界面。

### Docker Compose 配置

使用以下 Docker Compose 配置文件來同時部署 Ollama 和 Web UI：

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - 11434:11434
    volumes:
      - ollama:/root/.ollama
    container_name: ollama
    pull_policy: always
    tty: true
    restart: always
    # GPU 支持（如果有 NVIDIA GPU，請註釋掉以下行）
    #deploy:
    #  resources:
    #    reservations:
    #      devices:
    #        - driver: nvidia
    #          count: 1
    #          capabilities:
    #            - gpu

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    volumes:
      - open-webui:/app/backend/data
    depends_on:
      - ollama
    ports:
      - 3000:8080
    environment:
      - "OLLAMA_API_BASE_URL=http://ollama:11434/api"
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped

volumes:
  ollama: {}
  open-webui: {}
```

> **專業提示**：這份配置文件已經上傳到 Gist，您可以直接使用。

### 部署命令

```bash
wget https://gist.github.com/Heng-xiu/3871b011b0159f776f755fcd46fea857/raw/docker-compose.yml
docker-compose up -d
```

> **注意**：如果您有 NVIDIA GPU，請確保註釋掉 YAML 文件中的 GPU 相關行（17-24行）。

### 訪問 Web UI

部署完成後，您可以通過訪問 http://localhost:3000/ 來使用 Ollama WebUI。如果您是在遠程服務器上部署，請將 `localhost` 替換為服務器的 IP 地址。

> **專業提示**：如果 WebUI 鏡像連接失效，您可以訪問 Github Repo 查找最新的部署方法。

恭喜！您已經成功在短短兩分鐘內部署了 Ollama 和 Ollama WebUI，無需繁瑣的 pod 部署過程。

## 常見問題與解決方案

在使用 Ollama 和 Open WebUI 的過程中，您可能會遇到一些常見問題。以下是一些問題的解決方法：

### 1. Docker 網絡連接問題

**問題描述**：Docker 容器無法連接到主機上的服務，導致 Open WebUI 無法正常運行。

**解決方法**：使用 `host.docker.internal` 代替 `localhost` 來連接主機服務：

```yaml
environment:
  - API_URL=http://host.docker.internal:11434
```

### 2. Open WebUI 連接錯誤

**問題描述**：Open WebUI 顯示連接錯誤或需要更新。

**解決方法**：

```bash
docker-compose pull
docker-compose up -d
```

### 3. Open WebUI 啟動失敗

**問題描述**：Open WebUI 無法啟動，可能是由於配置錯誤或依賴項缺失。

**解決方法**：

```bash
docker-compose logs open-webui
```

### 4. 調試和日誌查看

**問題描述**：需要更多信息來調試問題。

**解決方法**：

```bash
# 查看 Ollama 日誌
tail -f /path/to/ollama/logs

# 查看 Open WebUI 日誌
docker-compose logs open-webui
```

> **專業提示**：定期檢查日誌可以幫助您及時發現和解決潛在問題，保持系統的穩定運行。

## 自定義模型：HuggingFace 轉換為 GGUF 格式

在 AI 開發領域，許多開發者經常在雲端上微調大型語言模型（LLMs），並希望能夠在本地環境中運行這些模型。然而，這個過程往往充滿挑戰，需要在各種平台和社區中尋找解決方案。幸運的是，GGUF 格式和 Ollama 的結合為這個問題提供了一個優雅的解決方案。

本節將指導您如何將模型轉換為 GGUF 格式、創建模型文件，並在 Ollama 上成功運行您的自定義 LLMs。無論您是研究人員、開發者，還是 AI 愛好者，這個指南都將幫助您在本地機器上充分利用您的自定義模型。

### 什麼是 GGUF？

GGUF（GGML Universal Format）是由 llama.cpp 團隊開發的 GGML 的後續版本，專為大型語言模型設計的量化格式。

> **專業提示**：GGUF 格式特別適合需要在資源受限環境中運行大型模型的場景，如個人電腦或移動設備。

來源：[GGUF 文檔](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)

### 轉換步驟

以下是將 HuggingFace 模型轉換為 Ollama 支持的 GGUF 格式的步驟：

#### 1. 安裝必要工具

首先，我們需要安裝 `llama.cpp` 和 `huggingface_hub`：

```bash
# clone llama.cpp Repo
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# 安裝 huggingface_hub
pip install huggingface_hub
```

#### 2. 下載模型

使用 `huggingface_hub` 下載所需的模型：

```python
from huggingface_hub import snapshot_download, login

login("你的 access token")

# 下载模型
snapshot_download(
    "google/gemma-2b",
    local_dir="gemma-2b",
    local_dir_use_symlinks=False,
    ignore_patterns=["*.gguf"]
)
```

#### 3. 轉換為 GGUF 格式

使用 `llama.cpp` 提供的轉換腳本：

```bash
# 進入 llama.cpp 目錄
cd llama.cpp

# 執行轉換腳本
python convert_hf_to_gguf.py gemma-2b --outtype f16 --outfile gemma-2b.fp16.gguf
```

#### 4. 模型量化（可選）

如果需要進一步優化模型大小和計算效率，可以進行量化：

```bash
# 量化模型
./build/bin/llama-quantize gemma-2b.fp16.gguf --output gemma-2b/gemma-2b-q4-m.gguf q4_k_m
```

> **注意**：量化可能會略微影響模型性能，但能顯著減少模型大小和推理時間。

#### 5. 上傳到 HuggingFace（可選）

如果您想分享您的轉換成果，可以將模型上傳到 HuggingFace：

```python
from huggingface_hub import HfApi

api = HfApi()
api.upload_folder(
    folder_path="gemma-2b/gemma-2b-q4-m.gguf",
    repo_id="你的 HuggingFace Repo ID",
    repo_type="model"
)
```

### 在 Ollama 中使用自定義模型

#### 創建 Modelfile

```bash
echo "FROM ./gemma-2b/gemma-2b-q4-m.gguf" > Modelfile
```

#### 創建和運行模型

```bash
ollama create my-custom-model -f ./Modelfile
ollama run my-custom-model
```

### 分享您的模型

#### 獲取公鑰

```bash
cat ~/.ollama/id_ed25519.pub
```

將公鑰添加到 Ollama 網站的設置中。

#### 上傳模型

```bash
ollama push <Your-name>/<Model-name>
```

成功上傳後，您可以在 [Ollama Hub](https://ollama.com/hengshiou/gemma-2b-q4) 中查看您的模型。

### 小結

通過本指南，您已經學會了如何將 HuggingFace 模型轉換為 Ollama 支持的 GGUF 格式，並成功在本地環境中部署和運行這些模型。這個過程涉及模型下載、格式轉換、可選的量化步驟，以及在 Ollama 中的使用和分享。

掌握這些技能將使您能夠更靈活地在本地環境中使用和實驗各種大型語言模型，無論是用於研究、開發還是個人項目。

> **專業提示**：本文所有操作步驟都可以在這個 Github Repo 中找到，歡迎參考和實踐。

通過實踐這些步驟，您不僅可以運行自定義模型，還可以深入了解模型轉換和優化的過程，為您的 AI 開發之旅增添新的維度。

## 結論

Ollama 為開發者和 AI 愛好者提供了一個強大而靈活的工具，使本地運行大型語言模型變得前所未有的簡單。無論您是想要進行 AI 研究、開發智能應用，還是僅僅出於好奇想要探索 AI 的潛力，Ollama 都為您提供了一個理想的起點。

隨著 AI 技術的不斷發展，Ollama 這樣的工具將在推動 AI 民主化和創新方面發揮越來越重要的作用。現在正是開始您的 Ollama 之旅的最佳時機，探索本地 AI 開發的無限可能！

即刻前往教學程式碼 Repo，親自搭建屬於自己的 LLM Server 吧！別忘了給專案按個星星並持續關注更新，讓我們一起探索 AI 代理的新境界。

## 參考資料

最近消息是，可以直接從 HuggingFace 上拉 GGUF 格式檔案，不用額外建立 manifest，具體操作已經收錄在 HuggingFace blog 當中，可以做參考，未來有機會再行整理：[https://huggingface.co/docs/hub/en/ollama](https://huggingface.co/docs/hub/en/ollama)