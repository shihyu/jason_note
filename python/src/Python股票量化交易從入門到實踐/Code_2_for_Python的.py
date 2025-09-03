#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
书籍《Python股票量化交易入门到实践 》案例例程
仅用于教学目的，严禁转发和用于盈利目的，违者必究
通过if True/False 语句 开关所要调试的例程
"""

# 第二章 量化语言Python的关键应用


# 2.2 开启Python的第一个程序

# 2.2.1 如何建立标准py文件
if False:
    import keyword

    def python_syntax():

        print(keyword.kwlist)
        """
        ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 
        'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 
        'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 
        'try', 'while', 'with', 'yield']
        """

    if __name__ == "__main__":
        print("This is main function!")
        python_syntax()

# 2.2.4调试助手print()函数
if False:
    print("Quant Trade")  # 输出字符串
    print(10.68)  # 输出数字

    str_var = "Quant Trade"  # 字符串
    print(str_var)  # 输出变量

    l_var = [1, 2, "a"]  # 列表
    print(l_var)

    t_var = (1, 2, "a")  # 元组
    print(t_var)

    d_var = {"a": 1, "b": 2}  # 字典
    print(d_var)
    """
    Quant Trade
    10.68
    Quant Trade
    [1, 2, 'a']
    (1, 2, 'a')
    {'a': 1, 'b': 2}
    """

    print("This is %s and Price is %2.2f" % ("Quant Trade", 10.68))
    # This is Quant Trade and Price is 10.68

    str_time = "2019-05-07 21:56:11"
    print(f"time is:{str_time}")
    # time is:2019-05-07 21:56:11

# 2.3 何为Python动态类型特征

# 2.3.1 变量的种类
if False:
    print("************************************")
    # 查看数值的类型  注：type()用于查询数据类型
    print(type(True))  # 结果为：<class 'bool'>
    print(type(123))  # 结果为：<class 'int'>
    print(type(1.12))  # 结果为：<class 'float'>
    print(type(3j + 1))  # 结果为：<class 'complex'>

    # 查看数值的运算
    a = 1
    b = 3
    print(a + b)  # 结果为：4
    print(a - b)  # 结果为：-2
    print(a * b)  # 结果为：3
    print(a / b)  # 结果为：0.3333333333333333
    print(a % b)  # 结果为：1
    print(a ** b)  # 结果为：1
    print(a // b)  # 结果为：0

    print("************************************")

    # 查看单引号、双引号、三引号包围的字符串常量
    print("one quote!")  # 结果为：one quote!
    print("one ' quote!")  # 结果为：one ' quote!
    print('one " quote!')  # 结果为：one " quote!
    print("two ' quote!")  # 结果为：two ' quote!
    print('two " quote!')  # 结果为：two " quote!
    print("""three quote!""")  # 结果为：three quote!
    print("""three ' quote!""")  # 结果为：three ' quote!
    print("""three "" quote!""")  # 结果为：three "" quote!
    print("""three \""" quote!""")  # 结果为：three """ quote!

    print("************************************")

    # 创建列表变量
    list_temp = ["close", "open", 2019, 2020, [1.1, 1.2], "10%"]

    # 列表访问
    print(list_temp[2])  # 访问列表中下标为2的元素 结果为：2019
    print(list_temp[1:5])  # 访问列表中下标为1到4的元素 结果为：['open', 2019, 2020, [1.1, 1.2]]
    # 列表二次赋值
    list_temp[2] = 2001
    print(list_temp)  # 列表内容变为：['close', 'open', 2001, 2020, [1.1, 1.2], '10%']

    # 统计列表元素个数
    print(len(list_temp))  # 结果为：6
    # 从列表中找出某个值第一个匹配项的索引位置
    print(list_temp.index("open"))  # 结果为：1
    # 在列表末尾添加新的元素
    list_temp.append("20%")
    # 移除列表中某个值的第一个匹配项
    list_temp.remove(2001)
    print(list_temp)  # 列表内容变为：['close', 'open', 2020, [1.1, 1.2], '10%', '20%']

    print("************************************")

    # 创建元组并初始化
    tuple_temp = ("close", "open", 2019, 2020, [1.1, 1.2], "10%")
    # 元组访问
    print(tuple_temp[1:5])  # 访问元组中为1到4的元素 结果为：('open', 2019, 2020, [1.1, 1.2])
    # 统计元组元素个数
    print(len(tuple_temp))  # 结果为：6
    # 从元组中找出某个值第一个匹配项的索引位置
    print(tuple_temp.index(2019))  # 结果为：2

    print("************************************")

    # 创建字典变量
    dict_temp = {"chapter1": "content1", "chapter2": "content1"}

    # string不可变类型能作为key
    key = "chapter3"
    dict_temp[key] = "content1"
    print(
        dict_temp
    )  # 字典内容变为：{'chapter1': 'content1', 'chapter2': 'content1', 'chapter3': 'content1'}

    # list可变类型不能作为key
    # key = [1, 2, 3]
    # dict_temp[key] = 'a list'
    # print(dict_temp) # 报错 TypeError: unhashable type: 'list'

    # 嵌套字典
    dict_temp = {
        "chapter1": {"name": "basic", "page": 31},
        "chapter2": {"name": "senior", "page": 42},
    }

    # 访问字典
    print(dict_temp["chapter2"])  # 访问结果为：{'name': 'senior', 'page': 42}
    print(dict_temp["chapter2"]["name"])  # 访问结果为：senior
    # print(dict_temp['chapter3']) #报错 KeyError: 'chapter3'

    # 添加字典
    dict_temp["chapter3"] = {"name": "middle", "page": 50}
    print(dict_temp)
    # 字典内容变为：
    # {'chapter1': {'name': 'basic', 'page': 31},
    # 'chapter2': {'name': 'senior', 'page': 42},
    # 'chapter3': {'name': 'middle', 'page': 50}}

    # 删除字典
    # del dict_temp['chapter2']['name'] #删除某个元素
    # dict_temp.clear()#{} #清空字典
    # del dict_temp  #删除字典

    # 字典操作函数和方法
    print(dict_temp.keys())
    # 返回keys结果：dict_keys(['chapter1', 'chapter2', 'chapter3'])
    print(dict_temp.values())
    # 返回values结果：dict_values([{'name': 'basic', 'page': 31}, {'name': 'senior', 'page': 42}, {'name': 'middle', 'page': 50}])
    print(dict_temp.items())
    # 返回items结果：dict_items([('chapter1', {'name': 'basic', 'page': 31}), ('chapter2', {'name': 'senior', 'page': 42}), ('chapter3', {'name': 'middle', 'page': 50})])

    print("************************************")

