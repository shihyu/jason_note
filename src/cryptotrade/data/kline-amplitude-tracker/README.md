# K線振幅追蹤器 (Kline Amplitude Tracker)

## 策略邏輯

### 核心目標
追蹤 Binance 所有 USDT 交易對的**每分鐘價格振幅**，並計算**過去一小時成交金額**，用於發現短線波動異常的幣種。

### 數據維度

| 欄位 | 說明 |
|------|------|
| Symbol | USDT 交易對名稱 |
| Minute | 當前分鐘時間 (UTC) |
| Open | 該分鐘第一筆成交價 |
| High | 該分鐘最高價 |
| Low | 該分鐘最低價 |
| Close | 該分鐘最後成交價 |
| Ampl% | 振幅百分比 = (High - Low) / Low × 100 |
| Vol(USDT,1h) | 過去一小時累計成交金額 (USDT) |

### 篩選邏輯

- **振幅排序**：結果依 `Ampl%` 降序排列，振幅越大的幣種排在前面
- **Top N 模式**：可透過 `--top N` 參數限制只顯示成交金額前 N 名的幣種
- **時效性**：每約 60 秒刷新一次數據

### 使用方式

```bash
# 安裝依賴
make install

# 顯示所有幣種（按振幅排序）
make run

# 只顯示過去一小時成交金額前 100 名
make run-top

# 自訂名次
python collect_usdt_trades.py --top 50
```

### 輸出範例

```
# USDT Pairs - 1 Min Tick Amplitude

│ Symbol │ Minute │ Open   │ High   │ Low    │ Close  │ Ampl%  │ Vol(USDT,1h) │
│ BTCUSDT│ 14:32  │ 67420  │ 67580  │ 67350  │ 67520  │ 0.34   │ 1.25B        │
│ ETHUSDT│ 14:32  │ 3520   │ 3545   │ 3510   │ 3530   │ 1.00   │ 850.20M      │
```

### 適用場景

- 發現短線波動異常的幣種
- 追蹤熱門交易對的流動性
- 輔助技術分析與交易決策
