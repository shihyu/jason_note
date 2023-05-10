dict1 = {"姓名": "赵杰", "年龄": 19, "年级": "大一", "学习成绩": "优"}
print("字典的初始数据：", dict1.items())
dict1["性别"] = "男"  # 添加新的数据项
print("\n添加数据项后字典是 : %s" % dict1.items())
dict1["学习成绩"] = "及格"  # 修改原有的数据项
print("\n修改数据项后字典是 : %s" % dict1.items())
del dict1["学习成绩"]  # 删除字典中的某一项数据
print("\n删除某一项数据后字典是 : %s" % dict1.items())
dict1.clear()  # 清空字典中所有数据项
print("\n清空所有数据后字典是 : %s" % dict1.items())