# 2.3.2动态类型的特性
if False:
    print("************************************")
    # int
    i = 5
    print(i)  # 结果为：5
    print(hex(id(i)))  # 结果为：0x10b6594c0
    # 重新创建值为6的int对象
    i += 1
    print(i)  # 结果为：6
    print(hex(id(i)))  # 结果为：0x10b6594e0
    # 指向数值5的内存地址
    j = 5
    print(j)  # 结果为：5
    print(hex(id(j)))  # 结果为：0x10b6594c0

    # float相同
    i = 1.5
    print(i)  # 结果为：1.5
    print(hex(id(i)))  # 结果为：0x10d81d780

    i += 1
    print(i)  # 结果为：2.5
    print(hex(id(i)))  # 结果为：0x10d81d600

    j = 1.5
    print(j)  # 结果为：1.5
    print(hex(id(j)))  # 结果为：0x10d81d780

    print("************************************")
    # list
    i = [1, 2, 3]
    print(i)  # 结果为：[1, 2, 3]
    print(hex(id(i)))  # 结果为：0x10b91e7c8

    # 验证容器对象包含的是指向各个元素对象的引用
    print(hex(id(i[0])))  # 结果为：0x10a2f0440
    print(hex(id(1)))  # 结果为：0x10a2f0440

    # append后仍指向同一内存地址
    i.append(4)
    print(i)  # 结果为：[1, 2, 3, 4]
    print(hex(id(i)))  # 结果为：0x10b91e7c8

    # j、k的值虽然相同，但指向的内存地址却不同
    j = [1.5, 2.5, 3.5]
    print(j)  # 结果为：[1.5, 2.5, 3.5]
    print(hex(id(j)))  # 结果为：0x10d81c548
    k = [1.5, 2.5, 3.5]
    print(k)  # 结果为：[1.5, 2.5, 3.5]
    print(hex(id(k)))  # 结果为：0x10d7dac48

    # 赋值语句让j、k指向同一个内存地址
    j = k
    print(j)  # 结果为：[1.5, 2.5, 3.5]
    print(hex(id(j)))  # 结果为：0x10d7dac48
    print(k)  # 结果为：[1.5, 2.5, 3.5]
    print(hex(id(k)))  # 结果为：0x10d7dac48

    # j、k任意一个list变量修改，会影响另外一个list变量的值
    j.append(4)
    print(j)  # 结果为：[1.5, 2.5, 3.5, 4]
    print(hex(id(j)))  # 结果为：0x10d7dac48
    print(k)  # 结果为：[1.5, 2.5, 3.5, 4]
    print(hex(id(k)))  # 结果为：0x10d7dac48

    # Python3.7 string
    s1 = "a" * 20
    s2 = "a" * 20
    print(hex(id(s1)), hex(id(s2)))  # 结果为：0x10b7f6540 0x10b7f6540

    s1 = "a" * 21
    s2 = "a" * 21
    print(hex(id(s1)), hex(id(s2)))  # 结果为：0x10b921348 0x10b921348

