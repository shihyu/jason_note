import python_native_example

# 1. 測試 Bound<PyList>
# 因為是 PyList，我們可以傳入混合型別，Rust 那邊只負責 iterate 和 print
print("1. 呼叫 print_number_list:")
python_native_example.print_number_list([100, "Hello", 3.14, True])
print("-" * 30)

# 2. 測試 Vec<u64> (自動轉換)
# 這裡必須傳入整數，如果傳入字串 PyO3 會拋出 TypeError
print("\n2. 呼叫 implicit_gil:")
data = [1, 2, 3, 4, 5]
print(f"Python 準備傳送列表: {data}")
python_native_example.implicit_gil(data)
print("-" * 30)

# 3. 測試 explicit_gil (使用 Python API)
print("\n3. 呼叫 explicit_gil:")
python_native_example.explicit_gil()
print("-" * 30)