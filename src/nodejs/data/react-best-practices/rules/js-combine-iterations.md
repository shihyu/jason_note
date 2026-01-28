---
title: 合併多次陣列迭代
impact: LOW-MEDIUM
impactDescription: 減少迭代次數
tags: javascript, 陣列, 迴圈, 效能
---

## 合併多次陣列迭代

多個 `.filter()` 或 `.map()` 呼叫會多次迭代陣列。將它們合併成一個迴圈。

**錯誤（3 次迭代）：**

```typescript
const admins = users.filter(u => u.isAdmin)
const testers = users.filter(u => u.isTester)
const inactive = users.filter(u => !u.isActive)
```

**正確（1 次迭代）：**

```typescript
const admins: User[] = []
const testers: User[] = []
const inactive: User[] = []

for (const user of users) {
  if (user.isAdmin) admins.push(user)
  if (user.isTester) testers.push(user)
  if (!user.isActive) inactive.push(user)
}
```