# 2.3.3 内存管理与回收
if False:
    # 验证引用计数
    import sys

    print(sys.getrefcount(1921))  # 3
    getre_val_1 = 1921
    print(sys.getrefcount(1921))  # 4
    getre_val_2 = getre_val_1
    print(sys.getrefcount(1921))  # 5
    getre_val_3 = [1921, 1922, 1923]
    print(sys.getrefcount(1921))  # 6

    getre_val_3[0] = 1924
    print(sys.getrefcount(1921))  # 5
    del getre_val_1  # 执行del getre_val_1语句后从当前名称空间中删除getre_val_1
    print(sys.getrefcount(1921))  # 4
    getre_val_2 = 1924
    print(sys.getrefcount(1921))  # 3

# 2.4 如何正确地创建函数
if False:
    # 2.4.1 def关键字定义函数
    print("***********# def关键字定义函数 *************")

    def stock_info(name):
        """内部代码块"""
        print("this stock is：" + name)

    stock_info("新希望")
    # 输出结果：this stock is：新希望

    def stock_info_1(name, close, open):
        print(name, close, open)

    # 位置实参
    stock_info_1("新希望", 11.5, 11.8)
    # 输出结果：新希望 11.5 11.8

    # 关键字实参
    stock_info_1(name="新希望", open=11.8, close=11.5)

    # 位置实参和关键字实参混合使用
    stock_info_1("新希望", open=11.8, close=11.5)

    def stock_info_2(name, open, close=11.5):
        print(name, open, close)

    # 调用时更改默认值
    stock_info_2("新希望", 11.8, 12)
    # 输出结果：新希望 11.8 12

    # 指定形参的默认值
    stock_info_2("新希望", 11.8)
    # 输出结果：新希望 11.8 11.5

    def stock_info_3(name, open, close=11.5, *args, **kwargs):

        print("name=", name)
        print("open=", open)
        print("close=", close)

        print("args=", args)
        print("kwargs=", kwargs)

        for i, element in enumerate(args):
            print("args %d-->%s" % (i, str(element)))

        for key in kwargs:
            print("kwargs %s-->%s" % (key, kwargs[key]))

    stock_info_3("新希望", 11.8, 12, 14, 16, 17)
    # 输出结果：
    """
    name= 新希望
    open= 11.8
    close= 12
    args= (14, 16, 17)
    kwargs= {}
    args 0-->14
    args 1-->16
    args 2-->17
    """

    stock_info_3("新希望", 11.8, 14, 16, 17, ave=12, high=15, low=2)
    # 输出结果：
    """
    name= 新希望
    open= 11.8
    close= 14
    args= (16, 17)
    kwargs= {'ave': 12, 'high': 15, 'low': 2}
    args 0-->16
    args 1-->17
    kwargs ave-->12
    kwargs high-->15
    kwargs low-->2
    """

    aTuple = (16, 17)  # or [16, 17]
    aDict = {"ave": 12, "high": 15, "low": 2}

    stock_info_3("新希望", 11.8, 14, *aTuple, **aDict)
    # 输出结果：
    """
    name= 新希望
    open= 11.8
    close= 14
    args= (16, 17)
    kwargs= {'ave': 12, 'high': 15, 'low': 2}
    args 0-->16
    args 1-->17
    kwargs ave-->12
    kwargs high-->15
    kwargs low-->2
    """

    stock_info_3("新希望", 11.8, 14, aTuple, aDict)
    # 输出结果：
    """
    name= 新希望
    open= 11.8
    close= 14
    args= ((16, 17), {'ave': 12, 'high': 15, 'low': 2})
    kwargs= {}
    args 0-->(16, 17)
    args 1-->{'ave': 12, 'high': 15, 'low': 2}
    """

