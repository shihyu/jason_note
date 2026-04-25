from getter_setter_example import RedEnvelope

envelope = RedEnvelope(888)

try:
    # 這裡會呼叫 Rust 裡的 set_amount 函式，並觸發檢查
    envelope.amount = 0
except ValueError as e:
    # 成功攔截到錯誤！
    print(e) # 輸出：紅包金額不能少於 1 塊錢，不要跟我說什麼一元復始！

try:
    # 這裡會呼叫 Rust 裡的 update_value 函式，並觸發檢查
    envelope.bling_bling = 999
    print(f"使用 update_value 成功更新為 {envelope.amount}")
except ValueError as e:
    print(e) 
