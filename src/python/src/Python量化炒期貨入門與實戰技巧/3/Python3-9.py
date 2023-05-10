myday = input("请输入今天星期几：")
day = int(myday)
if day == 1:
    print("\n新的一周开始，开始努力学习！")
elif day >= 2 and day <= 5:
    print("\n努力学习中！")
elif day == 6 or day == 7:
    print("\n世界这么大，我要出去看看！")
else:
    print("\n兄弟，一周就七天，您懂的！")
