# 🌐 網站變動追蹤工具 - changedetection.io 使用教學（Docker）

## 📦 安裝步驟

```bash
git clone https://github.com/dgtlmoon/changedetection.io.git
cd changedetection.io
docker compose up -d
````

這會啟動一個本機服務，使用 Docker 建立網站監控後台。

---

## 🌍 開啟網站管理介面

打開瀏覽器，輸入：

```
http://localhost:5000
```

如果是遠端主機，請改成伺服器的 IP，例如：

```
http://192.168.1.123:5000
```

---

## ➕ 新增要追蹤的網站

1. 點選右上角 **"Add new"**
2. 填入網址，例如：

   ```
   https://www.ptt.cc/bbs/Gossiping/index.html
   ```
3. （可選）設定：

   * **比對頻率**（預設每 5 分鐘）
   * **通知條件**
   * **只追蹤頁面某區塊**（使用 CSS Selector）

---

## 🔍 查看變更紀錄

當網頁有變動時：

* UI 會顯示「變更次數」
* 點進去可看到紅色（刪除）/綠色（新增）比對內容
* 可以選擇略過空白差異、時間戳等

---

## 🔧 常用操作

| 操作     | 指令                       |
| ------ | ------------------------ |
| 啟動服務   | `docker compose up -d`   |
| 停止服務   | `docker compose down`    |
| 查看 log | `docker compose logs -f` |

---

## ✅ 適用場景

* 商品價格變化追蹤
* 網頁公告是否更新
* 訂票、招生、報名通知
* 自己架設的簡易監控系統

---

## 📎 官方網站與原始碼

* GitHub: [https://github.com/dgtlmoon/changedetection.io](https://github.com/dgtlmoon/changedetection.io)

````

---

### 👉 儲存檔案指令

你可以在 Linux / Ubuntu 用這樣方式存成檔案：

```bash
nano changedetection-setup.md
# 貼上內容後 Ctrl+O 存檔，Ctrl+X 離開
````

或用任何你喜歡的編輯器（如 VSCode）直接貼上這份內容。

需要我幫你加上通知設定（例如 Telegram 或 email）說明到這份教學裡嗎？
