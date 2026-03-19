# 使用指南

一句總結：這個版本是「週資料牛熊切換 + 牛市只持有全市場相對強勢 `Top 10` + 熊市全空手」的回測，不使用個股放空，也沒有實作獨立停損價記錄。

## 參數

| 參數 | 預設值 | 說明 |
| --- | --- | --- |
| `ma_window` | `30` | 牛熊切換與個股趨勢判斷的週均線長度 |
| `breakout_window` | `20` | 近 `20` 週突破區間 |
| `volume_window` | `20` | 量增比較基準 |
| `relative_strength_window` | `4` | 相對強度視窗 |
| `top_n` | `10` | 持股數量 |
| `discount` | `0.3` | 券商折扣 |

## 1. 市場狀態分類

程式位置：
- [regime.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/regime.py#L4)

| Regime | 觸發條件 | 實際意義 |
| --- | --- | --- |
| `bull` | 大盤週收盤 > `30` 週均線，`30` 週均線斜率 > `flat_tolerance`，且近 `4` 週斜率 > `flat_tolerance x 2` | 允許建立多單 |
| `top` | 大盤週收盤 > `30` 週均線，但不滿足 `bull` 的動能條件 | 不持股，轉保守 |
| `bear` | 大盤週收盤 < `30` 週均線，且 `30` 週均線斜率 < `-flat_tolerance` | 全空手 |
| `base` | 其他情況，或資料不足 `30` 週 | 全空手 |

## 2. 選股邏輯

程式位置：
- [signal_builder.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/signal_builder.py#L21)

輸入：
- 週收盤價 `close`
- 週成交量 `volume`
- 大盤週收盤 `benchmark`

判斷條件：

| 條件 | 實作 | 程式位置 |
| --- | --- | --- |
| 個股站上 `30` 週均線 | `close.iloc[-1] > moving_average` | [signal_builder.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/signal_builder.py#L23) |
| 突破近 `20` 週高點 | `close.iloc[-1] > close.shift(1).rolling(20).max().iloc[-1]` | [signal_builder.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/signal_builder.py#L24) |
| 量增 | `volume.iloc[-1] > volume.rolling(20).mean().iloc[-1]` | [signal_builder.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/signal_builder.py#L25) |
| 相對大盤強勢 | `個股近 4 週報酬 - 大盤近 4 週報酬 > 0` | [signal_builder.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/signal_builder.py#L27) |

排序方式：
- 先過濾上面四個條件。
- 再依 `relative_strength` 由大到小排序。
- 取前 `10` 檔。
- 每檔等權重 `1 / 檔數`。

輸出：
- 一個週頻率的目標權重表 `weights`。

## 3. 進場邏輯

程式位置：
- [signal_builder.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/signal_builder.py#L45)
- [backtest_runner.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/backtest_runner.py#L14)

實際流程：

```text
讀到本週週資料
  -> 先判斷本週是否為 bull
  -> 如果不是 bull，本週目標權重全部為 0
  -> 如果是 bull，根據截至本週收盤的資料挑出 Top 10
  -> 把這份目標權重寫在本週日期
  -> 回測時做 positions.shift(1)
  -> 所以下一週才真正持有
```

重點：
- 這個版本不是「訊號當週立刻買」。
- 這個版本也不是「次交易日開盤價成交」。
- 它是「本週收盤後產生訊號，下一個週 bar 才開始承擔報酬」。

## 4. 出場邏輯

程式位置：
- [signal_builder.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/signal_builder.py#L54)

這版的實際出場，不是用獨立的停損單，而是每週重算目標權重後，未被保留的股票在下一週退出。

### 會觸發退出的情況

| 退出原因 | 是否已實作 | 實作方式 |
| --- | --- | --- |
| 大盤不是 `bull` | 是 | 權重直接清為 `0`，下一週退出 |
| 個股跌回 `30` 週均線下 | 是 | 因為不再通過選股條件，下一週退出 |
| 個股不再突破近 `20` 週高點 | 是 | 因為不再通過選股條件，下一週退出 |
| 個股量能不足 | 是 | 因為不再通過選股條件，下一週退出 |
| 個股相對強度轉弱 | 是 | 因為不再通過選股條件，下一週退出 |
| 跌破進場時的整理區低點 | 否 | 這版沒有記錄個股進場平台低點 |
| 固定停損價/移動停損 | 否 | 這版沒有實作 |

## 5. 成本模型

程式位置：
- [cost_model.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/cost_model.py#L1)
- [backtest_runner.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/backtest_runner.py#L30)

| 項目 | 計算方式 |
| --- | --- |
| 買進手續費率 | `0.001425 x 0.3 = 0.0004275` |
| 賣出手續費率 | `0.001425 x 0.3 = 0.0004275` |
| 賣出證交稅率 | `0.003` |
| 賣出總成本率 | `0.0004275 + 0.003 = 0.0034275` |

回測如何扣成本：
- 先算 `shift(1)` 後的實際持倉變化。
- 權重增加的部分，扣買進成本。
- 權重減少的部分，扣賣出成本。
- 成本直接從該週策略報酬扣掉。

這表示：
- 成本有扣。
- 但扣的是「權重比例成本」，不是逐筆成交股數、也不是含最低手續費門檻的實盤模型。

## 6. 未來數據檢查

### 檢查結論

- 沒有發現明確使用未來 bar 數據來決定當前週選股。
- 但這個回測的成交假設是「下一個週 bar 生效」，不是「次交易日開盤」。

### 依程式碼拆解

1. `build_target_weights()` 每次只切到 `close.iloc[: row_number + 1]`、`volume.iloc[: row_number + 1]`、`benchmark.iloc[: row_number + 1]`。
   - 程式位置：[signal_builder.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/signal_builder.py#L61)
   - 這代表某一週的選股，只用了該週以前的資料。
2. `select_long_candidates()` 的突破條件是 `close.shift(1).rolling(...).max()`。
   - 程式位置：[signal_builder.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/signal_builder.py#L24)
   - 這避免把當週收盤自己算進「過去高點」裡。
3. `BacktestRunner.run()` 先做 `positions.shift(1)`。
   - 程式位置：[backtest_runner.py](/home/shihyu/github/jason_note/src/strategy/finlab-bull-bear-backtest/src/backtest_runner.py#L15)
   - 所以本週決策不會吃到本週報酬。

### 限制

- 這版沒有開盤價資料，不能宣稱是「下週一開盤成交」。
- 實際上比較接近「以週資料做 next-bar 回測」。

## 7. 審查結果

### 已確認

- 成本有扣，而且買進與賣出的費率分開處理。
- 沒有直接 look-ahead bias。
- 熊市與頭部期都會轉空手。

### 尚未實作

- 個股放空。
- 反向 ETF。
- 跌破整理區低點停損。
- 次交易日開盤成交。
- 最低手續費、滑價、流動性限制。

## 執行方式

```bash
make run
```

或指定期間：

```bash
python3 src/main.py --start-date 2010-01-01 --end-date 2024-12-31 --debug
```

## 回測邏輯範例

```text
輸入：
  大盤週收盤站上 30W，短期斜率仍為正

處理：
  掃描全市場股票
  -> 排除未站上 30W 的股票
  -> 排除未突破 20W 高點的股票
  -> 排除量能不足股票
  -> 排除相對大盤不夠強的股票
  -> 依相對大盤強度排序取 Top 10
  -> 本週產生目標權重
  -> 下一週才真正持有

輸出：
  下一週生效的等權重持股組合
```
