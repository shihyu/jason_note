---
title: 防止 API 路由中的瀑布流鏈
impact: CRITICAL
impactDescription: 2-10 倍改善
tags: api-routes, server-actions, 瀑布流, 並行化
---

## 防止 API 路由中的瀑布流鏈

在 API 路由和 Server Actions 中，立即啟動獨立操作，即使你還沒有 await 它們。

**錯誤（config 等待 auth，data 等待兩者）：**

```typescript
export async function GET(request: Request) {
  const session = await auth()
  const config = await fetchConfig()
  const data = await fetchData(session.user.id)
  return Response.json({ data, config })
}
```

**正確（auth 和 config 立即啟動）：**

```typescript
export async function GET(request: Request) {
  const sessionPromise = auth()
  const configPromise = fetchConfig()
  const session = await sessionPromise
  const [config, data] = await Promise.all([
    configPromise,
    fetchData(session.user.id)
  ])
  return Response.json({ data, config })
}
```

對於更複雜的依賴鏈，使用 `better-all` 來自動最大化並行性（參見基於依賴的並行化）。
