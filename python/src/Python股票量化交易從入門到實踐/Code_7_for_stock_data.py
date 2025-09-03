#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
书籍《Python股票量化交易入门到实践 》案例例程
仅用于教学目的，严禁转发和用于盈利目的，违者必究
通过if True/False 语句 开关所要调试的例程
"""
# 注意！！！ 使用tushare pro时设置自己官网注册得到的token

# 第七章 股票行情数据的获取和处理——获取部分

import datetime
import numpy as np
import pandas_datareader.data as web
import pandas as pd
import matplotlib.pyplot as plt
import tushare as ts
import baostock as bs

# 参数设置
pd.set_option("display.expand_frame_repr", False)  # False不允许换行
pd.set_option("display.max_rows", 10)  # 显示的最大行数
pd.set_option("display.max_columns", 6)  # 显示的最大列数
pd.set_option("precision", 2)  # 显示小数点后的位数


def pd_data_000001SS():
    # 获取上证综指行情数据 pandas-datareade模块data.DataReader()方法
    df_stockload = web.DataReader(
        "000001.SS",
        "yahoo",
        datetime.datetime(2009, 1, 1),
        datetime.datetime(2019, 6, 1),
    )
    print(df_stockload.head())  # 查看前几行
    """
                   High      Low     Open    Close  Volume  Adj Close
    Date                                                             
    2009-01-05  1880.72  1844.09  1849.02  1880.72   67200    1880.72
    2009-01-06  1938.69  1871.97  1878.83  1937.15   99000    1937.15
    2009-01-07  1948.23  1920.52  1938.97  1924.01   92400    1924.01
    2009-01-08  1894.17  1862.26  1890.24  1878.18   80400    1878.18
    2009-01-09  1909.35  1875.16  1875.16  1904.86   71200    1904.86
    """
    print(df_stockload.tail())  # 查看末尾几行
    """
                   High      Low     Open    Close  Volume  Adj Close
    Date                                                             
    2019-05-27  2898.13  2833.04  2851.28  2892.38  196700    2892.38
    2019-05-28  2924.04  2887.08  2890.27  2909.91  223300    2909.91
    2019-05-29  2934.98  2890.67  2894.83  2914.70  199000    2914.70
    2019-05-30  2907.85  2881.38  2903.43  2905.80  205800    2905.80
    2019-05-31  2922.91  2895.58  2904.50  2898.70  195200    2898.70    
    """
    print(df_stockload.index)  # 查看行索引信息
    """
    DatetimeIndex(['2009-01-05', '2009-01-06', '2009-01-07', '2009-01-08',
                   '2009-01-09', '2009-01-12', '2009-01-13', '2009-01-14',
                   '2009-01-15', '2009-01-16',
                   ...
                   '2019-05-20', '2019-05-21', '2019-05-22', '2019-05-23',
                   '2019-05-24', '2019-05-27', '2019-05-28', '2019-05-29',
                   '2019-05-30', '2019-05-31'],
                  dtype='datetime64[ns]', name='Date', length=2529, freq=None)
    """
    print(df_stockload.columns)  # 查看列索引信息
    """
    Index(['High', 'Low', 'Open', 'Close', 'Volume', 'Adj Close'], dtype='object')    
    """
    print(df_stockload.shape)  # 查看形状
    """
    (2529, 6)
    """
    print(df_stockload.describe())  # 查看各列数据描述性统计
    """
              High      Low     Open    Close     Volume  Adj Close
    count  2529.00  2529.00  2529.00  2529.00    2529.00    2529.00
    mean   2809.12  2761.67  2785.12  2788.61  167012.57    2788.61
    std     542.75   525.35   535.37   535.78  120044.24     535.78
    min    1880.72  1844.09  1849.02  1863.37       0.00    1863.37
    25%    2338.78  2306.42  2322.32  2325.82   92900.00    2325.82
    50%    2837.86  2786.32  2813.19  2818.16  134000.00    2818.16
    75%    3159.67  3115.98  3137.65  3141.30  190800.00    3141.30
    max    5178.19  5103.40  5174.42  5166.35  857100.00    5166.35
    """
    print(df_stockload.info())  # 查看缺失及每列数据类型
    """
    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 2529 entries, 2009-01-05 to 2019-05-31
    Data columns (total 6 columns):
    High         2529 non-null float64
    Low          2529 non-null float64
    Open         2529 non-null float64
    Close        2529 non-null float64
    Volume       2529 non-null int64
    Adj Close    2529 non-null float64
    dtypes: float64(5), int64(1)
    memory usage: 138.3 KB
    None
    """


def pd_data_000651SZ():

    # 获取格力电器日线行情数据
    df_stockload = web.DataReader(
        "000651.SZ",
        "yahoo",
        datetime.datetime(2009, 1, 1),
        datetime.datetime(2019, 6, 1),
    )
    print(df_stockload.head())
    """
                High   Low  Open  Close    Volume  Adj Close
    Date                                                    
    2009-01-05  4.38  4.07  4.33   4.13  2.95e+07       2.36
    2009-01-06  4.14  3.94  4.14   4.01  8.74e+07       2.29
    2009-01-07  4.00  3.96  3.98   3.96  3.92e+07       2.26
    2009-01-08  3.97  3.86  3.87   3.94  3.35e+07       2.25
    2009-01-09  4.03  3.90  3.94   4.03  4.27e+07       2.30
    """
    print(df_stockload.tail())
    """
                 High    Low   Open  Close    Volume  Adj Close
    Date                                                       
    2019-05-27  54.50  52.98  54.01  54.05  3.52e+07      52.52
    2019-05-28  55.33  53.80  54.00  54.90  4.00e+07      53.35
    2019-05-29  54.66  53.70  54.13  54.10  2.95e+07      52.57
    2019-05-30  53.79  52.63  53.64  52.94  4.55e+07      51.44
    2019-05-31  53.53  52.17  52.90  52.31  3.74e+07      50.83    
    """


def ts_data_sh_hist():
    df_sh_hist = ts.get_hist_data("sh", start="2009-01-01", end="2019-06-01")

    print(df_sh_hist.head())
    """
                   open     high    close    ...        v_ma5    v_ma10    v_ma20
    date                                     ...                                 
    2019-05-31  2904.50  2922.91  2898.70    ...     2.04e+06  2.01e+06  2.23e+06
    2019-05-30  2903.42  2907.85  2905.81    ...     1.98e+06  2.08e+06  2.25e+06
    2019-05-29  2894.83  2934.98  2914.70    ...     1.97e+06  2.12e+06  2.29e+06
    2019-05-28  2890.27  2924.04  2909.91    ...     1.97e+06  2.15e+06  2.33e+06
    2019-05-27  2851.28  2898.13  2892.38    ...     1.95e+06  2.14e+06  2.38e+06
    
    [5 rows x 13 columns]
    """
    print(df_sh_hist.tail())
    """
                   open     high    close    ...        v_ma5    v_ma10    v_ma20
    date                                     ...                                 
    2017-06-20  3148.02  3150.46  3140.01    ...     1.38e+06  1.38e+06  1.38e+06
    2017-06-19  3122.16  3146.77  3144.37    ...     1.37e+06  1.37e+06  1.37e+06
    2017-06-16  3126.37  3134.25  3123.17    ...     1.38e+06  1.38e+06  1.38e+06
    2017-06-15  3125.59  3137.59  3132.49    ...     1.43e+06  1.43e+06  1.43e+06
    2017-06-14  3146.75  3149.17  3130.67    ...     1.38e+06  1.38e+06  1.38e+06
    
    [5 rows x 13 columns]
    """
    print(df_sh_hist.info())  # 查看行情数据概览信息
    """
    <class 'pandas.core.frame.DataFrame'>
    Index: 480 entries, 2019-05-31 to 2017-06-14
    Data columns (total 13 columns):
    open            480 non-null float64
    high            480 non-null float64
    close           480 non-null float64
    low             480 non-null float64
    volume          480 non-null float64
    price_change    480 non-null float64
    p_change        480 non-null float64
    ma5             480 non-null float64
    ma10            480 non-null float64
    ma20            480 non-null float64
    v_ma5           480 non-null float64
    v_ma10          480 non-null float64
    v_ma20          480 non-null float64
    dtypes: float64(13)
    memory usage: 52.5+ KB
    None
    """
    print(df_sh_hist.axes)  # 查看行和列的轴标签
    """
    [Index(['2019-05-31', '2019-05-30', '2019-05-29', '2019-05-28', '2019-05-27',
           '2019-05-24', '2019-05-23', '2019-05-22', '2019-05-21', '2019-05-20',
           ...
           '2017-06-27', '2017-06-26', '2017-06-23', '2017-06-22', '2017-06-21',
           '2017-06-20', '2017-06-19', '2017-06-16', '2017-06-15', '2017-06-14'],
          dtype='object', name='date', length=480), Index(['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change',
           'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'],
          dtype='object')]
    """


def ts_data_sh_k():
    df_sh_k = ts.get_k_data("sh", start="1990-06-01", end="2019-06-01")
    print(df_sh_k.head())
    """
                 date   open  close  ...     low  volume  code
    0  1990-12-19  113.1  113.1  ...   113.1  2650.0    sh
    1  1990-12-20  113.1  113.5  ...   112.8  1990.0    sh
    2  1990-12-21  113.5  113.5  ...   113.4  1190.0    sh
    3  1990-12-24  113.5  114.0  ...   113.3  8070.0    sh
    4  1990-12-25  114.0  114.1  ...   114.0  2780.0    sh
    """
    print(df_sh_k.info())
    """
    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 6782 entries, 0 to 6781
    Data columns (total 7 columns):
    date      6782 non-null object
    open      6782 non-null float64
    close     6782 non-null float64
    high      6782 non-null float64
    low       6782 non-null float64
    volume    6782 non-null float64
    code      6782 non-null object
    dtypes: float64(5), object(2)
    memory usage: 423.9+ KB
    None
    """


def ts_data_sh_h():
    df_sh_h = ts.get_h_data("sh", start="1990-06-01", end="2019-06-01")
    print(df_sh_h.head())
    """
    [Getting data:]  # Empty DataFrame
    Columns: []
    Index: []
    """


# 设置token
token = ""  # 输入你的token
pro = ts.pro_api(token)  # 初始化pro接口


def ts_data_pro_daily():

    # 获取格力电器日线行情数据
    df_gldq = pro.daily(ts_code="000651.SZ", start_date="20090101", end_date="20190601")

    print(df_gldq.head())
    """
         ts_code trade_date   open    ...     pct_chg        vol    amount
    0  000651.SZ   20190531  52.90    ...       -1.19  374222.12  1.97e+06
    1  000651.SZ   20190530  53.64    ...       -2.14  455447.77  2.41e+06
    2  000651.SZ   20190529  54.13    ...       -1.46  295262.21  1.60e+06
    3  000651.SZ   20190528  54.00    ...        1.57  399621.73  2.18e+06
    4  000651.SZ   20190527  54.01    ...        0.28  352294.27  1.89e+06

    [5 rows x 11 columns]
    """
    print(df_gldq.tail())
    """
            ts_code trade_date   open    ...      pct_chg        vol     amount
    2356  000651.SZ   20090109  17.82    ...         2.19   94494.54  169766.08
    2357  000651.SZ   20090108  17.51    ...        -0.61   74000.91  130851.09
    2358  000651.SZ   20090107  18.01    ...        -1.21   86723.22  155955.16
    2359  000651.SZ   20090106  18.73    ...        -2.89  193336.75  348609.53
    2360  000651.SZ   20090105  19.60    ...        -3.86   65225.54  122372.22    

    [5 rows x 11 columns]
    """

    print(df_gldq.info())
    """
    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 2361 entries, 0 to 2360
    Data columns (total 11 columns):
    ts_code       2361 non-null object
    trade_date    2361 non-null object
    open          2361 non-null float64
    high          2361 non-null float64
    low           2361 non-null float64
    close         2361 non-null float64
    pre_close     2361 non-null float64
    change        2361 non-null float64
    pct_chg       2361 non-null float64
    vol           2361 non-null float64
    amount        2361 non-null float64
    dtypes: float64(9), object(2)
    memory usage: 203.0+ KB
    None
    """

    print(df_gldq.axes)
    """
    [RangeIndex(start=0, stop=2361, step=1), Index(['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close',
           'change', 'pct_chg', 'vol', 'amount'],
          dtype='object')]
    """

    """ 规整化处理股票数据格式"""
    # 行索引时间格式规整化 方法一
    # df_gldq.index = pd.to_datetime(df_gldq.trade_date)
    # df_gldq.drop(axis=1, columns='trade_date', inplace=True)
    # print(df_gldq.head())
    """
                  ts_code   open   high    ...     pct_chg        vol    amount
    trade_date                             ...                                 
    2019-05-31  000651.SZ  52.90  53.53    ...       -1.19  374222.12  1.97e+06
    2019-05-30  000651.SZ  53.64  53.79    ...       -2.14  455447.77  2.41e+06
    2019-05-29  000651.SZ  54.13  54.66    ...       -1.46  295262.21  1.60e+06
    2019-05-28  000651.SZ  54.00  55.33    ...        1.57  399621.73  2.18e+06
    2019-05-27  000651.SZ  54.01  54.50    ...        0.28  352294.27  1.89e+06
    
    [5 rows x 10 columns]
    """
    # 行索引时间格式规整化 方法二
    df_gldq.trade_date = pd.DatetimeIndex(df_gldq.trade_date)
    df_gldq.set_index("trade_date", drop=True, inplace=True)
    print(df_gldq.head())
    """
                  ts_code   open   high    ...     pct_chg        vol    amount
    trade_date                             ...                                 
    2019-05-31  000651.SZ  52.90  53.53    ...       -1.19  374222.12  1.97e+06
    2019-05-30  000651.SZ  53.64  53.79    ...       -2.14  455447.77  2.41e+06
    2019-05-29  000651.SZ  54.13  54.66    ...       -1.46  295262.21  1.60e+06
    2019-05-28  000651.SZ  54.00  55.33    ...        1.57  399621.73  2.18e+06
    2019-05-27  000651.SZ  54.01  54.50    ...        0.28  352294.27  1.89e+06
    
    [5 rows x 10 columns]
    """

    df_gldq.sort_index(inplace=True)
    print(df_gldq.index)  # 查看行的轴标签
    """
    DatetimeIndex(['2009-01-05', '2009-01-06', '2009-01-07', '2009-01-08',
                   '2009-01-09', '2009-01-12', '2009-01-13', '2009-01-14',
                   '2009-01-15', '2009-01-16',
                   ...
                   '2019-05-20', '2019-05-21', '2019-05-22', '2019-05-23',
                   '2019-05-24', '2019-05-27', '2019-05-28', '2019-05-29',
                   '2019-05-30', '2019-05-31'],
                  dtype='datetime64[ns]', name='trade_date', length=2361, freq=None)
    """
    df_gldq.index = df_gldq.index.set_names("Date")
    print(df_gldq.index)  # 查看行的轴标签
    """
    DatetimeIndex(['2009-01-05', '2009-01-06', '2009-01-07', '2009-01-08',
                   '2009-01-09', '2009-01-12', '2009-01-13', '2009-01-14',
                   '2009-01-15', '2009-01-16',
                   ...
                   '2019-05-20', '2019-05-21', '2019-05-22', '2019-05-23',
                   '2019-05-24', '2019-05-27', '2019-05-28', '2019-05-29',
                   '2019-05-30', '2019-05-31'],
                  dtype='datetime64[ns]', name='Date', length=2361, freq=None)
    """

    recon_data = {
        "High": df_gldq.high,
        "Low": df_gldq.low,
        "Open": df_gldq.open,
        "Close": df_gldq.close,
        "Volume": df_gldq.vol,
    }
    df_recon = pd.DataFrame(recon_data)
    print(df_recon.columns)
    """
    Index(['Open', 'Close', 'High', 'Low', 'Volume'], dtype='object')
    """
    print(df_recon.head())
    """
                 High    Low   Open  Close     Volume
    Date                                             
    2009-01-05  19.80  18.40  19.60  18.69   65225.54
    2009-01-06  18.73  17.81  18.73  18.15  193336.75
    2009-01-07  18.10  17.90  18.01  17.93   86723.22
    2009-01-08  17.95  17.45  17.51  17.82   74000.91
    2009-01-09  18.25  17.65  17.82  18.21   94494.54
    """
    print(df_recon.tail())
    """
                 High    Low   Open  Close     Volume
    Date                                             
    2019-05-27  54.50  52.98  54.01  54.05  352294.27
    2019-05-28  55.33  53.80  54.00  54.90  399621.73
    2019-05-29  54.66  53.70  54.13  54.10  295262.21
    2019-05-30  53.79  52.63  53.64  52.94  455447.77
    2019-05-31  53.53  52.17  52.90  52.31  374222.12
    """


def ts_data_pro_ixdaily():
    df_sh = pro.index_daily(
        ts_code="000001.SH", start_date="19900601", end_date="20190601"
    )
    print(df_sh.tail())
    """
            ts_code trade_date  close   ...    pct_chg     vol  amount
    6950  000001.SH   19901225  120.2   ...    5.0e+00    15.0     6.5
    6951  000001.SH   19901224  114.5   ...    5.0e+00    32.0    31.1
    6952  000001.SH   19901221  109.1   ...    4.5e+00    28.0    16.1
    6953  000001.SH   19901220  104.4   ...    4.4e+00   197.0    85.0
    6954  000001.SH   19901219  100.0   ...   -2.0e-02  1260.0   494.3
    """
    print(df_sh.head())
    """
         ts_code trade_date   close   ...     pct_chg      vol   amount
    0  000001.SH   20190531  2898.7   ...        -0.2  2.0e+08  1.9e+08
    1  000001.SH   20190530  2905.8   ...        -0.3  2.1e+08  2.0e+08
    2  000001.SH   20190529  2914.7   ...         0.2  2.0e+08  2.0e+08
    3  000001.SH   20190528  2909.9   ...         0.6  2.2e+08  2.3e+08
    4  000001.SH   20190527  2892.4   ...         1.4  2.0e+08  1.9e+08
    """


def bs_data_sh():

    # 登陆系统
    lg = bs.login()
    # 获取历史行情数据
    fields = "date,open,high,low,close,volume"
    df_bs = bs.query_history_k_data(
        "sh.000001",
        fields,
        start_date="2009-01-01",
        end_date="2019-06-01",
        frequency="d",
        adjustflag="2",
    )  # <class 'baostock.data.resultset.ResultData'>
    # frequency="d"取日k线，adjustflag="3"默认不复权，1：后复权；2：前复权

    data_list = []

    while (df_bs.error_code == "0") & df_bs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(df_bs.get_row_data())
    result = pd.DataFrame(data_list, columns=df_bs.fields)
    result.close = result.close.astype("float64")
    result.open = result.open.astype("float64")
    result.low = result.low.astype("float64")
    result.high = result.high.astype("float64")
    result.volume = result.volume.astype("int")
    result.index = pd.to_datetime(result.date)

    print(result.head())
    """
                      date     open     high      low    close      volume
    date                                                                  
    2009-01-05  2009-01-05  1849.02  1880.72  1844.09  1880.72  6713671500
    2009-01-06  2009-01-06  1878.83  1938.69  1871.97  1937.14  9906675600
    2009-01-07  2009-01-07  1938.97  1948.23  1920.52  1924.01  9236008600
    2009-01-08  2009-01-08  1890.24  1894.17  1862.26  1878.18  8037400000
    2009-01-09  2009-01-09  1875.16  1909.35  1875.16  1904.86  7122477900
    """
    print(result.tail())
    """
                      date     open     high      low    close       volume
    date                                                                   
    2019-05-27  2019-05-27  2851.28  2898.13  2833.04  2892.38  19672090112
    2019-05-28  2019-05-28  2890.26  2924.04  2887.08  2909.91  22331055616
    2019-05-29  2019-05-29  2894.83  2934.98  2890.66  2914.70  19895881984
    2019-05-30  2019-05-30  2903.42  2907.85  2881.38  2905.80  20575878912
    2019-05-31  2019-05-31  2904.50  2922.91  2895.58  2898.70  19523057920
    """
    print(result.info())
    """
    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 2530 entries, 2009-01-05 to 2019-05-31
    Data columns (total 6 columns):
    date      2530 non-null object
    open      2530 non-null float64
    high      2530 non-null float64
    low       2530 non-null float64
    close     2530 non-null float64
    volume    2530 non-null int64
    dtypes: float64(4), int64(1), object(1)
    memory usage: 138.4+ KB
    None
    """
    print(result.axes)
    """
    [DatetimeIndex(['2009-01-05', '2009-01-06', '2009-01-07', '2009-01-08',
                   '2009-01-09', '2009-01-12', '2009-01-13', '2009-01-14',
                   '2009-01-15', '2009-01-16',
                   ...
                   '2019-05-20', '2019-05-21', '2019-05-22', '2019-05-23',
                   '2019-05-24', '2019-05-27', '2019-05-28', '2019-05-29',
                   '2019-05-30', '2019-05-31'],
                  dtype='datetime64[ns]', name='date', length=2530, freq=None), Index(['date', 'open', 'high', 'low', 'close', 'volume'], dtype='object')]
    """

    # 登出系统
    bs.logout()


def pro_daily_stock(code_val="000651.SZ", start_val="20090101", end_val="20190601"):
    # 获取股票日线行情数据
    df_stock = pro.daily(ts_code=code_val, start_date=start_val, end_date=end_val)
    df_stock.trade_date = pd.DatetimeIndex(df_stock.trade_date)
    df_stock.set_index("trade_date", drop=True, inplace=True)
    df_stock.sort_index(inplace=True)
    df_stock.index = df_stock.index.set_names("Date")

    recon_data = {
        "High": df_stock.high,
        "Low": df_stock.low,
        "Open": df_stock.open,
        "Close": df_stock.close,
        "Volume": df_stock.vol,
    }
    df_recon = pd.DataFrame(recon_data)

    return df_recon

    """
                 High    Low   Open  Close     Volume
    Date                                             
    2009-01-05  19.80  18.40  19.60  18.69   65225.54
    2009-01-06  18.73  17.81  18.73  18.15  193336.75
    2009-01-07  18.10  17.90  18.01  17.93   86723.22
    2009-01-08  17.95  17.45  17.51  17.82   74000.91
    2009-01-09  18.25  17.65  17.82  18.21   94494.54
    ...           ...    ...    ...    ...        ...
    2019-05-27  54.50  52.98  54.01  54.05  352294.27
    2019-05-28  55.33  53.80  54.00  54.90  399621.73
    2019-05-29  54.66  53.70  54.13  54.10  295262.21
    2019-05-30  53.79  52.63  53.64  52.94  455447.77
    2019-05-31  53.53  52.17  52.90  52.31  374222.12
    
    [2361 rows x 5 columns]
    """


def bs_k_data_stock(
    code_val="sz.000651",
    start_val="2009-01-01",
    end_val="2019-06-01",
    freq_val="d",
    adjust_val="3",
):

    # 登陆系统
    lg = bs.login()
    # 获取历史行情数据
    fields = "date,open,high,low,close,volume"
    df_bs = bs.query_history_k_data(
        code_val,
        fields,
        start_date=start_val,
        end_date=end_val,
        frequency=freq_val,
        adjustflag=adjust_val,
    )  # <class 'baostock.data.resultset.ResultData'>
    # frequency="d"取日k线，adjustflag="3"默认不复权，1：后复权；2：前复权

    data_list = []

    while (df_bs.error_code == "0") & df_bs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(df_bs.get_row_data())
    result = pd.DataFrame(data_list, columns=df_bs.fields)

    result.close = result.close.astype("float64")
    result.open = result.open.astype("float64")
    result.low = result.low.astype("float64")
    result.high = result.high.astype("float64")
    result.volume = result.volume.astype("float64")
    result.volume = result.volume / 100  # 单位转换：股-手
    result.date = pd.DatetimeIndex(result.date)
    result.set_index("date", drop=True, inplace=True)
    result.index = result.index.set_names("Date")

    recon_data = {
        "High": result.high,
        "Low": result.low,
        "Open": result.open,
        "Close": result.close,
        "Volume": result.volume,
    }
    df_recon = pd.DataFrame(recon_data)

    # 登出系统
    bs.logout()
    return df_recon
    """
                 High    Low   Open  Close     Volume
    Date                                             
    2009-01-05  19.80  18.40  19.60  18.69   65225.54
    2009-01-06  18.73  17.81  18.73  18.15  193336.75
    2009-01-07  18.10  17.90  18.01  17.93   86723.22
    2009-01-08  17.95  17.45  17.51  17.82   74000.91
    2009-01-09  18.25  17.65  17.82  18.21   94494.54
    ...           ...    ...    ...    ...        ...
    2019-05-27  54.50  52.98  54.01  54.05  352294.27
    2019-05-28  55.33  53.80  54.00  54.90  399621.73
    2019-05-29  54.66  53.70  54.13  54.10  295262.21
    2019-05-30  53.79  52.63  53.64  52.94  455447.77
    2019-05-31  53.53  52.17  52.90  52.31  374222.12
    
    [2530 rows x 5 columns]
    """


################################### 注册JSON格式自选股票池 #####################################
import json


def str_to_json():

    stock_index = [
        {
            "指数": {
                "上证综指": "sh.000001",
                "深证成指": "sz.399001",
                "沪深300": "sz.000300",
                "创业板指": "sz.399006",
                "上证50": "sh.000016",
                "中证500": "sh.000905",
                "中小板指": "sz.399005",
                "上证180": "sh.000010",
            }
        },
        {
            "股票": {
                "格力电器": "000651.SZ",
                "平安银行": "000001.SZ",
                "同花顺": "300033.SZ",
                "贵州茅台": "600519.SH",
                "浙大网新": "600797.SH",
            }
        },
    ]

    print(stock_index)
    """
    [{'指数': {'上证综指': 'sh.000001', '深证成指': 'sz.399001', '沪深300': 'sz.000300', '创业板指': 'sz.399006', '上证50': 'sh.000016', '中证500': 'sh.000905', '中小板指': 'sz.399005', '上证180': 'sh.000010'}}, 
     {'股票': {'格力电器': '000651.SZ', '平安银行': '000001.SZ', '同花顺': '300033.SZ', '贵州茅台': '600519.SH', '浙大网新': '600797.SH'}}]
    """
    print(type(stock_index))  # <class 'list'>

    # dumps: 将数据转换成字符串
    json_str = json.dumps(stock_index)
    print(json_str)
    # [{"\u6307\u6570": {"\u4e0a\u8bc1\u7efc\u6307": "sh.000001", "\u6df1\u8bc1\u6210\u6307": "sz.399001", "\u6caa\u6df1300": "sz.000300", "\u521b\u4e1a\u677f\u6307": "sz.399006", "\u4e0a\u8bc150": "sh.000016", "\u4e2d\u8bc1500": "sh.000905", "\u4e2d\u5c0f\u677f\u6307": "sz.399005", "\u4e0a\u8bc1180": "sh.000010"}}, {"\u80a1\u7968": {"\u683c\u529b\u7535\u5668": "000651.SZ", "\u5e73\u5b89\u94f6\u884c": "000001.SZ", "\u540c\u82b1\u987a": "300033.SZ", "\u8d35\u5dde\u8305\u53f0": "600519.SH", "\u6d59\u5927\u7f51\u65b0": "600797.SH"}}]
    print(type(json_str))  # <class 'str'>

    # dump: 将数据写入json文件中
    with open("stock_pool.json", "w", encoding="utf-8") as f:
        json.dump(stock_index, f, ensure_ascii=False, indent=4)


def tushare_to_json():
    # 设置token
    token = ""
    pro = ts.pro_api(token)  # 初始化pro接口

    index = {
        "上证综指": "sh.000001",
        "深证成指": "sz.399001",
        "沪深300": "sz.000300",
        "创业板指": "sz.399006",
        "上证50": "sh.000016",
        "中证500": "sh.000905",
        "中小板指": "sz.399005",
        "上证180": "sh.000010",
    }

    df = pro.stock_basic(exchange="", list_status="L")
    # print(df.head())
    """
         ts_code  symbol  name      area  industry  market list_date
    0  000001.SZ  000001  平安银行   深圳       银行     主板  19910403
    1  000002.SZ  000002   万科A   深圳     全国地产     主板  19910129
    2  000004.SZ  000004  国农科技   深圳     生物制药     主板  19910114
    3  000005.SZ  000005  世纪星源   深圳     环境保护     主板  19901210
    4  000006.SZ  000006  深振业A   深圳     区域地产     主板  19920427
    """

    codes = df.ts_code.values
    names = df.name.values
    stock = dict(zip(names, codes))
    # print(stock)
    # {'平安银行': '000001.SZ', '万科A': '000002.SZ', ......}

    stock_index = dict([("指数", index), ("股票", stock)])
    # print(stock_index)

    # stock_index = dict(stock, **index)  # 合并指数和个股成一个字典

    # dump: 将数据写入json文件中
    with open("stock_pool.json", "w", encoding="utf-8") as f:
        json.dump(stock_index, f, ensure_ascii=False, indent=4)


def json_to_str():

    # load: 将文件中的字符串变换为数据类型
    with open("stock_pool.json", "r") as load_f:
        stock_index = json.load(load_f)
    print(stock_index)  # <class 'dict'>
    # {'指数': {'上证综指': '000001.SH', ..... '上证180': '000010.SH'}, '股票': {'平安银行': '000001.SZ', '万科A': '000002.SZ', .....}}
    print(type(stock_index))  # <class 'dict'>

    print(stock_index["指数"]["上证综指"])  # sh.000001
    print(stock_index["股票"]["平安银行"])  # 000001.SZ
    return stock_index


################################### 多任务提速股票池数据获取 #####################################

from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

# 引用于2.6.2小节
import functools, time

# 定义测试代码执行时间的装饰器-三阶
def timeit_test(number=3, repeat=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(repeat):
                start = time.perf_counter()
                for _ in range(number):
                    func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                print("Time of {} used: {} ".format(i, elapsed))

        return wrapper

    return decorator


@timeit_test(number=1, repeat=1)
# 获取股票数据
def get_daily_data(start="20180101", end="20190101"):

    stock_index = json_to_str()  # 读取股票池Json文件
    for code in list(stock_index["股票"].values())[0:500]:
        try:
            df_data = pro_daily_stock(code, start, end)
            print("right code is %s" % code)
        except:
            print("error code is %s" % code)


def map_fun(code, start="20180101", end="20190101"):
    try:
        df_data = pro_daily_stock(code, start, end)
        # print("right code is %s" % code)
    except:
        print("error code is %s" % code)


@timeit_test(number=1, repeat=1)
def get_daily_thread():
    stock_index = json_to_str()  # 读取股票池Json文件
    itr_arg = [code for code in stock_index["股票"].values()]
    print(itr_arg)
    with ThreadPoolExecutor(max_workers=8) as executor:
        # map_fun 传入的要执行的map函数
        # itr_argn 可迭代的参数
        # resultn 返回的结果是一个生成器
        result = executor.map(map_fun, itr_arg[0:500])


@timeit_test(number=1, repeat=1)
def get_daily_multi():
    stock_index = json_to_str()  # 读取股票池Json文件
    itr_arg = [code for code in stock_index["股票"].values()]

    pool = Pool(8)  # 创建拥有8个进程数量的进程池
    # map_fun 传入的要执行的map函数
    # itr_argn 可迭代的参数
    pool.map(map_fun, itr_arg[0:500])
    pool.close()  # 关闭进程池，不再接受新的进程
    pool.join()  # 主进程阻塞等待子进程的退出


if __name__ == "__main__":

    # pd_data_000001SS()
    # pd_data_000651SZ()
    # ts_data_sh_hist()
    # ts_data_sh_h()
    # ts_data_sh_k()
    # ts_data_pro_daily()
    # ts_data_pro_ixdaily()
    # bs_data_sh()
    print(
        pro_daily_stock(code_val="000651.SZ", start_val="20180601", end_val="20190601")
    )
    print(
        bs_k_data_stock(
            code_val="sz.000651",
            start_val="2018-06-01",
            end_val="2019-06-01",
            freq_val="d",
            adjust_val="2",
        )
    )

    if False:
        # str_to_json()
        # tushare_to_json()
        json_to_str()

    if False:
        get_daily_data()  # Time of 0 used: 24.791494612
        # get_daily_thread() # Time of 0 used: 41.300545103  max_workers=8
        # get_daily_multi()  # Time of 0 used: 80.29256642700001
