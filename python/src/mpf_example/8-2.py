# python 8-2.py "20210101" "20220501"  "AAPL" ""  "1D"
# 載入套件
from plotly.offline import plot
import talib as ta
import plotly.graph_objs as go
import sys, Function

# 資料參數 (可自行調整)
SDate = sys.argv[1]  # 資料起始日
EDate = sys.argv[2]  # 資料結束日
Prod = sys.argv[3]  # 商品代碼
Kind = sys.argv[4]  # 商品種類
Cycle = sys.argv[5]  # K棒週期

# 取得K棒資料
KBar = Function.GetKBar(SDate, EDate, Prod, Kind, Cycle)
print(KBar)

# 計算技術指標
flag = False
KBar["CDL3BLACKCROWS"] = ta.CDL3BLACKCROWS(
    KBar["open"], KBar["high"], KBar["low"], KBar["close"]
)
print(KBar)
print(KBar["CDL3BLACKCROWS"].tolist(), len(KBar["CDL3BLACKCROWS"]))
for i in range(0, len(KBar["CDL3BLACKCROWS"])):
    signal = KBar.iloc[0]["CDL3BLACKCROWS"]
    if float(signal) < 0:
        print(KBar.index[i], signal)
        flag = True

if flag == False:
    print("期間內無觸發此型態訊號")

trace = go.Candlestick(  # x= pd.to_datetime(dfohlc.index.values),
    open=KBar["open"], high=KBar["high"], low=KBar["low"], close=KBar["close"]
)
data = [trace]

plot(data, filename="go_candle1.html")
