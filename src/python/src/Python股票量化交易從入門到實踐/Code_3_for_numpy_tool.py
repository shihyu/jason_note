#! /usr/bin/env python
# -*- encoding: utf-8 -*-

"""
书籍《Python股票量化交易入门到实践 》案例例程
仅用于教学目的，严禁转发和用于盈利目的，违者必究
通过if True/False 语句 开关所要调试的例程
"""

# 第三章 第三方库Numpy快速入门

import numpy as np

print(np.__version__)  # 1.15.1


# 3.1 初识N维数组对象
if False:
    array_1x6 = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], dtype=np.float64)
    print(array_1x6)
    """
    [1. 2. 3. 4. 5. 6.]
    """
    print(array_1x6.ndim)  # 1
    print(array_1x6.shape)  # (6,)
    print(array_1x6.dtype)  # float64

    array_2x6 = np.array(
        [[1.0, 2.0, 3.0, 4.0, 5.0, 6.0], [1.1, 2.1, 3.1, 4.1, 5.1, 6.1]]
    )
    print(array_2x6)
    """
    [[1.  2.  3.  4.  5.  6. ]
     [1.1 2.1 3.1 4.1 5.1 6.1]]
    """
    print(array_2x6.ndim)  # 2
    print(array_2x6.shape)  # (2, 6)
    print(array_2x6.dtype)  # float64

    array_2x3x6 = np.array(
        [
            [
                [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
                [1.1, 2.1, 3.1, 4.1, 5.1, 6.1],
                [1.2, 2.2, 3.2, 4.2, 5.2, 6.2],
            ],
            [
                [7.0, 8.0, 9.0, 10.0, 11.0, 12.0],
                [7.1, 8.1, 9.1, 10.1, 11.1, 12.1],
                [7.2, 8.2, 9.2, 10.2, 11.2, 12.2],
            ],
        ]
    )
    print(array_2x3x6)
    """
    [[[ 1.   2.   3.   4.   5.   6. ]
      [ 1.1  2.1  3.1  4.1  5.1  6.1]
      [ 1.2  2.2  3.2  4.2  5.2  6.2]]
      
     [[ 7.   8.   9.  10.  11.  12. ]
      [ 7.1  8.1  9.1 10.1 11.1 12.1]
      [ 7.2  8.2  9.2 10.2 11.2 12.2]]]
    """
    print(array_2x3x6.ndim)  # 3
    print(array_2x3x6.shape)  # (2, 3, 6)
    print(array_2x3x6.dtype)  # float64

# 3.2 N维数组对象特性 矢量运算和广播特性
if False:
    # Python for...in 循环
    list_4x3_a = [[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]]
    list_4x3_b = [[5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5]]
    list_4x3_c = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]

    for i in range(4):
        for j in range(3):
            list_4x3_c[i][j] = list_4x3_a[i][j] + list_4x3_b[i][j]
    print(list_4x3_c)  # [[6, 6, 6], [7, 7, 7], [8, 8, 8], [9, 9, 9]]

    # Numpy 矢量化运算——表达式
    array_4x3_a = np.array(
        [[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]]
    )  # 创建'numpy.ndarray'多维数组
    array_4x3_b = np.array([[5, 5, 5], [5, 5, 5], [5, 5, 5], [5, 5, 5]])
    print(array_4x3_a + array_4x3_b)
    """
    [[6 6 6]
     [7 7 7]
     [8 8 8]
     [9 9 9]]
    """

    # Numpy 广播特性——标量
    print(array_4x3_a + 5)
    """
    [[6 6 6]
     [7 7 7]
     [8 8 8]
     [9 9 9]]    
    """

    # Numpy 广播特性——兼容规则
    array_4x3 = np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]])
    array_1x3 = np.array([1, 2, 3])
    print(array_4x3 + array_1x3)
    """
    [[2 3 4]
     [3 4 5]
     [4 5 6]
     [5 6 7]]
    """

    array_4x3 = np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]])
    print(array_4x3)
    """
    [[1 1 1]
     [2 2 2]
     [3 3 3]
     [4 4 4]]
    """
    array_2x1 = np.array([[1], [1]])
    print(array_2x1)
    """
    [[1]
     [1]]    
    """
    # print(array_4x3 + array_2x1)
    # ValueError: operands could not be broadcast together with shapes (4,3) (2,1)
    array_4x3 = np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]])
    array_4x1 = np.array([[1], [1], [1], [1]])
    print(array_4x1)
    """
    [[1]
     [1]
     [1]
     [1]]    
    """
    print(array_4x3 + array_4x1)
    """
    [[2 2 2]
     [3 3 3]
     [4 4 4]
     [5 5 5]]
    """

