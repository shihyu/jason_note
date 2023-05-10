#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
书籍《Python股票量化交易入门到实践 》案例例程
仅用于教学目的，严禁转发和用于盈利目的，违者必究
通过if True/False 语句 开关所要调试的例程
"""

# 第四章 第三方库Pandas快速入门

import pandas as pd
import numpy as np

print(pd.__version__)  # 0.23.4

if False:
    deftype = [("date", np.str_, 10), ("close", np.float32), ("vol", np.uint32)]
    stock = np.array(
        [
            ("2019-01-11", 11.01, 1300000),
            ("2019-01-12", 12.11, 1200000),
            ("2019-01-13", 15.01, 1500000),
            ("2019-01-14", 13.01, 1600000,),
        ],
        dtype=deftype,
    )
    print(stock)
    """
    [('2019-01-11', 11.01, 1300000) ('2019-01-12', 12.11, 1200000)
     ('2019-01-13', 15.01, 1500000) ('2019-01-14', 13.01, 1600000)]
    """

# 4.2 Series的生成和访问
if False:
    if False:
        # Series的生成#
        # data = list
        s_list = pd.Series(
            [-1.55666192, 0.127451231, "str-AA", -1.37775038],
            index=["2019-01-11", "2019-01-12", "2019-01-13", "2019-01-14"],
        )
        print(s_list)  # 列表中包含多种数据类型
        """
        2019-01-11    -1.55666
        2019-01-12    0.127451
        2019-01-13      str-AA
        2019-01-14    -1.37775
        dtype: object
        """
        # data = ndarray
        s_ndarray = pd.Series(
            np.arange(4), index=["2019-01-11", "2019-01-12", "2019-01-13", "2019-01-14"]
        )
        print(s_ndarray)
        """
        2019-01-11    0
        2019-01-12    1
        2019-01-13    2
        2019-01-14    3
        dtype: int64
        """
        # data = scalar value
        s_scalar = pd.Series(
            5.0,
            index=["2019-01-11", "2019-01-12", "2019-01-13", "2019-01-14"],
            dtype="int8",
        )
        print(s_scalar)  # dtype指定元素为'int8'
        """
        2019-01-11    5
        2019-01-12    5
        2019-01-13    5
        2019-01-14    5
        dtype: int8
        """

        # data = dict
        s_dict = pd.Series(
            {"2019-01-11": 0.0, "2019-01-12": 1.0, "2019-01-13": 2.0, "2019-01-14": 3.0}
        )
        print(s_dict)
        """
        2019-01-11    0.0
        2019-01-12    1.0
        2019-01-13    2.0
        2019-01-14    3.0
        dtype: float64
        """
        # data = dict
        s_dict = pd.Series(
            {"2019-01-11": 0.0, "2019-01-12": 1.0},
            index=["2019-01-11", "2019-01-12", "2019-01-13", "2019-01-14"],
        )
        print(s_dict)  # 元素数量少于索引，缺失位置为NaN
        """
        2019-01-11    0.0
        2019-01-12    1.0
        2019-01-13    NaN
        2019-01-14    NaN
        dtype: float64
        """
    if False:
        # Series的访问

        # 创建被访问对象
        series_access = pd.Series(
            [10.23, 11.24, 12.25, 13.26],
            index=["2019-01-11", "2019-01-12", "2019-01-13", "2019-01-14"],
        )
        print(series_access)
        """
        2019-01-11    10.23
        2019-01-12    11.24
        2019-01-13    12.25
        2019-01-14    13.26
        dtype: float64
        """

        # 访问Series全部元素数值
        print(series_access.values)
        # [10.23 11.24 12.25 13.26]

        # 访问Series全部索引值
        print(series_access.index)
        # Index(['2019-01-11', '2019-01-12', '2019-01-13', '2019-01-14'], dtype='object')

        # 访问'2019-01-11'索引的元素值
        print(series_access["2019-01-11"])
        # 10.23

        # 访问'2019-01-11'和'2019-01-13'索引的元素值
        print(series_access[["2019-01-11", "2019-01-13"]])
        """
        2019-01-11    10.23
        2019-01-13    12.25
        dtype: float64
        """

        # 访问前两个数据
        print(series_access[:2])
        """
        2019-01-11    10.23
        2019-01-12    11.24
        dtype: float64        
        """

# 4.3 DataFrame的生成和访问
if True:
    if False:
        # DataFrame的生成
        # 以列表组成的字典形式创建DataFrame
        df_list_dict = pd.DataFrame(
            {"Close": [1.0, 2.0, 3.0, 5], "Open": [1.0, 2.0, 3.0, 4.0]},
            index=["2019-01-11", "2019-01-12", "2019-01-13", "2019-01-14"],
        )
        print(df_list_dict)  # 创建2行4列的表格
        """
                    Close  Open
        2019-01-11    1.0   1.0
        2019-01-12    2.0   2.0
        2019-01-13    3.0   3.0
        2019-01-14    5.0   4.0
        """
        # 以嵌套列表形式创建DataFrame
        df_list_list = pd.DataFrame(
            [[1.0, 2.0, 3.0, 5], [1.0, 2.0, 3.0, 4.0]],
            index=["2019-01-11", "2019-01-12"],
            columns=["Close", "Open", "Low", "High"],
        )
        print(df_list_list)
        """
                    Close  Open  Low  High
        2019-01-11    1.0   2.0  3.0   5.0
        2019-01-12    1.0   2.0  3.0   4.0
        """

        # 二维ndarray形式创建DataFrame
        ndarray_data = np.zeros(
            (2), dtype=[("Close", "i4"), ("Open", "f4"), ("Low", "a10")]
        )  # 整数、浮点和字符串
        print(ndarray_data)
        """
        [(0, 0., b'') (0, 0., b'')]
        """
        ndarray_data[:] = [(1, 2.0, "11.2"), (2, 3.0, "12.3")]
        df_ndarray = pd.DataFrame(
            data=ndarray_data, index=["2019-01-11", "2019-01-12"]
        )  # 使用默认的定列索引，也可指定列索引columns，这样最终按指定的顺序进行排列
        print(df_ndarray)
        """
                    Close  Open      Low
        2019-01-11      1   2.0  b'11.2'
        2019-01-12      2   3.0  b'12.3'
        """

        # 以Series组成的字典形式创建DataFrame
        series_data = {
            "Close": pd.Series(
                [1.0, 2.0, 3.0], index=["2019-01-11", "2019-01-12", "2019-01-13"]
            ),
            "Open": pd.Series(
                [1.0, 2.0, 3.0, 4.0],
                index=["2019-01-11", "2019-01-12", "2019-01-13", "2019-01-14"],
            ),
        }
        df_series = pd.DataFrame(series_data)
        print(df_series)
        """
                    Close  Open
        2019-01-11    1.0   1.0
        2019-01-12    2.0   2.0
        2019-01-13    3.0   3.0
        2019-01-14    NaN   4.0
        """

        df_dict_list = pd.DataFrame(
            [{"Close": 1, "Open": 2}, {"Close": 5, "Open": 10, "High": 20}],
            index=["2019-01-11", "2019-01-12"],
        )
        # 如果不指定行索引index DataFrame会自动加上行索引
        print(df_dict_list)
        """
                    Close  High  Open
        2019-01-11      1   NaN     2
        2019-01-12      5  20.0    10
        """

    if True:
        # 创建被访问DataFrame对象
        series_data = {
            "Close": pd.Series(
                [10.51, 10.52, 10.53, 10.54],
                index=["2019-01-11", "2019-01-12", "2019-01-13", "2019-01-14"],
            ),
            "Open": pd.Series(
                [12.31, 12.32, 12.33, 12.34],
                index=["2019-01-11", "2019-01-12", "2019-01-13", "2019-01-14"],
            ),
        }
        df_access = pd.DataFrame(series_data)
        print(df_access)
        """
                    Close   Open
        2019-01-11  10.51  12.31
        2019-01-12  10.52  12.32
        2019-01-13  10.53  12.33
        2019-01-14  10.54  12.34
        """

        # DataFrame的访问
        print("***********************访问全部元素 某行/列元素*******************")
        # 访问DataFrame全部的行索引
        print(df_access.index)
        # Index(['2019-01-11', '2019-01-12', '2019-01-13', '2019-01-14'], dtype='object')

        # 访问DataFrame全部的列索引
        print(df_access.columns)
        # Index(['Close', 'Open'], dtype='object')

        # 访问DataFrame全部的行和列索引
        print(df_access.axes)
        # [Index(['2019-01-11', '2019-01-12', '2019-01-13', '2019-01-14'], dtype='object'), Index(['Close', 'Open'], dtype='object')]

        # 访问DataFrame全部元素数值
        print(df_access.values)
        """
        [[10.51 12.31]
         [10.52 12.32]
         [10.53 12.33]
         [10.54 12.34]]
        """

        # 访问某列内容
        print(df_access["Open"])
        print(df_access.Open)
        """
        2019-01-11    12.31
        2019-01-12    12.32
        2019-01-13    12.33
        2019-01-14    12.34
        Name: Open, dtype: float64        
        """
        print(type(df_access["Open"]))  # 查看列类型
        # <class 'pandas.core.series.Series'>

        # 访问某一行内容
        print(df_access[0:1])
        """
                    Close   Open
        2019-01-11  10.51  12.31    
        """
        print(type(df_access[0:1]))  # 查看行类型
        # <class 'pandas.core.frame.DataFrame'>

        print("***************************DataFrame.iloc***************************")
        # 选取了'2019-01-11'行对应的'Close','Open'这两列的元素内容
        print(df_access.loc[["2019-01-11",], ["Close", "Open"]])
        """
                    Close   Open
        2019-01-11  10.51  12.31
        """

        # 选取了所有的行以及列索引为'Close','Open'的元素内容
        print(df_access.loc[:, ["Close", "Open"]])
        """
                    Close   Open
        2019-01-11  10.51  12.31
        2019-01-12  10.52  12.32
        2019-01-13  10.53  12.33
        2019-01-14  10.54  12.34
        """

        # 访问到'2019-01-11'这行的元素
        print(df_access.loc["2019-01-11"])
        """
        Close    10.51
        Open     12.31
        Name: 2019-01-11, dtype: float64
        """

        # 选取了前两行，第一列的元素。
        print(df_access.iloc[0:2, 0:1])
        """
                    Close
        2019-01-11  10.51
        2019-01-12  10.52
        """
        # 选取了前两行，所有列的元素
        print(df_access.iloc[0:2])
        """
                    Close   Open
        2019-01-11  10.51  12.31
        2019-01-12  10.52  12.32
        """
        # 除了指定某个范围方式选取外，还可自由选取行和列的位置所对应的数据元素，访问第0行和第2行，第一列和第二列的元素
        print(df_access.iloc[[0, 2], [0, 1]])
        """
                    Close   Open
        2019-01-11  10.51  12.31
        2019-01-13  10.53  12.33
        """
        # 采用混合标签和位置的方式访问元素 从'Open'列索引中获取第0个和第2个元素
        # print(df_access.ix[[0, 2], ['Open']])
        """
                     Open
        2019-01-11  12.31
        2019-01-13  12.33
        """

        print(df_access.index[[0, 2]])
        # Index(['2019-01-11', '2019-01-13'], dtype='object')
        print(df_access.loc[df_access.index[[0, 2]], ["Open"]])
        """
                     Open
        2019-01-11  12.31
        2019-01-13  12.33
        """

        print(df_access.columns.get_indexer(["Open"]))  # [1]
        print(df_access.columns.get_loc("Open"))  # 1
        print(df_access.iloc[[0, 2], df_access.columns.get_indexer(["Open"])])
        """
                     Open
        2019-01-11  12.31
        2019-01-13  12.33
        """

        print(df_access.index.get_loc("2019-01-12"))  # 1

        print("***************************条件表达式访问元素***************************")

        print(df_access.Open > df_access.Open.mean())
        """
        2019-01-11    False
        2019-01-12    False
        2019-01-13     True
        2019-01-14     True
        Name: Open, dtype: bool
        """

        print(df_access[df_access.Open > df_access.Open.mean()])
        """
                    Close   Open
        2019-01-13  10.53  12.33
        2019-01-14  10.54  12.34
        """
        print(df_access.loc[df_access.Open > df_access.Open.mean(), "Close"])
        """
        2019-01-13    10.53
        2019-01-14    10.54
        Name: Close, dtype: float64
        """

# 4.4 Python Pandas 时间序列的生成方法
if True:
    # Python datetime模块的使用
    from datetime import date, time, datetime, timedelta

    print("*****example-4.35*****")
    # date.resolution：date对象表示日期的最小单位
    print(f"date.resolution: {date.resolution}")
    # time.resolution：time对象表示时间的最小单位
    print(f"time.resolution: {time.resolution}")
    # datetime.resolution：datetime对象表示时间的最小单位
    print(f"datetime.resolution: {datetime.resolution}")
    """
    date.resolution: 1
    day, 0: 00:00
    time.resolution: 0:00: 00.000001
    datetime.resolution: 0:00: 00.000001
    """
    print("*********************\n")

    print("*****example-4.36*****")
    # date.max、date.min：date对象所能表示的最大、最小日期范围
    print(f"date.max: {date.max} and date.min: {date.min}")
    # time.max、time.min：time对象所能表示的最大、最小时间 范围
    print(f"time.max: {time.max} and time.min: {time.min}")
    # datetime.max、datetime.min：datetime对象所能表示的最大、最小时间范围
    print(f"datetime.max: {datetime.max} and datetime.min: {datetime.min}")
    """
    date.max: 9999-12-31 and date.min: 0001-01-01
    time.max: 23:59:59.999999 and time.min: 00:00:00
    datetime.max: 9999-12-31 23:59:59.999999 and datetime.min: 0001-01-01 00:00:00
    """
    print("*********************\n")

    print("*****example-4.37*****")
    # 构造datetime实例对象
    # datetime (year, month, day[ , hour[ , minute[ , second[ , microsecond[ , tzinfo]]]]])
    datetime_obj = datetime(2016, 10, 26, 10, 23, 15, 1)
    print(f"datetime: {datetime_obj}")
    # datetime: 2016-10-26 10:23:15.000001
    print("*********************\n")

    print("*****example-4.38*****")
    # replace 用参数指定代替原有对象中的属性生成新的datetime时间对象
    re_datetime_obj = datetime_obj.replace(day=27, hour=20)
    print(f"datetime: {re_datetime_obj}")
    #  .isoformat()：返回型如"YYYY-MM-DD HH:MM:SS"格式的字符串时间
    print(f"datetime.isoformat(): {datetime_obj.isoformat()}")
    # .strftime(fmt)：format自定义格式化时间字
    print(f'strftime():{datetime_obj.strftime("%Y-%M-%d %X")}')
    """
    datetime: 2016-10-27 20:23:15.000001
    datetime.isoformat(): 2016-10-26T10:23:15.000001
    strftime():2016-23-26 10:23:15
    """
    print("*********************\n")

    print("*****example-4.39*****")
    print(f'datetime.strptime():{datetime.strptime("2016-10-26", "%Y-%m-%d")}')
    print(f"fromtimestamp():{datetime.fromtimestamp(1429417200.0)}")
    print(f"utcfromtimestamp():{datetime.utcfromtimestamp(1429417200.0)}")
    print(f"datetime.now():{datetime.now()}")
    """
    datetime.strptime():2016-10-26 00:00:00
    fromtimestamp():2015-04-19 12:20:00
    utcfromtimestamp():2015-04-19 04:20:00
    datetime.now():2019-10-20 13:49:20.402097    
    """
    print("*********************\n")

    print("*****example-4.40*****")
    delta_obj = datetime.strptime(
        "2019-10-18 04:20:00", "%Y-%m-%d %X"
    ) - datetime.strptime("2019-10-01 04:20:00", "%Y-%m-%d %X")
    print(type(delta_obj), delta_obj)
    print(delta_obj.days, delta_obj.total_seconds())
    """
    <class 'datetime.timedelta'> 17 days, 0:00:00
    17 1468800.0    
    """
    print("*********************\n")

    print("*****example-4.41*****")
    dt = datetime.now()
    dt1 = dt + timedelta(days=1, hours=1)  # 明天 后1小时
    dt2 = dt + timedelta(days=-1)  # 昨天
    dt3 = dt - timedelta(days=1)  # 昨天
    print(f"{dt1}\n{dt2}\n{dt3}\n")
    """
    2019-10-21 14:49:20.402735
    2019-10-19 13:49:20.402735
    2019-10-19 13:49:20.402735
    """
    print("*********************\n")

    print("*****example-4.42*****")
    ts = pd.Timestamp(2019, 1, 1, 2, 3, 4)
    print(f"pd.Timestamp()-1：{ts}")
    ts = pd.Timestamp(datetime(2019, 1, 1, hour=2, minute=3, second=4))
    print(f"pd.Timestamp()-2：{ts}")
    ts = pd.Timestamp("2019-1-1 2:3:4")
    print(f"pd.Timestamp()-3：{ts}")
    print(f"pd.Timestamp()-type：{type(ts)}")
    """
    pd.Timestamp()-1：2019-01-01 02:03:04
    pd.Timestamp()-2：2019-01-01 02:03:04
    pd.Timestamp()-3：2019-01-01 02:03:04
    pd.Timestamp()-type：<class 'pandas._libs.tslibs.timestamps.Timestamp'>       
    """
    print("*********************\n")

    print("*****example-4.43*****")
    dt = pd.to_datetime(datetime(2019, 1, 1, hour=0, minute=1, second=1))
    print(f"pd.to_datetime()-1：{dt}")
    dt = pd.to_datetime("2019-1-1 0:1:1")
    print(f"pd.to_datetime()-2：{dt}")
    print(f"pd.to_datetime()-type：{type(dt)}")
    """
    pd.to_datetime()-1：2019-01-01 00:01:01
    pd.to_datetime()-2：2019-01-01 00:01:01
    pd.to_datetime()-type：<class 'pandas._libs.tslibs.timestamps.Timestamp'>
    """
    print("*********************\n")

    print("*****example-4.44*****")
    # pd.to_datetime生成自定义时间序列
    dtlist = pd.to_datetime(["2019-1-1 0:1:1", "2019-2-1 0:1:1", "2019-3-1 0:1:1"])
    print(f"pd.to_datetime()-list：{dtlist}")
    """
    pd.to_datetime()-list：DatetimeIndex(['2019-01-01 00:01:01', '2019-02-01 00:01:01',
                   '2019-03-01 00:01:01'],
                  dtype='datetime64[ns]', freq=None)    
    """
    print("*********************\n")

    print("*****example-4.45*****")
    dt_0 = pd.to_datetime(datetime(2019, 1, 1, hour=0, minute=0, second=0))
    dt_1 = dt_0 + pd.Timedelta(days=5, minutes=50, seconds=20)
    print(f"datetime-1:{dt_0}\ndatetime-2:{dt_1}")
    """
    datetime-1:2019-01-01 00:00:00
    datetime-2:2019-01-06 00:50:20    
    """
    print("*********************\n")

    print("*****example-4.46*****")
    date_rng = pd.date_range("2019-01-01", freq="M", periods=12)
    print(f"month date_range()：\n{date_rng}")

    period_rng = pd.period_range("2019-01-01", freq="M", periods=12)
    print(f"month period_range()：\n{period_rng}")
    """
    month date_range()：
    DatetimeIndex(['2019-01-31', '2019-02-28', '2019-03-31', '2019-04-30',
                   '2019-05-31', '2019-06-30', '2019-07-31', '2019-08-31',
                   '2019-09-30', '2019-10-31', '2019-11-30', '2019-12-31'],
                  dtype='datetime64[ns]', freq='M')
    month period_range()：
    PeriodIndex(['2019-01', '2019-02', '2019-03', '2019-04', '2019-05', '2019-06',
                 '2019-07', '2019-08', '2019-09', '2019-10', '2019-11', '2019-12'],
                dtype='period[M]', freq='M') 
    """

    print("*********************\n")

    print("*****example-4.47*****")
    date_rng = pd.date_range("2019-01-01", freq="W-SUN", periods=12)
    print(f"week date_range()：\n{date_rng}")

    period_rng = pd.period_range("2019-01-01", freq="W-SUN", periods=12)
    print(f"week period_range()：\n{period_rng}")
    """
    week date_range()：
    DatetimeIndex(['2019-01-06', '2019-01-13', '2019-01-20', '2019-01-27',
                   '2019-02-03', '2019-02-10', '2019-02-17', '2019-02-24',
                   '2019-03-03', '2019-03-10', '2019-03-17', '2019-03-24'],
                  dtype='datetime64[ns]', freq='W-SUN')
    week period_range()：
    PeriodIndex(['2018-12-31/2019-01-06', '2019-01-07/2019-01-13',
                 '2019-01-14/2019-01-20', '2019-01-21/2019-01-27',
                 '2019-01-28/2019-02-03', '2019-02-04/2019-02-10',
                 '2019-02-11/2019-02-17', '2019-02-18/2019-02-24',
                 '2019-02-25/2019-03-03', '2019-03-04/2019-03-10',
                 '2019-03-11/2019-03-17', '2019-03-18/2019-03-24'],
                dtype='period[W-SUN]', freq='W-SUN')    
    """
    print("*********************\n")

    print("*****example-4.48*****")
    date_rng = pd.date_range("2019-01-01 00:00:00", freq="H", periods=12)
    print(f"hour date_range()：\n{date_rng}")

    period_rng = pd.period_range("2019-01-01 00:00:00", freq="H", periods=12)
    print(f"hour period_range()：\n{period_rng}")
    """
    hour date_range()：
    DatetimeIndex(['2019-01-01 00:00:00', '2019-01-01 01:00:00',
                   '2019-01-01 02:00:00', '2019-01-01 03:00:00',
                   '2019-01-01 04:00:00', '2019-01-01 05:00:00',
                   '2019-01-01 06:00:00', '2019-01-01 07:00:00',
                   '2019-01-01 08:00:00', '2019-01-01 09:00:00',
                   '2019-01-01 10:00:00', '2019-01-01 11:00:00'],
                  dtype='datetime64[ns]', freq='H')
    hour period_range()：
    PeriodIndex(['2019-01-01 00:00', '2019-01-01 01:00', '2019-01-01 02:00',
                 '2019-01-01 03:00', '2019-01-01 04:00', '2019-01-01 05:00',
                 '2019-01-01 06:00', '2019-01-01 07:00', '2019-01-01 08:00',
                 '2019-01-01 09:00', '2019-01-01 10:00', '2019-01-01 11:00'],
                dtype='period[H]', freq='H')    
    """
    print("*********************\n")

    print("*****example-4.49-1*****")
    # 准备被访问DataFrame对象
    dates = pd.to_datetime(["2019-01-11", "2019-01-12", "2019-01-13", "2019-01-14"])
    print(dates)
    series_data_c = {
        "Close": pd.Series([11.12, 12.32, 13.42, 14.52], index=dates),
        "Open": pd.Series([21.12, 22.32, 23.42, 24.52], index=dates),
        "Low": pd.Series([11.12, 12.32, 13.42, 14.52], index=dates),
        "High": pd.Series([21.12, 22.32, 23.42, 24.52], index=dates),
        "Volume": pd.Series([21.12, 22.32, 23.42, 24.52], index=dates),
    }

    df_series_c = pd.DataFrame(
        series_data_c, columns=["Close", "Open", "Low", "High", "Volume"]
    )
    print(df_series_c)
    print("*********************\n")

    print("*****example-4.49-2*****")
    # 准备被访问DataFrame对象
    dates = pd.date_range("2019-01-11", freq="D", periods=4)
    print(dates)
    series_data_d = {
        "Close": pd.Series([11.12, 12.32, 13.42, 14.52], index=dates),
        "Open": pd.Series([21.12, 22.32, 23.42, 24.52], index=dates),
        "Low": pd.Series([11.12, 12.32, 13.42, 14.52], index=dates),
        "High": pd.Series([21.12, 22.32, 23.42, 24.52], index=dates),
        "Volume": pd.Series([21.12, 22.32, 23.42, 24.52], index=dates),
    }

    df_series_d = pd.DataFrame(
        series_data_d, columns=["Close", "Open", "Low", "High", "Volume"]
    )
    print(df_series_d)
    print("*********************\n")

    print("*****example-4.50*****")
    # date_range 生成一个时间区间段，间隔为天
    rng = pd.date_range("20190101", periods=12, freq="D")
    ts_d = pd.Series(np.arange(1, 13), index=rng)
    print(ts_d)

    print(ts_d.resample("5D", closed="left", label="left").sum())  # 左闭右开 1 - 5
    print(ts_d.resample("5D", closed="right", label="right").sum())  # 左开右闭 2 - 6

    ts_12h_asfreq = ts_d.resample("12H").asfreq()
    print(ts_12h_asfreq)
    """
    2019-01-01 00:00:00     1.0
    2019-01-01 12:00:00     NaN
    2019-01-02 00:00:00     2.0
    2019-01-02 12:00:00     NaN
    2019-01-03 00:00:00     3.0
    2019-01-03 12:00:00     NaN
    2019-01-04 00:00:00     4.0
    2019-01-04 12:00:00     NaN
    2019-01-05 00:00:00     5.0
    2019-01-05 12:00:00     NaN
    2019-01-06 00:00:00     6.0
    2019-01-06 12:00:00     NaN
    2019-01-07 00:00:00     7.0
    2019-01-07 12:00:00     NaN
    2019-01-08 00:00:00     8.0
    2019-01-08 12:00:00     NaN
    2019-01-09 00:00:00     9.0
    2019-01-09 12:00:00     NaN
    2019-01-10 00:00:00    10.0
    2019-01-10 12:00:00     NaN
    2019-01-11 00:00:00    11.0
    2019-01-11 12:00:00     NaN
    2019-01-12 00:00:00    12.0
    Freq: 12H, dtype: float64
    """
    ts_12h_ffill = ts_d.resample("12H").ffill()
    print(ts_12h_ffill)
    """
    2019-01-01 00:00:00     1
    2019-01-01 12:00:00     1
    2019-01-02 00:00:00     2
    2019-01-02 12:00:00     2
    2019-01-03 00:00:00     3
    2019-01-03 12:00:00     3
    2019-01-04 00:00:00     4
    2019-01-04 12:00:00     4
    2019-01-05 00:00:00     5
    2019-01-05 12:00:00     5
    2019-01-06 00:00:00     6
    2019-01-06 12:00:00     6
    2019-01-07 00:00:00     7
    2019-01-07 12:00:00     7
    2019-01-08 00:00:00     8
    2019-01-08 12:00:00     8
    2019-01-09 00:00:00     9
    2019-01-09 12:00:00     9
    2019-01-10 00:00:00    10
    2019-01-10 12:00:00    10
    2019-01-11 00:00:00    11
    2019-01-11 12:00:00    11
    2019-01-12 00:00:00    12
    Freq: 12H, dtype: int64
    """
    ts_12h_bfill = ts_d.resample("12H").bfill()
    print(ts_12h_bfill)
    """
    2019-01-01 00:00:00     1
    2019-01-01 12:00:00     2
    2019-01-02 00:00:00     2
    2019-01-02 12:00:00     3
    2019-01-03 00:00:00     3
    2019-01-03 12:00:00     4
    2019-01-04 00:00:00     4
    2019-01-04 12:00:00     5
    2019-01-05 00:00:00     5
    2019-01-05 12:00:00     6
    2019-01-06 00:00:00     6
    2019-01-06 12:00:00     7
    2019-01-07 00:00:00     7
    2019-01-07 12:00:00     8
    2019-01-08 00:00:00     8
    2019-01-08 12:00:00     9
    2019-01-09 00:00:00     9
    2019-01-09 12:00:00    10
    2019-01-10 00:00:00    10
    2019-01-10 12:00:00    11
    2019-01-11 00:00:00    11
    2019-01-11 12:00:00    12
    2019-01-12 00:00:00    12
    Freq: 12H, dtype: int64
    """

    ts_offset_ffill = ts_d.resample("6H", loffset="9.5H").ffill(limit=1)
    print(ts_offset_ffill)
    """
    2019-01-01 09:30:00     1.0
    2019-01-01 15:30:00     1.0
    2019-01-01 21:30:00     NaN
    2019-01-02 03:30:00     NaN
    2019-01-02 09:30:00     2.0
    2019-01-02 15:30:00     2.0
    2019-01-02 21:30:00     NaN
    2019-01-03 03:30:00     NaN
    2019-01-03 09:30:00     3.0
    2019-01-03 15:30:00     3.0
    2019-01-03 21:30:00     NaN
    2019-01-04 03:30:00     NaN
    2019-01-04 09:30:00     4.0
    2019-01-04 15:30:00     4.0
    2019-01-04 21:30:00     NaN
    2019-01-05 03:30:00     NaN
    2019-01-05 09:30:00     5.0
    2019-01-05 15:30:00     5.0
    2019-01-05 21:30:00     NaN
    2019-01-06 03:30:00     NaN
    2019-01-06 09:30:00     6.0
    2019-01-06 15:30:00     6.0
    2019-01-06 21:30:00     NaN
    2019-01-07 03:30:00     NaN
    2019-01-07 09:30:00     7.0
    2019-01-07 15:30:00     7.0
    2019-01-07 21:30:00     NaN
    2019-01-08 03:30:00     NaN
    2019-01-08 09:30:00     8.0
    2019-01-08 15:30:00     8.0
    2019-01-08 21:30:00     NaN
    2019-01-09 03:30:00     NaN
    2019-01-09 09:30:00     9.0
    2019-01-09 15:30:00     9.0
    2019-01-09 21:30:00     NaN
    2019-01-10 03:30:00     NaN
    2019-01-10 09:30:00    10.0
    2019-01-10 15:30:00    10.0
    2019-01-10 21:30:00     NaN
    2019-01-11 03:30:00     NaN
    2019-01-11 09:30:00    11.0
    2019-01-11 15:30:00    11.0
    2019-01-11 21:30:00     NaN
    2019-01-12 03:30:00     NaN
    2019-01-12 09:30:00    12.0
    Freq: 6H, dtype: float64
    """
    print("*********************\n")


# 4.5 DataFrame规整化处理
# 4.6 DataFrame的高效遍历
if True:
    print(
        "########## deal with data #####################################################"
    )
    np.random.seed(1)  # 设置相同的seed 每次生成的随机数相同 便于调试
    # 数据data：正态分布随机数组——close
    close_data = np.random.normal(loc=10.0, scale=1.0, size=1000)
    print(f"close_data：\n {format(close_data[0:10])}")  # 打印前10行
    """
    close_data：
     [11.62434536  9.38824359  9.47182825  8.92703138 10.86540763  7.6984613
     11.74481176  9.2387931  10.3190391   9.75062962]
    """
    # 数据data：open
    open_data = np.roll(close_data, 1)
    print(f"open_data：\n {format(open_data[0:10])}")  # 打印前10行
    """
    open_data：
     [ 9.81304498 11.62434536  9.38824359  9.47182825  8.92703138 10.86540763
      7.6984613  11.74481176  9.2387931  10.3190391 ]
    """
    # 数据data：high low
    high_data = np.where((open_data > close_data), open_data, close_data)
    print(f"high_data：\n {format(high_data[0:10])}")  # 打印前10行
    """
    high_data：
     [11.62434536 11.62434536  9.47182825  9.47182825 10.86540763 10.86540763
     11.74481176 11.74481176 10.3190391  10.3190391 ]
    """
    low_data = np.where((open_data <= close_data), open_data, close_data)
    print(f"low_data：\n {format(low_data[0:10])}")  # 打印前10行
    """
    low_data：
     [9.81304498 9.38824359 9.38824359 8.92703138 8.92703138 7.6984613
     7.6984613  9.2387931  9.2387931  9.75062962]
    """
    open_data[0], close_data[0], high_data[0], low_data[0] = (
        np.nan,
        np.nan,
        np.nan,
        np.nan,
    )

    # 行索引index:交易日期
    date_index = pd.date_range("2010-01-01", freq="D", periods=1000)
    print(f"生成日时间序列：\n{date_index}")
    """
    生成日时间序列：
    DatetimeIndex(['2010-01-01', '2010-01-02', '2010-01-03', '2010-01-04',
                   '2010-01-05', '2010-01-06', '2010-01-07', '2010-01-08',
                   '2010-01-09', '2010-01-10',
                   ...
                   '2012-09-17', '2012-09-18', '2012-09-19', '2012-09-20',
                   '2012-09-21', '2012-09-22', '2012-09-23', '2012-09-24',
                   '2012-09-25', '2012-09-26'],
                  dtype='datetime64[ns]', length=1000, freq='D')
    """

    period_index = pd.period_range("2010-01-01", freq="D", periods=1000)
    print(f"生成日时间序列：\n{period_index}")
    """
    生成日时间序列：
    PeriodIndex(['2010-01-01', '2010-01-02', '2010-01-03', '2010-01-04',
                 '2010-01-05', '2010-01-06', '2010-01-07', '2010-01-08',
                 '2010-01-09', '2010-01-10',
                 ...
                 '2012-09-17', '2012-09-18', '2012-09-19', '2012-09-20',
                 '2012-09-21', '2012-09-22', '2012-09-23', '2012-09-24',
                 '2012-09-25', '2012-09-26'],
                dtype='period[D]', length=1000, freq='D')
    """
    # 生成DataFrame格式的股票行情数据
    df_stock = pd.DataFrame(
        {"close": close_data, "open": open_data, "high": high_data, "low": low_data},
        index=date_index,
    )
    print(f"股票行情数据：\n {df_stock.head()}")  # 打印前5行数据
    """
    股票行情数据：
                     close       open       high       low
    2010-01-01        NaN        NaN        NaN       NaN
    2010-01-02   9.388244  11.624345  11.624345  9.388244
    2010-01-03   9.471828   9.388244   9.471828  9.388244
    2010-01-04   8.927031   9.471828   9.471828  8.927031
    2010-01-05  10.865408   8.927031  10.865408  8.927031
    """

    print(df_stock.tail())  # 查看末尾5行
    """
                    close       open       high       low
    2012-09-22   9.883556  11.291189  11.291189  9.883556
    2012-09-23   7.722702   9.883556   9.883556  7.722702
    2012-09-24   9.930375   7.722702   9.930375  7.722702
    2012-09-25  10.353870   9.930375  10.353870  9.930375
    2012-09-26   9.813045  10.353870  10.353870  9.813045
    """

    print(df_stock.columns)  # 查看列名
    """
    Index(['close', 'open', 'high', 'low'], dtype='object')
    """

    print(df_stock.index)  # 查看索引
    """
    DatetimeIndex(['2010-01-01', '2010-01-02', '2010-01-03', '2010-01-04',
                   '2010-01-05', '2010-01-06', '2010-01-07', '2010-01-08',
                   '2010-01-09', '2010-01-10',
                   ...
                   '2012-09-17', '2012-09-18', '2012-09-19', '2012-09-20',
                   '2012-09-21', '2012-09-22', '2012-09-23', '2012-09-24',
                   '2012-09-25', '2012-09-26'],
                  dtype='datetime64[ns]', length=1000, freq='D')
    """

    print(df_stock.shape)  # 查看形状
    """
    (1000, 4)
    """

    print(df_stock.describe())  # 查看各列数据描述性统计
    """
                close        open        high         low
    count  999.000000  999.000000  999.000000  999.000000
    mean    10.037225   10.039038   10.604220    9.472044
    std      0.980702    0.981961    0.793123    0.809584
    min      6.946236    6.946236    7.885836    6.946236
    25%      9.399818    9.399818   10.055265    8.960818
    50%     10.040371   10.042214   10.593579    9.524627
    75%     10.699507   10.707016   11.108617   10.008677
    max     13.958603   13.958603   13.958603   11.919792
    """

    print(df_stock.info())  # 查看缺失及每列数据类型
    """
    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 1000 entries, 2010-01-01 to 2012-09-26
    Freq: D
    Data columns (total 4 columns):
    close    999 non-null float64
    open     999 non-null float64
    high     999 non-null float64
    low      999 non-null float64
    dtypes: float64(4)
    memory usage: 39.1 KB
    None
    """

    print(df_stock.isnull().head())  # 判断数据缺失值 打印前几行
    """
                close   open   high    low
    2010-01-01   True   True   True   True
    2010-01-02  False  False  False  False
    2010-01-03  False  False  False  False
    2010-01-04  False  False  False  False
    2010-01-05  False  False  False  False
    """

    print(df_stock.notnull().head())  # 判断数据缺失值 打印前几行
    """
                close   open   high    low
    2010-01-01  False  False  False  False
    2010-01-02   True   True   True   True
    2010-01-03   True   True   True   True
    2010-01-04   True   True   True   True
    2010-01-05   True   True   True   True
    """

    print(df_stock[df_stock.isnull().T.any().T])  # 查看NAN值所在行
    # .T 数据转置
    # .any() 返回是否每列上包含至少一个为True元素（默认参数）
    """
                close  open  high  low
    2010-01-01    NaN   NaN   NaN  NaN
    """

    df_fillna = df_stock.fillna(method="bfill", axis=0)  # NAN值填充
    print(df_fillna.head())  # 判断缺失值是否被填充 打印前几行
    # 2010-01-01的数据被2010-01-02填充
    """
                    close       open       high       low
    2010-01-01   9.388244  11.624345  11.624345  9.388244
    2010-01-02   9.388244  11.624345  11.624345  9.388244
    2010-01-03   9.471828   9.388244   9.471828  9.388244
    2010-01-04   8.927031   9.471828   9.471828  8.927031
    2010-01-05  10.865408   8.927031  10.865408  8.927031
    """

    # 只要有一个缺失值就删除该行，于是删除了2010-01-01的行信息
    df_stock.dropna(axis=0, how="any", inplace=True)  # NAN值删除
    print(df_stock[df_stock.isnull().T.any().T])  # 查看NAN值所在行
    # 执行完缺失值删除后，再查看NAN值时发现已经没有NAN值了
    """
    Empty DataFrame
    Columns: [close, open, high, low]
    Index: []
    """

    df_stock_object = df_stock.applymap(lambda x: "%0.2f" % x)  # 保留2位小数
    print(df_stock_object.head())
    """
                close   open   high   low
    2010-01-02   9.39  11.62  11.62  9.39
    2010-01-03   9.47   9.39   9.47  9.39
    2010-01-04   8.93   9.47   9.47  8.93
    2010-01-05  10.87   8.93  10.87  8.93
    2010-01-06   7.70  10.87  10.87  7.70
    """
    print(df_stock_object.info())
    """
    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 999 entries, 2010-01-02 to 2012-09-26
    Freq: D
    Data columns (total 4 columns):
    close    999 non-null object
    open     999 non-null object
    high     999 non-null object
    low      999 non-null object
    dtypes: object(4)
    memory usage: 39.0+ KB
    None
    """

    df_stock = df_stock.round(2)  # 保留2位小数
    print(df_stock.info())
    """
    <class 'pandas.core.frame.DataFrame'>
    DatetimeIndex: 999 entries, 2010-01-02 to 2012-09-26
    Freq: D
    Data columns (total 4 columns):
    close    999 non-null float64
    open     999 non-null float64
    high     999 non-null float64
    low      999 non-null float64
    dtypes: float64(4)
    memory usage: 39.0 KB
    None
    """
    import matplotlib.pyplot as plt

    # 可视化 DataFrame数据
    df_visual = df_stock.loc["2010-01-01":"2012-01-01", ["close"]].plot(
        linewidth=1, figsize=(8, 6)
    )
    df_visual.set_xlabel("Time")
    df_visual.set_ylabel("Close price")
    df_visual.set_title("From 2010-01-01 to 2012-01-01")
    df_visual.legend()
    plt.show()

    # 数据data：随机整数数组——volume
    volume_data = np.random.randint(low=100000, high=200000, size=1000)

    # 生成DataFrame格式的股票成交量数据
    df_volume = pd.DataFrame({"volume": volume_data}, index=date_index)
    print(f"成交量数据：\n {df_volume.head()}")  # 打印前5行数据
    """
    成交量数据：
                 volume
    2010-01-01  191016
    2010-01-02  194447
    2010-01-03  166905
    2010-01-04  156091
    2010-01-05  176409
    """
    df_concat = pd.concat([df_stock, df_volume], axis=1, join="inner")
    print(df_concat.head())
    """
                close   open   high   low  volume
    2010-01-02   9.39  11.62  11.62  9.39  194447
    2010-01-03   9.47   9.39   9.47  9.39  166905
    2010-01-04   8.93   9.47   9.47  8.93  156091
    2010-01-05  10.87   8.93  10.87  8.93  176409
    2010-01-06   7.70  10.87  10.87  7.70  178237
    """

    df_merge = pd.merge(
        df_stock, df_volume, left_index=True, right_index=True, how="inner"
    )
    print(df_merge.head())
    """
                close   open   high   low  volume
    2010-01-02   9.39  11.62  11.62  9.39  194447
    2010-01-03   9.47   9.39   9.47  9.39  166905
    2010-01-04   8.93   9.47   9.47  8.93  156091
    2010-01-05  10.87   8.93  10.87  8.93  176409
    2010-01-06   7.70  10.87  10.87  7.70  178237
    """
    df_join = df_stock.join(df_volume, how="inner")
    print(df_join.head())
    """
                close   open   high   low  volume
    2010-01-02   9.39  11.62  11.62  9.39  194447
    2010-01-03   9.47   9.39   9.47  9.39  166905
    2010-01-04   8.93   9.47   9.47  8.93  156091
    2010-01-05  10.87   8.93  10.87  8.93  176409
    2010-01-06   7.70  10.87  10.87  7.70  178237
    """

    print(
        "########## loop compare#####################################################"
    )
    # for in遍历方式
    def forin_looping(df):
        df = df.assign(pct_change=0)  # 采用assign新增一列
        for i in np.arange(0, df.shape[0]):
            df.iloc[i, df.columns.get_loc("pct_change")] = (
                df.iloc[i]["high"] - df.iloc[i]["low"]
            ) / df.iloc[i]["open"]
        return df

    # print(forin_looping(df_concat)[0:5])
    """
                close   open   high   low  volume  pct_change
    2010-01-02   9.39  11.62  11.62  9.39  194447    0.191910
    2010-01-03   9.47   9.39   9.47  9.39  166905    0.008520
    2010-01-04   8.93   9.47   9.47  8.93  156091    0.057022
    2010-01-05  10.87   8.93  10.87  8.93  176409    0.217245
    2010-01-06   7.70  10.87  10.87  7.70  178237    0.291628
    """

    # iterrows()遍历方式
    def iterrows_loopiter(df):
        df = df.assign(pct_change=0)  # 采用assign新增一列
        for index, row in df.iterrows():
            df.loc[index, "pct_change"] = (row["high"] - row["low"]) / row["open"]
        return df

    # print(iterrows_loopiter(df_concat)[0:5])
    """
    数据与for in遍历方式返回相同
    """

    # apply()遍历方式
    df_concat["pct_change"] = df_concat.apply(
        lambda row: ((row["high"] - row["low"]) / row["open"]), axis=1
    )
    """
    数据与for in遍历方式返回相同
    """

    # Pandas series 的矢量化方式
    df_concat["pct_change"] = (df_concat["high"] - df_concat["low"]) / df_concat["open"]
    """
    数据与for in遍历方式返回相同
    """

    print(type(df_concat.values))

    # Numpy arrays的矢量化方式
    df_concat["pct_change"] = (
        df_concat["high"].values - df_concat["low"].values
    ) / df_concat["open"].values
    print(df_concat.head())
    """
    数据与for in遍历方式返回相同
    """

    if True:
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

        @timeit_test(number=10, repeat=1)
        def forin_test():
            forin_looping(df_concat)

        @timeit_test(number=10, repeat=1)
        def iterloop_test():
            iterrows_loopiter(df_concat)

        @timeit_test(number=10, repeat=1)
        def apply_test():
            df_concat["pct_change"] = df_concat.apply(
                lambda row: ((row["high"] - row["low"]) / row["open"]), axis=1
            )

        @timeit_test(number=10, repeat=1)
        def series_test():
            df_concat["pct_change"] = (
                df_concat["high"] - df_concat["low"]
            ) / df_concat["open"]

        @timeit_test(number=10, repeat=1)
        def ndarray_test():
            df_concat["pct_change"] = (
                df_concat["high"].values - df_concat["low"].values
            ) / df_concat["open"].values

        forin_test()  # Time of 0 used: 8.462902736
        iterloop_test()  # Time of 0 used: 4.0023713690000005
        apply_test()  # Time of 0 used: 0.25229068800000043
        series_test()  # Time of 0 used: 0.0036549980000000204
        ndarray_test()  # Time of 0 used: 0.0018982859999994162

# 4.7 DataFrame存储和加载
if True:
    df_concat.to_csv("table-stock.csv", columns=df_concat.columns, index=True)

    df_csvload = pd.read_csv(
        "table-stock.csv", parse_dates=True, index_col=0, encoding="gb2312"
    )
    print(f"加载csv数据：\n {df_csvload.head()}")  # 打印前5行数据
    """
    加载csv数据：
                 close   open   high   low  volume  pct_change
    2010-01-02   9.39  11.62  11.62  9.39  194447    0.191910
    2010-01-03   9.47   9.39   9.47  9.39  166905    0.008520
    2010-01-04   8.93   9.47   9.47  8.93  156091    0.057022
    2010-01-05  10.87   8.93  10.87  8.93  176409    0.217245
    2010-01-06   7.70  10.87  10.87  7.70  178237    0.291628
    """
    print(df_csvload.dtypes)
