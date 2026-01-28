---
title: 為重複查詢建立索引 Map
impact: LOW-MEDIUM
impactDescription: 100 萬次操作降為 2 千次
tags: javascript, map, 索引, 優化, 效能
---

## 為重複查詢建立索引 Map

多次使用相同鍵進行 `.find()` 查詢時應使用 Map。

**錯誤（每次查詢 O(n)）：**

```typescript
function processOrders(orders: Order[], users: User[]) {
  return orders.map(order => ({
    ...order,
    user: users.find(u => u.id === order.userId)
  }))
}
```

**正確（每次查詢 O(1)）：**

```typescript
function processOrders(orders: Order[], users: User[]) {
  const userById = new Map(users.map(u => [u.id, u]))

  return orders.map(order => ({
    ...order,
    user: userById.get(order.userId)
  }))
}
```

建立 Map 一次（O(n)），之後所有查詢都是 O(1)。
對於 1000 筆訂單 × 1000 個使用者：100 萬次操作 → 2 千次操作。
