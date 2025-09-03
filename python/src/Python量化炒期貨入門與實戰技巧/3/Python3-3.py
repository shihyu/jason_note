age = input("请输入您的年龄：")
yourage = int(age)
if yourage <= 0:
    print("\n您是在逗我吧!年龄不能小于或等于0！")
elif yourage < 18:
    print("\n您还未成年，不能登录游戏系统玩游戏！")
else:
    print("\n欢迎您登录游戏系统，正在登录，请耐心等待……")
