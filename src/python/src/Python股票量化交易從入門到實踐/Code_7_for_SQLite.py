#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
书籍《Python股票量化交易入门到实践 》案例例程
仅用于教学目的，严禁转发和用于盈利目的，违者必究
通过if True/False 语句 开关所要调试的例程
"""
# 注意！！！ 使用tushare pro时设置自己官网注册得到的token
# 第七章 股票行情数据的获取和处理——数据库部分

import numpy as np
import pandas as pd
import tushare as ts
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import mpl_finance as mpf
import datetime
import time
import talib
import sqlite3
from sqlalchemy import create_engine
from pandas.io import sql

from Code_7_for_stock_data import bs_k_data_stock, pro_daily_stock, json_to_str

# 参数设置
pd.set_option("display.expand_frame_repr", False)  # False不允许换行
pd.set_option("display.max_rows", 10)  # 显示的最大行数
pd.set_option("display.max_columns", 6)  # 显示的最大列数
pd.set_option("precision", 2)  # 显示小数点后的位数

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 用来正常显示中文标签
plt.rcParams["axes.unicode_minus"] = False  # 用来正常显示负号

conn = sqlite3.connect("stock-data.db")
c = conn.cursor()

# 设置token
token = ""  # 输入你的token
pro = ts.pro_api(token)  # 初始化pro接口

if False:
    try:
        # 创建表
        c.execute(
            """CREATE TABLE SZ000002
               (ID           INT PRIMARY KEY   NOT NULL,
               TIME          TEXT    NOT NULL,
               CODE          TEXT    NOT NULL,
               HIGH          REAL,
               LOW           REAL,
               CLOSE         REAL,
               OPEN          REAL,
               DESCRIPTION CHAR(50));"""
        )
        conn.commit()

        # 查询表结构
        c.execute("PRAGMA table_info(SZ000002)")
        print(c.fetchall())
        # [(0, 'ID', 'INT', 1, None, 1), (1, 'TIME', 'TEXT', 1, None, 0), (2, 'CODE', 'TEXT', 1, None, 0), (3, 'HIGH', 'REAL', 0, None, 0), (4, 'LOW', 'REAL', 0, None, 0), (5, 'CLOSE', 'REAL', 0, None, 0), (6, 'OPEN', 'REAL', 0, None, 0), (7, 'DESCRIPTION', 'CHAR(50)', 0, None, 0)]

        # 插入表
        c.execute(
            "INSERT INTO SZ000002 (ID,TIME,CODE,HIGH,LOW,CLOSE,OPEN,DESCRIPTION) \
              VALUES (1, '2019-1-1', 000002, 10.12, 10.12, 10.12, 10.12,'Buy Signal' )"
        )

        c.execute(
            "INSERT INTO SZ000002 (ID,TIME,CODE,HIGH,LOW,CLOSE,OPEN,DESCRIPTION) \
              VALUES (2, '2019-1-2', 000002, 10.13, 10.13, 10.13, 10.13,'Sell Signal' )"
        )

        c.execute(
            "INSERT INTO SZ000002 (ID,TIME,CODE,HIGH,LOW,CLOSE,OPEN,DESCRIPTION) \
              VALUES (3, '2019-1-3', 000002, 10.14, 10.14, 10.14, 10.14,'Buy Signal' )"
        )

        c.execute(
            "INSERT INTO SZ000002 (ID,TIME,CODE,HIGH,LOW,CLOSE,OPEN,DESCRIPTION) \
              VALUES (4, '2019-1-4', 000002, 10.15, 10.15, 10.15, 10.15,'Sell Signal' )"
        )
        conn.commit()

        # 查询表内容
        c.execute("select * from SZ000002")
        print(c.fetchall())
        # [(1, '2019-1-1', '2', 10.12, 10.12, 10.12, 10.12, 'Buy Signal'), (2, '2019-1-2', '2', 10.13, 10.13, 10.13, 10.13, 'Sell Signal'), (3, '2019-1-3', '2', 10.14, 10.14, 10.14, 10.14, 'Buy Signal'), (4, '2019-1-4', '2', 10.15, 10.15, 10.15, 10.15, 'Sell Signal')]

        # 更新表
        c.execute("UPDATE SZ000002 set DESCRIPTION = 'None' where ID=1")
        conn.commit()
        c.execute("select * from SZ000002")
        print(c.fetchall())
        # [(1, '2019-1-1', '2', 10.12, 10.12, 10.12, 10.12, 'None'), (2, '2019-1-2', '2', 10.13, 10.13, 10.13, 10.13, 'Sell Signal'), (3, '2019-1-3', '2', 10.14, 10.14, 10.14, 10.14, 'Buy Signal'), (4, '2019-1-4', '2', 10.15, 10.15, 10.15, 10.15, 'Sell Signal')]

        # 选择表
        cursor = conn.execute(
            "SELECT id, time, code, description from SZ000002 where HIGH < 10.15 and HIGH > 10.12"
        )
        for row in cursor:
            print(
                "ID = {}; TIME = {}; CODE = {}; description = {};".format(
                    row[0], row[1], row[2], row[3]
                )
            )
            # ID = 2; TIME = 2019-1-2; CODE = 2; description = Sell Signal;
            # ID = 3; TIME = 2019-1-3; CODE = 2; description = Buy Signal;

        # 删除表数据
        c.execute("DELETE from SZ000002 where ID=2;")
        conn.commit()
        c.execute("select * from SZ000002")
        print(c.fetchall())
        # [(1, '2019-1-1', '2', 10.12, 10.12, 10.12, 10.12, 'None'), (3, '2019-1-3', '2', 10.14, 10.14, 10.14, 10.14, 'Buy Signal'), (4, '2019-1-4', '2', 10.15, 10.15, 10.15, 10.15, 'Sell Signal')]

        # 删除一个表
        c.execute("drop table SZ000002")
        conn.commit()
        conn.close()
    except:
        # 删除一个表
        c.execute("drop table SZ000002")
        conn.commit()
        conn.close()


# 获取格力电器日线行情数据
if False:
    df_gldq = pro_daily_stock("000651.SZ", "20190101", "20190201")
    print(df_gldq.head())
    """
                 High    Low   Open  Close     Volume   
    Date                                                      
    2019-01-02  36.45  35.70  36.45  35.80  424789.84      
    2019-01-03  36.19  35.75  35.80  35.92  258798.02      
    2019-01-04  36.70  35.56  35.72  36.65  489612.13      
    2019-01-07  36.96  36.25  36.88  36.48  392690.76     
    2019-01-08  36.42  36.03  36.41  36.34  193021.64    
    """
else:
    df_gldq = pro.daily(ts_code="000651.SZ", start_date="20190101", end_date="20190201")
    print(df_gldq.head())
    """
         ts_code trade_date   open    ...     pct_chg        vol    amount
    0  000651.SZ   20190201  42.35    ...        0.50  408947.29  1.71e+06
    1  000651.SZ   20190131  41.08    ...        2.58  473745.89  1.96e+06
    2  000651.SZ   20190130  40.83    ...       -0.97  332306.54  1.36e+06
    3  000651.SZ   20190129  40.25    ...        2.01  522980.77  2.13e+06
    4  000651.SZ   20190128  40.10    ...        0.98  518476.65  2.11e+06
    
    [5 rows x 11 columns]
    """
if False:
    df_gldq.to_sql(
        name="STOCK000651",
        con=conn,
        index=False,
        # index_label='id',
        if_exists="replace",
    )

    """
    #直接调用sql中的to_sql() 与 DataFrame调用自身的方法效果相同 self参数不同而已
    sql.to_sql(pa,
               name='STOCK600111',
               con=conn,
               index=False,
               #index_label='molecule_id',
               if_exists='append')
    """
    sql_gldq = pd.read_sql_query("select * from 'STOCK000651';", conn)

    print(df_gldq.head())
    # 删除一个表
    c.execute("drop table STOCK000651")
    conn.commit()
    conn.close()

if False:
    # 获取当前最新的股票代码
    def get_stock_code():
        codes = pro.stock_basic(
            exchange="",
            list_status="L",
            fields="ts_code,symbol,name,area,industry,list_date",
        ).ts_code.values
        return codes

    # print(get_stock_code())
    """
    ['000001.SZ' '000002.SZ' '000004.SZ' ... '688122.SH' '688333.SH'
     '688388.SH']
    """

from concurrent.futures import ThreadPoolExecutor


def map_fun(
    code, start="20190101", end="20190201", table_name="STOCK000001", con_name=conn
):
    try:
        data = pro_daily_stock(code, start, end)
        data.to_sql(table_name, con_name, index=False, if_exists="append")
    except:
        print("error code is %s" % code)


def stock_to_sql(table_name, con_name):
    stock_code = json_to_str()  # 读取股票池Json文件
    itr_arg = [code for code in stock_code["股票"].values()]
    print(itr_arg)
    with ThreadPoolExecutor(max_workers=8) as executor:
        # map_fun 传入的要执行的map函数
        # itr_argn 可迭代的参数
        # resultn 返回的结果是一个生成器
        result = executor.map(map_fun, itr_arg)


def stock_to_sql_for(table_name, con_name, start="20190101", end="20190201"):

    stock_code = json_to_str()
    for code in stock_code["股票"].values():
        try:
            data = pro.daily(ts_code=code, start_date=start, end_date=end)
            time.sleep(0.2)
            data.to_sql(table_name, con_name, index=False, if_exists="append")
            print("right code is %s" % code)
        except:
            print("error code is %s" % code)

    # 读取整张表数据
    df = pd.read_sql_query("select * from " + table_name, con_name)
    print(df)
    """
             ts_code trade_date   open    ...     pct_chg       vol    amount
    0      000001.SZ   20190201  11.20    ...        0.90  1.01e+06  1.13e+06
    1      000001.SZ   20190131  10.98    ...        1.37  8.32e+05  9.23e+05
    2      000001.SZ   20190130  10.95    ...       -0.45  7.12e+05  7.85e+05
    3      000001.SZ   20190129  10.96    ...        0.55  8.27e+05  9.05e+05
    4      000001.SZ   20190128  11.04    ...       -0.55  1.04e+06  1.14e+06
    ...          ...        ...    ...    ...         ...       ...       ...
    82400  603999.SH   20190108   5.06    ...       -0.20  4.08e+04  2.08e+04
    82401  603999.SH   20190107   5.00    ...        1.40  4.30e+04  2.15e+04
    82402  603999.SH   20190104   4.70    ...        5.05  4.70e+04  2.31e+04
    82403  603999.SH   20190103   4.79    ...        0.00  1.83e+04  8.77e+03
    82404  603999.SH   20190102   4.86    ...       -1.86  1.73e+04  8.32e+03
    
    [82405 rows x 11 columns]
    """


if False:
    stock_to_sql_for("STOCK000001", conn)  # 下载/更新数据库


if False:
    df = pd.read_sql_query(
        "select * from 'STOCK000001' where close > 9 and close < 10  and pct_chg > 5 and trade_date == '20190128'",
        conn,
    )
    print(df.loc[:, ["ts_code", "trade_date", "close", "pct_chg", "vol"]])
    """
         ts_code trade_date  close  pct_chg        vol
    0  000603.SZ   20190128   9.62     5.48   79957.80
    1  002127.SZ   20190128   9.34     6.02  178280.73
    2  600992.SH   20190128   9.12     6.92  110388.24
    3  601615.SH   20190128   9.10    10.04   12091.95
    """

if False:  # pct_chg > 5 条形图
    df = pd.read_sql_query("select * from 'STOCK000001' where pct_chg > 5", conn)
    count_ = df.groupby("trade_date")["ts_code"].count()

    # 绘图
    plt.bar(
        range(len(count_.index)),
        count_.values,
        align="center",
        color="steelblue",
        alpha=0.8,
    )
    # 添加轴标签
    plt.ylabel("count")
    # 添加刻度标签
    plt.xticks(range(len(count_.index)), count_.index, rotation=45)
    # 添加标题
    plt.title("pct_chg > 5 time distribution")
    # 为每个条形图添加数值标签
    for x, y in enumerate(count_.values):
        plt.text(x, y, "%s" % y, ha="center")
    # 显示图形
    plt.show()

if False:  # pct_chg < -5 条形图
    df = pd.read_sql_query("select * from 'STOCK000001' where pct_chg < -5", conn)
    count_ = df.groupby("trade_date")["ts_code"].count()

    # 绘图
    plt.bar(
        range(len(count_.index)),
        count_.values,
        align="center",
        color="steelblue",
        alpha=0.8,
    )
    # 添加轴标签
    plt.ylabel("count")
    # 添加刻度标签
    plt.xticks(range(len(count_.index)), count_.index, rotation=45)
    # 添加标题
    plt.title("pct_chg < -5 time distribution")
    # 为每个条形图添加数值标签
    for x, y in enumerate(count_.values):
        plt.text(x, y, "%s" % y, ha="center")
    # 显示图形
    plt.show()


if False:
    # 慕课网手记集合：Python基础系列讲解——如何使用自带的SQLite数据库
    conn = sqlite3.connect("stock-data.db")
    c = conn.cursor()

    # 创建表1
    c.execute(
        """CREATE TABLE STOCK600123
           (ID INT PRIMARY KEY   NOT NULL,
           TIME          TEXT    NOT NULL,
           CODE          INT     NOT NULL,
           HIGH          REAL,
           LOW           REAL,
           CLOSE         REAL,
           OPEN          REAL,
           DESCRIPTION CHAR(50));"""
    )
    conn.commit()
    # 查询表结构
    c.execute("PRAGMA table_info(STOCK600123)")
    print(c.fetchall())

    # 创建表2
    c.execute(
        """CREATE TABLE STOCK600111
           (ID INT PRIMARY KEY   NOT NULL,
           TIME          TEXT    NOT NULL,
           CODE          INT     NOT NULL,
           HIGH          REAL,
           LOW           REAL,
           CLOSE         REAL,
           OPEN          REAL,
           DESCRIPTION CHAR(50));"""
    )
    conn.commit()

    # 查询所有表
    c.execute("SELECT name from sqlite_master where type='table'")
    print(c.fetchall())

    # 插入表
    c.execute(
        "INSERT INTO STOCK600123 (ID,TIME,CODE,HIGH,LOW,CLOSE,OPEN,DESCRIPTION) \
          VALUES (1, '2019-1-1', 600123, 10.12, 10.12, 10.12, 10.12,'event1' )"
    )

    c.execute(
        "INSERT INTO STOCK600123 (ID,TIME,CODE,HIGH,LOW,CLOSE,OPEN,DESCRIPTION) \
          VALUES (2, '2019-1-2', 600123, 10.13, 10.13, 10.13, 10.13,'event2' )"
    )

    c.execute(
        "INSERT INTO STOCK600123 (ID,TIME,CODE,HIGH,LOW,CLOSE,OPEN,DESCRIPTION) \
          VALUES (3, '2019-1-3', 600123, 10.14, 10.14, 10.14, 10.14,'event3' )"
    )

    c.execute(
        "INSERT INTO STOCK600123 (ID,TIME,CODE,HIGH,LOW,CLOSE,OPEN,DESCRIPTION) \
          VALUES (4, '2019-1-4', 600123, 10.15, 10.15, 10.15, 10.15,'event4' )"
    )
    conn.commit()

    c.execute("select * from STOCK600123")
    print(c.fetchall())
    conn.commit()

    # 更新表
    c.execute("UPDATE STOCK600123 set CODE = 600888 where ID=1")
    conn.commit()
    c.execute("select * from STOCK600123")
    print(c.fetchall())

    # 筛选条件 进行组合查询
    c.execute("SELECT * from STOCK600123 where HIGH <= 10.13 and LOW >= 10.12")
    print(c.fetchall())

    # 模糊查询
    c.execute("SELECT * from STOCK600123 where CODE like '%600123%'")
    print(c.fetchall())

    # 排序查询
    c.execute("SELECT * from STOCK600123 where CODE like '%600123%' order by HIGH desc")
    print(c.fetchall())

    # 统计与计算
    c.execute("SELECT count(*) from STOCK600123")  # 统计个数 [(4,)]
    print(c.fetchall())
    c.execute("SELECT MAX(HIGH) from STOCK600123")  # 统计最大 [(10.15,)]
    print(c.fetchall())
    c.execute("SELECT SUM(HIGH) from STOCK600123")  # 统计之和 [(40.54,)]
    print(c.fetchall())
    c.execute("SELECT AVG(HIGH) from STOCK600123")  # 统计平均 [(10.135,)]
    print(c.fetchall())

    # 分组
    c.execute("SELECT MAX(HIGH) from STOCK600123 where CODE = 600123 group by TIME")
    print(c.fetchall())

    # 分页查询
    c.execute("SELECT * from STOCK600123 limit 2,1")
    print(c.fetchall())

    # 删除表数据
    c.execute("DELETE from STOCK600123 where ID=2;")
    conn.commit()

    # 选择表
    cursor = conn.execute("SELECT id, time, code, description from STOCK600123")
    for row in cursor:
        print(
            "ID = {}; TIME = {}; CODE = {}; description = {};\n".format(
                row[0], row[1], row[2], row[3]
            )
        )

    # 删除一个表
    c.execute("drop table STOCK600123")
    c.execute("drop table STOCK600111")
    conn.commit()

    conn.close()
