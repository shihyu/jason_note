dict1 = {"姓名": "赵杰", "年龄": 19, "年级": "大一", "学习成绩": "优"}
print("姓名：", dict1["姓名"])
print("年龄：", dict1["年龄"])
print("年级：", dict1["年级"])
print("学习成绩：", dict1["学习成绩"])
print("\n字典所有值是 : ", tuple(dict1.values()))  # 以元组方式返回字典中的所有值
print("\n字典所有的键是: ", list(dict1.keys()))  # 以列表方式返回字典中的所有键
print("\n字典所有值和键是 : %s" % dict1.items())  # 利用items()方法同时访问字典中的值和键
