import time

scale = 35
print("开始执行程序", "*" * 45, "\n")
# 调用一次perf_counter()，从计算机系统里随机选一个时间点A，计算其距离当前时间点B1有多少秒。
# 当第二次调用该函数时，默认从第一次调用的时间点A算起，距离当前时间点B2有多少秒。
# 两个函数取差，即实现从时间点B1到B2的计时功能。
start = time.perf_counter()
for i in range(scale + 1):
    a = "*" * i  # i个长度的 * 符号
    b = "." * (scale - i)
    c = (i / scale) * 100  # 显示当前进度，百分之多少
    dur = time.perf_counter() - start  # 计时，计算进度条走到某一百分比的用时
    print("百分比:%.3f %% %s %s %.2f秒" % (c, a, b, dur))  # 格式化输出
    time.sleep(0.1)  # 在输出下一个百分之几的进度前，停止0.1秒
print("\n" + "程序执行结束", "*" * 45)
