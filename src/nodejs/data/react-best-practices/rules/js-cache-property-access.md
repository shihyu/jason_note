---
title: 在迴圈中快取屬性存取
impact: LOW-MEDIUM
impactDescription: 減少查詢次數
tags: javascript, 迴圈, 優化, 快取
---

## 在迴圈中快取屬性存取

在熱點路徑中快取物件屬性查詢。

**錯誤（3 次查詢 × N 次迭代）：**

```typescript
for (let i = 0; i < arr.length; i++) {
  process(obj.config.settings.value)
}
```

**正確（總共 1 次查詢）：**

```typescript
const value = obj.config.settings.value
const len = arr.length
for (let i = 0; i < len; i++) {
  process(value)
}
```
