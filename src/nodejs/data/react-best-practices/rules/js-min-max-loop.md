---
title: 使用迴圈而非排序來找最小/最大值
impact: LOW
impactDescription: O(n) 而非 O(n log n)
tags: javascript, 陣列, 效能, 排序, 演算法
---

## 使用迴圈而非排序來找最小/最大值

找出最小或最大元素只需要遍歷陣列一次。排序是浪費且較慢的方式。

**錯誤（O(n log n) - 排序找最新）：**

```typescript
interface Project {
  id: string
  name: string
  updatedAt: number
}

function getLatestProject(projects: Project[]) {
  const sorted = [...projects].sort((a, b) => b.updatedAt - a.updatedAt)
  return sorted[0]
}
```

對整個陣列排序只為了找到最大值。

**錯誤（O(n log n) - 排序找最舊和最新）：**

```typescript
function getOldestAndNewest(projects: Project[]) {
  const sorted = [...projects].sort((a, b) => a.updatedAt - b.updatedAt)
  return { oldest: sorted[0], newest: sorted[sorted.length - 1] }
}
```

當只需要最小/最大值時仍進行不必要的排序。

**正確（O(n) - 單次迴圈）：**

```typescript
function getLatestProject(projects: Project[]) {
  if (projects.length === 0) return null

  let latest = projects[0]

  for (let i = 1; i < projects.length; i++) {
    if (projects[i].updatedAt > latest.updatedAt) {
      latest = projects[i]
    }
  }

  return latest
}

function getOldestAndNewest(projects: Project[]) {
  if (projects.length === 0) return { oldest: null, newest: null }

  let oldest = projects[0]
  let newest = projects[0]

  for (let i = 1; i < projects.length; i++) {
    if (projects[i].updatedAt < oldest.updatedAt) oldest = projects[i]
    if (projects[i].updatedAt > newest.updatedAt) newest = projects[i]
  }

  return { oldest, newest }
}
```

單次遍歷陣列，無複製，無排序。

**替代方案（對小型陣列使用 Math.min/Math.max）：**

```typescript
const numbers = [5, 2, 8, 1, 9]
const min = Math.min(...numbers)
const max = Math.max(...numbers)
```

這對小型陣列有效，但由於展開運算子的限制，對非常大的陣列可能較慢。使用迴圈方法更可靠。
