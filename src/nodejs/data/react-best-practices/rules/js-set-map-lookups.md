---
title: 使用 Set/Map 進行 O(1) 查詢
impact: LOW-MEDIUM
impactDescription: O(n) 降為 O(1)
tags: javascript, set, map, 資料結構, 效能
---

## 使用 Set/Map 進行 O(1) 查詢

將陣列轉換為 Set/Map 以進行重複的成員檢查。

**錯誤（每次檢查 O(n)）：**

```typescript
const allowedIds = ['a', 'b', 'c', ...]
items.filter(item => allowedIds.includes(item.id))
```

**正確（每次檢查 O(1)）：**

```typescript
const allowedIds = new Set(['a', 'b', 'c', ...])
items.filter(item => allowedIds.has(item.id))
```