# 3.3 高效处理的性能对比
if False:
    # 引用于2.6.2小节
    import functools, time

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

        # 测试Numpy数组和等价的Python列表性能差距

    if False:

        @timeit_test(number=1, repeat=1)
        def list_test():
            my_list = list(range(1000000))

        @timeit_test(number=1, repeat=1)
        def ndarray_test():
            my_arr = np.arange(1000000)

        list_test()  # Time of 0 used: 0.04712673199999998
        ndarray_test()  # Time of 0 used: 0.0014547089999999985

    else:

        @timeit_test(number=1, repeat=1)
        def list_test():
            my_list = []
            for num in range(1000000):
                my_list.append(num * 2.0)

        @timeit_test(number=1, repeat=1)
        def ndarray_test():
            my_arr = np.arange(1000000)
            my_arr = my_arr * 2.0

        list_test()  # Time of 0 used: 0.15243656000000003
        ndarray_test()  # Time of 0 used: 0.009769811999999989

    # ndarray处理数据的机制
    print(np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]]).shape)
    # (4, 3)
    print(np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]]).dtype)
    # int64
    print(np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]]).strides)
    # (24, 8)

# 条件表达式选取元素
if False:
    array_4x3 = np.array(
        [[1.1, 1.2, 1.3], [2.1, 2.2, 2.3], [3.1, 3.2, 3.3], [4.1, 4.2, 4.3]]
    )
    print(array_4x3)
    """
    [[1.1 1.2 1.3]
     [2.1 2.2 2.3]
     [3.1 3.2 3.3]
     [4.1 4.2 4.3]]
    """

    print(array_4x3[[True, False, False, False]])
    # [[1.1 1.2 1.3]]

    print(array_4x3[[True, False, False, False], 1])
    # [1.2]

    print(array_4x3 < 2)
    """
    [[ True  True  True]
     [False False False]
     [False False False]
     [False False False]]
    """
    print(array_4x3[array_4x3 < 2])
    # [1.1 1.2 1.3]

# 3.4 常用数组处理函数
if True:
    print("*****example-3.14*****")
    # ones(shape, dtype=None, order='C')
    array_one = np.ones(shape=(2, 4))
    print(array_one)
    """
    [[1. 1. 1. 1.]
     [1. 1. 1. 1.]]
    """
    print("*********************\n")

    print("*****example-3.15*****")
    # np.full(shape, fill_value, dtype=None, order=’C’)
    array_full = np.full(shape=(2, 4), fill_value=10)
    print(array_full)
    """
    [[10 10 10 10]
     [10 10 10 10]]    
    """
    print("*********************\n")

    print("*****example-3.16*****")
    # np.eye(N, M=None, k=0, dtype=float)
    array_eye = arr_eys = np.eye(4, M=6)
    print(array_eye)
    """
     [[1. 0. 0. 0. 0. 0.]
     [0. 1. 0. 0. 0. 0.]
     [0. 0. 1. 0. 0. 0.]
     [0. 0. 0. 1. 0. 0.]]   
    """
    print("*********************\n")

    print("*****example-3.17*****")
    # np.linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None) 等差数列
    # start指定开始值;stop指定终值;num指定元素个数;endpoint指定等差数列是否包含终值
    array_linspace = np.linspace(start=0, stop=5, num=10, endpoint=False)
    print(array_linspace)
    """
    [0.  0.5 1.  1.5 2.  2.5 3.  3.5 4.  4.5]
    """
    print("*********************\n")

    print("*****example-3.18*****")
    np.random.seed(1)  # 设置相同的seed 每次生成的随机数相同 便于调试
    # randint(low, high=None, size=None, dtype='l') # 指定上下限范围的随机数组
    array_randint = np.random.randint(1, 4, size=10)
    print(array_randint)
    """
    [2 1 1 2 2 1 1 2 1 2]
    """

    print("*********************\n")

    print("*****example-3.19*****")
    np.random.seed(1)  # 设置相同的seed 每次生成的随机数相同 便于调试
    # binomial(n, p, size=None) # 符合二项分布的随机数组
    array_binomial = np.random.binomial(1, 0.5, size=10)
    print(array_binomial)
    """
    [1 1 1 0 1 0 0 1 1 0]
    """
    print("*********************\n")

    print("*****example-3.20*****")
    np.random.seed(1)  # 设置相同的seed 每次生成的随机数相同 便于调试
    # randn(*dn) # 标准正态分布随机数组
    array_randn = np.random.randn(3, 4)
    print(array_randn)
    """
    [[ 1.62434536 -0.61175641 -0.52817175 -1.07296862]
     [ 0.86540763 -2.3015387   1.74481176 -0.7612069 ]
     [ 0.3190391  -0.24937038  1.46210794 -2.06014071]]    
    """
    print("*********************\n")

    print("*****example-3.21*****")
    np.random.seed(1)  # 设置相同的seed 每次生成的随机数相同 便于调试
    # rand(*dn) # 0-1之间均匀分布的随机数组
    array_rand = np.random.rand(3, 4)
    print(array_rand)
    """
    [[4.17022005e-01 7.20324493e-01 1.14374817e-04 3.02332573e-01]
     [1.46755891e-01 9.23385948e-02 1.86260211e-01 3.45560727e-01]
     [3.96767474e-01 5.38816734e-01 4.19194514e-01 6.85219500e-01]]      
    """
    print("*********************\n")

    print("*****example-3.22*****")
    np.random.seed(1)  # 设置相同的seed 每次生成的随机数相同 便于调试
    # normal(loc=0.0, scale=1.0, size=None)
    array_normal = np.random.normal(loc=10.0, scale=1.0, size=(1, 3, 2))
    print(array_normal)
    """
    [[[11.62434536  9.38824359]
      [ 9.47182825  8.92703138]
      [10.86540763  7.6984613 ]]]    
    """
    print("*********************\n")

    print("*****example-3.23*****")
    array_4x3_234 = np.array([[1, 0, 1], [-2, 2, 2], [3, -3, 3], [4, 4, -4]])
    array_sign = np.sign(array_4x3_234)
    print(array_sign)
    """
    [[ 1  0  1]
     [-1  1  1]
     [ 1 -1  1]
     [ 1  1 -1]]    
    """
    print("*********************\n")

    print("*****example-3.24*****")
    array_4x3_235 = np.array([[1, 1, 1], [-2, np.nan, 2], [3, np.nan, 3], [4, 4, -4]])
    array_isnan = np.isnan(array_4x3_235)
    print(array_isnan)
    """
    [[False False False]
     [False  True False]
     [False  True False]
     [False False False]]    
    """
    print("*********************\n")

    print("*****example-3.25*****")
    # np.where(cond,x,y)：满足条件（cond）输出x，不满足输出y
    array_4x3_236 = np.array([[1, 1, 1], [-2, 8, 2], [3, 9, 3], [4, 4, -4]])
    array_where = np.where(array_4x3_236 > 5, 5, 0)
    print(array_where)
    """
    [[0 0 0]
     [0 5 0]
     [0 5 0]
     [0 0 0]]    
    """
    print("*********************\n")


