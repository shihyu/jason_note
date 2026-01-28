---
title: 延遲 Await 直到需要時
impact: HIGH
impactDescription: 避免阻塞未使用的程式碼路徑
tags: async, await, 條件式, 優化
---

## 延遲 Await 直到需要時

將 `await` 操作移到實際使用它們的分支中，以避免阻塞不需要它們的程式碼路徑。

**錯誤（阻塞兩個分支）：**

```typescript
async function handleRequest(userId: string, skipProcessing: boolean) {
  const userData = await fetchUserData(userId)

  if (skipProcessing) {
    // 立即返回但仍然等待了 userData
    return { skipped: true }
  }

  // 只有這個分支使用 userData
  return processUserData(userData)
}
```

**正確（只在需要時阻塞）：**

```typescript
async function handleRequest(userId: string, skipProcessing: boolean) {
  if (skipProcessing) {
    // 立即返回而不等待
    return { skipped: true }
  }

  // 只在需要時擷取
  const userData = await fetchUserData(userId)
  return processUserData(userData)
}
```

**另一個範例（提早返回優化）：**

```typescript
// 錯誤：總是擷取權限
async function updateResource(resourceId: string, userId: string) {
  const permissions = await fetchPermissions(userId)
  const resource = await getResource(resourceId)

  if (!resource) {
    return { error: 'Not found' }
  }

  if (!permissions.canEdit) {
    return { error: 'Forbidden' }
  }

  return await updateResourceData(resource, permissions)
}

// 正確：只在需要時擷取
async function updateResource(resourceId: string, userId: string) {
  const resource = await getResource(resourceId)

  if (!resource) {
    return { error: 'Not found' }
  }

  const permissions = await fetchPermissions(userId)

  if (!permissions.canEdit) {
    return { error: 'Forbidden' }
  }

  return await updateResourceData(resource, permissions)
}
```

當跳過的分支經常被執行，或當延遲的操作很昂貴時，這種優化特別有價值。
