# WebSocket Ping / Pong 心跳機制完整整理

> WebSocket Ping / Pong 是協議層級的心跳機制，用來確認連線是否存活，與應用層資料無關。

---

## 一、Ping / Pong 是什麼？

- WebSocket **控制幀（Control Frame）**
- 不會進入 `on_message`
- 由協議保證行為正確性

用途：
1. 檢測連線是否仍然存活
2. 防止 Proxy / NAT 關閉閒置連線
3. 偵測斷線與 RTT 延遲

---

## 二、誰會發 Ping？

- Client 或 Server **任何一方**
- 常見是 Server 定期發送（20–60 秒）

---

## 三、標準流程示意圖

```
Server                    Client
  |                        |
  | ---- Ping ----------> |
  |                        |
  | <--- Pong ----------- |
  |                        |
```

WebSocket library 會：
1. 自動回 Pong
2. 再觸發 `on_ping` callback

---

## 四、on_ping / on_pong 觸發時機

### on_ping
- 對方送 Ping
- **不需要手動回 Pong**
- 僅作為通知用途

### on_pong
- 自己送 Ping
- 對方回 Pong 後觸發

---

## 五、是否需要手動回應？

❌ 不需要  
❌ 也不應該

正確做法：
```python
def on_ping(ws, msg):
    pass
```

---

## 六、什麼時候 on_ping 有用？

- 監控連線活躍狀態
- Debug / 記錄 log
- 統計心跳頻率

單純維持連線 → 不需要

---

## 七、一直收到 Ping 代表什麼？

### 正常
- Server 有在維護連線
- 心跳頻率合理（20–60 秒）

### 異常
- Ping < 2 秒
- CPU / log 爆量
- Server 設定錯誤

---

## 八、主動發 Ping

```python
ws.ping("keep-alive")
```

收到 Pong 後：
```python
def on_pong(ws, msg):
    print("連線正常")
```

---

## 九、重點總結

| 問題 | 答案 |
|----|----|
| 收到 Ping 要回嗎 | 不用 |
| Pong 誰處理 | WebSocket library |
| on_ping 用途 | 監控 |
| on_message 會收到嗎 | 不會 |

---

一句話總結：

**Ping / Pong 是 WebSocket 的保命機制，你只需要觀察，不需要干預。**
