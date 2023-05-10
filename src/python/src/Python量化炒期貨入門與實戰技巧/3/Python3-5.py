stuscore = input("请输入学生的成绩：")
score = int(stuscore)
if score > 100:
    print("\n学生的成绩最高为100，您太会逗了！")
elif score == 100:
    print("\n您太历害了，满分，是A级！")
elif score >= 90:
    print("\n您的成绩很优秀，是A级！")
elif score >= 82:
    print("\n您的成绩优良，是B级，还要努力呀！")
elif score >= 75:
    print("\n您的成绩中等，是C级，加油再行哦！")
elif score >= 50:
    print("\n您的成绩差，是D级，不要放弃，爱拼才会赢！")
elif score >= 0:
    print("\n您的成绩很差，是E级，只要努力，一定会有所进步！")
else:
    print("\n哈哈，您输错了吧，不可能0分以下！")