# 2.5 初识Python面向对象
if False:
    print("**********1.面向对象的机制**************")
    # 1.面向对象的机制
    # 1.2 '元类'和'类'及'object'和'type'的关系
    print("**********1.2 '元类'和'类'及'object'和'type'的关系**************")
    # __bases__查看list的父类
    print(list.__bases__)  # 结果：(<type 'object'>,)

    mylist = [1, 2, 3]
    # __class__查看mylist的类
    print(mylist.__class__)  # 结果： <type 'list'>

    # __bases__查看mylist的父类
    # print(mylist.__bases__) #结果：AttributeError: 'list' object has no attribute '__bases__'

    # __class__查看list的类
    print(list.__class__)  # 结果：<type 'type'>

    print("************************************")

    # object是type的实例
    print(object.__class__)  # 结果： <type 'type'>
    print(type(object))  # type()方法可获取对象的类型 结果：<type 'type'>
    # type本身也是自己的实例
    print(type.__class__)  # 结果：<type 'type'>

    # object是type的父类
    print(type.__bases__)  # 结果：(<type 'object'>,)
    # object自身并没有父类
    print(object.__bases__)  # 结果：()

    print("***********1.3 经典类classic classes和新式类new-style classes的区别**********")

    # 1.3 经典类classic classes和新式类new-style classes的区别

    # Python3.7  class C ：<type 'type'>的实例；<type 'object'>的子类
    class C:
        pass

    print(C.__class__)  # 结果： <type 'type'>
    print(C.__bases__)  # 结果：(<type 'object'>,)

    # Python2.7
    # class C类型为老式的classobj
    class C:
        pass

    print(type(C))  # 结果： <type 'classobj'>

    # class C显式继承'object'，成为新式类
    class C(object):
        pass

    print(type(C))  # 结果： <type 'type'>

# 2.6 如何用面向对象思维编程
if False:
    print("***********# 如何正确地构建类 *************")
    # 定义类Human Class
    class Human(object):

        century = 21

        def __init__(self, name, age):
            self.name = name
            self.age = age
            print("init work")

        def speak(self, language):
            print("%s has speak %s ability" % (self.name, language))

        def write(self, word):
            print("%s has write %s ability" % (self.name, word))

        def walk(self):
            print("%s has walk ability" % self)

    print(Human.__bases__)  # __bases__属性列出其基类 (<class 'object'>,)

    print("***********# 类与实例的联系及区别 *************")

    Allen = Human("Allen-Cart", 16)  # 输出结果：init work
    print(Allen.name, Allen.age)  # 输出结果：Allen-Cart 16

    print(Allen.speak, Allen.write, Allen.walk)
    # <bound method Human.speak of <__main__.Human object at 0x10ab50160>>
    # <bound method Human.write of <__main__.Human object at 0x10ab50160>>
    # <bound method Human.walk of <__main__.Human object at 0x10ab50160>>

    print(Human.speak, Human.write, Human.walk)
    # <function Human.speak at 0x110ba5378>
    # <function Human.write at 0x110ba5400>
    # <function Human.walk at 0x110ba5488>

    Allen.speak("Chinese")  # Allen-Cart has speak Chinese ability
    Allen.write("Chinese")  # Allen-Cart has write Chinese ability
    Allen.walk()  # <__main__.Human object at 0x10ab50160> has walk ability.

    Human.walk("James")  # James has walk ability

    from types import FunctionType, MethodType

    # isinstance() 函数判断一个对象是否是一个已知的类型
    print(isinstance(Human.walk, FunctionType))  # True
    print(isinstance(Allen.walk, MethodType))  # True

    print(Human.__dict__)
    """
    {'__module__': '__main__', 
    'century': 21, 
    '__init__': <function Human.__init__ at 0x106b4e2f0>, 
    'speak': <function Human.speak at 0x106b4e378>, 
    'write': <function Human.write at 0x106b4e400>, 
    'walk': <function Human.walk at 0x106b4e488>, 
    '__dict__': <attribute '__dict__' of 'Human' objects>, 
    '__weakref__': <attribute '__weakref__' of 'Human' objects>, '__doc__': None}
    """

    print(Allen.__dict__)
    """
    {'name': 'Allen-Cart', 'age': 16}
    """

    print(Human.century)  # 通过类访问 结果为：21
    print(Allen.century)  # 通过实例访问 结果为：21

    Human.century += 1  # 通过类更新
    print(Human.century)  # 结果为：22
    print(Allen.century)  # 实例访问 值已被改变 结果为：22

    Allen.century += 1  # 通过实例更新
    print(Allen.century)  # 实例访问 值已被改变 结果为：23
    print(Human.century)  # 类访问 值未改变 结果为：22

    print(Allen.__dict__)
    """
    {'name': 'Allen-Cart', 'age': 16, 'century': 23}
    """

    del Allen.century  # 删除实例属性
    print(Allen.century)  # 实例访问 访问到类属性 结果为：22

    # 定义类Human_A Class
    class Human_A(object):

        century = {"A": 21}

        def __init__(self, name, age):
            self.name = name
            self.age = age
            print("init work")

        def speak(self, language):
            print("%s has speak %s ability" % (self.name, language))

        def write(self, word):
            print("%s has write %s ability" % (self.name, word))

        def walk(self):
            print("%s has walk ability" % self)

    Jahn = Human_A("Jahn-Cart", 22)  # 输出结果：init work

    # 可变变量的类属性 访问
    print(Human_A.century)  # 通过类访问 结果为：{'A': 21}
    print(Jahn.century)  # 通过实例访问 结果为：{'A': 21}

    Jahn.century["B"] = "32"  # 通过实例更新

    print(Human_A.century)  # 类访问 值已被改变 结果为：{'A': 21, 'B': '32'}
    print(Jahn.century)  # 实例访问 值已被改变 结果为：{'A': 21, 'B': '32'}

    # 定义类Human_B Class
    class Human_B(object):

        century = 21
        name = "Allen"

        def __init__(self, name, age):
            self.name = name
            self.age = age
            print("init work")

        @staticmethod
        def speak(language):
            print("%s has speak %s ability" % (Human_B.name, language))

        def write(self, word):
            print("%s has write %s ability" % (self.name, word))

        @classmethod
        def walk(cls):
            print("%s has walk ability" % cls.name)

    Human_B.speak("Chinese")  # 结果为：Allen has speak Chinese ability
    Human_B.walk()  # 结果为：Allen has walk ability

    class Programmer(Human):
        def __init__(self, name, age, language, tool):
            Human.__init__(self, name, age)
            self.language = language
            self.tool = tool
            print("init programmer")

        def develop(self):
            print("%s has develop ability" % self.name)

        def speech(self):
            print("%s has speech ability" % self.name)

    print(Programmer.__bases__)  # __bases__属性列出其基类 (<class '__main__.Human'>,)

    Michael = Programmer("Michael-wang", 16, "JAVA", "computer")
    #  结果为：init work  init programmer

    print(
        Michael.century, Michael.name, Michael.age, Michael.language, Michael.tool
    )  # 结果为：22 Michael-wang 16 JAVA computer
    Michael.speak("Chinese")  # 结果为：Michael-wang has speak Chinese ability
    Michael.write("Chinese")  # 结果为：Michael-wang has write Chinese ability
    Michael.develop()  # 结果为：Michael-wang has develop ability
    Michael.speech()  # 结果为：Michael-wang has speech ability

    # 创建Computer类
    class Computer:
        def __init__(self, model, brand):
            self.model = model
            self.brand = brand

        def open_sys(self):
            print("%s has been opened" % self.model)

        def close_sys(self):
            print("%s has been closed" % self.model)

    # Programmer增加Computer属性
    Jack = Programmer("Jack", 21, "China", Computer("X10", "dell"))
    print(Jack.tool.model, Jack.tool.brand)  # 结果为：X10 dell
    Jack.tool.open_sys()  # 调用Computer的方法 结果为：X10 has been opened
    Jack.tool.close_sys()  # 调用Computer的方法 结果为：X10 has been closed


