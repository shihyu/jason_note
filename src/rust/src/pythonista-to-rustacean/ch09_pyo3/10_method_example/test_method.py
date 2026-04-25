from method_example import RedEnvelope

# 創建一個 88 塊的紅包
envelope = RedEnvelope(88)
print("得到了一個 88 元的紅包")

# 再加 12 塊，湊個整數
envelope.add_money(12)
print("紅包 88 + 12 =", envelope.amount) # 100

# 拿走 20 塊
envelope.take_money(20)
print("紅包被抽走 20 =", envelope.amount) # 80