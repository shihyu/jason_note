#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
书籍《Python股票量化交易入门到实践 》案例例程
仅用于教学目的，严禁转发和用于盈利目的，违者必究
通过if True/False 语句 开关所要调试的例程
"""

# 第五章 第三方库Matplotlib快速入门

import matplotlib.pyplot as plt
import mpl_finance as mpf  # 替换 import matplotlib.finance as mpf
import numpy as np
import pandas as pd

# 正常显示画图时出现的中文和负号
# from pylab import mpl
# mpl.rcParams['font.sans-serif']=['SimHei']
# mpl.rcParams['axes.unicode_minus']=False

# 5.1 两种绘图方式的区分
if False:
    # 函数式绘图
    # 创建图形并设置大小
    plt.figure(figsize=(12, 8))

    # 生成数据
    start_val = 0  # 开始值
    stop_val = 10  # 终值
    num_val = 1000  # 样本
    x = np.linspace(start_val, stop_val, num_val)
    y = np.sin(x)

    # y=sin(x)图
    # '--g,'：format_string方式，等同于linestyle、color、marker的结合，即破折线、绿色、像素点
    # lw：linewidth，用于设置线条宽度
    # label：设置线条的标签为'sin(x)'
    plt.plot(x, y, "--g,", lw=2, label="sin(x)")
    """
    # 添加sin()的最高点注释
    plt.annotate(u'最高点',
                 xy = (np.pi/2, 1),#箭头指向点的坐标
                 xytext = (np.pi/2, 1.3),#注释文本左端的坐标
                 weight = 'regular',#注释文本的字体粗细风格，bold是粗体，regular是正常粗细
                 color = 'g',#注释文本的颜色
                 fontsize = 15,#注释文本的字体大小
                 arrowprops = {#arrowprops：arrow properties,以字典格式设置箭头属性
                     'arrowstyle': '->',#箭头类型
                     'connectionstyle': 'arc3',#连接类型
                     'color': 'g'#箭头颜色
                 })

    # 添加sin()的最低点注释
    plt.annotate(u'最低点',
                 xy = (np.pi*3/2, -1),
                 xytext = (np.pi*3/2, -1.3),
                 weight = 'regular',
                 color = 'r',
                 fontsize = 15,
                 arrowprops = {
                     'arrowstyle': '->',
                     'connectionstyle': 'arc3',
                     'color': 'r'
                 })
    """
    # 调整坐标轴范围
    x_min = 0  # x轴数值范围最小值
    x_max = 10  # x轴数值范围最大值
    y_min = -1.5  # y轴数值范围最小值
    y_max = 1.5  # y轴数值范围最小值
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    # 设置轴标签
    plt.xlabel("X 轴", fontsize=15)
    plt.ylabel("Y 轴", fontsize=15)

    # 设置坐标轴标签
    x_location = np.arange(0, 10, 2)  # x轴坐标位置
    x_labels = [
        "2019-01-01",
        "2019-02-01",
        "2019-03-01",
        "2019-04-01",
        "2019-05-01",
    ]  # x轴坐标显示标签
    y_location = np.arange(-1, 1.5, 1)  # y轴坐标位置
    y_labels = [u"最小值", u"零值", u"最大值"]  # y轴坐标显示标签
    plt.xticks(x_location, x_labels, rotation=45, fontsize=15)
    plt.yticks(y_location, y_labels, fontsize=15)
    """
    # 添加sin()的水平/垂直参考线
    plt.axhline(y=min(y), c='blue', ls=':', lw=2)
    plt.axvline(x=np.pi*3/2, c='blue', ls='-.', lw=2)

    # 添加sin()平行于x/y轴的参考区域
    plt.axhspan(ymin=0, ymax=1, facecolor='purple', alpha=0.3)
    plt.axvspan(xmin=np.pi*2, xmax=np.pi*5/2, facecolor='g', alpha=0.3)
    """
    # 设置网格线
    # ls：linestyle，用于设置线条类型
    # color：设置网格的线条颜色
    plt.grid(True, ls=":", color="r", alpha=0.5)

    # 设置标题
    plt.title(u"函数式绘图vs对象式绘图", fontsize=25)
    # 添加图例
    plt.legend(loc="upper right", fontsize=15)

    # 显示图形
    plt.show()

if True:

    # 对象式绘图
    # pyplot模块中的figure()函数创建名为fig的Figure对象
    fig = plt.figure(figsize=(12, 8))

    # 在Figure对象中创建一个Axes对象，每个Axes对象即为一个绘图区域
    ax = fig.add_subplot(111)

    # 生成数据
    start_val = 0  # 开始值
    stop_val = 10  # 终值
    num_val = 1000  # 样本
    x = np.linspace(start_val, stop_val, num_val)
    y = np.sin(x)

    # y=sin(x)图
    # '--g,'：format_string方式，等同于linestyle、color、marker的结合，即破折线、绿色、像素点
    # lw：linewidth，用于设置线条宽度
    # label：设置线条的标签为'sin(x)'
    ax.plot(x, y, "--g", lw=2, label="sin(x)")

    if True:
        # 生成右侧y轴
        ax_aux = ax.twinx()  # instantiate a second axes that shares the same x-axis
        ax_aux.plot(x, np.arange(1000), color="blue", label="line 1000")
        # 设置坐标轴标签
        y_location = np.arange(0, 1000, 100)  # y轴坐标位置
        y_labels = np.arange(0, 1000, 100)  # y轴坐标显示标签
        ax.set_yticks(y_location)
        ax.set_yticklabels(y_labels, fontsize=15)

        # 设置轴标签
        ax_aux.set_ylabel("Y 轴-辅助", fontsize=15)

    if False:
        # 添加sin()的最高点注释
        ax.annotate(
            u"最高点",
            xy=(np.pi / 2, 1),  # 箭头指向点的坐标
            xytext=(np.pi / 2, 1.3),  # 注释文本左端的坐标
            weight="regular",  # 注释文本的字体粗细风格，bold是粗体，regular是正常粗细
            color="g",  # 注释文本的颜色
            fontsize=15,  # 注释文本的字体大小
            arrowprops={  # arrowprops：arrow properties,以字典格式设置箭头属性
                "arrowstyle": "->",  # 箭头类型
                "connectionstyle": "arc3",  # 连接类型
                "color": "g",  # 箭头颜色
            },
        )

        # 添加sin()的最低点注释
        ax.annotate(
            u"最低点",
            xy=(np.pi * 3 / 2, -1),
            xytext=(np.pi * 3 / 2, -1.3),
            weight="regular",
            color="r",
            fontsize=15,
            arrowprops={"arrowstyle": "->", "connectionstyle": "arc3", "color": "r"},
        )
    if False:
        # 添加sin()的水平/垂直参考线
        ax.axhline(y=min(y), c="blue", ls=":", lw=2)
        ax.axvline(x=np.pi * 3 / 2, c="blue", ls="-.", lw=2)

        # 添加sin()平行于x/y轴的参考区域
        ax.axhspan(ymin=0, ymax=1, facecolor="purple", alpha=0.3)
        ax.axvspan(xmin=np.pi * 2, xmax=np.pi * 5 / 2, facecolor="g", alpha=0.3)

    # 调整坐标轴范围
    x_min = 0  # x轴数值范围最小值
    x_max = 10  # x轴数值范围最大值
    y_min = -1.5  # y轴数值范围最小值
    y_max = 1.5  # y轴数值范围最小值
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # 设置坐标轴标签
    x_location = np.arange(0, 10, 2)  # x轴坐标位置
    x_labels = [
        "2019-01-01",
        "2019-02-01",
        "2019-03-01",
        "2019-04-01",
        "2019-05-01",
    ]  # x轴坐标显示标签
    y_location = np.arange(-1, 1.5, 1)  # y轴坐标位置
    y_labels = [u"最小值", u"零值", u"最大值"]  # y轴坐标显示标签
    ax.set_xticks(x_location)
    ax.set_yticks(y_location)
    ax.set_xticklabels(x_labels, rotation=45, fontsize=15)
    ax.set_yticklabels(y_labels, fontsize=15)

    # 设置轴标签
    ax.set_xlabel("X 轴", fontsize=15)
    ax.set_ylabel("Y 轴", fontsize=15)
    # 设置网格线
    ax.grid(True, ls=":", color="r", alpha=0.5)
    # 设置标题
    ax.set_title(u"函数式绘图vs对象式绘图", fontsize=25)
    # 添加图例
    if True:
        ax.legend(loc="upper right", fontsize=15)
    else:  # 双轴图例
        fig.legend(
            loc="upper right",
            bbox_to_anchor=(1, 1),
            bbox_transform=ax.transAxes,
            fontsize=15,
        )
    # 显示图形
    plt.show()

# 5.2 常用图表类型的绘制

if False:  # 绘制标注点样式

    fig = plt.figure(figsize=(12, 8))
    # 在Figure对象中创建一个Axes对象，每个Axes对象即为一个绘图区域
    ax = fig.add_subplot(111)
    x = np.arange(10, 20)
    y = np.around(np.log(x), 2)
    ax.plot(x, y, marker="o")

    ax.annotate(
        u"样式1",
        xy=(x[1], y[1]),
        xytext=(80, 10),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", connectionstyle="angle3,angleA=80,angleB=50"),
    )

    ax.annotate(
        u"样式2",
        xy=(x[3], y[3]),
        xytext=(80, 10),
        textcoords="offset points",
        arrowprops=dict(facecolor="black", shrink=0.05, width=5),
    )

    ax.annotate(
        u"样式3",
        xy=(x[5], y[5]),
        xytext=(80, 10),
        textcoords="offset points",
        arrowprops=dict(facecolor="green", headwidth=5, headlength=10),
        bbox=dict(boxstyle="circle,pad=0.5", fc="yellow", ec="k", lw=1, alpha=0.5),
    )  # fc为facecolor,ec为edgecolor,lw为lineweight

    ax.annotate(
        u"样式4",
        xy=(x[7], y[7]),
        xytext=(80, 10),
        textcoords="offset points",
        arrowprops=dict(facecolor="blue", headwidth=5, headlength=10),
        bbox=dict(boxstyle="round,pad=0.5", fc="gray", ec="k", lw=1, alpha=0.5),
    )
    # 显示图形
    plt.show()


if False:  # 绘制成交量条形图
    # 对象式绘图
    # pyplot模块中的figure()函数创建名为fig的Figure对象
    fig = plt.figure(figsize=(12, 8))
    # 在Figure对象中创建一个Axes对象，每个Axes对象即为一个绘图区域
    ax = fig.add_subplot(111)
    # pandas生成时间序列
    date_index = pd.date_range("2019-01-01", freq="D", periods=10)
    # 分别模拟生成涨跌时的成交量数据
    red_bar = [1000, 0, 0, 0, 879, 986, 213, 0, 0, 0]
    green_bar = [0, 200, 599, 567, 0, 0, 0, 234, 998, 489]
    # 绘制条形图
    ax.bar(date_index, red_bar, facecolor="red")
    ax.bar(date_index, green_bar, facecolor="green")
    # 设置轴标签
    ax.set_xlabel(u"交易日", fontsize=15)
    ax.set_ylabel(u"手", fontsize=15)
    # 设置标题
    ax.set_title(u"成交量", fontsize=25)
    # 显示图形
    plt.show()

if False:  # 绘制直方图
    # 对象式绘图
    # pyplot模块中的figure()函数创建名为fig的Figure对象
    fig = plt.figure(figsize=(12, 8))
    # 在Figure对象中创建一个Axes对象，每个Axes对象即为一个绘图区域
    ax = fig.add_subplot(111)
    # 绘制直方图
    ax.hist(
        np.random.normal(loc=0, scale=1, size=1000), bins=50, density=False, color="b"
    )
    # 设置轴标签
    ax.set_xlabel(u"样本值", fontsize=15)
    ax.set_ylabel(u"频数", fontsize=15)
    # 设置标题
    ax.set_title(u"正态分布直方图", fontsize=25)
    # 显示图形
    plt.show()

if False:  # 绘制K线图A
    # 对象式绘图
    # pyplot模块中的figure()函数创建名为fig的Figure对象
    fig = plt.figure(figsize=(12, 8))
    # 在Figure对象中创建一个Axes对象，每个Axes对象即为一个绘图区域
    ax = fig.add_subplot(111)
    # 绘制K线图
    opens = [
        2320.36,
        2300,
        2295.35,
        2347.22,
        2360.75,
        2385.43,
        2376.41,
        2424.92,
        2411,
        2432.68,
    ]
    closes = [
        2320.26,
        2291.3,
        2347.5,
        2358.98,
        2382.48,
        2385.42,
        2419.02,
        2428.15,
        2433.13,
        2334.48,
    ]
    lows = [
        2287.3,
        2288.26,
        2295.35,
        2337.35,
        2347.89,
        2371.23,
        2369.57,
        2417.58,
        2403.3,
        2427.7,
    ]
    highs = [
        2362.94,
        2308.38,
        2345.92,
        2363.8,
        2382.48,
        2383.76,
        2391.82,
        2421.15,
        2440.38,
        2441.73,
    ]
    mpf.candlestick2_ochl(
        ax, opens, closes, highs, lows, width=0.5, colorup="r", colordown="g"
    )  # 绘制K线走势
    # pandas生成时间序列
    date_index = pd.date_range("2019-01-01", freq="D", periods=10)
    # 设置x轴的范围
    ax.set_xlim(0, 10)
    # X轴刻度设定 每15天标一个日期
    ax.set_xticks(np.arange(0, 10))
    # 标签设置为日期
    ax.set_xticklabels(
        [date_index.strftime("%Y-%m-%d")[index] for index in ax.get_xticks()]
    )
    # 设置轴标签
    ax.set_xlabel(u"日期", fontsize=15)
    ax.set_ylabel(u"价格", fontsize=15)
    # 设置标题
    ax.set_title(u"日K线图", fontsize=25)
    # 显示图形
    plt.show()

if False:  # 绘制K线图B
    # 对象式绘图
    # pyplot模块中的figure()函数创建名为fig的Figure对象
    fig = plt.figure(figsize=(12, 8))
    # 在Figure对象中创建一个Axes对象，每个Axes对象即为一个绘图区域
    ax = fig.add_subplot(111)
    # 绘制K线图
    opens = [
        2320.36,
        2300,
        2295.35,
        2347.22,
        2360.75,
        2385.43,
        2376.41,
        2424.92,
        2411,
        2432.68,
    ]
    closes = [
        2320.26,
        2291.3,
        2347.5,
        2358.98,
        2382.48,
        2385.42,
        2419.02,
        2428.15,
        2433.13,
        2334.48,
    ]
    lows = [
        2287.3,
        2288.26,
        2295.35,
        2337.35,
        2347.89,
        2371.23,
        2369.57,
        2417.58,
        2403.3,
        2427.7,
    ]
    highs = [
        2362.94,
        2308.38,
        2345.92,
        2363.8,
        2382.48,
        2383.76,
        2391.82,
        2421.15,
        2440.38,
        2441.73,
    ]
    # 使用zip方法生成数据列表
    ohlc = list(zip(np.arange(0, 10), opens, closes, highs, lows))
    mpf.candlestick_ochl(ax, ohlc, width=0.5, colorup="r", colordown="g", alpha=1.0)
    # pandas生成时间序列
    date_index = pd.date_range("2019-01-01", freq="D", periods=10)
    # 设置x轴的范围
    ax.set_xlim(0, 10)
    # X轴刻度设定 每天标一个日期
    ax.set_xticks(np.arange(0, 10))
    # 标签设置为日期
    ax.set_xticklabels(
        [date_index.strftime("%Y-%m-%d")[index] for index in ax.get_xticks()]
    )
    # 设置轴标签
    ax.set_xlabel(u"日期", fontsize=15)
    ax.set_ylabel(u"价格", fontsize=15)
    # 设置标题
    ax.set_title(u"日K线图", fontsize=25)
    # 显示图形
    plt.show()

if False:
    # 图形对象中属性参数的调节

    # 单条线：
    # plot([x], y, [fmt], data=None, **kwargs)
    # 多条线一起画
    # plot([x], y, [fmt], [x2], y2, [fmt2], ..., **kwargs)

    plt.plot([1, 2, 3, 4, 5], [3, 4, 5, 6, 7], "go--")
    plt.plot(
        [1, 2, 3, 4, 5], [2, 3, 4, 5, 6], color="green", marker="o", linestyle="dashed"
    )
    plt.plot([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], c="g", marker="o", ls="dashed")
    plt.show()

    plt.plot(
        [1, 2, 3, 4, 5],
        [2, 3, 4, 5, 6],
        color="green",
        marker="o",
        linestyle="dashed",
        linewidth=2,
    )
    plt.plot([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], c="g", marker="o", ls="dashed", lw=5)
    plt.show()

if False:
    np.random.seed(1)
    # add_subplot()函数

    fig = plt.figure(figsize=(12, 8))
    ax1 = fig.add_subplot(211)  # 子图以2行1列排布，当前创建的第一个Axes对象
    ax2 = fig.add_subplot(212)  # 创建另一个Axes对象
    ax1.plot(
        np.arange(100),
        np.random.randint(0, 10, 100),
        label=u"0-10随机数",
        ls="-",
        c="r",
        lw=1,
    )
    ax2.plot(
        np.arange(100),
        np.random.randint(10, 20, 100),
        label=u"10-20随机数",
        ls="-",
        c="y",
        lw=1,
    )
    plt.show()

    print(ax1, ax2)
    # AxesSubplot(0.0321644,0.536528;0.955336x0.444722)
    # AxesSubplot(0.0321644,0.0459028;0.955336x0.444722)

    # add_axes()函数
    fig = plt.figure(figsize=(12, 8))
    ax1 = fig.add_axes([0.0321644, 0.536528, 0.955336, 0.444722])
    ax2 = fig.add_axes([0.0321644, 0.0459028, 0.955336, 0.444722])
    ax1.plot(
        np.arange(100),
        np.random.randint(0, 10, 100),
        label=u"0-10随机数",
        ls="-",
        c="r",
        lw=1,
    )
    ax2.plot(
        np.arange(100),
        np.random.randint(10, 20, 100),
        label=u"10-20随机数",
        ls="-",
        c="y",
        lw=1,
    )
    plt.show()
    print(ax1, ax2)
    # Axes(0.0321644,0.536528;0.955336x0.444722)
    # Axes(0.0321644,0.0459028;0.955336x0.444722)

    # subplot()函数
    plt.figure(figsize=(12, 8))
    plt.subplot(211)
    plt.plot(
        np.arange(100),
        np.random.randint(0, 10, 100),
        label=u"0-10随机数",
        ls="-",
        c="r",
        lw=1,
    )
    plt.subplot(212)
    plt.plot(
        np.arange(100),
        np.random.randint(10, 20, 100),
        label=u"10-20随机数",
        ls="-",
        c="y",
        lw=1,
    )
    plt.show()

    # subplot()函数 遍历显示图形
    fig_ps, axes_ps = plt.subplots(2, 3)
    print(fig_ps, axes_ps)
    for i in range(2):
        for j in range(3):
            axes_ps[i, j].plot(
                np.arange(100), np.random.randint(0, 10, 100), color="y", alpha=0.5
            )
    plt.show()
    """
    Figure(640x480) 
    [[<matplotlib.axes._subplots.AxesSubplot object at 0x11d23bcc0>
      <matplotlib.axes._subplots.AxesSubplot object at 0x11d26c2b0>
      <matplotlib.axes._subplots.AxesSubplot object at 0x11d2a0860>]
     [<matplotlib.axes._subplots.AxesSubplot object at 0x11d2d2e10>
      <matplotlib.axes._subplots.AxesSubplot object at 0x11d310400>
      <matplotlib.axes._subplots.AxesSubplot object at 0x11d33f9b0>]]
    """

if False:
    import matplotlib.gridspec as gridspec  # 分割子图

    fig = plt.figure(figsize=(12, 8), dpi=100, facecolor="white")  # 创建fig对象
    gs = gridspec.GridSpec(3, 3)
    graph_ax1 = fig.add_subplot(gs[0, :])
    graph_ax2 = fig.add_subplot(gs[1, 0:2])
    graph_ax3 = fig.add_subplot(gs[1:3, 2])
    graph_ax4 = fig.add_subplot(gs[2, 0:2])
    plt.show()

    fig = plt.figure(figsize=(12, 8), dpi=100, facecolor="white")  # 创建fig对象
    gs = gridspec.GridSpec(
        3,
        3,
        left=0.08,
        bottom=0.15,
        right=0.99,
        top=0.96,
        wspace=0.5,
        hspace=0.5,
        width_ratios=[2, 2, 1],
        height_ratios=[2, 1, 1],
    )

    graph_ax1 = fig.add_subplot(gs[0, :])
    graph_ax2 = fig.add_subplot(gs[1, 0:2])
    graph_ax3 = fig.add_subplot(gs[1:3, 2])
    graph_ax4 = fig.add_subplot(gs[2, 0:2])
    plt.show()

""" 
ax1 = plt.subplot2grid((3,3), (0,0), colspan=3)
ax2 = plt.subplot2grid((3,3), (1,0), colspan=2)
ax3 = plt.subplot2grid((3,3), (1,2), rowspan=2)
ax4 = plt.subplot2grid((3,3), (2,0))
ax5 = plt.subplot2grid((3,3), (2,1))
"""
