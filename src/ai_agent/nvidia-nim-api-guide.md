# NVIDIA NIM API 申請教學

NVIDIA 提供免費 API，可使用超過 100 個 AI 模型，包括 DeepSeek V4、Llama 4、Qwen、Gemma、GLM 等。

---

## 📝 註冊步驟

### Step 1: 前往 NVIDIA Build 平台

開啟官網：https://build.nvidia.com

### Step 2: 註冊/登入帳號

| 方式 | 說明 |
|------|------|
| 信箱註冊 | 推薦，最穩定 |
| 手機驗證 | +886 台灣號碼可用，但可能遇到驗證限制 |

### Step 3: 完成帳號驗證

根據提示完成信箱或手機驗證。

### Step 4: 取得 API Key

1. 登入後前往：https://build.nvidia.com/settings/api-keys
2. 點選 **Generate API Key**
3. 在彈出視窗點選 **Confirm**
4. 複製取得的 API Key（格式：`nvapi-xxxxx`）

> ⚠️ **注意**：API Key 只顯示一次，請立即儲存！

---

## ⚠️ 常見問題

### 手機驗證失敗

很多使用者反映會提示：
> "This phone number has exceeded limits, please try a different phone number"

**解決方案：**
1. 嘗試不同時段（避開高峰）
2. 使用信箱註冊驗證更穩定
3. 如持續失敗，可在 [NVIDIA Developer Forums](https://forums.developer.nvidia.com/) 發文求助
4. 嘗試更換其他手機號碼

---

## 🔧 API 使用方法

### curl 測試

```bash
curl -X POST "https://integrate.api.nvidia.com/v1/chat/completions" \
  -H "Authorization: Bearer nvapi-xxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ai/deepseek-v4-pro",
    "messages": [{"role": "user", "content": "你好，介紹一下自己"}],
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

### Python 呼叫

```python
from openai import OpenAI

# 初始化用戶端
client = OpenAI(
    api_key="nvapi-xxxxx",  # 替換為你的 API Key
    base_url="https://integrate.api.nvidia.com/v1"
)

# 送出請求
response = client.chat.completions.create(
    model="meta/llama-3.1-405b-instruct",
    messages=[
        {"role": "user", "content": "你好，請介紹一下自己"}
    ],
    temperature=0.7,
    max_tokens=1024
)

# 輸出結果
print(response.choices[0].message.content)
```

### Claude Code 設定

編輯 `~/.claude/settings.json`：

```json
{
  "ANTHROPIC_BASE_URL": "https://integrate.api.nvidia.com/v1",
  "ANTHROPIC_API_KEY": "nvapi-xxxxx"
}
```

---

## 🆓 支援的模型清單

### 中國模型

| 模型 | 模型 ID | 說明 |
|------|---------|------|
| DeepSeek V4 Pro | `deepseek-ai/deepseek-v4-pro` | 最新旗艦 |
| DeepSeek R1 | `deepseek-ai/deepseek-r1` | 推理增強 |
| Qwen 2.5 | `qwen/qwen-2.5-72b-instruct` | 通義千問 |
| Qwen Coder | `qwen/qwen2.5-coder-32b-instruct` | 程式專用 |
| GLM | 可在平台搜尋 | 智譜 AI 模型 |

### 國際模型

| 模型 | 模型 ID | 說明 |
|------|---------|------|
| Llama 3.1 405B | `meta/llama-3.1-405b-instruct` | Meta 最大模型 |
| Llama 4 | `meta/llama-4-...` | 新一代模型 |
| Mistral Large 3 | `mistralai/mistral-large-3` | 歐洲最強 |
| Gemma 4 | `google/gemma-...` | Google 開源 |

### NVIDIA 自家研發

| 模型 | 模型 ID | 說明 |
|------|---------|------|
| Nemotron | `nvidia/nemotron-...` | NVIDIA 最佳化模型 |

---

## 💰 免費額度說明

NVIDIA 提供免費 API Credits：

- **用途**：原型開發、效能評估、學習測試
- **限制**：有配額上限，超出需付費
- **優勢**：合規官方管道，無需中轉站

---

## 🔗 相關連結

| 資源 | 連結 |
|------|------|
| 官網首頁 | https://build.nvidia.com |
| API Key 頁面 | https://build.nvidia.com/settings/api-keys |
| 模型目錄 | https://build.nvidia.com/explore |
| 開發者論壇 | https://forums.developer.nvidia.com/ |
| 官方文件 | https://docs.nvidia.com/nim/ |

---

## 📚 參考資料

- [NVIDIA NIM 官方文件](https://docs.nvidia.com/nim/)
- [零成本玩轉頂規 AI - CSDN 教學](https://openeuler.csdn.net/6a059d6d10ee7a33f27274cc.html)
- [NVIDIA 免費 API 教學 - YouTube](https://www.youtube.com/watch?v=eirsXaSY91M)

---

## ✅ 檢查清單

申請前請確認：

- [ ] 已準備有效信箱地址
- [ ] 手機號（可選，信箱驗證更穩定）
- [ ] 已前往 https://build.nvidia.com
- [ ] 完成帳號註冊與驗證
- [ ] 已產生並儲存 API Key

申請後請測試：

- [ ] 用 curl 測試 API 連通性
- [ ] 確認模型回傳正常回應
- [ ] 檢查 API Key 格式正確（`nvapi-` 開頭）

---

*文件產生時間：2026-05-31*