# 2.7 深入for_in循环
if False:
    print("***********# 深入for_in循环遍历结构 *************")

    # 比较 while 和 for in 循环的效率
    import time

    start_w = time.perf_counter()
    s, i = 0, 0
    while i < 10000:
        i = i + 1
        s = s + i
    end_w = time.perf_counter()
    print("Time while：", end_w - start_w)  # talib time consuming

    start_f = time.perf_counter()
    s = 0
    for i in range(1, 10001):
        s = s + i
    end_f = time.perf_counter()
    print("Time for：", end_f - start_f)  # Pandas time consuming

    # 单步的方式模拟迭代的过程
    x = [1, 2, 3]
    its = x.__iter__()  # 列表是可迭代对象，否则会提示不是迭代对象
    print(its)  #  返回 <list_iterator object at 0x100bde400>
    print(next(its))  # its包含next()方法，说明its是迭代器  返回 1
    print(next(its))  #  返回 2
    print(next(its))  # 返回 3
    # print(next(its))
    # Traceback (most recent call last):
    # File "<stdin>", line 1, in <module>
    # StopIteration

    # 实现可迭代对象
    class MyRange:
        def __init__(self, num):
            self.i = 0
            self.num = num

        def __iter__(self):
            return self

        def __next__(self):
            if self.i < self.num:
                i = self.i
                self.i += 1
                return i
            else:
                raise StopIteration()

    for i in MyRange(6):
        print(i)  # 返回 0 1 2 3 4 5

    ###############################遍历一个范围内的数字###############################
    print("*********** 遍历一个范围内的数字 *************")
    for i in range(6):
        print(i)  # 返回 0 1 2 3 4 5

    ###############################正向遍历/反向遍历一个集合###############################
    print("*********** 正向遍历/反向遍历一个集合 *************")
    colors = ["red", "green", "blue", "yellow"]
    # 正向遍历
    for i in range(len(colors)):
        print(colors[i])
    # 推荐更好的简练方法
    for color in colors:
        print(color)  # 返回 'red', 'green', 'blue', 'yellow'

    # 反向遍历
    for i in range(len(colors) - 1, -1, -1):
        print(colors[i])
    # 推荐更好的简练方法
    for color in reversed(colors):
        print(color)  # 返回 'yellow', 'blue', 'green', 'red'

    ###############################遍历一个集合及其下标###############################
    print("*********** 遍历一个集合及其下标 *************")
    colors = ["red", "green", "blue", "yellow"]
    for i in range(len(colors)):
        print(i, "--->", colors[i])
    # 推荐更好的简练方法
    for i, color in enumerate(colors):
        print(i, "--->", color)
    # 返回结果：
    # 0 ---> red
    # 1 ---> green
    # 2 ---> blue
    # 3 ---> yellow
    ###############################遍历两个集合###############################
    print("*********** 遍历两个集合 *************")
    names = ["raymond", "rachel", "matthew"]
    colors = ["red", "green", "blue", "yellow"]

    print(zip(names, colors))  # 返回是一个对象 <zip object at 0x102234388>
    print(
        list(zip(names, colors))
    )  # list()转换为列表 [('raymond', 'red'), ('rachel', 'green'), ('matthew', 'blue')]

    n = min(len(names), len(colors))
    for i in range(n):
        print(names[i], "--->", colors[i])
    # 推荐更好的简练方法
    for name, color in zip(names, colors):
        print(name, "--->", color)
    # 返回结果：
    # raymond ---> red
    # rachel ---> green
    # matthew ---> blue

    ###############################有序地遍历###############################
    print("*********** 有序地遍历 *************")
    colors = [("red", 1), ("green", 3), ("blue", 5), ("yellow", 2)]
    # 正序 key=none
    for color in sorted(colors):
        print(color)
    # 返回结果：
    # ('blue', 5)
    # ('green', 3)
    # ('red', 1)
    # ('yellow', 2)

    # 正序 key=lambda s:s[1]
    for color in sorted(colors, key=lambda s: s[1]):
        print(color)
    # 返回结果：
    # ('red', 1)
    # ('yellow', 2)
    # ('green', 3)
    # ('blue', 5)

    # 倒序 key=none
    for color in sorted(colors, reverse=True):
        print(color)
    # 返回结果：
    # ('yellow', 2)
    # ('red', 1)
    # ('green', 3)
    # ('blue', 5)

    # 倒序 key=lambda s:s[1]
    for color in sorted(colors, key=lambda s: s[1], reverse=True):
        print(color)
    # 返回结果：
    # ('blue', 5)
    # ('green', 3)
    # ('yellow', 2)
    # ('red', 1)

    ###############################在循环内识别多个退出点############################
    print("*********** 在循环内识别多个退出点 *************")

    def find(seq, target):
        found = False
        for i, value in enumerate(seq):
            if value == target:
                found = True
                break
        if not found:
            return -1
        return i

    print(find(range(10, 20), 15))  # 5

    # 推荐更好的简练方法
    def find(seq, target):
        for i, value in enumerate(seq):
            if value == target:
                break
        else:
            return -1
        return i

    print(find(range(10, 20), 30))  # -1

    ###############################遍历字典的key###############################
    print("*********** 遍历字典的key *************")
    d = {"matthew": "blue", "rachel": "green", "raymond": "red"}

    for k in d.keys():
        print(k)
    # 返回结果
    # matthew
    # rachel
    # raymond

    for k in d.values():
        print(k)
    # 返回结果
    # blue
    # green
    # red

    for k in d.items():
        print(k)
    # 返回结果
    # ('matthew', 'blue')
    # ('rachel', 'green')
    # ('raymond', 'red')

    for k, v in d.items():
        print(k, "--->", v)
    # 返回结果
    # matthew ---> blue
    # rachel ---> green
    # raymond ---> red

    print(d.keys())  # dict_keys(['matthew', 'rachel', 'raymond'])
    print(list(d.keys()))  # ['matthew', 'rachel', 'raymond']

    # for k in d.keys():
    #    if k.startswith('r'):
    #        del d[k]
    # RuntimeError: dictionary changed size during iteration

    for k in list(d.keys()):
        if k.startswith("r"):
            del d[k]
    ###############################列表解析和生成器###############################
    # 列表解析对比例程
    def num():
        a = []
        for i in range(10):
            a.append(i)
        return a

    print(num())

    a = [x for x in range(10)]  # 结果返回：[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    print(a)

    # 函数方式实现生成器
    def gensquares(N):
        for i in range(N):
            yield i ** 2

    print(gensquares(5))  # 结果返回：<generator object gensquares at 0x10ae3a7c8>
    for i in gensquares(5):
        print(i)
    # 返回结果
    # 0
    # 1
    # 4
    # 9
    # 16
    # 表达式方式实现生成器
    print(x ** 2 for x in range(5))  # 结果返回：<generator object <genexpr> at 0x10e2f57c8>
    print(list(x ** 2 for x in range(5)))  # 结果返回：[0, 1, 4, 9, 16]

    a = (x ** 2 for x in range(5))
    print(a)  # <generator object <genexpr> at 0x10e2f57c8>
    # next迭代一次生成一个元素
    print(next(a))  # 0
    print(next(a))  # 1
    print(next(a))  # 4

    print("***********#    *************")

