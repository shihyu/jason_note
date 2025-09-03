#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
书籍《Python股票量化交易入门到实践 》案例例程
仅用于教学目的，严禁转发和用于盈利目的，违者必究
通过if True/False 语句 开关所要调试的例程
"""

# 第九章 构建股票量化交易策略体系——建立择时策略
#

import pandas_datareader.data as web
import pandas as pd
import numpy as np
import datetime
import talib
import random
import matplotlib.pyplot as plt
import mpl_finance as mpf  # 替换 import matplotlib.finance as mpf
import matplotlib.gridspec as gridspec  # 分割子图

from Code_7_for_stock_data import bs_k_data_stock, pro_daily_stock, json_to_str
from Code_8_for_tech_indicator import MplVisualIf
from Code_9_for_risk_Profit import (
    draw_trade_chart,
    draw_absolute_profit,
    draw_relative_profit,
    draw_closemax_risk,
    draw_profitmax_risk,
    MultiTraceIf,
)

# 参数设置
pd.set_option("display.expand_frame_repr", False)  # False不允许换行
pd.set_option("display.max_rows", 10)  # 显示的最大行数
pd.set_option("display.max_columns", 6)  # 显示的最大列数
pd.set_option("precision", 1)  # 显示小数点后的位数

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 用来正常显示中文标签
plt.rcParams["axes.unicode_minus"] = False  # 用来正常显示负号

df_stockload = pro_daily_stock("000651.SZ", "20180601", "20190601")
print(df_stockload.describe())
"""
        High    Low   Open  Close   Volume
