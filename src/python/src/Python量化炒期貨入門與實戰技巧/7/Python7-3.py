# 类定义
class people:
    # 定义基本属性
    name = ""
    age = 0
    # 定义私有属性,私有属性在类外部无法直接进行访问
    __weight = 0
    # 定义构造方法
    def __init__(self, n, a, w):
        self.name = n
        self.age = a
        self.__weight = w

    # 定义speak方法
    def speak(self):
        print("%s 说: 我 %d 岁。" % (self.name, self.age))


# 单继承类
class student(people):
    grade = ""

    def __init__(self, n, a, w, g):
        # 调用父类的构函
        people.__init__(self, n, a, w)
        self.grade = g

    # 覆写父类的方法
    def speak(self):
        print("%s 说: 我 %d 岁了，我在读 %d 年级。" % (self.name, self.age, self.grade))


# 利用input()函数动态输入学生的信息
sname = input("请输入学生的姓名：")
sage = int(input("请输入学生的年龄："))
sweight = int(input("请输入学生的体重："))
sgrade = int(input("请输入学生所在的年级："))
s = student(sname, sage, sweight, sgrade)  # 类的实例化
s.speak()  # 调用类中的方法
