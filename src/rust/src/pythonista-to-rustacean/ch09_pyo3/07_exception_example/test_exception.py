import exception_example

try:
    exception_example.validate_input("good")
    print("Input is valid!")
    # 注意，我們是透過 `exception_example.InvalidInputError` 完整路徑來捕捉
except exception_example.InvalidInputError as e:
    print(f"Caught an error: {e}")
# 會引發例外的呼叫
try:
    exception_example.validate_input("bad")
except exception_example.InvalidInputError as e:
    print(f"Caught an error: {e}")

# --- 1. 成功呼叫的範例 ---
# 一個符合 User 結構的 JSON 字串
valid_json = '{"name": "Alice", "age": 30}'

try:
    # 呼叫 Rust 函式
    name, age = exception_example.user_from_json(valid_json)
    
    print("✅ 解析成功！")
    print(f"   - 姓名 (Name): {name}")
    print(f"   - 年齡 (Age): {age}")
    
    # 驗證回傳的型別
    print(f"   - 姓名型別 (Name type): {type(name)}")
    print(f"   - 年齡型別 (Age type): {type(age)}")

except ValueError as e:
    print(f"❌ 預期成功，但解析失敗: {e}")

print("-" * 20)

# --- 2. 失敗呼叫的範例 (捕捉例外) ---
# 一個格式錯誤的 JSON (age 的值是字串，但 Rust 中定義為 u8)
invalid_json = '{"name": "Bob", "age": "twenty"}'

try:
    print("⏳ 嘗試解析一個無效的 JSON...")
    exception_example.user_from_json(invalid_json)

except ValueError as e:
    # 這裡的 ValueError 就是從 Rust 的 PyValueError::new_err() 轉換過來的
    print("✅ 成功捕捉到預期的例外！")
    print(f"   - 例外類型 (Exception type): {type(e)}")
    print(f"   - 錯誤訊息 (Error message): {e}")
