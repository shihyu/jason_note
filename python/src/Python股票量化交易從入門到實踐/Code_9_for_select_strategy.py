#!/usr/bin/python
# coding=utf-8

"""
书籍《Python股票量化交易入门到实践 》案例例程
仅用于教学目的，严禁转发和用于盈利目的，违者必究
通过if True/False 语句 开关所要调试的例程
"""

# 第九章 构建股票量化交易策略体系——建立选股策略

import pandas as pd
import tushare as ts
import numpy as np
import json
import time
import datetime
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels import regression
import pandas_datareader.data as web
from concurrent.futures import ThreadPoolExecutor

# use other chapters program
from Code_7_for_stock_data import bs_k_data_stock, pro_daily_stock, json_to_str

# 参数设置
pd.set_option("display.expand_frame_repr", False)  # False不允许换行
pd.set_option("display.max_rows", 10)  # 显示的最大行数
pd.set_option("display.max_columns", 6)  # 显示的最大列数
pd.set_option("precision", 2)  # 显示小数点后的位数

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 用来正常显示中文标签
plt.rcParams["axes.unicode_minus"] = False  # 用来正常显示负号

################################### 走势线性回归建立选股模型 #####################################
df_stockload = bs_k_data_stock("sz.000651", "2018-06-01", "2019-06-01")
df_stockload_fst = bs_k_data_stock("sz.000651", "2018-06-01", "2019-01-01")
df_stockload_sec = bs_k_data_stock("sz.000651", "2019-01-01", "2019-06-01")


def linear_regression_temp():
    seq_num = 100
    x = np.linspace(0, 10, seq_num)
    X = sm.add_constant(x)
    beta = np.array([1, 5])
    e = np.random.normal(size=seq_num)
    Y = np.dot(X, beta) + e
    model = regression.linear_model.OLS(Y, X)
    # model = sm.OLS(Y,X)
    results = model.fit()
    print(results.params)  # [1.38760035 4.91969889]
    # print(results.summary())


def linear_regression_close(stock):

    y_arr = stock.Close.values
    x_arr = np.arange(0, len(y_arr))

    x_b_arr = sm.add_constant(x_arr)  # 添加常数列1
    model = regression.linear_model.OLS(y_arr, x_b_arr).fit()  # 使用OLS做拟合
    rad = model.params[1]  # y = kx + b :params[1] = k
    intercept = model.params[0]  # y = kx + b :params[0] = b
    reg_y_fit = x_arr * rad + intercept
    deg = np.rad2deg(rad)  # 弧度转换为角度
    print(deg)
    # matplotlib 绘制
    plt.scatter(x_arr, y_arr, s=1, c="g", marker="o", alpha=1)  # 画点
    # plt.plot(x_arr, y_arr)
    plt.plot(x_arr, reg_y_fit, "r")
    plt.title(
        u"格力电器" + " y = " + str(round(rad, 2)) + " * x + " + str(round(intercept, 2))
    )
    plt.legend(["close", "linear"], loc="best")
    plt.show()


def close_to_deg(code, start="2018-01-01", end="2019-01-01"):
    deg_data = []
    try:
        df_data = bs_k_data_stock(code, start, end)
        y_arr = df_data.Close.values
        x_arr = np.arange(0, len(y_arr))
        x_b_arr = sm.add_constant(x_arr)  # 添加常数列1
        model = regression.linear_model.OLS(y_arr, x_b_arr).fit()  # 使用OLS做拟合
        rad = model.params[1]  # y = kx + b :params[1] = k
        deg_data = np.rad2deg(rad)  # 弧度转换为角度
    except:
        print("error code is %s" % code)
    return deg_data


def get_daily_deg():
    stock_index = json_to_str()
    itr_arg = [code for code in stock_index["股票"].values()]
    # print(itr_arg)
    with ThreadPoolExecutor(max_workers=8) as executor:
        deg_result = dict(zip(itr_arg, executor.map(close_to_deg, itr_arg)))
        for code, deg in deg_result.items():
            print("code({}) deg is: {}".format(code, deg))
            """
            code(000078.SZ) deg is: -0.8507411387896914
            code(000088.SZ) deg is: -0.8573982904083389
            code(000089.SZ) deg is: -0.21092336527744301
            code(000090.SZ) deg is: -1.6363976354642142
            code(000096.SZ) deg is: -1.2395661356191432
            ......
            """
        sorted_data = sorted(deg_result.items(), key=lambda x: x[1], reverse=True)
        print(sorted_data)
        # ('000860.SZ', 5.408956055007121), ('000010.SZ', -0.13332703483617436).....