# 2.8 巧用装饰器测试代码效率
if False:
    print("***********# 巧用装饰器测试代码效率 *************")

    import time
    from timeit import timeit
    from timeit import repeat

    current = "part2"
    if current == "part1":
        # part1
        # 创建一个元素为递增的整数列表
        def for_generate_list(size=1000000):
            start = time.perf_counter()
            my_list = []
            for num in range(size):
                my_list.append(num)
            elapsed = time.perf_counter() - start
            print("Time used: {} ".format(elapsed))

        # 调用函数打印结果：
        for_generate_list()  # Time used: 0.09452888500000003

    elif current == "part2":
        # part2
        # 创建一个元素为递增的整数列表——待测试的函数
        def for_generate_list(size=1000000):
            my_list = []
            for num in range(size):
                my_list.append(num)

        # stmt 需要测试的函数或语句，字符串形式
        # setup 运行的环境，本例子中表示 if __name__ == '__main__':
        # number 被测试的函数或语句，执行的次数，本例表示执行1次for_generate_list()。省缺则默认是10000次
        # 综上：此函数表示在if __name__ == '__main__'的条件下，执行1次for_generate_list()消耗的时间
        elapsed = timeit(
            stmt="for_generate_list()",
            setup="from __main__ import for_generate_list",
            number=1,
        )
        print("Time used:", elapsed)  # 打印结果：Time used: 0.10997585000000004

        t_elapsed = repeat(
            stmt="for_generate_list()",
            setup="from __main__ import for_generate_list",
            number=1,
            repeat=5,
        )
        print(
            "Time used:", t_elapsed
        )  # 打印结果：Time used: [0.10610366399999999, 0.11713108100000003, 0.12187103300000002, 0.105048064, 0.107227619]
        print("Time of min used:", min(t_elapsed))  # 打印结果：Time of min used: 0.105048064

    elif current == "part3":
        # part3
        # 定义测试代码执行时间的装饰器-二阶
        def timeit_test(func):
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                print("Time used: {} ".format(elapsed))

            return wrapper

        @timeit_test
        def for_generate_list(size=1000000):
            print("list size is: {} ".format(size))
            my_list = []
            for num in range(size):
                my_list.append(num)

        for_generate_list(1000000)
        # list size is: 1000000
        # Time used: 0.10935139800000002
        print(
            "func name is {}:".format(for_generate_list.__name__)
        )  # func name is wrapper:

    elif current == "part4":
        # part4
        # 定义测试代码执行时间的装饰器-三阶
        def timeit_test(number=3, repeat=3):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    for i in range(repeat):
                        start = time.perf_counter()
                        for _ in range(number):
                            func(*args, **kwargs)
                        elapsed = time.perf_counter() - start
                        print("Time of {} used: {} ".format(i, elapsed))

                return wrapper

            return decorator

        @timeit_test(number=2, repeat=2)
        def for_generate_list(size=1000000):
            print("list size is: {} ".format(size))
            my_list = []
            for num in range(size):
                my_list.append(num)

        for_generate_list(900000)
        # list size is: 900000
        # list size is: 900000
        # Time of 0
        # used: 0.19475456300000002
        # list size is: 900000
        # list size is: 900000
        # Time of 1
        # used: 0.192571865
        print(
            "func name is {}:".format(for_generate_list.__name__)
        )  # func name is wrapper:

    elif current == "part5":
        # part5
        import functools

        # 定义测试代码执行时间的装饰器-三阶
        def timeit_test(number=3, repeat=3):
            def decorator(func):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    for i in range(repeat):
                        start = time.perf_counter()
                        for _ in range(number):
                            func(*args, **kwargs)
                        elapsed = time.perf_counter() - start
                        print("Time of {} used: {} ".format(i, elapsed))

                return wrapper

            return decorator

        @timeit_test(number=2, repeat=2)
        def for_generate_list(size=1000000):
            print("list size is: {} ".format(size))
            my_list = []
            for num in range(size):
                my_list.append(num)

        for_generate_list(size=900000)
        # list size is: 900000
        # list size is: 900000
        # Time of 0 used: 0.192424283
        # list size is: 900000
        # list size is: 900000
        # Time of 1 used: 0.19034953399999993

    print(
        "func name is {}:".format(for_generate_list.__name__)
    )  # func name is for_generate_list:

    print("***********#   *************")

