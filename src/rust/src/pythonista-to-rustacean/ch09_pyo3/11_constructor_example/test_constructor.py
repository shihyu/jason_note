from constructor_example import RedEnvelope

# 測試錯誤處理
try:
    RedEnvelope(amount=0)
except ValueError as e:
    print(f"建立失敗: {e}")

# 測試單例模式
lucky_a = RedEnvelope(amount=888)
lucky_b = RedEnvelope(amount=888)
print(f"兩個幸運紅包是同一個物件: {lucky_a is lucky_b}")

# 測試一般實例
normal_a = RedEnvelope(amount=100)
normal_b = RedEnvelope(amount=100)
print(f"兩個普通紅包是同一個物件: {normal_a is normal_b}")