count  238.0  238.0  238.0  238.0  2.4e+02
mean    44.0   42.8   43.4   43.4  5.4e+05
std      6.7    6.2    6.4    6.5  3.0e+05
min     36.0   35.4   35.7   35.7  1.1e+05
25%     38.9   37.8   38.4   38.4  3.6e+05
50%     41.3   40.4   40.9   40.8  4.8e+05
75%     47.3   46.0   47.0   46.6  6.2e+05
max     65.4   60.9   63.7   65.0  3.2e+06
"""
app = MplVisualIf()
#####################################制定唐奇安通道突破择时策略#####################################
def get_ndays_signal(stock_dat, N1=15, N2=5):
    # 海龟策略-唐奇安通道突破(N日突破) 买入/卖出信号
    stock_dat["N1_High"] = stock_dat.High.rolling(window=N1).max()  # 计算最近N1个交易日最高价
    expan_max = stock_dat.High.expanding().max()  # 滚动计算当前交易日为止的最大值
    stock_dat["N1_High"].fillna(value=expan_max, inplace=True)  # 填充前N1个nan
    # print(stock_dat.head())
    """
                High   Low  Open  Close   Volume  N1_High
    Date                                                 
    2018-06-01  47.3  46.3  47.3   46.6  5.0e+05     47.3
    2018-06-04  48.3  47.0  47.0   47.8  1.0e+06     48.3
    2018-06-05  48.8  47.9  48.0   48.5  1.0e+06     48.8
    2018-06-06  48.8  48.1  48.5   48.4  5.5e+05     48.8
    2018-06-07  48.9  47.9  48.8   48.0  5.6e+05     48.9
    """

    stock_dat["N2_Low"] = stock_dat.Low.rolling(window=N2).min()  # 计算最近N2个交易日最低价
    expan_min = stock_dat.Low.expanding().min()
    stock_dat["N2_Low"].fillna(value=expan_min, inplace=True)  # 目前出现过的最小值填充前N2个nan
    # print(stock_dat.head())
    """
                High   Low  Open   ...     Volume  N1_High  N2_Low
    Date                           ...                            
    2018-06-01  47.3  46.3  47.3   ...    5.0e+05     47.3    46.3
    2018-06-04  48.3  47.0  47.0   ...    1.0e+06     48.3    46.3
    2018-06-05  48.8  47.9  48.0   ...    1.0e+06     48.8    46.3
    2018-06-06  48.8  48.1  48.5   ...    5.5e+05     48.8    46.3
    2018-06-07  48.9  47.9  48.8   ...    5.6e+05     48.9    46.3
    
    [5 rows x 7 columns]
    """
    # 收盘价超过N1最高价 买入股票
    buy_index = stock_dat[stock_dat.Close > stock_dat.N1_High.shift(1)].index
    # 收盘价超过N2最低价 卖出股票
    sell_index = stock_dat[stock_dat.Close < stock_dat.N2_Low.shift(1)].index

    # print(f'Buy-Time: \n {buy_index}')
    # print(f'Sell-Time: \n {sell_index}')

    stock_dat.loc[buy_index, "Signal"] = 1
    stock_dat.loc[sell_index, "Signal"] = -1

    stock_dat["Signal"] = stock_dat.Signal.shift(1)
    # print(stock_dat[stock_dat['signal'].notna()])
    stock_dat["Signal"].fillna(method="ffill", inplace=True)  # 与前面元素值保持一致
    stock_dat["Signal"].fillna(value=-1, inplace=True)  # 序列最前面几个NaN值用-1填充
    return stock_dat


def draw_ndays_annotate(stock_dat):

    # 绘制唐奇安通道突破/N日突破
    signal_shift = stock_dat.Signal.shift(1)
    signal_shift.fillna(value=-1, inplace=True)  # 序列最前面的NaN值用-1填充
    list_signal = np.sign(stock_dat.Signal - signal_shift)  # 计算买卖点

    down_cross = stock_dat[list_signal < 0]
    up_cross = stock_dat[list_signal > 0]

    # print(f'Buy-Time: \n {up_cross}')
    # print(f'Sell-Time: \n {down_cross}')

    layout_dict = {
        "figsize": (14, 7),
        "index": stock_dat.index,
        "draw_kind": {
            "ochl": {
                "Open": stock_dat.Open,
                "Close": stock_dat.Close,
                "High": stock_dat.High,
                "Low": stock_dat.Low,
            },
            "line": {"N1_High": stock_dat.N1_High, "N2_Low": stock_dat.N2_Low},
            "annotate": {
                "down": {
                    "andata": down_cross,
                    "va": "top",
                    "xy_y": "N2_Low",
                    "xytext": (-10, -stock_dat["Close"].mean()),
                    "fontsize": 8,
                    "arrow": dict(facecolor="green", shrink=0.1),
                },
                "up": {
                    "andata": up_cross,
                    "va": "bottom",
                    "xy_y": "N1_High",
                    "xytext": (-10, stock_dat["Close"].mean()),
                    "fontsize": 8,
                    "arrow": dict(facecolor="red", shrink=0.1),
                },
            },
        },
        "title": "000651 格力电器-唐奇安通道突破",
        "ylabel": "价格",
        "xlabel": "日期",
        "xticks": 15,
        "legend": "best",
        "xticklabel": "%Y-%m-%d",
    }  # strftime
    app.fig_output(**layout_dict)


#####################################融入ATR跟踪止盈止损策略#####################################
def draw_atr_chart(stock_dat):

    stock_dat["atr14"] = talib.ATR(
        stock_dat.High.values,
        stock_dat.Low.values,
        stock_dat.Close.values,
        timeperiod=14,
    )  # 计算ATR14
    stock_dat["atr21"] = talib.ATR(
        stock_dat.High.values,
        stock_dat.Low.values,
        stock_dat.Close.values,
        timeperiod=21,
    )  # 计算ATR21
    layout_dict = {
        "figsize": (14, 5),
        "index": stock_dat.index,
        "draw_kind": {"line": {"atr14": stock_dat.atr14, "atr21": stock_dat.atr21},},
        "title": "000651 格力电器-ATR",
        "ylabel": "波动幅度",
        "xlabel": "日期",
        "xticks": 15,
        "legend": "best",
        "xticklabel": "%Y-%m-%d",
    }  # strftime
    app.fig_output(**layout_dict)


def get_ndays_atr_signal(stock_dat, N1=15, N2=5, n_win=3.4, n_loss=1.8):
    # 海龟策略-唐奇安通道突破(N日突破) 买入/卖出信号
    stock_dat["N1_High"] = stock_dat.High.rolling(window=N1).max()  # 计算最近N1个交易日最高价
    expan_max = stock_dat.High.expanding().max()  # 滚动计算当前交易日为止的最大值
    stock_dat["N1_High"].fillna(value=expan_max, inplace=True)  # 填充前N1个nan
    stock_dat["N2_Low"] = stock_dat.Low.rolling(window=N2).min()  # 计算最近N2个交易日最低价
    expan_min = stock_dat.Low.expanding().min()
    stock_dat["N2_Low"].fillna(value=expan_min, inplace=True)  # 目前出现过的最小值填充前N2个nan

    stock_dat["ATR21"] = talib.ATR(
        stock_dat.High.values,
        stock_dat.Low.values,
        stock_dat.Close.values,
        timeperiod=21,
    )  # 计算ATR21
    # 收盘价超过N1最高价 买入股票
    buy_index = stock_dat[stock_dat.Close > stock_dat.N1_High.shift(1)].index
    # 收盘价超过N2最低价 卖出股票
    sell_index = stock_dat[stock_dat.Close < stock_dat.N2_Low.shift(1)].index
    # print(f'Buy-Time: \n {buy_index}')
    # print(f'Sell-Time: \n {sell_index}')

    stock_dat.loc[buy_index, "Signal"] = 1
    stock_dat.loc[sell_index, "Signal"] = -1
    stock_dat["Signal"] = stock_dat.Signal.shift(1)

    # print(stock_dat[stock_dat['signal'].notna()])
    buy_price = 0

    for kl_index, today in stock_dat.iterrows():
        # if today.Close > today.N1_High:
        if (buy_price == 0) and (today.Signal == 1):
            buy_price = today.Close
            # stockdata.loc[kl_index, 'signal'] = 1
        # 到达收盘价少于买入价后触发卖出
        elif (
            (buy_price != 0)
            and (buy_price > today.Close)
            and ((buy_price - today.Close) > n_loss * today.ATR21)
        ):
            print(f'止损时间:{kl_index.strftime("%y.%m.%d")} 止损价格:{round(today.Close, 2)}')
            stock_dat.loc[kl_index, "Signal"] = -1
            buy_price = 0
        # 到达收盘价多于买入价后触发卖出
        elif (
            (buy_price != 0)
            and (buy_price < today.Close)
            and ((today.Close - buy_price) > n_win * today.ATR21)
        ):
            print(f'止盈时间:{kl_index.strftime("%y.%m.%d")} 止盈价格:{round(today.Close, 2)}')
            stock_dat.loc[kl_index, "Signal"] = -1
            buy_price = 0
        elif (buy_price != 0) and (today.Signal == -1):
            stock_dat.loc[kl_index, "Signal"] = -1
            buy_price = 0
        else:
            pass

    stock_dat["Signal"].fillna(method="ffill", inplace=True)  # 与前面元素值保持一致
    stock_dat["Signal"].fillna(value=-1, inplace=True)  # 序列最前面几个NaN值用0填充

    return stock_dat


#####################################蒙特卡洛法最优化策略参数#####################################
# 枚举法最优化策略参数

# 度量策略资金收益 —— 改造
def draw_absolute_profit_opt(stock_dat):

    cash_hold = 100000  # 初始资金
    posit_num = 0  # 持股数目
    skip_days = False  # 持股/持币状态
    slippage = 0.01  # 滑点，默认为0.01
    c_rate = 5.0 / 10000  # 手续费，commission，默认万分之5
    t_rate = 1.0 / 1000  # 印花税，tax，默认千分之1

    # 绝对收益—资金的度量
    for kl_index, today in stock_dat.iterrows():
        # 买入/卖出执行代码
        if today.Signal == 1 and skip_days == False:  # 买入
            skip_days = True
            posit_num = int(cash_hold / (today.Close + slippage))  # 资金转化为股票
            posit_num = int(posit_num / 100) * 100  # 买入股票最少100股，对posit_num向下取整百
            buy_cash = posit_num * (today.Close + slippage)  # 计算买入股票所需现金
            # 计算手续费，不足5元按5元收，并保留2位小数
            commission = round(max(buy_cash * c_rate, 5), 2)
            cash_hold = cash_hold - buy_cash - commission

        elif today.Signal == -1 and skip_days == True:  # 卖出 避免未买先卖
            skip_days = False
            sell_cash = posit_num * (today.Close - slippage)  # 计算卖出股票得到的现金 卖出股票可以不是整百。
            # 计算手续费，不足5元按5元收，并保留2位小数
            commission = round(max(sell_cash * c_rate, 5), 2)
            # 计算印花税，保留2位小数
            tax = round(sell_cash * t_rate, 2)
            cash_hold = cash_hold + sell_cash - commission - tax  # 剩余现金

        if skip_days == True:  # 持股
            stock_dat.loc[kl_index, "total"] = posit_num * today.Close + cash_hold
        else:  # 空仓
            stock_dat.loc[kl_index, "total"] = cash_hold

    return stock_dat["total"][-1]


def enum_optimize_para(stock_dat):
    n_para_list = []
    profit_list = []
    for n1 in range(20, 60):
        n_para_list.append(n1)
        profit_list.append(draw_absolute_profit_opt(get_ndays_signal(stock_dat, N1=n1)))
    print(n_para_list, profit_list)
    profit_max = max(profit_list)
    print(profit_list.index(max(profit_list)))
    n1_max = n_para_list[profit_list.index(max(profit_list))]

    plt.bar(n_para_list, profit_list)
    plt.annotate(
        "n1=" + str(n1_max) + "\n" + str(profit_max),
        xy=(n1_max, profit_max),
        xytext=(n1_max - 5, profit_max - 10),
        arrowprops=dict(facecolor="yellow", shrink=0.1),
        horizontalalignment="left",
        verticalalignment="top",
    )

    # 设置坐标标签字体大小
    plt.xlabel("N1参数")
    plt.ylabel("资金收益")
    # 设置坐标轴的取值范围
    plt.xlim(min(n_para_list) - 1, max(n_para_list) + 1)
    plt.ylim(min(profit_list) * 0.99, max(profit_list) * 1.01)
    # 设置x坐标轴刻度
    plt.xticks(np.arange(min(n_para_list), max(n_para_list) + 1, 1))
    # 设置图例字体大小
    plt.legend(["profit_list"], loc="best")
    plt.title("N1最优参数")
    plt.show()


# 蒙特卡洛 小实验计算定积分
def draw_fx_square():
    plt.figure()
    x_array = np.linspace(0, 3, 50)  # 等差数
    plt.plot(x_array, np.square(x_array), lw=2, label="$y=x^2$")

    plt.plot([1, 1], [0, np.square(2)], color="r")
    plt.plot([2, 2], [0, np.square(2)], color="r")
    plt.plot([1, 2], [np.square(2), np.square(2)], color="r")
    plt.plot([1, 2], [0, 0], color="r")

    plt.xlabel("x axis")
    plt.ylabel("y axis")
    plt.legend(loc="best")
    plt.show()


def cal_integral_mc(n=100000):

    x_min, x_max = 1.0, 2.0
    y_min, y_max = 0.0, 4.0
    Area = 4
    m = 0

    for i in range(0, n + 1):
        x = random.uniform(x_min, x_max)
        y = random.uniform(y_min, y_max)
        # x*x > y 表示该点位于曲线的下面。
        if x * x > y:
            m += 1
    # 所求的积分值即为曲线下方的面积
    return Area * m / float(n)


def draw_integral_mc(n=1000):

    x_min, x_max = 1.0, 2.0
    y_min, y_max = 0.0, 4.0
    Area = 4
    m = 0

    plt.figure()
    x_array = np.linspace(0, 3, 50)  # 等差数
    plt.plot(x_array, np.square(x_array), lw=2, label="$y=x^2$")

    plt.plot([1, 1], [0, np.square(2)], color="r")
    plt.plot([2, 2], [0, np.square(2)], color="r")
    plt.plot([1, 2], [np.square(2), np.square(2)], color="r")
    plt.plot([1, 2], [0, 0], color="r")

    for i in range(0, n + 1):
        x = random.uniform(x_min, x_max)
        y = random.uniform(y_min, y_max)
        # x*x > y 表示该点位于曲线的下面。
        if x * x > y:
            m += 1
            # s：标记大小 c：标记颜色
            plt.scatter(x, y, s=0.1, c="r", marker="o", alpha=1)  # 画点 点数太多时程序卡死
        else:
            plt.scatter(x, y, s=0.1, c="g", marker="o", alpha=1)  # 画点 点数太多时程序卡死
    # 所求的积分值即为曲线下方的面积
    print(Area * m / float(n))
    plt.show()


# 蒙特卡洛参数最优化 框架
def cal_ndayavg_mc_frame(stock_dat, n=500):

    n1_min, n1_max = 10, 30
    n2_min, n2_max = 5, 15
    win_min, win_max = 1.5, 2.5
    loss_min, loss_max = 0.5, 1.5

    opt_para_list = []
    profit_list = []

    for i in range(0, n + 1):
        n1 = int(random.uniform(n1_min, n1_max))
        n2 = int(random.uniform(n2_min, n2_max))
        win = round(random.uniform(win_min, win_max), 1)
        loss = round(random.uniform(loss_min, loss_max), 1)
        opt_para_list.append([n1, n2, win, loss])
        # 此处添加策略代码

    return opt_para_list


def cal_ndayavg_mc(stock_dat, n=500):

    n1_min, n1_max = 10, 30
    n2_min, n2_max = 5, 15
    win_min, win_max = 1.5, 2.5
    loss_min, loss_max = 0.5, 1.5

    opt_para_list = []
    profit_list = []

    for i in range(0, n + 1):
        n1 = int(random.uniform(n1_min, n1_max))
        n2 = int(random.uniform(n2_min, n2_max))
        win = round(random.uniform(win_min, win_max), 1)
        loss = round(random.uniform(loss_min, loss_max), 1)
        opt_para_list.append([n1, n2, win, loss])
        # 此处添加策略代码
        profit_list.append(
            draw_absolute_profit_opt(get_ndays_atr_signal(stock_dat, n1, n2, win, loss))
        )

    profit_max = max(profit_list)  # maximize the profit
    opt_para_max = opt_para_list[
        profit_list.index(max(profit_list))
    ]  # correspond parametes
    print(
        "maximize the profit is %s and correspond parametes are %s "
        % (profit_max, opt_para_max)
    )

    plt.bar(np.arange(0, len(opt_para_list), 1), profit_list)
    plt.annotate(
        str(opt_para_max) + "\n" + str(profit_max),
        xy=(opt_para_list.index(opt_para_max), profit_max),
        xytext=(opt_para_list.index(opt_para_max) - 10, profit_max - 10),
        arrowprops=dict(facecolor="yellow", shrink=0.1),
        horizontalalignment="left",
        verticalalignment="top",
    )

    # 设置坐标标签字体大小
    plt.xlabel("N1 N2 win loss 参数")
    plt.ylabel("资金收益")
    # 设置坐标轴的取值范围
    plt.ylim(min(profit_list) * 0.99, max(profit_list) * 1.01)
    # 设置图例字体大小
    plt.legend(["profit_list"], loc="best")
    plt.title("蒙特卡洛最优参数")
    plt.show()


#####################################基于凯利公式量化仓位管理####################################
# 模拟是否仓位在f时资金增长的速度最快
def positmanage_test(play_cnt=1000, win_rate=0.6, position=1):
    my_money = np.zeros(play_cnt)
    my_money[0] = 1000
    for i in range(1, play_cnt):
        binomial = np.random.binomial(1, win_rate, 1)
        once_chip = my_money[i - 1] * position  # 下注资金
        if binomial == True:
            my_money[i] = my_money[i - 1] + once_chip
        else:
            my_money[i] = my_money[i - 1] - once_chip
        if my_money[i] <= 0:
            break
    return my_money[-1]


def verify_kelly_profit():

    post_list = []
    profit_list = []

    for v_post in np.arange(0, 1.5, 0.1):  # [0-1]每间隔0.1产生一个下注仓位

        post_list.append(v_post)
        profit_list.append(
            positmanage_test(play_cnt=1000, win_rate=0.6, position=v_post)
        )

    profit_max = max(profit_list)  # maximize the profit
    post_max = post_list[profit_list.index(max(profit_list))]  # correspond position
    print(
        "maximize the profit is %s and correspond position are %s "
        % (profit_max, post_max)
    )

    plt.bar(np.arange(0, len(post_list)), profit_list)
    plt.annotate(
        str(post_max) + "\n" + str(profit_max),
        xy=(post_list.index(post_max), profit_max),
        xytext=(post_list.index(post_max) - 2, profit_max),
        arrowprops=dict(facecolor="yellow", shrink=0.1),
        horizontalalignment="left",
        verticalalignment="top",
    )

    plt.xlabel("仓位比例")
    plt.ylabel("资金收益")
    plt.xticks(
        np.arange(0, len(post_list)), ["%.1f" % (i) for i in np.arange(0, 1.5, 0.1)]
    )  # 设置坐标轴的刻度范围
    plt.ylim(min(profit_list) * 0.99, max(profit_list) * 1.01)  # 设置坐标轴的取值范围
    plt.title("验证凯利公式仓位比例与资金最大化")
    plt.show()


if __name__ == "__main__":

    layout_dict = {
        "figsize": (16, 8),
        "nrows": 3,
        "ncols": 1,
        "left": 0.07,
        "bottom": 0.12,
        "right": 0.95,
        "top": 0.94,
        "wspace": None,
        "hspace": 0,
        "height_ratios": [1.5, 1, 1],
        "subplots": ["kgraph", "cashgraph", "cmppfgraph"],
    }

    subplots_dict = {
        "graph_fst": {
            "graph_name": "kgraph",
            "graph_type": {"trade": None, "close_retrace": None},
            "title": "000651 格力电器-回测分析",
            "ylabel": "价格",
            "xticks": 15,
            "legend": "best",
        },
        "graph_sec": {
            "graph_name": "cashgraph",
            "graph_type": {"cash_profit": 100000},  # 初始资金
            "ylabel": "资金收益和回撤",
            "xticks": 15,
            "legend": "best",
        },
        "graph_fth": {
            "graph_name": "cmppfgraph",
            "graph_type": {"cmp_profit": None},
            "ylabel": "策略收益VS基准收益",
            "xlabel": "日期",
            "xticks": 15,
            "legend": "best",
            "xticklabels": "%Y-%m-%d",
        },
    }
    if False:
        # print(get_ndays_signal(df_stockload.copy(deep=True)))  # 海龟策略-唐奇安通道突破(N日突破) 买入/卖出信号
        draw_ndays_annotate(
            get_ndays_signal(df_stockload.copy(deep=True))
        )  # 海龟策略-唐奇安通道突破(N日突破) 买入/卖出信号

        draw_stock = MultiTraceIf(**layout_dict)
        draw_stock.graph_run(
            get_ndays_signal(df_stockload.copy(deep=True)), **subplots_dict
        )

    if False:
        # draw_atr_chart(df_stockload.copy(deep=True))
        # get_ndays_atr_signal(df_stockload.copy(deep=True))
        # draw_trade_chart(get_ndays_atr_signal(df_stockload.copy(deep=True))) # 交易获利/亏损区间可视化
        draw_stock = MultiTraceIf(**layout_dict)
        draw_stock.graph_run(
            get_ndays_atr_signal(df_stockload.copy(deep=True)), **subplots_dict
        )

    if True:
        enum_optimize_para(df_stockload.copy(deep=True))
        # draw_fx_square()
        # print(cal_integral_mc())
        # draw_integral_mc()
        # print(cal_ndayavg_mc_frame()) # [[10, 9, 2.3, 1.1] ...... [14, 7, 2.1, 1.2], [29, 6, 2.3, 1.3]]
        cal_ndayavg_mc(df_stockload.copy(deep=True), 200)

    if False:
        # verify_kelly_profit()
        draw_trade_chart(
            get_ndays_atr_signal(
                df_stockload.copy(deep=True), N1=10, N2=9, n_loss=2.5, n_win=1.2
            )
        )  # 交易获利/亏损区间可视化
        # loss count:5 and win count:7, Pwin:0.58
        # loss profit:0.04 and win profit:0.08
