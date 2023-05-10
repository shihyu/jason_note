# 定义递归函数myn()
def myn(n):
    if n == 0 or n == 1:
        result = 1
    else:
        result = myn(n - 1) * n  # 递归调用
    return result


# 调用函数
print("递归函数的返回值：", myn(8))
