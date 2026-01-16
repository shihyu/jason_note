---
title: 使用 React.cache() 進行請求內去重
impact: MEDIUM
impactDescription: 請求內去重
tags: server, 快取, react-cache, 去重
---

## 使用 React.cache() 進行請求內去重

使用 `React.cache()` 進行伺服器端請求去重。認證和資料庫查詢最能受益。

**使用方式：**

```typescript
import { cache } from 'react'

export const getCurrentUser = cache(async () => {
  const session = await auth()
  if (!session?.user?.id) return null
  return await db.user.findUnique({
    where: { id: session.user.id }
  })
})
```

在單一請求中，多次呼叫 `getCurrentUser()` 只會執行一次查詢。
