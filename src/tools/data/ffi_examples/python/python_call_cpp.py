#!/usr/bin/env python3
"""
Python 調用 C++ 函式庫範例
"""

import ctypes
import os
import sys
from pathlib import Path

# 設定 LD_LIBRARY_PATH 以找到 libmath.so
lib_dir = Path(__file__).parent.parent / 'c_libs'
if 'LD_LIBRARY_PATH' in os.environ:
    os.environ['LD_LIBRARY_PATH'] = f"{lib_dir}:{os.environ['LD_LIBRARY_PATH']}"
else:
    os.environ['LD_LIBRARY_PATH'] = str(lib_dir)

# 設定函式庫路徑
lib_path = Path(__file__).parent.parent / 'c_libs'
if sys.platform == 'win32':
    lib_file = lib_path / 'cpp_wrapper.dll'
elif sys.platform == 'darwin':
    lib_file = lib_path / 'libcpp_wrapper.dylib'
else:
    lib_file = lib_path / 'libcpp_wrapper.so'

# 載入 C++ 函式庫
try:
    lib = ctypes.CDLL(str(lib_file))
except OSError as e:
    print(f"錯誤：無法載入函式庫 {lib_file}")
    print(f"請先執行 make 來編譯 C++ 函式庫")
    sys.exit(1)

# Calculator 類別函數簽名
lib.Calculator_new.argtypes = (ctypes.c_char_p,)
lib.Calculator_new.restype = ctypes.c_void_p

lib.Calculator_delete.argtypes = (ctypes.c_void_p,)
lib.Calculator_delete.restype = None

lib.Calculator_multiply.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
lib.Calculator_multiply.restype = ctypes.c_int

lib.Calculator_divide.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
lib.Calculator_divide.restype = ctypes.c_int

lib.Calculator_add_and_factorial.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
lib.Calculator_add_and_factorial.restype = ctypes.c_int

lib.Calculator_power.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
lib.Calculator_power.restype = ctypes.c_int

lib.Calculator_get_history_size.argtypes = (ctypes.c_void_p,)
lib.Calculator_get_history_size.restype = ctypes.c_int

lib.Calculator_get_history_item.argtypes = (ctypes.c_void_p, ctypes.c_int)
lib.Calculator_get_history_item.restype = ctypes.c_int

lib.Calculator_clear_history.argtypes = (ctypes.c_void_p,)
lib.Calculator_clear_history.restype = None

lib.Calculator_sum_history.argtypes = (ctypes.c_void_p,)
lib.Calculator_sum_history.restype = ctypes.c_int

# 字串處理函數簽名
lib.cpp_to_upper.argtypes = (ctypes.c_char_p,)
lib.cpp_to_upper.restype = ctypes.POINTER(ctypes.c_char)

lib.cpp_to_lower.argtypes = (ctypes.c_char_p,)
lib.cpp_to_lower.restype = ctypes.POINTER(ctypes.c_char)

lib.cpp_repeat_string.argtypes = (ctypes.c_char_p, ctypes.c_int)
lib.cpp_repeat_string.restype = ctypes.POINTER(ctypes.c_char)

lib.cpp_free_string.argtypes = (ctypes.POINTER(ctypes.c_char),)
lib.cpp_free_string.restype = None

# 其他函數簽名
lib.cpp_fibonacci_sum.argtypes = (ctypes.c_int,)
lib.cpp_fibonacci_sum.restype = ctypes.c_int

lib.cpp_calculate_distance.argtypes = (ctypes.c_double, ctypes.c_double, 
                                       ctypes.c_double, ctypes.c_double)
lib.cpp_calculate_distance.restype = ctypes.c_double

lib.cpp_sort_array.argtypes = (ctypes.POINTER(ctypes.c_int), ctypes.c_int)
lib.cpp_sort_array.restype = ctypes.POINTER(ctypes.c_int)

lib.cpp_free_array.argtypes = (ctypes.POINTER(ctypes.c_int),)
lib.cpp_free_array.restype = None

class Calculator:
    """Python 封裝的 C++ Calculator 類別"""
    
    def __init__(self, name="Python Calculator"):
        self.obj = lib.Calculator_new(name.encode('utf-8'))
    
    def __del__(self):
        if hasattr(self, 'obj') and self.obj:
            lib.Calculator_delete(self.obj)
    
    def multiply(self, a, b):
        return lib.Calculator_multiply(self.obj, a, b)
    
    def divide(self, a, b):
        return lib.Calculator_divide(self.obj, a, b)
    
    def add_and_factorial(self, a, b):
        return lib.Calculator_add_and_factorial(self.obj, a, b)
    
    def power(self, base, exp):
        return lib.Calculator_power(self.obj, base, exp)
    
    def get_history(self):
        size = lib.Calculator_get_history_size(self.obj)
        history = []
        for i in range(size):
            history.append(lib.Calculator_get_history_item(self.obj, i))
        return history
    
    def clear_history(self):
        lib.Calculator_clear_history(self.obj)
    
    def sum_history(self):
        return lib.Calculator_sum_history(self.obj)

