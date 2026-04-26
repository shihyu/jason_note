from static_method_example import RedEnvelope

# 直接用類別 RedEnvelope 呼叫，取得一個超級吉利紅包
super_envelope = RedEnvelope.super_lucky()
print(f"超級吉利紅包：{super_envelope.amount}") # 888


class GoldenEnvelope(RedEnvelope):
    def __new__(cls, amount):
        # 金紅包的金額自動加倍
        # 呼叫父類別的建構子，但傳入的是加倍後的金額
        return super().__new__(cls, amount * 2)

# 注意，我們是透過子類別 GoldenEnvelope 來呼叫 from_blessing
golden_envelope = GoldenEnvelope.from_blessing("發發發")

# 因為 cls 代表 GoldenEnvelope，所以 __new__ 的加倍邏輯會被正確執行
print(golden_envelope.amount)  # 輸出 1776 (888 * 2)

# 雖然 __new__ 的邏輯有執行，但因為 Rust 端函式最後 .extract::<Self>()
# 的限制，最終回傳的物件型別會被「還原」成父類別 RedEnvelope。
print(type(golden_envelope))   # <class 'class_example.RedEnvelope'>