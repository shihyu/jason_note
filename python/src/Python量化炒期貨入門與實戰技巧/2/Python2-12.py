str = "how are you?"
print("将字符串的第一个字符转换为大写: ", str.capitalize())
str = "www.baidu.com"
print("指定的宽度50并且居中的字符串: ", str.center(50, "*"))
str = "www.qq.com"
sub = "q"
print("返回字符串中某字符出现的次数: ", str.count(sub))
print()
str = "this is\tstring example....wow!!!"
print("原始字符串: ", str)
print("替换 \\t 符号: ", str.expandtabs())
print("使用16个空格替换 \\t 符号: ", str.expandtabs(16))
print()
str1 = "I like python!"
str2 = "pyth"
print("在str1字符串中查找str2:", str1.find(str2))
print("在str1字符串中查找str2,从第6个字符开始:", str1.find(str2, 5))
print("在str1字符串中查找str2,从第11个字符开始:", str1.find(str2, 10))
print()
str = "qd2019"  # 字符串只有字母和数字
print(str.isalnum())
str = "www.163.com"  # 字符串除了字母和数字，还有小数点
print(str.isalnum())
str = "python"  # 字符串只有字母
print(str.isalpha())
str = "www.baidu.com"  # 字符串除了字母，还有别的字符
print(str.isalpha())
str = "123456"  # 字符串只有数学
print(str.isdigit())
str = "I like python!"
print(str.isdigit())
str = "GOOD,python"  # 字符串有大写定母
print(str.islower())
str = "good,python"  # 字符串只有小写定母
print(str.islower())
str = "       "  # 字符串中只包含空白
print(str.isspace())
str = "I like python!"
print(str.isspace())
str = "I LIKE PYTHON"  # 字符串只有大写定母
print(str.isupper())
str = "I Like Python!"
print(str.isupper())
print()
s1 = "-"
s2 = ""
seq = ("p", "y", "t", "h", "o", "n")  # 字符串序列
print(s1.join(seq))
print(s2.join(seq))
print()
str = "python"
print("字符串长度:", len(str))  # 字符串长度
l = [1, 2, 3, 4, 5]
print("列表元素个数:", len(l))  # 列表元素个数
print()
str = "I like python!"
print("左对齐：", str.ljust(50, "*"))
print("右对齐：", str.rjust(50, "*"))
print()
str = "     I like python!     "
print("删除字符串左边的空格：", str.lstrip())
print("删除字符串右边的空格：", str.rstrip())
print("删除字符串左右两边的空格：", str.strip())
print()
str = "python"
print("最大字符: " + max(str))
print("最小字符: " + min(str))
str = "www.qdlike.com"
print("网站原来的网址：", str)
print("网站新的网址：", str.replace("www.qdlike.com", "www.chinalike.com"))
str = "I like python!"
print(str.split())
print("ab c\n\nde fg\rkl\r\n".splitlines())
print()
str = "I like python!"
print("将字符串中大写转换为小写，小写转换为大写:", str.swapcase())
print("转换字符串中的小写字母为大写: ", str.upper())
print("转换字符串中的大写字母为小写: ", str.lower())
