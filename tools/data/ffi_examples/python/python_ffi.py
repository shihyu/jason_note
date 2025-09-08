#!/usr/bin/env python3
"""
Python FFI 範例 - 調用 C 函數庫
"""

import ctypes
import os
import sys
from pathlib import Path

# 設定函式庫路徑
lib_path = Path(__file__).parent.parent / 'c_libs'
if sys.platform == 'win32':
    lib_file = lib_path / 'math.dll'
elif sys.platform == 'darwin':
    lib_file = lib_path / 'libmath.dylib'
else:
    lib_file = lib_path / 'libmath.so'

# 載入 C 函式庫
try:
    lib = ctypes.CDLL(str(lib_file))
except OSError as e:
    print(f"錯誤：無法載入函式庫 {lib_file}")
    print(f"請先執行 make 來編譯 C 函式庫")
    sys.exit(1)

# 定義 Point 結構體
class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int),
                ("y", ctypes.c_int)]

# 定義函數簽名
# 基本數學運算
lib.add.argtypes = (ctypes.c_int, ctypes.c_int)
lib.add.restype = ctypes.c_int

lib.factorial.argtypes = (ctypes.c_int,)
lib.factorial.restype = ctypes.c_int

lib.fibonacci.argtypes = (ctypes.c_int,)
lib.fibonacci.restype = ctypes.c_int

# 字串操作
lib.say_hello.argtypes = (ctypes.c_char_p,)
lib.say_hello.restype = None

lib.reverse_string.argtypes = (ctypes.c_char_p,)
lib.reverse_string.restype = None

# 陣列操作
lib.sum_array.argtypes = (ctypes.POINTER(ctypes.c_int), ctypes.c_int)
lib.sum_array.restype = ctypes.c_int

# 結構體相關函數
lib.create_point.argtypes = (ctypes.c_int, ctypes.c_int)
lib.create_point.restype = Point

lib.manhattan_distance.argtypes = (Point, Point)
lib.manhattan_distance.restype = ctypes.c_int

def test_basic_math():
    """測試基本數學運算"""
    print("=== 測試基本數學運算 ===")
    
    # 測試加法
    result = lib.add(10, 20)
    print(f"add(10, 20) = {result}")
    assert result == 30, "加法測試失敗"
    
    # 測試階乘
    fact = lib.factorial(5)
    print(f"factorial(5) = {fact}")
    assert fact == 120, "階乘測試失敗"
    
    # 測試斐波那契
    fib = lib.fibonacci(10)
    print(f"fibonacci(10) = {fib}")
    assert fib == 55, "斐波那契測試失敗"
    
    print("✓ 基本數學運算測試通過\n")

def test_string_operations():
    """測試字串操作"""
    print("=== 測試字串操作 ===")
    
    # 測試打招呼
    lib.say_hello(b"Python")
    
    # 測試字串反轉
    # 注意：需要創建可修改的 c_char 陣列
    test_str = ctypes.create_string_buffer(b"Hello World")
    print(f"原始字串: {test_str.value.decode()}")
    lib.reverse_string(test_str)
    print(f"反轉後: {test_str.value.decode()}")
    assert test_str.value == b"dlroW olleH", "字串反轉測試失敗"
    
    print("✓ 字串操作測試通過\n")

def test_array_operations():
    """測試陣列操作"""
    print("=== 測試陣列操作 ===")
    
    # 創建整數陣列
    arr = (ctypes.c_int * 5)(1, 2, 3, 4, 5)
    
    # 計算陣列總和
    total = lib.sum_array(arr, 5)
    print(f"陣列 [1, 2, 3, 4, 5] 的總和 = {total}")
    assert total == 15, "陣列總和測試失敗"
    
    print("✓ 陣列操作測試通過\n")

def test_struct_operations():
    """測試結構體操作"""
    print("=== 測試結構體操作 ===")
    
    # 創建點
    p1 = lib.create_point(3, 4)
    p2 = lib.create_point(6, 8)
    
    print(f"點1: ({p1.x}, {p1.y})")
    print(f"點2: ({p2.x}, {p2.y})")
    
    # 計算曼哈頓距離
    distance = lib.manhattan_distance(p1, p2)
    print(f"曼哈頓距離 = {distance}")
    assert distance == 7, "曼哈頓距離測試失敗"
    
    print("✓ 結構體操作測試通過\n")

def main():
    """主函數"""
    print("Python FFI 範例 - 調用 C 函數庫\n")
    print(f"使用函式庫: {lib_file}\n")
    
    try:
        test_basic_math()
        test_string_operations()
        test_array_operations()
        test_struct_operations()
        
        print("=" * 40)
        print("✅ 所有測試通過！")
        print("=" * 40)
        
    except AssertionError as e:
        print(f"❌ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()