# 2.9 多进程和多线程的提速方案
if False:
    print("***********# 多进程和多线程的提速方案 *************")
    from threading import Thread
    from multiprocessing import Process
    from timeit import timeit
    import time

    current = "IO"

    if current == "CPU":
        # CPU密集型任务
        def count(n):
            while n > 0:
                n -= 1

        # 单线程方式
        def test_normal():
            count(1000000)
            count(1000000)

        # 多线程方式
        def test_Thread():
            t1 = Thread(target=count, args=(1000000,))
            t2 = Thread(target=count, args=(1000000,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()

        # 多进程方式
        def test_Process():
            t1 = Process(target=count, args=(1000000,))
            t2 = Process(target=count, args=(1000000,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()

        if __name__ == "__main__":
            print(
                "test_normal",
                timeit("test_normal()", "from __main__ import test_normal", number=30),
            )
            print(
                "test_Process",
                timeit(
                    "test_Process()", "from __main__ import test_Process", number=30
                ),
            )
            print(
                "test_Thread",
                timeit("test_Thread()", "from __main__ import test_Thread", number=30),
            )

    elif current == "IO":
        # IO密集型任务
        def count():
            time.sleep(0.01)

        # 单线程方式
        def test_normal():
            count()
            count()

        # 多线程方式
        def test_Thread():
            t1 = Thread(target=count, args=())
            t2 = Thread(target=count, args=())
            t1.start()
            t2.start()
            t1.join()
            t2.join()

        # 多进程方式
        def test_Process():
            t1 = Process(target=count, args=())
            t2 = Process(target=count, args=())
            t1.start()
            t2.start()
            t1.join()
            t2.join()

        if __name__ == "__main__":
            print(
                "test_normal",
                timeit("test_normal()", "from __main__ import test_normal", number=100),
            )
            print(
                "test_Process",
                timeit(
                    "test_Process()", "from __main__ import test_Process", number=100
                ),
            )
            print(
                "test_Thread",
                timeit("test_Thread()", "from __main__ import test_Thread", number=100),
            )

    print("***********#   *************")

# 2.10 未雨绸缪的异常处理机制
if False:
    print("***********# 未雨绸缪的异常处理机制 *************")

    if False:  # 语法错误案例1
        result = var * 10
        # Traceback (most recent call last):
        # NameError: name 'var' is not defined

    if False:  # 语法错误案例2
        list_data = []
        result = list_data[2] * 10
        # Traceback (most recent call last):
        # IndexError: list index out of range

    if True:  # 语法错误案例2
        try:
            list_data = []
            result = var * 10
            result = list_data[2] * 10
        except NameError:
            print("NameError is happened！")
        except IndexError:
            print("IndexError is happened！")
        except Exception:
            print("Other except is happened！")

    if False:  # 语法错误案例3
        try:
            list_data = []
            result = var * 10
            result = list_data[2] * 10
        except (NameError, IndexError):
            print("NameError or IndexError is happened！")
        except Exception:
            print("Other except is happened！")

    if False:  # 语法错误案例4
        try:
            list_data = []
            result = var * 10
            result = list_data[2] * 10
        except (NameError, IndexError) as e:
            print("NameError or IndexError is happened！")
            print(e.args)  # 执行提示 ("name 'var' is not defined",)
        except Exception as e:
            print("Other except is happened！")

    if False:  # 语法错误案例5
        try:
            var = 1
            list_data = [0, 1, 2]
            result = var * 10
            result = list_data[2] * 10
        except (NameError, IndexError) as e:
            print("NameError or IndexError is happened！")
            print(e.args)  # 执行提示 ("name 'var' is not defined",)
        except Exception as e:
            print("Other except is happened！")
        else:
            print("No except happened！")

    if False:  # 语法错误案例6
        try:
            var = 1
            list_data = [0, 1, 2]
            result = var * 10
            result = list_data[2] * 10
        except (NameError, IndexError) as e:
            print("NameError or IndexError is happened！")
            print(e.args)  # 执行提示 ("name 'var' is not defined",)
        except Exception as e:
            print("Other except is happened！")
        else:
            result = 1 + "quant"
            # Traceback (most recent call last):
            # TypeError: unsupported operand type(s) for +: 'int' and 'str'

    if True:  # 语法错误案例7
        try:
            f = open("code.txt", "w")
            result = var * 10
            result = list_data[2] * 10
        except (NameError, IndexError) as e:
            print("NameError or IndexError is happened！")
            print(e.args)  # 执行提示 ("name 'var' is not defined",)
        except Exception as e:
            print("Other except is happened！")
        finally:
            print("finally file close！")
            f.close()

    print("***********#    *************")
