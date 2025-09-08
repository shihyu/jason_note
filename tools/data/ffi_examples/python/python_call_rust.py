#!/usr/bin/env python3
"""
Python 調用 Rust 函式庫範例
"""

import ctypes
import platform
import sys
from pathlib import Path

# 設定 Rust 函式庫路徑
lib_path = Path(__file__).parent.parent / 'rust_libs' / 'rust_lib' / 'target' / 'release'
system = platform.system()

if system == "Linux":
    lib_file = lib_path / 'librust_lib.so'
elif system == "Darwin":  # macOS
    lib_file = lib_path / 'librust_lib.dylib'
elif system == "Windows":
    lib_file = lib_path / 'rust_lib.dll'
else:
    print(f"不支援的系統: {system}")
    sys.exit(1)

# 載入 Rust 函式庫
try:
    lib = ctypes.CDLL(str(lib_file))
except OSError as e:
    print(f"錯誤：無法載入函式庫 {lib_file}")
    print(f"請先執行 make 來編譯 Rust 函式庫")
    sys.exit(1)

# 定義 RustVector 結構體
class RustVector(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double),
                ("y", ctypes.c_double)]

# 定義函數簽名
# 基本數學運算
lib.rust_add.argtypes = (ctypes.c_int, ctypes.c_int)
lib.rust_add.restype = ctypes.c_int

lib.rust_multiply.argtypes = (ctypes.c_int, ctypes.c_int)
lib.rust_multiply.restype = ctypes.c_int

lib.rust_sqrt.argtypes = (ctypes.c_double,)
lib.rust_sqrt.restype = ctypes.c_double

lib.rust_is_prime.argtypes = (ctypes.c_int,)
lib.rust_is_prime.restype = ctypes.c_int

# 字串操作
lib.rust_greet.argtypes = (ctypes.c_char_p,)
lib.rust_greet.restype = ctypes.c_void_p  # 返回指標

lib.rust_free_string.argtypes = (ctypes.c_void_p,)
lib.rust_free_string.restype = None

lib.rust_utf8_char_count.argtypes = (ctypes.c_char_p,)
lib.rust_utf8_char_count.restype = ctypes.c_int

# 陣列操作
lib.rust_array_average.argtypes = (ctypes.POINTER(ctypes.c_double), ctypes.c_int)
lib.rust_array_average.restype = ctypes.c_double

lib.rust_array_max.argtypes = (ctypes.POINTER(ctypes.c_int), ctypes.c_int)
lib.rust_array_max.restype = ctypes.c_int

# 向量操作
lib.rust_create_vector.argtypes = (ctypes.c_double, ctypes.c_double)
lib.rust_create_vector.restype = RustVector

lib.rust_vector_length.argtypes = (RustVector,)
lib.rust_vector_length.restype = ctypes.c_double

lib.rust_vector_add.argtypes = (RustVector, RustVector)
lib.rust_vector_add.restype = RustVector

def test_basic_math():
    """測試基本數學運算"""
    print("=== 測試 Rust 基本數學運算 ===")
    
    # 測試加法和乘法
    result = lib.rust_add(5, 3)
    print(f"rust_add(5, 3) = {result}")
    assert result == 8, "加法測試失敗"
    
    result = lib.rust_multiply(4, 7)
    print(f"rust_multiply(4, 7) = {result}")
    assert result == 28, "乘法測試失敗"
    
    # 測試平方根
    result = lib.rust_sqrt(16.0)
    print(f"rust_sqrt(16.0) = {result}")
    assert result == 4.0, "平方根測試失敗"
    
    # 測試質數判斷
    primes = [2, 3, 5, 7, 11, 13, 17, 19]
    non_primes = [1, 4, 6, 8, 9, 10, 12, 15]
    
    for p in primes:
        assert lib.rust_is_prime(p) == 1, f"{p} 應該是質數"
    for np in non_primes:
        assert lib.rust_is_prime(np) == 0, f"{np} 不應該是質數"
    
    print("質數判斷測試通過")
    print("✓ 基本數學運算測試通過\n")

def test_string_operations():
    """測試字串操作"""
    print("=== 測試 Rust 字串操作 ===")
    
    # 測試問候語生成
    greeting_ptr = lib.rust_greet(b"Python")
    if greeting_ptr:
        # 將指標轉換為字串
        greeting = ctypes.cast(greeting_ptr, ctypes.c_char_p).value.decode('utf-8')
        print(f"Rust 問候語: {greeting}")
        assert "Hello, Python from Rust!" == greeting, "問候語測試失敗"
        
        # 釋放 Rust 分配的記憶體
        lib.rust_free_string(greeting_ptr)
    
    # 測試 UTF-8 字元計數
    test_strings = [
        (b"Hello", 5),
        (b"", 0),
        ("你好世界".encode('utf-8'), 4),  # 中文字元
        ("😀😁😂".encode('utf-8'), 3),    # Emoji
    ]
    
    for s, expected_count in test_strings:
        count = lib.rust_utf8_char_count(s)
        print(f"字串 '{s.decode('utf-8') if s else ''}' 的字元數: {count}")
        assert count == expected_count, f"UTF-8 字元計數測試失敗: {s}"
    
    print("✓ 字串操作測試通過\n")

def test_array_operations():
    """測試陣列操作"""
    print("=== 測試 Rust 陣列操作 ===")
    
    # 測試平均值計算
    double_arr = (ctypes.c_double * 5)(1.0, 2.0, 3.0, 4.0, 5.0)
    avg = lib.rust_array_average(double_arr, 5)
    print(f"陣列 [1.0, 2.0, 3.0, 4.0, 5.0] 的平均值 = {avg}")
    assert avg == 3.0, "平均值測試失敗"
    
    # 測試最大值查找
    int_arr = (ctypes.c_int * 7)(3, 7, 2, 9, 1, 5, 8)
    max_val = lib.rust_array_max(int_arr, 7)
    print(f"陣列 [3, 7, 2, 9, 1, 5, 8] 的最大值 = {max_val}")
    assert max_val == 9, "最大值測試失敗"
    
    print("✓ 陣列操作測試通過\n")

def test_vector_operations():
    """測試向量操作"""
    print("=== 測試 Rust 向量操作 ===")
    
    # 創建向量
    v1 = lib.rust_create_vector(3.0, 4.0)
    v2 = lib.rust_create_vector(1.0, 2.0)
    
    print(f"向量1: ({v1.x}, {v1.y})")
    print(f"向量2: ({v2.x}, {v2.y})")
    
    # 計算向量長度
    length = lib.rust_vector_length(v1)
    print(f"向量1 的長度 = {length}")
    assert length == 5.0, "向量長度測試失敗"
    
    # 向量相加
    v3 = lib.rust_vector_add(v1, v2)
    print(f"向量1 + 向量2 = ({v3.x}, {v3.y})")
    assert v3.x == 4.0 and v3.y == 6.0, "向量相加測試失敗"
    
    print("✓ 向量操作測試通過\n")

def main():
    """主函數"""
    print("Python 調用 Rust 函式庫範例\n")
    print(f"使用函式庫: {lib_file}\n")
    
    try:
        test_basic_math()
        test_string_operations()
        test_array_operations()
        test_vector_operations()
        
        print("=" * 40)
        print("✅ 所有 Rust FFI 測試通過！")
        print("=" * 40)
        
    except AssertionError as e:
        print(f"❌ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()