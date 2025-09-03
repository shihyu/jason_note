# 載入套件
import yfinance as yf
import mplfinance as mpf
import numpy as np

# 透過Yfinance取得K棒歷史資料
def GetKBar(SDate, EDate, Prod, Kind, Cycle):
    # 轉換日期格式
    SDate = SDate[:4] + "-" + SDate[4:6] + "-" + SDate[6:]
    EDate = EDate[:4] + "-" + EDate[4:6] + "-" + EDate[6:]
    # 指數前面要加 ^ 符號
    if Kind == "Index":
        Prod = "^" + Prod
    # 從 yahoo finance 下載資料
    Data = yf.download(Prod, start=SDate, end=EDate, interval=Cycle)
    # 將欄位名稱改為英文小寫
    Data.columns = [i.lower() for i in Data.columns]
    # 因python會有小數點精確度問題，故將股價取到小數後兩位
    Data.open = [round(i, 2) for i in Data.open]
    Data.high = [round(i, 2) for i in Data.high]
    Data.low = [round(i, 2) for i in Data.low]
    Data.close = [round(i, 2) for i in Data.close]
    return Data


# 圖片物件
class DrawKBar:
    # 初始設定
    def __init__(self, KBar):
        self.KBar = KBar
        self.TableList = []

    # 新增附圖
    def Add(
        self,
        data,
        panel=0,
        type="line",
        marker=".",
        color="black",
        scatter=False,
        ylabel="",
    ):
        # Table = mpf.make_addplot(data,panel=panel,type=type,color=color)
        Table = mpf.make_addplot(
            data,
            panel=panel,
            type=type,
            marker=marker,
            color=color,
            scatter=scatter,
            ylabel=ylabel,
            secondary_y=False,
        )
        self.TableList.append(Table)

    # 顯示圖片
    def Show(self):
        KBar_color = mpf.make_marketcolors(
            up="red", down="green", edge="inherit", wick="inherit", volume="inherit"
        )
        KBar_style = mpf.make_mpf_style(
            base_mpf_style="yahoo", edgecolor="black", marketcolors=KBar_color
        )
        mpf.plot(
            self.KBar,
            type="candle",
            style=KBar_style,
            volume=True,
            addplot=self.TableList,
        )


# 計算績效KPI
def GetKPI(ProfitList):
    # 將 List 轉為 numpy array 格式
    ProfitList = np.array(ProfitList)
    print()

    # 交易次數
    TotalNum = len(ProfitList)
    print("交易次數:", TotalNum, "次")

    # 總損益
    TotalProfit = round(sum(ProfitList), 2)
    print("總損益:", TotalProfit, "元")

    # 平均損益
    if TotalNum == 0:
        AvgProfit = None
    else:
        AvgProfit = round(TotalProfit / TotalNum, 2)
    print("平均損益:", AvgProfit, "元")

    # 總勝率
    Win = [i for i in ProfitList if i > 0]  # 獲利的部分
    Loss = [i for i in ProfitList if i < 0]  # 虧損的部分
    if TotalNum == 0:
        WinRate = None
    else:
        WinRate = round(len(Win) / TotalNum * 100, 2)
    print("總勝率:", WinRate, "%")

    # 平均獲利
    if len(Win) == 0:
        AvgWin = None
    else:
        AvgWin = round(np.mean(Win), 2)
    print("平均獲利:", AvgWin, "元")

    # 平均虧損
    if len(Loss) == 0:
        AvgLoss = None
    else:
        AvgLoss = round(np.mean(Loss), 2)
    print("平均虧損:", AvgLoss, "元")

    # 獲利因子
    if sum(Loss) == 0:
        ProfitFactor = None
    else:
        ProfitFactor = round(sum(Win) / abs(sum(Loss)), 2)
    print("獲利因子:", ProfitFactor, "倍")

    # 最大資金回落
    MaxCapital = 0
    Capital = 0
    MDD = 0
    DD = 0
    for i in ProfitList:
        Capital += i
        MaxCapital = max(MaxCapital, Capital)
        DD = round(MaxCapital - Capital, 2)
        MDD = max(MDD, DD)
    print("最大資金回落:", abs(MDD), "元")
