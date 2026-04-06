---
title: Python
tags: [python, scripting, ai, data-science]
sources: []
created: 2026-04-07
updated: 2026-04-07
---

# Python

## 語言定位

> Python 是一種膠水語言，以簡潔語法、丰富生態聞名，AI/資料科學領域首選。

## 核心特性

- **直譯語言**：寫完即跑，無需編譯
- **Dynamic typing**：彈性但需小心
- **GIL**：直譯器層級的全域鎖
- **duck typing**：看重行為而非型別
- **pip + venv**：簡單的套件管理

## 語法速查

```python
# 變數（不需要型別宣告）
x = 10
name = "Alice"

# 函式
def add(a: int, b: int) -> int:
    return a + b

# Lambda
square = lambda x: x ** 2

# 類別
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def distance(self, other: 'Point') -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5

# 例外處理
try:
    result = 10 / 0
except ZeroDivisionError:
    print("cannot divide by zero")
finally:
    cleanup()

# 非同步
import asyncio

async def fetch():
    await asyncio.sleep(1)
    return "done"
```

## Python 併發模型

- **threading**：執行緒（有 GIL，CPU-bound 效果差）
- **asyncio**：協作式多工，I/O-bound 友好
- **multiprocessing**：多程序，繞過 GIL
- **concurrent.futures**：統一介面

## Python 生態

| 領域 | 常用庫 |
|------|--------|
| Web 框架 | FastAPI, Django, Flask |
| 資料科學 | pandas, numpy, matplotlib |
| 機器學習 | PyTorch, TensorFlow, scikit-learn |
| 爬蟲 | requests, BeautifulSoup, scrapy |
| 自動化 | selenium, pyautogui |

## 相關概念

- [[concepts/錯誤處理]]
- [[concepts/設計模式]]

## 相關專案

- [[projects/chatbot|Chatbot]] - 可能使用 Python

## 外部資源

- [Python Docs](https://docs.python.org/3/)
- [Real Python](https://realpython.com/)
