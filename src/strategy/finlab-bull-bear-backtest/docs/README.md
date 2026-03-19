# FinLab 牛熊多空回測

這個專案把「`30` 週均線區分牛熊、牛市只做強勢股、熊市全空手」整理成可執行的台股回測程式。

## 快速開始

```bash
cd finlab-bull-bear-backtest
make build
make test
make run
```

## 回測規格

- 市場狀態：`bull` / `top` / `bear` / `base`
- 牛市條件：大盤在 `30` 週均線上方，長短期斜率都維持正向
- 做多標的：全市場相對大盤強勢 `Top 10`
- 進場條件：站上 `30` 週均線、量增、突破近 `20` 週高點
- 熊市處理：`cash`
- 台股成本：
  - 買進手續費：`0.1425% x 0.3`
  - 賣出手續費：`0.1425% x 0.3`
  - 證交稅：`0.3%`

## 使用範例

```bash
python3 src/main.py --start-date 2020-01-01 --debug
```