def test_calculator():
    """測試 Calculator 類別"""
    print("=== 測試 C++ Calculator 類別 ===")
    
    calc = Calculator("測試計算器")
    
    # 測試基本運算
    result = calc.multiply(6, 7)
    print(f"6 * 7 = {result}")
    assert result == 42, "乘法測試失敗"
    
    result = calc.divide(20, 4)
    print(f"20 / 4 = {result}")
    assert result == 5, "除法測試失敗"
    
    # 測試混合 C/C++ 功能
    result = calc.add_and_factorial(3, 2)
    print(f"factorial(3 + 2) = {result}")
    assert result == 120, "混合運算測試失敗"
    
    # 測試冪次方
    result = calc.power(2, 8)
    print(f"2^8 = {result}")
    assert result == 256, "冪次方測試失敗"
    
    # 測試歷史記錄
    history = calc.get_history()
    print(f"運算歷史: {history}")
    assert len(history) == 3, "歷史記錄數量錯誤"  # multiply, divide, power
    
    sum_hist = calc.sum_history()
    print(f"歷史記錄總和: {sum_hist}")
    
    calc.clear_history()
    history = calc.get_history()
    assert len(history) == 0, "清除歷史記錄失敗"
    
    print("✓ Calculator 類別測試通過\n")

def test_string_operations():
    """測試字串處理"""
    print("=== 測試 C++ 字串處理 ===")
    
    # 測試轉大寫
    result_ptr = lib.cpp_to_upper(b"hello world")
    result = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode('utf-8')
    print(f"轉大寫: 'hello world' -> '{result}'")
    assert result == "HELLO WORLD", "轉大寫測試失敗"
    lib.cpp_free_string(result_ptr)
    
    # 測試轉小寫
    result_ptr = lib.cpp_to_lower(b"HELLO WORLD")
    result = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode('utf-8')
    print(f"轉小寫: 'HELLO WORLD' -> '{result}'")
    assert result == "hello world", "轉小寫測試失敗"
    lib.cpp_free_string(result_ptr)
    
    # 測試重複字串
    result_ptr = lib.cpp_repeat_string(b"abc", 3)
    result = ctypes.cast(result_ptr, ctypes.c_char_p).value.decode('utf-8')
    print(f"重複字串: 'abc' * 3 = '{result}'")
    assert result == "abcabcabc", "重複字串測試失敗"
    lib.cpp_free_string(result_ptr)
    
    print("✓ 字串處理測試通過\n")

def test_advanced_operations():
    """測試進階運算"""
    print("=== 測試 C++ 進階運算 ===")
    
    # 測試斐波那契數列總和
    result = lib.cpp_fibonacci_sum(10)
    print(f"前 10 個斐波那契數的總和 = {result}")
    # 0+1+1+2+3+5+8+13+21+34+55 = 143
    assert result == 143, "斐波那契總和測試失敗"
    
    # 測試距離計算
    distance = lib.cpp_calculate_distance(0.0, 0.0, 3.0, 4.0)
    print(f"點 (0,0) 到 (3,4) 的距離 = {distance}")
    assert abs(distance - 5.0) < 0.001, "距離計算測試失敗"
    
    # 測試陣列排序
    arr = (ctypes.c_int * 5)(5, 2, 8, 1, 9)
    sorted_ptr = lib.cpp_sort_array(arr, 5)
    
    sorted_arr = []
    for i in range(5):
        sorted_arr.append(sorted_ptr[i])
    
    print(f"排序前: [5, 2, 8, 1, 9]")
    print(f"排序後: {sorted_arr}")
    assert sorted_arr == [1, 2, 5, 8, 9], "陣列排序測試失敗"
    
    lib.cpp_free_array(sorted_ptr)
    
    print("✓ 進階運算測試通過\n")

def main():
    """主函數"""
    print("Python 調用 C++ 函式庫範例\n")
    print(f"使用函式庫: {lib_file}\n")
    
    try:
        test_calculator()
        test_string_operations()
        test_advanced_operations()
        
        print("=" * 40)
        print("✅ 所有 C++ FFI 測試通過！")
        print("=" * 40)
        
    except AssertionError as e:
        print(f"❌ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()