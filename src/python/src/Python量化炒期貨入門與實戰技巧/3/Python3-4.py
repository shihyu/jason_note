mygain = input("请输入你当前年份的利润：")
gain = float(mygain)
# 根据不同的利润，编写不同的提成计算方法
reward1 = 100000 * 0.05
reward2 = reward1 + 100000 * 0.08
reward3 = reward2 + 200000 * 0.1
reward4 = reward3 + 200000 * 0.15
reward5 = reward4 + 400000 * 0.2
# 利用if语句实现，根据输入利润的多少，计算出奖金提成来
if gain < 100000:
    reward = gain * 0.05
elif gain < 2000000:
    reward = reward1 + (gain - 100000) * 0.08
elif gain < 4000000:
    reward = reward2 + (gain - 200000) * 0.1
elif gain < 6000000:
    reward = reward3 + (gain - 400000) * 0.15
elif gain < 10000000:
    reward = reward4 + (gain - 600000) * 0.2
else:
    reward = reward5 + (gain - 1000000) * 0.25
print("\n\n员工的利润是：", gain, "\t员工的奖金是：", reward)
