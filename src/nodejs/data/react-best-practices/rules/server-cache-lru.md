---
title: 跨請求 LRU 快取
impact: HIGH
impactDescription: 跨請求快取
tags: server, 快取, lru, 跨請求
---

## 跨請求 LRU 快取

`React.cache()` 只在單一請求內有效。對於跨連續請求共享的資料（使用者點擊按鈕 A 然後點擊按鈕 B），使用 LRU 快取。

**實作方式：**

```typescript
import { LRUCache } from 'lru-cache'

const cache = new LRUCache<string, any>({
  max: 1000,
  ttl: 5 * 60 * 1000  // 5 分鐘
})

export async function getUser(id: string) {
  const cached = cache.get(id)
  if (cached) return cached

  const user = await db.user.findUnique({ where: { id } })
  cache.set(id, user)
  return user
}

// 請求 1：資料庫查詢，結果被快取
// 請求 2：快取命中，無資料庫查詢
```

當連續的使用者操作在幾秒內訪問需要相同資料的多個端點時使用。

**使用 Vercel 的 [Fluid Compute](https://vercel.com/docs/fluid-compute)：** LRU 快取特別有效，因為多個並發請求可以共享相同的函數實例和快取。這意味著快取可以跨請求持續存在，而無需 Redis 等外部儲存。

**在傳統 serverless 環境中：** 每次調用都在隔離環境中執行，因此考慮使用 Redis 進行跨進程快取。

參考資料：[https://github.com/isaacs/node-lru-cache](https://github.com/isaacs/node-lru-cache)