def get_daily_deg_for(start="2018-01-01", end="2019-01-01"):
    with open("stock_20_pool.json", "r") as load_f:
        stock_index = json.load(load_f)  # 读取股票池Json文件
    deg_data = {}
    for code in stock_index["股票"].values():
        try:
            df_data = pro_daily_stock(code, start, end)
            y_arr = df_data.Close.values
            x_arr = np.arange(0, len(y_arr))
            x_b_arr = sm.add_constant(x_arr)  # 添加常数列1
            model = regression.linear_model.OLS(y_arr, x_b_arr).fit()  # 使用OLS做拟合
            rad = model.params[1]  # y = kx + b :params[1] = k
            deg_data[code] = np.rad2deg(rad)  # 弧度转换为角度
            print("code({}) deg is: {}".format(code, deg_data[code]))
        except:
            print("error code is %s" % code)
        """
        code(000001.SZ) deg is: -0.7817675279466058
        code(000002.SZ) deg is: -3.289481035965825
        code(000004.SZ) deg is: -1.8039825425329399
        code(000005.SZ) deg is: -0.35793989587357994
        code(000006.SZ) deg is: -0.8170351064359175
        code(000007.SZ) deg is: -2.463852093183183
        code(000008.SZ) deg is: -1.6635671526120404
        code(000009.SZ) deg is: -0.6245565900455877
        code(000010.SZ) deg is: -0.13332703483617436
        code(000011.SZ) deg is: -2.0670175459648163
        code(000012.SZ) deg is: -1.284680281224533
        code(000014.SZ) deg is: -0.7018486455802234
        code(000016.SZ) deg is: -0.9143360317950662
        code(000017.SZ) deg is: -0.42342752255013144
        code(000018.SZ) deg is: -1.285172202328646
        code(000019.SZ) deg is: -1.2514496436146723
        code(000020.SZ) deg is: -0.9492849996535324
        code(300710.SZ) deg is: -4.703853345031707
        code(300711.SZ) deg is: -2.7791310372928755
        code(300712.SZ) deg is: -2.688855307947049
        """
    sorted_data = sorted(deg_data.items(), key=lambda x: x[1], reverse=True)
    print(sorted_data)
    # [('000010.SZ', -0.13332703483617436), ('000005.SZ', -0.35793989587357994), ('000017.SZ', -0.42342752255013144), ('000009.SZ', -0.6245565900455877), ('000014.SZ', -0.7018486455802234), ('000001.SZ', -0.7817675279466058), ('000006.SZ', -0.8170351064359175), ('000016.SZ', -0.9143360317950662), ('000020.SZ', -0.9492849996535324), ('000019.SZ', -1.2514496436146723), ('000012.SZ', -1.284680281224533), ('000018.SZ', -1.285172202328646), ('000008.SZ', -1.6635671526120404), ('000004.SZ', -1.8039825425329399), ('000011.SZ', -2.0670175459648163), ('000007.SZ', -2.463852093183183), ('300712.SZ', -2.688855307947049), ('300711.SZ', -2.7791310372928755), ('000002.SZ', -3.289481035965825), ('300710.SZ', -4.703853345031707)]


def linear_regmove_close(stock, cycle=30):
    # 将移动窗口绘制股票收盘价线性回归拟合角度曲线

    y_arr = stock.Close.values
    x_arr = np.arange(0, len(y_arr))
    x_b_arr = sm.add_constant(x_arr)  # 添加常数列1
    model = regression.linear_model.OLS(y_arr, x_b_arr).fit()  # 使用OLS做拟合
    rad = model.params[1]  # y = kx + b :params[1] = k
    intercept = model.params[0]  # y = kx + b :params[0] = b
    reg_y_fit = x_arr * rad + intercept

    fig, ax1 = plt.subplots(1, 1, figsize=(14, 7), dpi=80)
    ax1.plot(x_arr, reg_y_fit, color="tab:red")
    ax1.scatter(x_arr, y_arr, s=1, c="g", marker="o", alpha=1)

    for kl_index in np.arange(0, stock.shape[0]):
        if kl_index >= cycle:
            y_arr = stock.Close[kl_index - cycle : kl_index].values
            x_arr = np.arange(0, len(y_arr))
            x_b_arr = sm.add_constant(x_arr)  # 添加常数列1
            model = regression.linear_model.OLS(y_arr, x_b_arr).fit()  # 使用OLS做拟合
            rad = model.params[1]  # y = kx + b :params[1] = k
            stock.loc[stock.index[kl_index], "ang"] = np.rad2deg(rad)  # 弧度转换为角度

    ax2 = ax1.twinx()  # 辅助Y轴绘制不同比例的图形
    ax2.plot(np.arange(0, len(stock.index)), stock.ang)
    ax2.set_title(u"格力电器" + " Move Angle")
    ax2.legend(["Angle"], loc="best")
    plt.show()


if True:
    # linear_regression_temp()
    # linear_regression_close(df_stockload.copy(deep=True))
    # get_daily_deg()
    # get_daily_deg_for()
    # linear_regression_close(df_stockload_fst.copy(deep=True))
    # linear_regression_close(df_stockload_sec.copy(deep=True))
    linear_regmove_close(df_stockload.copy(deep=True))

"""
# 获取当前交易的股票代码和名称
def get_code():
    df = pro.stock_basic(exchange='', list_status='L')
    codes=df.ts_code.values
    names=df.name.values
    stock=dict(zip(names,codes))
    stocks=dict(stock,**index) # 合并指数和个股成一个字典
    return stocks

def get_daily_data(stock, start,end):    
    # 如果代码在字典index里，则取的是指数数据
    code=get_code()[stock]
    if code in index.values():
        df=pro.index_daily(ts_code=code,start_date=start, end_date=end)
    # 否则取的是个股数据
    else:
        df=pro.daily(ts_code=code, adj='qfq',start_date=start, end_date=end)
    # 将交易日期设置为索引值
    df.index=pd.to_datetime(df.trade_date)
    df=df.sort_index()
    df['ret']=df.close/df.close.shift(1)-1 # 计算收益率
    return df
"""
