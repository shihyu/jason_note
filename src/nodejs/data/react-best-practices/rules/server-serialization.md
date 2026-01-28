---
title: 最小化 RSC 邊界的序列化
impact: HIGH
impactDescription: 減少資料傳輸大小
tags: server, rsc, 序列化, props
---

## 最小化 RSC 邊界的序列化

React Server/Client 邊界會將所有物件屬性序列化為字串，並嵌入 HTML 回應和後續的 RSC 請求中。這些序列化的資料直接影響頁面大小和載入時間，因此**大小非常重要**。只傳遞客戶端實際使用的欄位。

**錯誤（序列化所有 50 個欄位）：**

```tsx
async function Page() {
  const user = await fetchUser()  // 50 個欄位
  return <Profile user={user} />
}

'use client'
function Profile({ user }: { user: User }) {
  return <div>{user.name}</div>  // 只使用 1 個欄位
}
```

**正確（只序列化 1 個欄位）：**

```tsx
async function Page() {
  const user = await fetchUser()
  return <Profile name={user.name} />
}

'use client'
function Profile({ name }: { name: string }) {
  return <div>{name}</div>
}
```
