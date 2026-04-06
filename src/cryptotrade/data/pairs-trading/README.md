# K線配對交易策略 (Kline Pairs Trading)

## 策略目標

**核心目標**：利用 Binance 永續合約 1分鐘K線數據，實現配對交易策略，追求**高盈虧比**。

---

## 策略邏輯

### 進場條件

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `entry_amp` | 進場振幅閾值 | 0.5% |
| `top_n` | 每次取振幅前幾名 | 5 |

**進場邏輯**：
1. 每分鐘結束後，計算所有 USDT 永續合約的振幅：`Ampl% = (High - Low) / Low × 100`
2. 按振幅降序排列，取前 `top_n` 名
3. **做多**振幅第1名的幣種
4. **做空**振幅第3、4、5名的幣種

### 出場條件

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `exit_amp_ratio` | 出場振幅閾值 = `entry_amp × ratio` | 0.33 (N/3) |
| `stop_loss_ratio` | 止損振幅 = `entry_amp × ratio` | 2.0 (N×2) |
| `max_hold` | 最大持有分鐘數 | 5 |

**出場邏輯**：
- **停利**：振幅收縮到 `exit_amp` 以下，自動平倉
- **止損**：振幅擴大到 `stop_loss`，強制止損
- **強制平倉**：超過 `max_hold` 分鐘仍未平倉

---

## 專案架構

```
pairs-trading/
├── Makefile
├── requirements.txt
├── README.md
├── src/
│   ├── downloader.py      # Binance Futures 數據下載
│   ├── strategy.py        # 配對交易核心邏輯
│   ├── backtester.py     # 向量化回測引擎
│   └── analyzer.py        # 績效分析
├── data/raw/             # K線數據 (parquet)
└── results/              # 回測結果
```

---

## 使用方式

```bash
# 安裝依賴
make install

# 下載永續合約歷史數據 (2022-01-01 ~ 2024-01-01)
make download

# 執行回測
make backtest

# 分析結果
make analyze

# 執行測試
make test

# 清理數據
make clean
```

---

## 參數空間

| 參數 | 範圍 | 預設 |
|------|------|------|
| `entry_amp` | 0.3% ~ 1.0% | 0.5% |
| `top_n` | 5, 7 | 5 |
| `exit_amp_ratio` | 0.3 ~ 0.4 | 0.33 |
| `stop_loss_ratio` | 1.5 ~ 2.5 | 2.0 |
| `max_hold` | 3, 5, 7 分鐘 | 5 |

---

## 評估指標

1. **盈虧比 (Profit Factor)**：> 2.0
2. **夏普比率 (Sharpe)**：> 1.5
3. **勝率 (Win Rate)**：> 45%
4. **最大回撤 (Max DD)**：< 20%

---

## 數據來源

- **API**: Binance Futures (`fapi.binance.com`)
- **Endpoint**: `/fapi/v1/klines`
- **Interval**: 1m
- **Symbol**: USDT 永續合約

---

## 注意事項

- 這是純回測系統，不構成投資建議
- 過去績效不代表未來表現
- 請自行承擔交易風險
