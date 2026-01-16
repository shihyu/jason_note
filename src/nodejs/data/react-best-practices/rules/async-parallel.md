---
title: 對獨立操作使用 Promise.all()
impact: CRITICAL
impactDescription: 2-10 倍改善
tags: async, 並行化, promises, 瀑布流
---

## 對獨立操作使用 Promise.all()

當非同步操作沒有相互依賴時，使用 `Promise.all()` 並行執行它們。

**錯誤（循序執行，3 次往返）：**

```typescript
const user = await fetchUser()
const posts = await fetchPosts()
const comments = await fetchComments()
```

**正確（並行執行，1 次往返）：**

```typescript
const [user, posts, comments] = await Promise.all([
  fetchUser(),
  fetchPosts(),
  fetchComments()
])
```
