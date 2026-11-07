# 依賴注入與測試邊界：Python 範例對照

這份文件說明兩個原則：讓物件從外部取得依賴，以及讓測試替身留在測試程式中。以下用使用者查詢與圖書借閱作為簡單範例。

## 一、依賴注入取代全域變數

「依賴」是函式完成工作所需的其他物件，例如資料庫、通知服務、時鐘或設定。「注入」是由呼叫端將物件傳入。

### 直接讀全域物件

```python
# app.py
db = RealDatabase()


def get_user(user_id):
    return db.find_user(user_id)
```

`get_user()` 的參數看不出它需要資料庫。測試若修改 `app.db`，同一個 Python 行程內的其他呼叫也會受到影響；匯入模組時還可能直接建立真實連線。

### 由呼叫端傳入依賴

```python
# users.py
def get_user(user_id, db):
    return db.find_user(user_id)


# main.py：正式入口負責建立真實依賴
db = RealDatabase()
user = get_user(7, db)


# tests/test_users.py：測試只傳入測試替身
class FakeDatabase:
    def find_user(self, user_id):
        return {"id": user_id, "name": "小林"}


assert get_user(7, FakeDatabase()) == {"id": 7, "name": "小林"}
```

`get_user()` 的執行路徑只有一條。正式入口決定傳入 `RealDatabase`，測試決定傳入 `FakeDatabase`；兩者不需改動全域狀態。

| 比較 | 直接讀全域物件 | 由呼叫端傳入 |
| --- | --- | --- |
| 依賴是否可見 | 藏在函式內 | 出現在參數或建構子 |
| 測試如何替換 | 修改模組屬性或使用 `patch` | 傳入測試替身 |
| 多個實例 | 容易共用同一份可變狀態 | 可各自持有不同依賴 |
| 建立真實連線的時機 | 可能發生在匯入時 | 由正式入口控制 |

## 二、測試專用程式碼不進正式流程

正式業務邏輯不必辨識「我正在執行測試」。正式程式可以定義正式環境與測試共同使用的介面或方法；測試替身與測試情境則放在 `tests/`。

### 在正式借閱流程加入測試開關

```python
def borrow_book(book_id, member_id, loans, skip_eligibility_check=False):
    if not skip_eligibility_check:  # 為了測試而新增的正式分支
        check_eligibility(member_id)
    loans.record(book_id, member_id)


# 測試方便，但正式呼叫端也可能傳入 True。
borrow_book("BOOK-7", "MEMBER-3", loans, skip_eligibility_check=True)
```

這個設計讓測試走一條跳過檢查的路，無法證明正式借閱時有執行資格檢查。

### 讓測試替換外部依賴，保留同一條流程

```python
# borrowing.py：正式邏輯
def borrow_book(book_id, member_id, eligibility_checker, loans):
    eligibility_checker.check(member_id)
    loans.record(book_id, member_id)


# main.py：正式入口
borrow_book("BOOK-7", "MEMBER-3", RealEligibilityChecker(), RealLoanRepository())


# tests/test_borrowing.py：測試替身只存在於 tests/
class FakeEligibilityChecker:
    def __init__(self):
        self.checked = []

    def check(self, member_id):
        self.checked.append(member_id)


class FakeLoanRepository:
    def __init__(self):
        self.recorded = []

    def record(self, book_id, member_id):
        self.recorded.append((book_id, member_id))


checker = FakeEligibilityChecker()
loans = FakeLoanRepository()
borrow_book("BOOK-7", "MEMBER-3", checker, loans)
assert checker.checked == ["MEMBER-3"]
assert loans.recorded == [("BOOK-7", "MEMBER-3")]
```

| 比較 | 測試開關放在正式流程 | 測試替身留在 `tests/` |
| --- | --- | --- |
| 正式程式是否有測試專用分支 | 有 | 無 |
| 測試是否執行相同的業務步驟 | 可能跳過 | 是 |
| 測試是否寫入真實借閱紀錄 | 開關只略過檢查，仍須另行替換借閱儲存庫 | 測試替身只記錄呼叫，不會寫入正式資料庫 |

## 套用原則

- 由正式入口建立資料庫與其他外部服務，再傳入需要它們的函式或物件。
- 資格檢查屬於正式借閱流程；測試應替換檢查器與借閱資料庫，確認檢查與紀錄都確實發生。
- 若正式模組保留只供舊測試使用 `patch` 替換的名稱，應評估能否改用依賴注入提供測試替身。

共同使用的介面或方法可以放在正式程式；測試專用的替身、假資料與斷言應放在 `tests/`。
