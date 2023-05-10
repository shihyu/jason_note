import random  # 导入random标准库

gameplayer = int(input("请输入您要出的拳，其中1表示布、2表示剪刀、3表示石头 :"))
gamecomputer = random.randint(1, 3)  # 产生一个1~3的随机整数
if (
    (gameplayer == 1 and gamecomputer == 3)
    or (gameplayer == 2 and gamecomputer == 1)
    or (gameplayer == 3 and gamecomputer == 2)
):
    print("\n您是高手，您赢了！")
elif gameplayer == gamecomputer:
    print("\n您和计算机一样历害，平了！")
else:
    print("\n计算机就是历害，计算机赢了！")