# 3.4.3 线性代数处理函数
if False:
    matrix_a = np.mat("1 3 5; 2 4 6")
    matrix_b = np.mat([[1, 3, 5], [2, 4, 6]])
    print(matrix_a)
    """
     [[1 3 5]
     [2 4 6]]   
    """
    print(matrix_b)
    """
    [[1 3 5]
     [2 4 6]]    
    """
    print(type(matrix_a))  # <class 'numpy.matrixlib.defmatrix.matrix'>
    print(type(matrix_b))  # <class 'numpy.matrixlib.defmatrix.matrix'>
    array_c = np.array([[1, 3, 5], [2, 4, 6]])
    print(array_c)
    """
    [[1 3 5]
     [2 4 6]]
    """
    print(type(array_c))  # <class 'numpy.ndarray'>

    # 构建一个4*4的随机数组
    array_1 = np.random.rand(4, 4)
    print(array_1)
    """
    [[0.75092745 0.19999372 0.91697249 0.83692052]
     [0.89880097 0.10333959 0.64811766 0.89136818]
     [0.98629936 0.10134345 0.36475073 0.03950319]
     [0.16878454 0.08078799 0.38428045 0.36453119]]
    """
    print(type(array_1))  # <class 'numpy.ndarray'>
    # 使用np.mat函数将数组转化为矩阵
    matrix_1 = np.mat(array_1)
    print(matrix_1)
    """
    [[0.75092745 0.19999372 0.91697249 0.83692052]
     [0.89880097 0.10333959 0.64811766 0.89136818]
     [0.98629936 0.10134345 0.36475073 0.03950319]
     [0.16878454 0.08078799 0.38428045 0.36453119]]
    """
    print(type(matrix_1))  # <class 'numpy.matrixlib.defmatrix.matrix'>

    A = np.mat([[1, 2], [3, 4]])
    B = np.mat([[1, 2], [3, 4]])
    print(np.dot(A, B))
    """
    [[ 7 10]
    [15 22]]
    """

    A = np.mat([[1, 2], [3, 4]])
    B = np.linalg.inv(A)
    print(A)
    """
    [[1 2]
     [3 4]]
    """
    print(B)
    """
    [[-2.   1. ]
     [ 1.5 -0.5]]
    """

    A = np.mat([[1, 1, 1], [0, 2, 5], [2, 5, -1]])
    B = np.mat([[6], [-4], [27]])
    print("计算：A^(-1)B：")
    X = np.linalg.solve(A, B)
    print(X)  # x = 5, y = 3, z = -2 的解
    """
    [[ 5.]
     [ 3.]
     [-2.]]
    """
