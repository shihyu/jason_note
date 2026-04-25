# 假設上述 Rust 程式碼已編譯為 enum2class_example
from enum2class_example import * 

# 模擬一個權限不足的呼叫
status_code = run_cli_tool("sudo apt update", as_root=False)

# 在 Python 中，可以直接與整數進行比較
if status_code != 0:
    print("執行時發生錯誤！")
    if status_code == 126:
        print("錯誤原因: 權限不足")

# 同時，也可以與 enum 成員本身進行比較，保有可讀性。
# PyO3 確保了這兩種比較方式的結果是一致的。
assert status_code == ExitCode.PermissionDenied
assert (status_code == 126) == (status_code == ExitCode.PermissionDenied) # True

email = create_notification("user@example.com")
sms = create_notification("+886912345678")

def send_notification(notif: Notification):
    # 使用 isinstance 進行類型檢查
    if isinstance(notif, Notification.Email):
        print(f"發送郵件給 {notif.recipient}，主旨：{notif.subject}")
        return

    # 也可以使用 match
    match notif:
        case Notification.Sms(_0=phone_number):
            # ._0 代表元組變體的第一個欄位
            print(f"發送簡訊到 {phone_number}")
        case Notification.NoOp():
            print("無操作")
        case _:
            print("未知的通知類型")

send_notification(email)
send_notification(sms)
