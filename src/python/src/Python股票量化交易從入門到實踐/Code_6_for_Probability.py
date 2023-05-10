#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
书籍《Python股票量化交易入门到实践 》案例例程
仅用于教学目的，严禁转发和用于盈利目的，违者必究
通过if True/False 语句 开关所要调试的例程
"""

# 第六章 统计概率理论快速入门

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# import matplotlib.mlab as mlab 已弃用
import scipy.stats
import random

np.random.seed(0)

# 6.2 深入理解伯努利分布
if False:
    # 二项分布实现例程
    # 同时抛掷5枚硬币，出现正面朝上的次数——试验10次
    print(np.random.binomial(5, 0.5, 10))
    # [3 3 3 3 2 3 2 4 4 2]
    # 同时抛掷5枚硬币，则5次同时为正面发生的概率——采样size=100000次
    print(sum(np.random.binomial(5, 0.5, size=100000) == 5) / 100000.0)
    # 0.03123
    # 同时抛掷5枚硬币，则4次同时为反面发生的概率——采样size=5000次
    print(sum(np.random.binomial(5, 0.5, size=100000) == 4) / 100000.0)
    # 同时抛掷5枚硬币，则3次同时为反面发生的概率——采样size=5000次
    print(sum(np.random.binomial(5, 0.5, size=100000) == 3) / 100000.0)
    # 同时抛掷5枚硬币，则2次同时为反面发生的概率——采样size=5000次
    print(sum(np.random.binomial(5, 0.5, size=100000) == 2) / 100000.0)
    # 同时抛掷5枚硬币，则1次同时为反面发生的概率——采样size=5000次
    print(sum(np.random.binomial(5, 0.5, size=100000) == 1) / 100000.0)
    # 同时抛掷5枚硬币，则0次同时为反面发生的概率——采样size=5000次
    print(sum(np.random.binomial(5, 0.5, size=100000) == 0) / 100000.0)

# 6.3 深入理解正态分布

if False:
    # 单独绘制正态分布 直方图例程
    import matplotlib.pyplot as plt

    plt.hist(
        np.random.normal(loc=-2, scale=0.5, size=10000),
        bins=50,
        density=True,
        color="g",
    )
    plt.hist(
        np.random.normal(loc=0, scale=1, size=10000), bins=50, density=True, color="b"
    )
    plt.hist(
        np.random.normal(loc=2, scale=1.5, size=10000), bins=50, density=True, color="r"
    )
    plt.show()

if False:
    # 标准正态分布转换实现
    import matplotlib.pyplot as plt

    plt.hist(
        np.random.normal(loc=0, scale=1, size=10000) * 0.5 - 2,
        bins=50,
        density=True,
        color="g",
    )
    plt.hist(
        np.random.normal(loc=0, scale=1, size=10000), bins=50, density=True, color="b"
    )
    plt.hist(
        np.random.normal(loc=0, scale=1, size=10000) * 1.5 + 2,
        bins=50,
        density=True,
        color="r",
    )
    plt.show()

if False:
    # 直方图例程上增加概率密度曲线
    import matplotlib.pyplot as plt

    _, bins, _ = plt.hist(
        np.random.normal(loc=0, scale=1, size=10000), bins=50, density=True
    )
    plt.plot(
        bins,
        1.0 / (np.sqrt(2 * np.pi) * 1) * np.exp(-((bins - 0) ** 2) / (2 * 1 ** 2)),
        label="$\mu$=%.1f, $\sigma^2$=%.1f" % (0, 1),
        lw=2,
    )  # 公式计算求得函数值
    plt.show()

if False:

    import matplotlib.pyplot as plt
    import scipy.stats

    # 正态分布实现例程
    def draw_normal(mu=0, sigma=1, size=10000):
        np.random.seed(0)
        dnormal = np.random.normal(mu, sigma, size=size)
        # dnormal = mu + sigma * np.random.randn(size)#np.random.randn(size)标准正态分布
        _, bins, _ = plt.hist(dnormal, bins=50, density=True)
        # 拟合曲线
        # y = mlab.normpdf(bins, mu, sigma) 已弃用
        y = scipy.stats.norm.pdf(bins, mu, sigma)
        plt.plot(
            bins, y, label="$\mu$=%.1f, $\sigma^2$=%.1f" % (mu, sigma)
        )  # scipy.stats.norm方式求得函数值

        plt.xlabel("Expectation")
        plt.ylabel("Probability")
        plt.title("histogram of normal distribution:")

    draw_normal(0, 1, 10000)
    draw_normal(-2, 0.5, 10000)
    draw_normal(2, 1.5, 10000)
    plt.legend(loc=0, ncol=1)  # loc自适应、ncol列的数量
    plt.show()

if False:
    # 绘制正态分布概率密度函数曲线
    import matplotlib.pyplot as plt
    import numpy as np
    import math

    def gd(x, mu=0, sigma=1):
        # 根据公式，由自变量x计算因变量的值

        # Argument:
        #    x: array
        #        输入数据（自变量）
        #    mu: float
        #        均值
        #    sigma: float
        #        方差

        left = 1 / (np.sqrt(2 * math.pi) * np.sqrt(sigma))
        right = np.exp(-((x - mu) ** 2) / (2 * sigma))
        return left * right

    x = np.arange(-4, 5, 0.1)
    # 因变量（不同均值或方差）
    y_2 = gd(x, 0, 1.0)
    plt.plot(x, y_2, color="blue")
    # 设置坐标系
    # plt.xlim(-5.0, 5.0)
    # plt.ylim(0, 1)
    # 设置轴标签
    plt.xlabel("x")
    plt.ylabel("f(x)")
    # x_location = np.arange(-3.0, 4.0, 1) # x轴坐标位置 匹配 3\sigma 2\sigma 1\sigma
    x_location = [-2.58, -1.96, -1, 0, 1, 1.96, 2.58]  #
    x_labels = [
        "$\mu-2.58\sigma$",
        "$\mu-1.96\sigma$",
        "$\mu-1\sigma$",
        "$\mu$",
        "$\mu+1\sigma$",
        "$\mu+1.96\sigma$",
        "$\mu+2.58\sigma$",
    ]  # x轴坐标显示标签
    plt.xticks(x_location, x_labels, rotation=45)

    ax = plt.gca()
    ax.spines["right"].set_color("none")  # 隐藏上右边
    ax.spines["top"].set_color("none")  # 隐藏上边
    # ax.xaxis.set_ticks_position('bottom')#移动轴
    # ax.spines['bottom'].set_position(('data', 0))
    # ax.yaxis.set_ticks_position('left')
    # ax.spines['left'].set_position(('data', 0))
    plt.legend(labels=["$\mu = 0, \sigma^2=1.0$"])
    plt.show()

if False:
    # 交易者人数
    trader = 50

    # 创建简易的市场模型
    def simpmarket(
        win_rate,
        play_cnt=1000,
        stock_num=9,
        position=0.01,
        commission=0.01,
        lever=False,
    ):
        my_money = np.zeros(play_cnt)
        my_money[0] = 1000
        lose_count = 1
        binomial = np.random.binomial(stock_num, win_rate, play_cnt)
        # print(binomial)
        for i in range(1, play_cnt):
            if my_money[i - 1] * position * lose_count <= my_money[i - 1]:  # 资金充足
                once_chip = my_money[i - 1] * position * lose_count
            else:
                break
            if binomial[i] > stock_num // 2:  # 一半以上的股票上涨
                # 三目运算
                # 如果lever == False 结果为真，则不加注，my_money[i] = my_money[i-1] + once_chip
                # 如果lever == False 结果为假，则加注，my_money[i] = my_money[i-1] + once_chip*lose_count
                my_money[i] = (
                    my_money[i - 1] + once_chip
                    if lever == False
                    else my_money[i - 1] + once_chip * lose_count
                )
                lose_count = 1
            else:
                my_money[i] = (
                    my_money[i - 1] - once_chip
                    if lever == False
                    else my_money[i - 1] - once_chip * lose_count
                )
                lose_count += 1
            my_money[i] -= commission
            # print("lose",lose_count)
            # print("money",my_money[i])
            if my_money[i] <= 0:
                break
        return my_money

    # plot与hist二选一
    # 概率50% 无手续费 参加1000次
    # _ = [plt.plot(np.arange(1000), simpmarket(0.5, play_cnt=1000,  stock_num=9, commission = 0)) \
    #                                                               for _ in np.arange(0,trader)]
    # _ = plt.hist([simpmarket(0.5, play_cnt=1000, stock_num=9, commission = 0)[-1] \
    #                                                               for _ in np.arange(0, trader)], bins=30)

    # 概率50% 手续费0.01 参加500000次
    # _ = [plt.plot(np.arange(500000), simpmarket(0.5, play_cnt=500000,  stock_num=9, commission = 0.01)) \
    #                                                               for _ in np.arange(0,trader)]
    # _ = plt.hist([simpmarket(0.5, play_cnt=500000, stock_num=9, commission = 0.01)[-1]
    #                                                               for _ in np.arange(0, trader)], bins=30)

    # 概率50% 无手续费 参加1000次 始能加注
    # _ = [plt.plot(np.arange(1000), simpmarket(0.5, play_cnt=1000,  stock_num=9, commission=0, lever=True)) \
    #                                                               for _ in np.arange(0,trader)]
    # _ = plt.hist([simpmarket(0.5, play_cnt=1000, stock_num=9, commission = 0, lever=True)[-1] \
    #                                                                for _ in np.arange(0, trader)], bins=30)

    # 创建简易的市场模型应用仓位管理
    def positmanage(play_cnt=1000, stock_num=9, commission=0.01):
        my_money = np.zeros(play_cnt)
        my_money[0] = 1000
        win_rate = random.uniform(0.5, 1)  # 生成[0.5,1)之间的浮点数
        binomial = np.random.binomial(stock_num, win_rate, play_cnt)
        for i in range(1, play_cnt):
            once_chip = my_money[i - 1] * (win_rate * 1 - (1 - win_rate)) / 1  # 凯利公式下注
            if binomial[i] > stock_num // 2:
                # 三目运算
                # 如果lever == False 结果为真，my_money[i] = my_money[i-1] + once_chip
                # 如果lever == False 结果为假，my_money[i] = my_money[i-1] + once_chip*lose_count
                my_money[i] = my_money[i - 1] + once_chip
            else:
                my_money[i] = my_money[i - 1] - once_chip
            my_money[i] -= commission
            if my_money[i] <= 0:
                break

        return my_money

    # 仓位管理 手续费0.01 参加5次
    _ = [
        plt.plot(np.arange(5), positmanage(play_cnt=5, stock_num=9, commission=0.01))
        for _ in np.arange(0, trader)
    ]
    # _ = plt.hist([positmanage(play_cnt=5, stock_num=9, commission = 0)[-1] \
    #                                                                for _ in np.arange(0, trader)], bins=30)
    plt.show()

if False:

    def random_walk(nsteps=1000):

        draws = np.random.randint(0, 2, size=nsteps)
        # print(f'random walk direction is {draws}')# random walk direction is [1 0 1 ... 0 1 0]
        steps = np.where(draws > 0, 1, -1)  # 将0转换为-1
        walk = steps.cumsum()  # 累加方式记录轨迹
        return walk

    # 单次标注随机漫步轨迹
    def draw_random_walk():
        walk_steps = 2000
        walk_path = random_walk(walk_steps)

        # 统计漫步过程中，终点、前进和后退最大的距离
        start_y = start_x = 0
        end_y = walk_path[-1], end_x = walk_steps - 1
        print("在{}次漫步中，终点的距离：{}".format(walk_steps, end_y))

        max_y = walk_path.max()
        max_x = walk_path.argmax()
        print("在{}次漫步中，第{}步前进最远的距离：{}".format(walk_steps, max_x, max_y))

        min_y = walk_path.min()
        min_x = walk_path.argmin()
        print("在{}次漫步中，第{}步后退最远的距离：{}".format(walk_steps, min_x, min_y))

        # 统计漫步过程中，距离原点为30的索引
        # greater_or_equal_30 = np.abs(walk_path) >= 30
        # print('在{}次漫步中，距离超过30的总数为：{}'.format(walk_steps, greater_or_equal_30.sum()))

        # 首次到达30的索引
        # first_30 = greater_or_equal_30.argmax()
        # print('在{}次漫步中，首次距离超过30的索引：{}'.format(walk_steps, first_30))

        # value = np.where(greater_or_equal_30 == True)
        # print('在1000次漫步中，距离超过30的索引：{}'.format(value))
        """
        在1000次漫步中，距离超过30的索引：(array([551, 552, 553, 563, 564, 565, 567, 568, 569, 575, 576, 577, 578,... 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989,990, 991, 992, 993, 994, 995, 996, 997, 998, 999]),)
        """
        x = np.linspace(0, 2000, num=2000)
        # y2 = np.ones(2000)*30
        # y3 = -y2
        # 绘制+-30线
        # plt.plot(x, y2, color='r', linewidth=1, linestyle='--', label='+30')
        # plt.plot(x, y3, color='g', linewidth=1, linestyle='--', label='-30')

        # 绘制出漫步的足迹
        plt.plot(x, walk_path, color="b", linewidth=1, label="walk step")

        # 绘制关键点
        # plt.scatter([max_x,min_x,first_30], [max_y,min_y,walk_path[first_30]], s=30, color=['r','g','b'])

        # 添加标注
        # 起点坐标

        plt.annotate(
            "start:({},{})".format(start_x, start_y),
            xy=(start_x, start_y),
            xycoords="data",
            xytext=(+50, +20),
            textcoords="offset points",
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.5),  # 增加外框
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"),
        )

        # 终点坐标
        plt.annotate(
            "end:({},{})".format(end_x, end_y),
            xy=(end_x, end_y),
            xycoords="data",
            xytext=(-50, +20),
            textcoords="offset points",
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.5),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"),
        )

        # 最大距离坐标
        plt.annotate(
            "max:({},{})".format(max_x, max_y),
            xy=(max_x, max_y),
            xycoords="data",
            xytext=(-20, +20),
            textcoords="offset points",
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.5),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"),
        )
        # 最小距离坐标
        plt.annotate(
            "min:({},{})".format(min_x, min_y),
            xy=(min_x, min_y),
            xycoords="data",
            xytext=(-20, +20),
            textcoords="offset points",
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.5),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"),
        )

        # 首次到达30距离的坐标
        """
        if walk_path[first_30]==30:
            plt.annotate(
                'first arrive to 30:({},{})'.format(first_30, walk_path[first_30]),
                xy=(first_30, walk_path[first_30]),
                xycoords='data',
                xytext=(-20, +20),
                textcoords='offset points',
                fontsize=8,
                arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2")
            )
        """
        # 图例
        plt.legend(loc="best")
        # plt.ylim(-200, 200)
        plt.xlabel("游走步数")
        plt.ylabel("分布轨迹")
        plt.title(u"模拟随机漫步")
        plt.show()

    # 多组随机漫步-bar
    def simbar_random_walk():
        # 模拟多个随机漫步，这里生成了15组随机数
        nwalks = 15
        nsteps = 1000
        # 仅需要对参数size稍作修改
        draws = np.random.randint(0, 2, size=(nwalks, nsteps))
        steps = np.where(draws > 0, 1, -1)
        walks = steps.cumsum(axis=1)  # 横向累加

        # 最远距离
        max_distance = walks.max(axis=1)
        print("{}组随机漫步中，距离最远为：{}".format(nwalks, max_distance))
        """15组随机漫步中，距离最远为：[26 32 24 44 36 65 40 33 46 74 31 25 28 43 48]"""

        # 距离原点超过30
        values = np.abs(walks) >= 30
        # 每组的随机漫步中，是否存在距离超过30
        hits30 = np.any(values, axis=1)  # 横向查找
        print("{}组随机漫步中，共有{}组存在距离超过30的，具体为：{}".format(nwalks, hits30.sum(), hits30))
        """
        15组随机漫步中，共有11组存在距离超过30的，具体为：
        [False  True False  True  True  True  True  True  True  True  True False False  True  True]
        """
        # 在这些距离超过30的数组中，首次移动到30的索引
        value = (np.abs(walks[hits30]) >= 30).argmax(axis=1)
        value_mean = np.mean(value)
        print(
            "{}组随机漫步中，首次移动到30的索引为：{}，平均需{}次移动".format(nwalks, value, np.int(value_mean))
        )
        """15组随机漫步中，首次移动到30的索引为：[813 321 143 269 385 577 771 251 843 911 743]，平均需547次移动"""

        # 均值
        distance_mean = max_distance.mean()
        # 大于均值
        greater_mean = np.where(max_distance > distance_mean, max_distance, 0)
        # 小于均值
        smaller_mean = np.where(max_distance <= distance_mean, max_distance, 0)

        plt.figure(num=2)
        plt.title("random walk")
        x = np.arange(nwalks)
        # 绘制柱状图
        l1 = plt.bar(x, greater_mean, color="r")
        l2 = plt.bar(x, smaller_mean, color="g")
        # 绘制数据
        for x0, y0 in zip(x, max_distance):
            plt.text(
                x0, y0, "{}".format(y0), ha="center", va="bottom", fontdict={"size": 8}
            )
        # 绘制均线
        plt.plot(x, np.ones(nwalks) * distance_mean, color="b", linestyle="--")
        # 绘制30线
        plt.plot(x, np.ones(nwalks) * 30, color="y", linestyle="--")
        # 添加注释
        plt.text(
            -0.5,
            distance_mean,
            "mean:{:.2f}".format(distance_mean),
            ha="right",
            fontdict={"size": 8},
        )

        # 设置图例
        plt.legend(
            handles=[l1, l2], labels=["greater mean", "smaller mean"], loc="best"
        )
        # 设置坐标轴刻度format
        plt.xticks(x)
        plt.show()

    # 将随机漫步用直方图显示
    def sim_normal_distribution():
        end_path = [random_walk(nsteps=2000)[-1] for _ in np.arange(0, 1000)]
        _, bins, _ = plt.hist(end_path, bins=50, density=True)
        plt.xlabel("游走步数")
        plt.ylabel("分布轨迹")
        plt.title(u"模拟随机漫步")
        plt.show()

    # draw_random_walk()
    # sim_normal_distribution()
    # simbar_random_walk()
