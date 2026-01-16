---
title: 函數提前返回
impact: LOW-MEDIUM
impactDescription: 避免不必要的運算
tags: javascript, 函數, 優化, 提前返回
---

## 函數提前返回

當結果已確定時提前返回，跳過不必要的處理。

**錯誤（找到答案後仍處理所有項目）：**

```typescript
function validateUsers(users: User[]) {
  let hasError = false
  let errorMessage = ''

  for (const user of users) {
    if (!user.email) {
      hasError = true
      errorMessage = 'Email required'
    }
    if (!user.name) {
      hasError = true
      errorMessage = 'Name required'
    }
    // 即使已發現錯誤，仍繼續檢查所有使用者
  }

  return hasError ? { valid: false, error: errorMessage } : { valid: true }
}
```

**正確（發現第一個錯誤時立即返回）：**

```typescript
function validateUsers(users: User[]) {
  for (const user of users) {
    if (!user.email) {
      return { valid: false, error: 'Email required' }
    }
    if (!user.name) {
      return { valid: false, error: 'Name required' }
    }
  }

  return { valid: true }
}
```
