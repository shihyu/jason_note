import os, glob, sys, re, math, random, datetime, zlib

print("当前的工作目录:", os.getcwd())
print()
print("当前目录下所有以py为后缀的文件：", glob.glob("*.py"))
print()
print("当前文件的路径及名称：", sys.argv)
print("显示字母f开头的单词：", re.findall(r"\bf[a-z]*", "which foot or hand fell fastest"))
print("调用数学math函数，计算cos(math.pi / 4)的值：", math.cos(math.pi / 4))
print("调用random函数，显示0~1之间的随机数:", random.random())
print("当前的日期和时间是 %s" % datetime.datetime.now())
print(
    "没有压缩之前的长度和压缩之后的长度：",
    len(b"witch which has which witches wrist watch!"),
    len(zlib.compress(b"witch which has which witches wrist watch!")),
)
